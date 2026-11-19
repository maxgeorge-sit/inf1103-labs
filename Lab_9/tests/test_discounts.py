import ast
import contextlib
import io
import os
import unittest

from bulk_discount import BulkDiscount
from discount_strategy import DiscountStrategy
from inventory_manager import parse_discount
from no_discount import NoDiscount
from order import Order
from percentage_discount import PercentageDiscount
from physical_product import PhysicalProduct
from supplier import Supplier

# The project folder: the one that holds this tests folder.
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_order(discount: DiscountStrategy | None = None) -> Order:
    # An order whose lines add up to 250: two desks at 125.00 each.
    supplier = Supplier("S001", "Acme Components", "sales@acme.example.com")
    desk = PhysicalProduct("P101", "Desk", 125.00, 10, supplier, 20)
    order = Order("O001", discount)
    order.add_order_line(desk, 2)
    return order


class RecordingDiscount(DiscountStrategy):
    # A strategy written here, in the test, that Order has never seen.
    # It records each total it is given, and always answers 1.0.
    def __init__(self) -> None:
        self.received: list[float] = []

    def apply(self, total: float) -> float:
        self.received.append(total)
        return 1.0


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


class TestOrderDiscounts(unittest.TestCase):
    def test_order_uses_no_discount_by_default(self) -> None:
        """An order given no strategy uses NoDiscount."""
        order = make_order()
        self.assertIsInstance(order.get_discount(), NoDiscount)
        self.assertAlmostEqual(order.calculate_total(), 250.0)

    def test_order_takes_a_strategy_when_created(self) -> None:
        """Lines adding up to 250, with BulkDiscount(200, 20), total 230."""
        self.assertAlmostEqual(make_order(BulkDiscount(200, 20)).calculate_total(), 230.0)

    def test_set_discount_changes_the_strategy(self) -> None:
        """set_discount(PercentageDiscount(10)) on the same order makes it 225."""
        order = make_order(BulkDiscount(200, 20))
        order.set_discount(PercentageDiscount(10))
        self.assertIsInstance(order.get_discount(), PercentageDiscount)
        self.assertAlmostEqual(order.calculate_total(), 225.0)

    def test_total_goes_through_the_strategy(self) -> None:
        """A new strategy works with no change to Order: it gets the subtotal."""
        recorder = RecordingDiscount()
        order = make_order(recorder)
        self.assertEqual(order.calculate_total(), 1.0)
        self.assertEqual(recorder.received, [250.0])

    def test_two_orders_can_share_one_strategy(self) -> None:
        """Two orders can use the same PercentageDiscount object."""
        shared = PercentageDiscount(10)
        first = make_order(shared)
        second = make_order(shared)
        self.assertIs(first.get_discount(), second.get_discount())
        self.assertAlmostEqual(first.calculate_total(), 225.0)
        self.assertAlmostEqual(second.calculate_total(), 225.0)

    def test_only_strategies_are_accepted(self) -> None:
        """Order refuses a discount that isn't a DiscountStrategy."""
        with self.assertRaises(ValueError):
            Order("O002", 0.1)
        with self.assertRaises(ValueError):
            make_order().set_discount("10%")

    def test_order_has_no_discount_if_elif(self) -> None:
        """Order's code has no if/elif about discount types."""
        with open(os.path.join(PROJECT_FOLDER, "order.py")) as file:
            source = file.read()

        tree = ast.parse(source)
        calculate_total = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "calculate_total"
        )
        self.assertFalse(any(isinstance(node, ast.If) for node in ast.walk(calculate_total)))

        # Order may name NoDiscount, its default, but no other strategy.
        for strategy in DiscountStrategy.__subclasses__():
            if strategy is not NoDiscount:
                with self.subTest(strategy=strategy.__name__):
                    self.assertNotIn(strategy.__name__, source)

    def test_display_shows_the_saving(self) -> None:
        """With a discount, the order shows its subtotal, discount and total."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            make_order(BulkDiscount(200, 20)).display_information()

        self.assertIn("Subtotal: $250.00", output.getvalue())
        self.assertIn("Discount: -$20.00", output.getvalue())
        self.assertIn("Total: $230.00", output.getvalue())

    def test_display_without_a_discount_shows_only_the_total(self) -> None:
        """With NoDiscount, the order shows just its total."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            make_order().display_information()

        self.assertIn("Total: $250.00", output.getvalue())
        self.assertNotIn("Subtotal", output.getvalue())


class TestDiscountChoice(unittest.TestCase):
    def test_each_number_picks_its_strategy(self) -> None:
        """Create Order's discount numbers pick the matching strategy."""
        self.assertIsInstance(parse_discount("1"), NoDiscount)
        self.assertIsInstance(parse_discount("2"), PercentageDiscount)
        self.assertIsInstance(parse_discount("3"), BulkDiscount)

    def test_other_entries_are_refused(self) -> None:
        """Any other entry is refused, so the user is asked again."""
        for entry in ["0", "4", "", "two", "1.5"]:
            with self.subTest(entry=entry):
                with self.assertRaises(ValueError):
                    parse_discount(entry)
