from constants import DIVIDER
from discount_strategy import DiscountStrategy
from no_discount import NoDiscount
from order_line import OrderLine
from product import Product


# An Order is made of OrderLine objects (composition). It creates its own
# lines, never takes in a line made elsewhere, and its lines go when it goes.
# It also uses a DiscountStrategy (association). The strategy decides the
# discount, so Order holds no if/elif about discount types.
class Order:
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None) -> None:
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("Order ID must be non-empty text.")

        self.__order_id: str = order_id.strip().upper()
        self.__order_lines: list[OrderLine] = []
        # With no discount given, the order uses NoDiscount, so it always has
        # a strategy to call.
        self.__discount: DiscountStrategy = NoDiscount()
        if discount is not None:
            self.set_discount(discount)

    def get_order_id(self) -> str:
        return self.__order_id

    def get_discount(self) -> DiscountStrategy:
        return self.__discount

    def set_discount(self, discount: DiscountStrategy) -> None:
        # Any strategy will do: Order never asks which kind it is.
        if not isinstance(discount, DiscountStrategy):
            raise ValueError("Discount must be a DiscountStrategy object.")

        self.__discount = discount

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

    def calculate_subtotal(self) -> float:
        # Each OrderLine works out its own subtotal.
        total = 0.0
        for order_line in self.__order_lines:
            total += order_line.calculate_subtotal()

        return total

    def calculate_total(self) -> float:
        # The strategy turns the subtotal into the total, whichever it is.
        return self.__discount.apply(self.calculate_subtotal())

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
        subtotal = self.calculate_subtotal()
        total = self.calculate_total()
        # The saving is the gap between the two, whatever the strategy is.
        if total < subtotal:
            print(f"Subtotal: ${subtotal:.2f}")
            print(f"Discount: -${subtotal - total:.2f}")

        print(f"Total: ${total:.2f}")