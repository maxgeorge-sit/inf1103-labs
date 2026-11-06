import json
import math
import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeVar

INVENTORY_FILE = "inventory.json"
DIVIDER = "-" * 48

# The shapes of the records saved in inventory.json: a supplier's details,
# and a product's details with its supplier's record inside.
SupplierRecord = dict[str, str]
ProductRecord = dict[str, str | float | int | SupplierRecord]


# ---------- Supplier class ----------

# A supplier exists on its own: products refer to it (association), but a
# supplier is not part of a product, and a product is not part of it.
class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        if not isinstance(supplier_id, str) or not supplier_id.strip():
            raise ValueError("Supplier ID must be non-empty text.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Supplier name must be non-empty text.")

        if not isinstance(contact_email, str):
            raise ValueError("Contact email must be text.")

        # An email address needs text on both sides of the @ sign.
        user, at_sign, domain = contact_email.strip().partition("@")
        if not user or not at_sign or not domain:
            raise ValueError("Contact email must look like name@example.com.")

        self.__supplier_id: str = supplier_id.strip().upper()
        self.__name: str = name.strip()
        self.__contact_email: str = contact_email.strip()

    def get_supplier_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    def display_information(self) -> None:
        print(f"Supplier ID: {self.__supplier_id}")
        print(f"Name: {self.__name}")
        print(f"Contact Email: {self.__contact_email}")

    # The supplier's details as they are saved in inventory.json.
    def to_dict(self) -> SupplierRecord:
        return {
            "supplier_id": self.__supplier_id,
            "name": self.__name,
            "contact_email": self.__contact_email,
        }


# ---------- Product class ----------
class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier) -> None:
        if not isinstance(product_id, str) or not product_id.strip():
            raise ValueError("Product ID must be non-empty text.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Product name must be non-empty text.")

        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise ValueError("Price must be a number.")

        if not math.isfinite(price) or price < 0:
            raise ValueError("Price must be 0 or more.")

        # The Supplier is created on its own and handed in, so the product
        # refers to it (association) instead of owning it.
        if not isinstance(supplier, Supplier):
            raise ValueError("Supplier must be a Supplier object.")

        self.__product_id: str = product_id.strip().upper()
        self.__name: str = name.strip()
        self.__price: float = float(price)
        self.__supplier: Supplier = supplier

        # Goes through update_stock() so the same stock rules apply here as well.
        self.__stock: int = 0
        self.update_stock(stock)

    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def update_stock(self, quantity: int) -> None:
        # The Product checks the value before it changes its own stock.
        # bool counts as int in Python, so True/False are rejected too.
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Stock must be a whole number.")

        if quantity < 0:
            raise ValueError("Stock cannot be negative.")

        self.__stock = quantity

    def display_information(self) -> None:
        print(f"ID: {self.__product_id}")
        print(f"Name: {self.__name}")
        print(f"Price: ${self.__price:.2f}")
        print(f"Stock: {self.__stock}")

        # The product asks its supplier for the supplier's own details.
        supplier = self.__supplier
        print(f"Supplier: {supplier.get_name()} ({supplier.get_supplier_id()})")

    # __str__ is a public special
    # method like __init__, not a private one. print(product) uses it.
    def __str__(self) -> str:
        return (
            f"ID: {self.__product_id} | Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | Stock: {self.__stock}"
        )

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass


# ---------- CanBeShipped interface ----------

class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


# ---------- Shared check for product subclasses ----------

def check_positive_number(value: float, label: str) -> float:
    # Used by each subclass to check the extra number it adds.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number.")

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be greater than 0.")

    return float(value)


# ---------- PhysicalProduct class ----------

# One parent class (Product) plus one interface (CanBeShipped).
class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float) -> None:
        # super() runs Product's constructor, which checks and stores the
        # ID, name, price, stock and supplier as it does for any product.
        super().__init__(product_id, name, price, stock, supplier)

        # The attribute only physical products have: weight in kilograms.
        self.__weight: float = check_positive_number(weight, "Weight")

    def get_weight(self) -> float:
        return self.__weight

    # Overrides Product's version: Product prints the ID, name, price,
    # stock and supplier, then this method adds the one line that is new.
    def display_information(self) -> None:
        super().display_information()
        print(f"Weight: {self.__weight:.2f} kg")

    # The same idea for the one-line version that print(product) uses.
    def __str__(self) -> str:
        return f"{super().__str__()} | Weight: {self.__weight:.2f} kg"

    def get_fulfilment_info(self) -> str:
        return "This product requires physical shipping."

    # Required by CanBeShipped. Simple rule: a $5.00 base fee plus $2.00 per kg.
    def calculate_shipping_cost(self) -> float:
        return 5.00 + 2.00 * self.__weight


# ---------- DigitalProduct class ----------

