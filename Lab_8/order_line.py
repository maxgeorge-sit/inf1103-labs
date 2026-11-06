from product import Product


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
