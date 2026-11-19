from abc import ABC, abstractmethod


# The Strategy pattern. Each way of discounting an order is its own class,
# and every one of them provides apply(). Order only ever calls apply(), so
# a new discount means a new class, never a change to Order.
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        pass
