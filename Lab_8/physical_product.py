from can_be_shipped import CanBeShipped
from product import Product, ProductRecord, check_positive_number
from supplier import Supplier


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

    def to_dict(self) -> ProductRecord:
        record = super().to_dict()
        record["type"] = "physical"
        record["weight"] = self.__weight
        return record

    def get_fulfilment_info(self) -> str:
        return "This product requires physical shipping."

    # Required by CanBeShipped. Simple rule: a $5.00 base fee plus $2.00 per kg.
    def calculate_shipping_cost(self) -> float:
        return 5.00 + 2.00 * self.__weight
