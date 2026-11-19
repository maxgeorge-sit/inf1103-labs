import ast
import contextlib
import csv
import inspect
import io
import os
import tempfile
import unittest
from unittest import mock

import inventory_manager
from digital_product import DigitalProduct
from inventory import Inventory
from inventory_manager import get_positive_float, load_products
from physical_product import PhysicalProduct
from product_factory import ProductFactory
from supplier import Supplier

# The project folder: the one that holds this tests folder.
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The products.csv from section 5.2 of the brief.
BRIEF_CSV = (
    "product_type,product_id,name,price,stock_quantity\n"
    "physical,P001,Desk Lamp,25.00,10\n"
    "digital,D001,Photo Editor,49.90,100\n"
    "service,S001,Installation,30.00,5\n"
    "physical,P002,Office Chair,abc,3\n"
    "physical,P003,Monitor Stand,39.50,7\n"
)


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


class TestLoadProducts(unittest.TestCase):
    def setUp(self) -> None:
        # A temporary folder, so these tests never touch your own files.
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = os.path.join(folder.name, "products.csv")
        self.supplier = Supplier("S001", "Acme Components", "sales@acme.example.com")
        self.inventory = Inventory()

    def load(self, contents: str | None) -> list[str]:
        # Writes the CSV text (None leaves no file), loads it, and returns
        # the lines load_products() printed.
        if contents is not None:
            with open(self.path, "w", newline="") as file:
                file.write(contents)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            load_products(self.path, self.inventory, self.supplier)
        return output.getvalue().splitlines()

    def test_brief_file_loads_three_products(self) -> None:
        """The brief's file: two bad rows reported and skipped, three loaded."""
        printed = self.load(BRIEF_CSV)
        self.assertEqual(printed, [
            "Row 4 skipped: Unknown product type: service",
            "Row 5 skipped: Price 'abc' is not a number.",
            "3 products loaded.",
            "Load attempt finished.",
        ])
        products = self.inventory.get_products()
        self.assertEqual([product.get_product_id() for product in products], ["P001", "D001", "P003"])
        self.assertIsInstance(products[0], PhysicalProduct)
        self.assertIsInstance(products[1], DigitalProduct)
        for product in products:
            self.assertIs(product.get_supplier(), self.supplier)

    def test_missing_file_is_handled_gracefully(self) -> None:
        """A missing file: except and finally run, else doesn't, and nothing crashes."""
        printed = self.load(None)
        self.assertEqual(printed, [
            f"Products file not found: {self.path}",
            "Load attempt finished.",
        ])
        self.assertEqual(self.inventory.get_products(), [])

    def test_load_products_uses_try_except_else_finally(self) -> None:
        """load_products() opens the file inside try / except / else / finally."""
        tree = ast.parse(inspect.getsource(load_products))
        outer_try = next(node for node in ast.walk(tree) if isinstance(node, ast.Try))
        caught = [ast.unparse(handler.type) for handler in outer_try.handlers if handler.type]
        self.assertEqual(caught, ["FileNotFoundError"])
        self.assertTrue(outer_try.orelse, "the try has no else block")
        self.assertTrue(outer_try.finalbody, "the try has no finally block")

    def test_finally_runs_even_when_loading_stops(self) -> None:
        """If an unexpected error stops the load, finally still prints its line."""
        with open(self.path, "w", newline="") as file:
            file.write(BRIEF_CSV)

        output = io.StringIO()
        with (
            mock.patch("csv.reader", side_effect=csv.Error("damaged file")),
            contextlib.redirect_stdout(output),
            self.assertRaises(csv.Error),
        ):
            load_products(self.path, self.inventory, self.supplier)

        self.assertEqual(output.getvalue().splitlines(), ["Load attempt finished."])

    def test_rows_are_created_through_the_factory(self) -> None:
        """Each row reaches ProductFactory.create(); the abc row fails before it does."""
        with mock.patch.object(ProductFactory, "create", wraps=ProductFactory.create) as create:
            self.load(BRIEF_CSV)

        self.assertEqual([call.args[0] for call in create.call_args_list],
                         ["physical", "digital", "service", "physical"])

    def test_loaded_products_get_the_default_size(self) -> None:
        """The file has no weights, so the factory gives the default size."""
        self.load(BRIEF_CSV)
        lamp = self.inventory.find_product("P001")
        self.assertIsInstance(lamp, PhysicalProduct)
        self.assertEqual(lamp.get_weight(), ProductFactory.DEFAULT_SIZE)

    def test_duplicate_ids_are_reported_and_skipped(self) -> None:
        """A row whose ID is already in the inventory is reported and skipped."""
        self.inventory.add_product(
            ProductFactory.create("physical", "P001", "Laptop", 1200.00, 15, self.supplier, 2.1)
        )
        printed = self.load(BRIEF_CSV)
        self.assertIn("Row 2 skipped: P001 is already in the inventory.", printed)
        self.assertIn("2 products loaded.", printed)
        self.assertEqual(self.inventory.find_product("P001").get_name(), "Laptop")

    def test_rows_with_other_problems_are_reported(self) -> None:
        """Wrong value counts, bad stock and a price of 0 are each reported and skipped."""
        printed = self.load(
            "product_type,product_id,name,price,stock_quantity\n"
            "physical,P010,Lamp,25.00\n"
            "physical,P011,Chair,80.00,many\n"
            "digital,D010,Free App,0,10\n"
            "\n"
            "digital,D011,Paid App,4.99,10\n"
        )
        self.assertEqual(printed, [
            "Row 2 skipped: Expected 5 values but found 4.",
            "Row 3 skipped: Stock quantity 'many' is not a whole number.",
            "Row 4 skipped: Price must be greater than zero.",
            "1 products loaded.",
            "Load attempt finished.",
        ])


class TestSpecificExceptions(unittest.TestCase):
    def test_every_except_names_a_specific_exception(self) -> None:
        """No except in the program catches every exception."""
        broad = []
        for filename in sorted(os.listdir(PROJECT_FOLDER)):
            if filename.endswith(".py"):
                with open(os.path.join(PROJECT_FOLDER, filename)) as file:
                    tree = ast.parse(file.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        names = [] if node.type is None else [
                            name.id for name in ast.walk(node.type) if isinstance(name, ast.Name)
                        ]
                        if node.type is None or "Exception" in names or "BaseException" in names:
                            broad.append(f"{filename}, line {node.lineno}")

        self.assertEqual(broad, [])
