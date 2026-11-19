from discount_strategy import DiscountStrategy


# The strategy an order uses when it has no discount: the total stays as it is.
class NoDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total
