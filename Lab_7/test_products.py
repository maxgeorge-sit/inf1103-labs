# Checks for the Lab 7 product classes.
# Run it from your project folder with:  python test_products.py

import contextlib
import io
import os
import tempfile

from inventory_manager import (
    INVENTORY_FILE,
    DigitalProduct,
    Inventory,
    PhysicalProduct,
    Product,
    load_inventory,
    save_inventory,
)

results = []


def check(passed, description):
    # Records one check and prints PASS or FAIL next to what was checked.
    results.append(passed)
    if passed:
        print(f"PASS: {description}")
    else:
        print(f"FAIL: {description}")


def show_heading(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def printed_by(method):
    # Runs a method and returns the text it printed, so a check can read it.
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        method()
    return buffer.getvalue()


def test_physical_product():
    show_heading("Physical products store and display their weight")
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 5, 3.5)

    output = printed_by(guitar.display_information)
    print("guitar.display_information() prints:")
    print(output)
    print("print(guitar) prints:")
    print(guitar)
    print()

    check(isinstance(guitar, Product), "a PhysicalProduct is-a Product")
    check(guitar.get_weight() == 3.5, "the weight is stored")
    check("Name: Guitar" in output, "the shared product details are displayed")
    check("Weight: 3.50 kg" in output, "the weight is displayed")
    check("Weight: 3.50 kg" in str(guitar), "print(guitar) shows the weight too")

    try:
        PhysicalProduct("P006", "Broken Item", 1.00, 1, -2)
        check(False, "a negative weight is refused")
    except ValueError:
        check(True, "a negative weight is refused")


def test_digital_product():
    show_heading("Digital products store and display their download size")
    operating_system = DigitalProduct("D002", "Operating System", 139.99, 50, 4500)

    output = printed_by(operating_system.display_information)
    print("operating_system.display_information() prints:")
    print(output)
    print("print(operating_system) prints:")
    print(operating_system)
    print()

    check(isinstance(operating_system, Product), "a DigitalProduct is-a Product")
    check(operating_system.get_download_size() == 4500, "the download size is stored")
    check("Name: Operating System" in output, "the shared product details are displayed")
    check("Download Size: 4500.00 MB" in output, "the download size is displayed")
    check(
        "Download Size: 4500.00 MB" in str(operating_system),
        "print(operating_system) shows the download size too",
    )

    try:
        DigitalProduct("D003", "Empty Download", 1.00, 1, 0)
        check(False, "a download size of 0 is refused")
    except ValueError:
        check(True, "a download size of 0 is refused")


def test_fulfilment_info():
    show_heading("Both subclasses implement get_fulfilment_info()")
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 5, 3.5)
    operating_system = DigitalProduct("D002", "Operating System", 139.99, 50, 4500)

    print(f"Guitar: {guitar.get_fulfilment_info()}")
    print(f"Operating System: {operating_system.get_fulfilment_info()}")
    print()

    check("shipping" in guitar.get_fulfilment_info(), "PhysicalProduct says it is shipped")
    check(
        "digitally" in operating_system.get_fulfilment_info(),
        "DigitalProduct says it is delivered digitally",
    )


def test_abstract_product():
    show_heading("The abstract Product class cannot be created directly")

    try:
        Product("X001", "Mystery Item", 10.00, 1)
        check(False, "creating a Product directly is refused")
    except TypeError as error:
        print(f"TypeError: {error}")
        print()
        check(True, "creating a Product directly is refused")

    # A subclass that leaves out the abstract method is refused as well.
    class UnfinishedProduct(Product):
        pass

    try:
        UnfinishedProduct("X002", "Unfinished Item", 10.00, 1)
        check(False, "a subclass without get_fulfilment_info() is refused")
    except TypeError:
        check(True, "a subclass without get_fulfilment_info() is refused")


def test_inventory_operations():
    show_heading("Inventory operations continue to work")
    inventory = Inventory()
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 5, 3.5)
    operating_system = DigitalProduct("D002", "Operating System", 139.99, 50, 4500)

    added_guitar = inventory.add_product(guitar)
    added_system = inventory.add_product(operating_system)
    added_copy = inventory.add_product(DigitalProduct("p005", "Copy", 1.00, 1, 1))
    found = inventory.search_product("d002")
    if found is not None:
        found.update_stock(45)

    output = printed_by(inventory.display_all)
    print(output)

    check(added_guitar, "a PhysicalProduct can be added")
    check(added_system, "a DigitalProduct can be added")
    check(not added_copy, "a duplicate ID is refused")
    check(found is operating_system, "search finds a product by ID, ignoring case")
    check(operating_system.get_stock() == 45, "update_stock() changes the stock")
    check(
        "Weight: 3.50 kg" in output and "Download Size: 4500.00 MB" in output,
        "display_all() shows each product's own extra detail",
    )


def test_json_round_trip():
    show_heading("JSON saving and loading keep each product's type")
    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P005", "Guitar", 350.00, 5, 3.5))
    inventory.add_product(DigitalProduct("D002", "Operating System", 139.99, 50, 4500))
    restored = Inventory()

    # Save and load inside a temporary folder, so your real
    # inventory.json is never touched by the test.
    original_folder = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_folder:
        os.chdir(temp_folder)
        try:
            saved = save_inventory(inventory)
            with open(INVENTORY_FILE, "r") as file:
                print(f"The saved {INVENTORY_FILE}:")
                print(file.read())
            print()
            load_inventory(restored)
        finally:
            os.chdir(original_folder)
    print()

    guitar = restored.search_product("P005")
    operating_system = restored.search_product("D002")
    check(saved, "save_inventory() wrote the file")
    check(
        isinstance(guitar, PhysicalProduct) and guitar.get_weight() == 3.5,
        "the guitar comes back as a PhysicalProduct with its weight",
    )
    check(
        isinstance(operating_system, DigitalProduct)
        and operating_system.get_download_size() == 4500,
        "the operating system comes back as a DigitalProduct with its download size",
    )


def main():
    test_physical_product()
    test_digital_product()
    test_fulfilment_info()
    test_abstract_product()
    test_inventory_operations()
    test_json_round_trip()

    passed = results.count(True)
    print()
    print("=" * 60)
    print(f"{passed} of {len(results)} checks passed.")


if __name__ == "__main__":
    main()
