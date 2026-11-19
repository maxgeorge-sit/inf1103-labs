import math
from abc import ABC, abstractmethod

from supplier import Supplier, SupplierRecord

# The shape of a product's record in inventory.json, with its supplier's
# record inside.
ProductRecord = dict[str, str | float | int | SupplierRecord]


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

    # The product's details as they are saved in inventory.json. Each
    # subclass adds its own fields, so save_inventory() never has to ask
    # which kind of product it has.
    def to_dict(self) -> ProductRecord:
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
            "supplier": self.__supplier.to_dict(),
        }

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass


# A check shared by the product subclasses.
def check_positive_number(value: float, label: str) -> float:
    # Used by each subclass to check the extra number it adds.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number.")

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be greater than 0.")

    return float(value)
