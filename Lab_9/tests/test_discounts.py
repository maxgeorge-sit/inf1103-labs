import unittest

from bulk_discount import BulkDiscount
from discount_strategy import DiscountStrategy
from no_discount import NoDiscount
from percentage_discount import PercentageDiscount


class TestDiscountStrategies(unittest.TestCase):
    def test_discount_strategy_is_abstract(self) -> None:
        """DiscountStrategy can't be created on its own."""
        with self.assertRaises(TypeError):
            DiscountStrategy()

    def test_every_strategy_is_a_discount_strategy(self) -> None:
        """Each discount inherits from DiscountStrategy."""
        for strategy in [NoDiscount(), PercentageDiscount(10), BulkDiscount(200, 20)]:
            with self.subTest(strategy=type(strategy).__name__):
                self.assertIsInstance(strategy, DiscountStrategy)

    def test_no_discount_keeps_the_total(self) -> None:
        """NoDiscount returns the total unchanged."""
        self.assertEqual(NoDiscount().apply(250.0), 250.0)

    def test_percentage_discount_takes_a_percentage_off(self) -> None:
        """PercentageDiscount(10) takes 10% off: 250 becomes 225."""
        self.assertAlmostEqual(PercentageDiscount(10).apply(250.0), 225.0)

    def test_bulk_discount_from_the_threshold_up(self) -> None:
        """BulkDiscount(200, 20) takes 20 off a total of 200 or more."""
        discount = BulkDiscount(200, 20)
        self.assertAlmostEqual(discount.apply(250.0), 230.0)
        self.assertAlmostEqual(discount.apply(200.0), 180.0)

    def test_bulk_discount_below_the_threshold(self) -> None:
        """BulkDiscount(200, 20) leaves a total under 200 unchanged."""
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(199.99), 199.99)

    def test_invalid_percentages_are_refused(self) -> None:
        """A percentage must be a number above 0 and no more than 100."""
        for percentage in [0, -5, 150, "10", True]:
            with self.subTest(percentage=percentage):
                with self.assertRaises(ValueError):
                    PercentageDiscount(percentage)

    def test_invalid_bulk_discounts_are_refused(self) -> None:
        """A bulk amount must be above 0 and no more than the threshold."""
        for threshold, amount in [(200, 0), (200, -5), (10, 20), ("200", 20), (200, "20")]:
            with self.subTest(threshold=threshold, amount=amount):
                with self.assertRaises(ValueError):
                    BulkDiscount(threshold, amount)