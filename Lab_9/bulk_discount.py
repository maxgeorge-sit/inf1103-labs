from discount_strategy import DiscountStrategy


# Takes a fixed amount off any total that reaches a threshold:
# BulkDiscount(200, 20) takes 20 off a total of 200 or more.
class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, amount: float) -> None:
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            raise ValueError("Threshold must be a number.")

        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number.")

        # An amount no bigger than the threshold means a discounted total
        # can never drop below zero.
        if not 0 < amount <= threshold:
            raise ValueError("Amount must be more than 0 and no more than the threshold.")

        self.__threshold: float = float(threshold)
        self.__amount: float = float(amount)

    def get_threshold(self) -> float:
        return self.__threshold

    def get_amount(self) -> float:
        return self.__amount

    def apply(self, total: float) -> float:
        if total >= self.__threshold:
            return total - self.__amount

        return total
