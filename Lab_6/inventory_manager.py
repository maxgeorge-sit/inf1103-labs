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

        # Goes through update_stock() so the same stock rules apply here as well.
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


    def __str__(self):
        return (
            f"ID: {self.__product_id} | Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | Stock: {self.__stock}"
        )


# ---------- Inventory class ----------

class Inventory:
    def __init__(self):
        self.__products = []

    def add_product(self, product):
        if self.search_product(product.get_product_id()) is not None:
            return False

        self.__products.append(product)
        return True

    def search_product(self, product_id):
        product_id = product_id.strip().upper()

        for product in self.__products:
            if product.get_product_id() == product_id:
                return product

        return None

    def display_all(self):
        print("\nCurrent Inventory")
        print(DIVIDER)

        if not self.__products:
            print("No products in inventory.")

        for product in self.__products:
            print(product)

        print(DIVIDER)

    # Returns a copy, so other code can read the products but cannot add
    # or remove any without going through the Inventory.
    def get_products(self):
        return list(self.__products)


# ---------- File handling ----------

def load_inventory(inventory):
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

    # Each saved dictionary becomes a Product object.
    for item in data:
        product = Product(item["id"], item["name"], item["price"], item["stock"])
        inventory.add_product(product)

    print("Inventory loaded successfully.")


def save_inventory(inventory):
    # Each Product becomes a dictionary again, because JSON cannot store objects.
    data = []
    for product in inventory.get_products():
        data.append({
            "id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock(),
        })

    try:
        with open(INVENTORY_FILE, "w") as file:
            json.dump(data, file, indent=4)
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


# ---------- Main program ----------

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

    if inventory.search_product(product_id) is not None:
        print(f"\nError: Product ID {product_id.upper()} already exists.")
        return

    name = ask_until_valid("Product Name: ", parse_text)
    price = ask_until_valid("Price: ", parse_price)
    stock = ask_until_valid("Stock Quantity: ", parse_stock)

    product = Product(product_id, name, price, stock)
    inventory.add_product(product)
    print("\nProduct added successfully!")


def update_stock_menu(inventory):
    print("\nUpdate Stock")
    product_id = ask_until_valid("Enter Product ID: ", parse_text)
    product = inventory.search_product(product_id)

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


def search_product_menu(inventory):
    print("\nSearch Product")
    product_id = ask_until_valid("Enter Product ID: ", parse_text)
    product = inventory.search_product(product_id)

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print(DIVIDER)
    product.display_information()
    print(DIVIDER)


def main():
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory = Inventory()
    load_inventory(inventory)

    print()
    show_menu()

    while True:
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