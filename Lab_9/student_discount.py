from discount_strategy import DiscountStrategy


# A fourth strategy, added without changing Order: students get 5% off.
class StudentDiscount(DiscountStrategy):
    PERCENTAGE: int = 5

    def apply(self, total: float) -> float:
        return total * (100 - self.PERCENTAGE) / 100