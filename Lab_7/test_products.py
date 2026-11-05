# Checks for the Lab 7 product classes.
# Run it from your project folder with:  python test_products.py

import contextlib
import io

from inventory_manager import PhysicalProduct, Product

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

    check(isinstance(guitar, Product), "a PhysicalProduct is-a Product")
    check(guitar.get_weight() == 3.5, "the weight is stored")
    check("Name: Guitar" in output, "the shared product details are displayed")
    check("Weight: 3.50 kg" in output, "the weight is displayed")

    try:
        PhysicalProduct("P006", "Broken Item", 1.00, 1, -2)
        check(False, "a negative weight is refused")
    except ValueError:
        check(True, "a negative weight is refused")

    print()
    print("print(guitar) uses the __str__ inherited from Product, so no weight yet:")
    print(guitar)


def main():
    test_physical_product()

    passed = results.count(True)
    print()
    print("=" * 60)
    print(f"{passed} of {len(results)} checks passed.")


if __name__ == "__main__":
    main()
