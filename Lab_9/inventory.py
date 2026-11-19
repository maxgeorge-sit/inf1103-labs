from constants import DIVIDER
from product import Product


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
