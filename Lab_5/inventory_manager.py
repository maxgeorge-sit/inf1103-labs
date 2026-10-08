import json
import os

INVENTORY_FILE = "inventory.json"
DIVIDER = "-" * 48


def search_product(inventory, product_id):
    product_id = product_id.strip().upper()

    for product in inventory:
        if product["id"] == product_id:
            return product

    return None


def add_product(inventory, product_id, name, price, stock):
    product_id = product_id.strip().upper()

    if search_product(inventory, product_id) is not None:
        return False

    product = {
        "id": product_id,
        "name": name.strip(),
        "price": price,
        "stock": stock,
    }
    inventory.append(product)
    return True


def update_stock(inventory, product_id, new_stock):
    product = search_product(inventory, product_id)

    if product is None:
        return False

    product["stock"] = new_stock
    return True


def display_product(product):
    print(DIVIDER)
    print(f"ID: {product['id']}")
    print(f"Name: {product['name']}")
    print(f"Price: ${product['price']:.2f}")
    print(f"Stock: {product['stock']}")
    print(DIVIDER)


def display_all(inventory):
    print("\nCurrent Inventory")
    print(DIVIDER)

    if not inventory:
        print("No products in inventory.")

    for product in inventory:
        print(
            f"ID: {product['id']} | Name: {product['name']} | "
            f"Price: ${product['price']:.2f} | Stock: {product['stock']}"
        )

    print(DIVIDER)


def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        print(f"{INVENTORY_FILE} not found. Starting with an empty inventory.")
        return []

    print(f"{INVENTORY_FILE} found.")

    try:
        with open(INVENTORY_FILE, "r") as file:
            inventory = json.load(file)
    except (OSError, ValueError):
        print(f"Could not read {INVENTORY_FILE}. Starting with an empty inventory.")
        return []

    if not isinstance(inventory, list):
        print(f"{INVENTORY_FILE} has an unexpected format. Starting with an empty inventory.")
        return []

    print("Inventory loaded successfully.")
    return inventory


def main():
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory = load_inventory()
    display_all(inventory)

if __name__ == "__main__":
    main()