import json
import math
import os

INVENTORY_FILE = "inventory.json"
DIVIDER = "-" * 48


# ---------- Product class ----------

class Product:
    def __init__(self, product_id, name, price, stock):
        if not isinstance(product_id, str) or not product_id.strip():
            raise ValueError("Product ID must be non-empty text.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Product name must be non-empty text.")

        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise ValueError("Price must be a number.")

        if not math.isfinite(price) or price < 0:
            raise ValueError("Price must be 0 or more.")

        self.__product_id = product_id.strip().upper()
        self.__name = name.strip()
        self.__price = float(price)

        # Goes through update_stock() so that the same stock rules apply here.
        self.__stock = 0
        self.update_stock(stock)

    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    def update_stock(self, quantity):
        # The Product checks the value before it changes its own stock.
        # bool counts as int in Python, so True/False are rejected too.
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Stock must be a whole number.")

        if quantity < 0:
            raise ValueError("Stock cannot be negative.")

        self.__stock = quantity

    def display_information(self):
        print(f"ID: {self.__product_id}")
        print(f"Name: {self.__name}")
        print(f"Price: ${self.__price:.2f}")
        print(f"Stock: {self.__stock}")

    # __str__ has two underscores on BOTH sides, so it is a public special
    # method like __init__, not a private one. print(product) uses it.
    def __str__(self):
        return (
            f"ID: {self.__product_id} | Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | Stock: {self.__stock}"
        )


# ---------- Data functions ----------

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


# ---------- Persistence ----------

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


def save_inventory(inventory):
    try:
        with open(INVENTORY_FILE, "w") as file:
            json.dump(inventory, file, indent=4)
    except OSError as error:
        print(f"Error: Could not save inventory ({error}).")
        return False

    return True


# ---------- Input validation ----------

def parse_text(entry):
    if not entry:
        raise ValueError("This field cannot be empty.")

    return entry


def parse_stock(entry):
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


def parse_price(entry):
    try:
        price = float(entry)
    except ValueError:
        raise ValueError("Enter a valid price, e.g. 299.99.") from None

    if not math.isfinite(price):
        raise ValueError("Enter a valid price, e.g. 299.99.")

    if price < 0:
        raise ValueError("Price cannot be negative.")

    return price


def ask_until_valid(prompt, parser):
    while True:
        try:
            return parser(input(prompt).strip())
        except ValueError as error:
            print(f"Error: {error}")


# ---------- Menu ----------

def show_menu():
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")


def add_product_menu(inventory):
    print("\nAdd New Product")
    product_id = ask_until_valid("Product ID: ", parse_text)

    if search_product(inventory, product_id) is not None:
        print(f"\nError: Product ID {product_id.upper()} already exists.")
        return

    name = ask_until_valid("Product Name: ", parse_text)
    price = ask_until_valid("Price: ", parse_price)
    stock = ask_until_valid("Stock Quantity: ", parse_stock)

    add_product(inventory, product_id, name, price, stock)
    print("\nProduct added successfully!")


def update_stock_menu(inventory):
    print("\nUpdate Stock")
    product_id = ask_until_valid("Enter Product ID: ", parse_text)
    product = search_product(inventory, product_id)

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product['name']}")
    print(f"Current Stock: {product['stock']}")

    print()
    new_stock = ask_until_valid("New Stock Quantity: ", parse_stock)

    update_stock(inventory, product_id, new_stock)
    print("\nStock updated successfully!")


def search_product_menu(inventory):
    print("\nSearch Product")
    product_id = ask_until_valid("Enter Product ID: ", parse_text)
    product = search_product(inventory, product_id)

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    display_product(product)


def main():
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory = load_inventory()

    print()
    show_menu()

    while True:
        choice = input("\nEnter option: ").strip()

        if choice == "1":
            display_all(inventory)
        elif choice == "2":
            add_product_menu(inventory)
        elif choice == "3":
            update_stock_menu(inventory)
        elif choice == "4":
            search_product_menu(inventory)
        elif choice == "5":
            print("\nSaving inventory...")
            if save_inventory(inventory):
                print(f"Inventory saved successfully to {INVENTORY_FILE}.")
        elif choice == "6":
            print("\nSaving inventory before exit...")
            if save_inventory(inventory):
                print("Inventory saved successfully.")
            else:
                print("Warning: Your changes were NOT saved.")

            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("\nInvalid option. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()