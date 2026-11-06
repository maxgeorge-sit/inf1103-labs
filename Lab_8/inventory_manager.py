import json
import math
import os
from collections.abc import Callable
from typing import TypeVar

# Each class lives in its own file; this file is the program around them:
# saving and loading, input checks, and the menu.
from can_be_shipped import CanBeShipped
from constants import DIVIDER
from digital_product import DigitalProduct
from inventory import Inventory
from order import Order
from physical_product import PhysicalProduct
from product import Product, ProductRecord
from supplier import Supplier, SupplierRecord

INVENTORY_FILE = "inventory.json"


# ---------- File handling ----------

def create_supplier(record: SupplierRecord, suppliers: dict[str, Supplier]) -> Supplier:
    # Products saved with the same supplier ID get one shared Supplier
    # object, so the association is rebuilt exactly as it was saved.
    supplier = Supplier(record["supplier_id"], record["name"], record["contact_email"])
    existing = suppliers.get(supplier.get_supplier_id())

    if existing is not None:
        return existing

    suppliers[supplier.get_supplier_id()] = supplier
    return supplier


def create_product(record: ProductRecord, suppliers: dict[str, Supplier]) -> Product:
    supplier = create_supplier(record["supplier"], suppliers)

    # The "type" saved with each record says which subclass to rebuild.
    if record["type"] == "physical":
        return PhysicalProduct(
            record["id"], record["name"], record["price"], record["stock"],
            supplier, record["weight"],
        )

    if record["type"] == "digital":
        return DigitalProduct(
            record["id"], record["name"], record["price"], record["stock"],
            supplier, record["download_size"],
        )

    raise ValueError(f"Unknown product type: {record['type']}")


def load_inventory(inventory: Inventory) -> None:
    if not os.path.exists(INVENTORY_FILE):
        print(f"{INVENTORY_FILE} not found. Starting with an empty inventory.")
        return

    print(f"{INVENTORY_FILE} found.")

    try:
        with open(INVENTORY_FILE, "r") as file:
            data = json.load(file)
    except (OSError, ValueError):
        print(f"Could not read {INVENTORY_FILE}. Starting with an empty inventory.")
        return

    if not isinstance(data, list):
        print(f"{INVENTORY_FILE} has an unexpected format. Starting with an empty inventory.")
        return

    # Each saved dictionary becomes a PhysicalProduct or DigitalProduct.
    # A record that is rejected (missing field, unknown type, negative
    # stock, ...) or has a duplicate ID is skipped.
    skipped = 0
    # The suppliers met so far, by ID, so products can share them.
    suppliers: dict[str, Supplier] = {}
    for item in data:
        try:
            product = create_product(item, suppliers)
        except (KeyError, TypeError, ValueError):
            skipped += 1
            continue

        if not inventory.add_product(product):
            skipped += 1

    if skipped > 0:
        print(f"Warning: Skipped {skipped} invalid or duplicate product record(s).")
        print("They will be left out the next time the inventory is saved.")

    print("Inventory loaded successfully.")


