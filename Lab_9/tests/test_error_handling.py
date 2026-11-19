import contextlib
import io
import unittest
from unittest import mock

import inventory_manager
from inventory import Inventory
from inventory_manager import get_positive_float


def ask(*entries: str) -> tuple[float, list[str]]:
    # Runs get_positive_float() as if the user typed these entries, one per
    # prompt, and returns the value it gave back and the lines it printed.
    output = io.StringIO()
    with mock.patch("builtins.input", side_effect=entries), contextlib.redirect_stdout(output):
        value = get_positive_float("Price: ")
    return value, output.getvalue().splitlines()


class TestGetPositiveFloat(unittest.TestCase):
    def test_predict_first_entries(self) -> None:
        """abc, then -5, then 12.50: two messages, then 12.5 comes back."""
        value, printed = ask("abc", "-5", "12.50")
        self.assertEqual(value, 12.5)
        self.assertEqual(printed, [
            "Please enter a valid number, e.g. 12.50",
            "Please enter a number greater than zero.",
        ])

    def test_zero_is_refused(self) -> None:
        """0 is refused, and the user is asked again."""
        value, printed = ask("0", "3")
        self.assertEqual(value, 3.0)
        self.assertEqual(printed, ["Please enter a number greater than zero."])

    def test_entries_that_are_not_usable_numbers(self) -> None:
        """An empty entry, nan and inf are refused, and the user is asked again."""
        value, printed = ask("", "nan", "inf", "2")
        self.assertEqual(value, 2.0)
        self.assertEqual(printed, ["Please enter a valid number, e.g. 12.50"] * 3)

    def test_spaces_around_a_number_are_fine(self) -> None:
        """Spaces around a valid number don't matter."""
        self.assertEqual(ask(" 7.25 "), (7.25, []))

    def test_add_product_asks_again_for_a_bad_price(self) -> None:
        """Add Product doesn't crash on a bad price: it asks again."""
        entries = ["1", "P101", "Desk Lamp", "abc", "-5", "25", "10",
                   "S009", "Nordic Lights", "hello@nordic.example.com", "1.2"]
        inventory = Inventory()
        output = io.StringIO()
        with mock.patch("builtins.input", side_effect=entries), contextlib.redirect_stdout(output):
            inventory_manager.add_product_menu(inventory)

        product = inventory.find_product("P101")
        self.assertIsNotNone(product)
        self.assertEqual(product.get_price(), 25.0)
        self.assertIn("Please enter a valid number, e.g. 12.50", output.getvalue())
        self.assertIn("Please enter a number greater than zero.", output.getvalue())