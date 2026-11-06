import contextlib
import io
import os
import tempfile

from inventory_manager import (
    INVENTORY_FILE,
    CanBeShipped,
    DigitalProduct,
    Inventory,
    PhysicalProduct,
    Product,
    Supplier,
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


def make_supplier() -> Supplier:
    # A new Supplier for a test to use.
    return Supplier("S001", "Acme Components", "sales@acme.example.com")


def test_physical_product():
    show_heading("Physical products store and display their weight")
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 5, make_supplier(), 3.5)

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
        PhysicalProduct("P006", "Broken Item", 1.00, 1, make_supplier(), -2)
        check(False, "a negative weight is refused")
    except ValueError:
        check(True, "a negative weight is refused")


def test_digital_product():
    show_heading("Digital products store and display their download size")
    operating_system = DigitalProduct("D002", "Operating System", 139.99, 50, make_supplier(), 4500)

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
        DigitalProduct("D003", "Empty Download", 1.00, 1, make_supplier(), 0)
        check(False, "a download size of 0 is refused")
    except ValueError:
        check(True, "a download size of 0 is refused")


def test_fulfilment_info():
    show_heading("Both subclasses implement get_fulfilment_info()")
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 5, make_supplier(), 3.5)
    operating_system = DigitalProduct("D002", "Operating System", 139.99, 50, make_supplier(), 4500)

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
        Product("X001", "Mystery Item", 10.00, 1, make_supplier())
        check(False, "creating a Product directly is refused")
    except TypeError as error:
        print(f"TypeError: {error}")
        print()
        check(True, "creating a Product directly is refused")

    # A subclass that leaves out the abstract method is refused as well.
    class UnfinishedProduct(Product):
        pass

    try:
        UnfinishedProduct("X002", "Unfinished Item", 10.00, 1, make_supplier())
        check(False, "a subclass without get_fulfilment_info() is refused")
    except TypeError:
        check(True, "a subclass without get_fulfilment_info() is refused")


def test_shipping_cost():
    show_heading("Physical products can calculate shipping costs")
    print("Rule: a $5.00 base fee plus $2.00 per kg")
    print()

    for weight, expected in [(0.2, 5.40), (3.5, 12.00), (10.0, 25.00)]:
        parcel = PhysicalProduct("P100", "Parcel", 10.00, 1, make_supplier(), weight)
        cost = parcel.calculate_shipping_cost()
        check(
            round(cost, 2) == expected,
            f"a {weight} kg product costs ${cost:.2f} to ship (expected ${expected:.2f})",
        )

    # A class that signs CanBeShipped must keep the contract.
    class Crate(CanBeShipped):
        pass

    try:
        Crate()
        check(False, "signing CanBeShipped without calculate_shipping_cost() is refused")
    except TypeError:
        check(True, "signing CanBeShipped without calculate_shipping_cost() is refused")


def test_digital_not_shippable():
    show_heading("Digital products are not required to implement shipping")
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 5, make_supplier(), 3.5)
    operating_system = DigitalProduct("D002", "Operating System", 139.99, 50, make_supplier(), 4500)

    check(isinstance(guitar, CanBeShipped), "a PhysicalProduct signs CanBeShipped")
    check(
        not isinstance(operating_system, CanBeShipped),
        "a DigitalProduct does not sign CanBeShipped",
    )
    check(
        not hasattr(operating_system, "calculate_shipping_cost"),
        "a DigitalProduct has no shipping method and can still be created",
    )


def test_supplier():
    show_heading("A Supplier stores and displays its own details")
    supplier = Supplier("s001", "Acme Components", "sales@acme.example.com")

    output = printed_by(supplier.display_information)
    print("supplier.display_information() prints:")
    print(output)

    check(supplier.get_supplier_id() == "S001", "the supplier ID is stored, in capitals")
    check(supplier.get_name() == "Acme Components", "the name is stored")
    check(
        supplier.get_contact_email() == "sales@acme.example.com",
        "the contact email is stored",
    )
    check(
        "Contact Email: sales@acme.example.com" in output,
        "display_information() shows the supplier's details",
    )

    try:
        Supplier("S002", "No Email Ltd", "not-an-email")
        check(False, "an email without an @ sign is refused")
    except ValueError:
        check(True, "an email without an @ sign is refused")