def save_inventory(inventory: Inventory) -> bool:
    # Each Product turns itself into a dictionary, as JSON cannot store
    # objects. Python runs the right to_dict() for each kind of product.
    data: list[ProductRecord] = []
    for product in inventory.get_products():
        data.append(product.to_dict())

    try:
        with open(INVENTORY_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        print(f"Error: Could not save inventory ({error}).")
        return False

    return True


# ---------- Input validation ----------

def parse_text(entry: str) -> str:
    if not entry:
        raise ValueError("This field cannot be empty.")

    return entry


def parse_stock(entry: str) -> int:
    if entry.startswith(("-", "+")):
        digits = entry[1:]
    else:
        digits = entry

    if not digits.isdigit():
        raise ValueError("Enter a whole number.")

    try:
        quantity = int(entry)
    except ValueError:
        raise ValueError("Enter a valid integer.") from None

    if quantity < 0:
        raise ValueError("Negative quantities are not allowed.")

    return quantity


def parse_price(entry: str) -> float:
    try:
        price = float(entry)
    except ValueError:
        raise ValueError("Enter a valid price, e.g. 299.99.") from None

    if not math.isfinite(price):
        raise ValueError("Enter a valid price, e.g. 299.99.")

    if price < 0:
        raise ValueError("Price cannot be negative.")

    return price


def parse_product_type(entry: str) -> str:
    choice = entry.lower()

    if choice in ("1", "physical"):
        return "physical"

    if choice in ("2", "digital"):
        return "digital"

    raise ValueError("Enter 1 for Physical or 2 for Digital.")


def parse_positive_number(entry: str) -> float:
    try:
        number = float(entry)
    except ValueError:
        raise ValueError("Enter a number, e.g. 2.5.") from None

    if not math.isfinite(number) or number <= 0:
        raise ValueError("Enter a number greater than 0.")

    return number


def parse_email(entry: str) -> str:
    # An email address needs text on both sides of the @ sign.
    user, at_sign, domain = entry.partition("@")
    if not user or not at_sign or not domain:
        raise ValueError("Enter an email address like name@example.com.")

    return entry


def parse_quantity(entry: str) -> int:
    # An order needs at least 1 of a product.
    quantity = parse_stock(entry)

    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")

    return quantity


# T stands for whatever type the parser returns, so ask_until_valid() returns
# that same type: a str from parse_text(), an int from parse_stock(), and so on.
T = TypeVar("T")


def ask_until_valid(prompt: str, parser: Callable[[str], T]) -> T:
    while True:
        try:
            return parser(input(prompt).strip())
        except ValueError as error:
            print(f"Error: {error}")


# ---------- Main program ----------

def show_menu() -> None:
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Remove Product")
    print("6. Create Order")
    print("7. Save Inventory")
    print("8. Exit")
    print("----------------------------")


def find_supplier(inventory: Inventory, supplier_id: str) -> Supplier | None:
    # Suppliers are reached through the products that refer to them.
    supplier_id = supplier_id.strip().upper()

    for product in inventory.get_products():
        supplier = product.get_supplier()
        if supplier.get_supplier_id() == supplier_id:
            return supplier

    return None


def choose_supplier(inventory: Inventory) -> Supplier:
    # Reuses a supplier the inventory already knows, or creates a new one.
    supplier_id = ask_until_valid("Supplier ID: ", parse_text)
    supplier = find_supplier(inventory, supplier_id)

    if supplier is not None:
        print(f"Using existing supplier: {supplier.get_name()}")
        return supplier

    name = ask_until_valid("Supplier Name: ", parse_text)
    contact_email = ask_until_valid("Supplier Email: ", parse_email)
    return Supplier(supplier_id, name, contact_email)


def add_product_menu(inventory: Inventory) -> None:
    print("\nAdd New Product")
    product_type = ask_until_valid(
        "Product Type (1 = Physical, 2 = Digital): ", parse_product_type
    )
    product_id = ask_until_valid("Product ID: ", parse_text)

    if inventory.find_product(product_id) is not None:
        print(f"\nError: Product ID {product_id.upper()} already exists.")
        return

    name = ask_until_valid("Product Name: ", parse_text)
    price = ask_until_valid("Price: ", parse_price)
    stock = ask_until_valid("Stock Quantity: ", parse_stock)
    supplier = choose_supplier(inventory)

    # Ask for the one extra detail this type needs, then create that subclass.
    if product_type == "physical":
        weight = ask_until_valid("Weight (kg): ", parse_positive_number)
        product = PhysicalProduct(product_id, name, price, stock, supplier, weight)
    else:
        download_size = ask_until_valid("Download Size (MB): ", parse_positive_number)
        product = DigitalProduct(product_id, name, price, stock, supplier, download_size)

    inventory.add_product(product)
    print("\nProduct added successfully!")


def update_stock_menu(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    product_id = ask_until_valid("Enter Product ID: ", parse_text)
    product = inventory.find_product(product_id)

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}")

    print()
    new_stock = ask_until_valid("New Stock Quantity: ", parse_stock)

    product.update_stock(new_stock)
    print("\nStock updated successfully!")


def search_product_menu(inventory: Inventory) -> None:
    print("\nSearch Product")
    product_id = ask_until_valid("Enter Product ID: ", parse_text)
    product = inventory.find_product(product_id)

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print(DIVIDER)
    product.display_information()
    print(f"Fulfilment: {product.get_fulfilment_info()}")

    # Only products that sign CanBeShipped have a shipping cost.
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")

    print(DIVIDER)


def remove_product_menu(inventory: Inventory) -> None:
    print("\nRemove Product")
    product_id = ask_until_valid("Enter Product ID: ", parse_text)
    product = inventory.remove_product(product_id)

    if product is None:
        print("\nProduct not found.")
        return

    # Only the inventory's reference is gone: the Product object itself is intact.
    print(f"\n{product.get_name()} ({product.get_product_id()}) was removed from the inventory.")


def create_order_menu(inventory: Inventory) -> None:
    print("\nCreate Order")
    order = Order(ask_until_valid("Order ID: ", parse_text))
    print("Enter a Product ID to add it to the order, or press Enter to finish.")

    while True:
        product_id = input("Product ID: ").strip()
        if not product_id:
            break

        product = inventory.find_product(product_id)
        if product is None:
            print("Product not found.")
            continue

        quantity = ask_until_valid("Quantity: ", parse_quantity)
        # The Order creates the OrderLine: this menu never makes one itself.
        order.add_order_line(product, quantity)
        print(f"Added {quantity} x {product.get_name()}.")

    if not order.get_order_lines():
        print("\nNo products were added, so no order was created.")
        return

    print()
    order.display_information()
    # When this function ends, the Order and its OrderLines go with it.
    # The products stay in the inventory.


def run_menu(inventory: Inventory) -> None:
    while True:
        print()
        show_menu()
        choice = input("\nEnter option: ").strip()

        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product_menu(inventory)
        elif choice == "3":
            update_stock_menu(inventory)
        elif choice == "4":
            search_product_menu(inventory)
        elif choice == "5":
            remove_product_menu(inventory)
        elif choice == "6":
            create_order_menu(inventory)
        elif choice == "7":
            print("\nSaving inventory...")
            if save_inventory(inventory):
                print(f"Inventory saved successfully to {INVENTORY_FILE}.")
        elif choice == "8":
            print("\nSaving inventory before exit...")
            if save_inventory(inventory):
                print("Inventory saved successfully.")
            else:
                print("Warning: Your changes were NOT saved.")

            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            return
        else:
            print("\nInvalid option. Please enter a number from 1 to 8.")


def main() -> None:
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory = Inventory()
    load_inventory(inventory)

    # Ctrl+C, or input that ends early,
    # stops the program with a message instead of a traceback.
    try:
        run_menu(inventory)
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram stopped. Changes since the last save were not saved.")


if __name__ == "__main__":
    main()