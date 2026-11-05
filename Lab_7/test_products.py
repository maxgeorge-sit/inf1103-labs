# Checks for the Lab 7 product classes.
# Run it from your project folder with:  python test_products.py

import contextlib
import io

from inventory_manager import DigitalProduct, PhysicalProduct, Product

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


def main():
    test_physical_product()
    test_digital_product()

    passed = results.count(True)
    print()
    print("=" * 60)
    print(f"{passed} of {len(results)} checks passed.")


if __name__ == "__main__":
    main()
