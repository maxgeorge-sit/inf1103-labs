from discount_strategy import DiscountStrategy


# Takes a percentage off the whole total: PercentageDiscount(10) is 10% off.
class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float) -> None:
        # bool counts as a number in Python, so True/False are refused too.
        if isinstance(percentage, bool) or not isinstance(percentage, (int, float)):
            raise ValueError("Percentage must be a number.")

        if not 0 < percentage <= 100:
            raise ValueError("Percentage must be more than 0 and no more than 100.")

        self.__percentage: float = float(percentage)

    def get_percentage(self) -> float:
        return self.__percentage

    def apply(self, total: float) -> float:
        return total * (100 - self.__percentage) / 100