def test_association():
    show_heading("Supplier and Product are associated, and exist independently")
    supplier = Supplier("S001", "Acme Components", "sales@acme.example.com")
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 5, supplier, 3.5)
    operating_system = DigitalProduct("D002", "Operating System", 139.99, 50, supplier, 4500)

    for product in [guitar, operating_system]:
        print(f"The supplier, reached through {product.get_name()}:")
        product.get_supplier().display_information()
        print()

    check(guitar.get_supplier() is supplier, "the PhysicalProduct stores a reference to the Supplier")
    check(
        operating_system.get_supplier() is supplier,
        "the DigitalProduct refers to the same Supplier object",
    )
    check(
        "Supplier: Acme Components (S001)" in printed_by(guitar.display_information),
        "a product's display_information() includes its supplier",
    )
    check(guitar is not supplier, "the Supplier and the Products are separate objects")

    # Predict first: can each product still show its supplier after this line?
    del supplier
    print("After del supplier, the guitar can still reach its supplier:")
    guitar.get_supplier().display_information()
    print()
    check(
        guitar.get_supplier().get_name() == "Acme Components"
        and operating_system.get_supplier().get_name() == "Acme Components",
        "after del supplier, both products still reach the Supplier",
    )

    # Each side can exist without the other.
    spare_supplier = Supplier("S009", "Spare Parts Co", "hello@spare.example.com")
    check(spare_supplier.get_name() == "Spare Parts Co", "a Supplier can exist with no products")

    del guitar
    check(
        operating_system.get_supplier().get_name() == "Acme Components",
        "deleting a product does not delete its Supplier",
    )

    try:
        PhysicalProduct("P006", "Desk", 120.00, 2, "Acme Components", 15)
        check(False, "a supplier's name instead of a Supplier object is refused")
    except ValueError:
        check(True, "a supplier's name instead of a Supplier object is refused")


def test_inventory_operations():
    show_heading("Inventory operations continue to work")
    inventory = Inventory()
    guitar = PhysicalProduct("P005", "Guitar", 350.00, 5, make_supplier(), 3.5)
    operating_system = DigitalProduct("D002", "Operating System", 139.99, 50, make_supplier(), 4500)

    added_guitar = inventory.add_product(guitar)
    added_system = inventory.add_product(operating_system)
    added_copy = inventory.add_product(DigitalProduct("p005", "Copy", 1.00, 1, make_supplier(), 1))
    found = inventory.find_product("d002")
    if found is not None:
        found.update_stock(45)

    output = printed_by(inventory.display_all)
    print(output)

    check(added_guitar, "a PhysicalProduct can be added")
    check(added_system, "a DigitalProduct can be added")
    check(not added_copy, "a duplicate ID is refused")
    check(found is operating_system, "find_product() finds a product by ID, ignoring case")
    check(operating_system.get_stock() == 45, "update_stock() changes the stock")
    check(
        "Weight: 3.50 kg" in output and "Download Size: 4500.00 MB" in output,
        "display_all() shows each product's own extra detail",
    )


def test_aggregation():
    show_heading("Inventory aggregates Products: removing one does not destroy it")

    # 1. The product exists before any inventory does.
    lamp = PhysicalProduct("P007", "Desk Lamp", 35.00, 12, make_supplier(), 1.2)
    inventory_a = Inventory()
    inventory_b = Inventory()

    # 2. Add it to Inventory A.
    inventory_a.add_product(lamp)
    check(inventory_a.find_product("P007") is lamp, "the product is added to Inventory A")

    # 3. Remove it again. Predict first: does the product still work?
    removed = inventory_a.remove_product("P007")
    check(removed is lamp, "remove_product() hands back the same Product object")
    check(inventory_a.find_product("P007") is None, "Inventory A no longer holds it")

    lamp.update_stock(10)
    print("The removed product still works:")
    lamp.display_information()
    print()
    check(lamp.get_stock() == 10, "the removed product can still be used")

    # 4. Add the same object to Inventory B.
    inventory_b.add_product(lamp)
    check(inventory_b.find_product("p007") is lamp, "the same object is now in Inventory B")

    # 5. Empty Inventory B. The product is not destroyed.
    inventory_b.remove_product("P007")
    check(inventory_b.get_products() == [], "Inventory B is now empty")
    check(lamp.get_name() == "Desk Lamp", "the product still exists after both inventories let go")
    check(inventory_a.remove_product("P999") is None, "removing an unknown ID returns None")


def test_json_round_trip():
    show_heading("JSON saving and loading keep each product's type")
    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P005", "Guitar", 350.00, 5, make_supplier(), 3.5))
    inventory.add_product(DigitalProduct("D002", "Operating System", 139.99, 50, make_supplier(), 4500))
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

    guitar = restored.find_product("P005")
    operating_system = restored.find_product("D002")
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
    check(
        guitar is not None
        and operating_system is not None
        and guitar.get_supplier().get_name() == "Acme Components"
        and guitar.get_supplier() is operating_system.get_supplier(),
        "the supplier comes back too, as one Supplier shared by both products",
    )


def main():
    test_physical_product()
    test_digital_product()
    test_fulfilment_info()
    test_abstract_product()
    test_shipping_cost()
    test_digital_not_shippable()
    test_supplier()
    test_association()
    test_inventory_operations()
    test_aggregation()
    test_json_round_trip()

    passed = results.count(True)
    print()
    print("=" * 60)
    print(f"{passed} of {len(results)} checks passed.")


if __name__ == "__main__":
    main()
