from constants import DIVIDER
from order_line import OrderLine
from product import Product


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