class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float) -> None:
        # Same pattern as PhysicalProduct: Product's constructor runs first.
        super().__init__(product_id, name, price, stock, supplier)

        # A digital product has no weight; it has a download size in megabytes.
        self.__download_size: float = check_positive_number(download_size, "Download size")

    def get_download_size(self) -> float:
        return self.__download_size

    # Overrides both methods the same way PhysicalProduct does.
    def display_information(self) -> None:
        super().display_information()
        print(f"Download Size: {self.__download_size:.2f} MB")

    def __str__(self) -> str:
        return f"{super().__str__()} | Download Size: {self.__download_size:.2f} MB"

    def get_fulfilment_info(self) -> str:
        return "This product is delivered digitally as a download."


# ---------- Inventory class ----------

# An Inventory groups Product objects (aggregation). The products are made
# elsewhere and handed in, and removing one does not destroy it.
class Inventory:
    def __init__(self) -> None:
        # Typed with the base class, so the list can hold any kind of Product.
        self.__products: list[Product] = []

    def add_product(self, product: Product) -> bool:
        if self.find_product(product.get_product_id()) is not None:
            return False

        self.__products.append(product)
        return True

    def remove_product(self, product_id: str) -> Product | None:
        # Takes the product out of this inventory and hands it back intact,
        # so it can still be used, or added to another inventory.
        product = self.find_product(product_id)

        if product is not None:
            self.__products.remove(product)

        return product

    def find_product(self, product_id: str) -> Product | None:
        product_id = product_id.strip().upper()

        for product in self.__products:
            if product.get_product_id() == product_id:
                return product

        return None

    def display_all(self) -> None:
        print("\nCurrent Inventory")
        print(DIVIDER)

        if not self.__products:
            print("No products in inventory.")

        for product in self.__products:
            print(product)

        print(DIVIDER)

    # Returns a copy, so other code can read the products but cannot add 
    # or remove any without going through the Inventory.
    def get_products(self) -> list[Product]:
        return list(self.__products)


# ---------- OrderLine class ----------

# One product and the quantity ordered. An OrderLine refers to its Product
# (association) but does not own it: the product carries on without it.
class OrderLine:
    def __init__(self, product: Product, quantity: int) -> None:
        if not isinstance(product, Product):
            raise ValueError("An order line needs a Product object.")

        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError("Quantity must be a whole number of 1 or more.")

        self.__product: Product = product
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def __str__(self) -> str:
        product = self.__product
        return (
            f"{self.__quantity} x {product.get_name()} ({product.get_product_id()}) "
            f"@ ${product.get_price():.2f} = ${self.calculate_subtotal():.2f}"
        )


# ---------- Order class ----------

# An Order is made of OrderLine objects (composition). It creates its own
# lines, never takes in a line made elsewhere, and its lines go when it goes.
class Order:
    def __init__(self, order_id: str) -> None:
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("Order ID must be non-empty text.")

        self.__order_id: str = order_id.strip().upper()
        self.__order_lines: list[OrderLine] = []

    def get_order_id(self) -> str:
        return self.__order_id

    def add_order_line(self, product: Product, quantity: int) -> None:
        # The Order creates the OrderLine itself.
        order_line = OrderLine(product, quantity)
        self.__order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        product_id = product_id.strip().upper()

        for order_line in self.__order_lines:
            if order_line.get_product().get_product_id() == product_id:
                # The line belongs only to this order, so this ends its use.
                self.__order_lines.remove(order_line)
                return True

        return False

    def calculate_total(self) -> float:
        # Each OrderLine works out its own subtotal.
        total = 0.0
        for order_line in self.__order_lines:
            total += order_line.calculate_subtotal()

        return total

    # Returns a copy, so lines can only be added or removed through the Order.
    def get_order_lines(self) -> list[OrderLine]:
        return list(self.__order_lines)

    def display_information(self) -> None:
        print(f"Order {self.__order_id}")
        print(DIVIDER)

        if not self.__order_lines:
            print("No products in this order.")

        for order_line in self.__order_lines:
            print(order_line)

        print(DIVIDER)
        print(f"Total: ${self.calculate_total():.2f}")


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
    # Each Product becomes a dictionary again as JSON cannot store objects.
    data: list[ProductRecord] = []
    for product in inventory.get_products():
        record: ProductRecord = {
            "id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock(),
            "supplier": product.get_supplier().to_dict(),
        }

        # Add the type label, used when loading, and the extra field
        # that only this kind of product has.
        if isinstance(product, PhysicalProduct):
            record["type"] = "physical"
            record["weight"] = product.get_weight()
        elif isinstance(product, DigitalProduct):
            record["type"] = "digital"
            record["download_size"] = product.get_download_size()

        data.append(record)

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
    print("5. Save Inventory")
    print("6. Exit")
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
            return
        else:
            print("\nInvalid option. Please enter a number from 1 to 6.")


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