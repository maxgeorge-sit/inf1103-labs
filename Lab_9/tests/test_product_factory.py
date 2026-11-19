import ast
import contextlib
import inspect
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import inventory_manager
from digital_product import DigitalProduct
from inventory import Inventory
from physical_product import PhysicalProduct
from product import Product
from product_factory import ProductFactory
from supplier import Supplier

# The project folder: the one that holds this tests folder.
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_supplier() -> Supplier:
    return Supplier("S001", "Acme Components", "sales@acme.example.com")


class TestProductFactory(unittest.TestCase):
    def test_creates_a_physical_product(self) -> None:
        """create("physical", ...) builds a PhysicalProduct, with size as its weight."""
        product = ProductFactory.create("physical", "P101", "Desk Lamp", 25.00, 10, make_supplier(), 1.2)
        self.assertIsInstance(product, PhysicalProduct)
        self.assertEqual(product.get_product_id(), "P101")
        self.assertEqual(product.get_name(), "Desk Lamp")
        self.assertEqual(product.get_price(), 25.00)
        self.assertEqual(product.get_stock(), 10)
        self.assertEqual(product.get_weight(), 1.2)

    def test_creates_a_digital_product(self) -> None:
        """create("digital", ...) builds a DigitalProduct, with size as its download size."""
        product = ProductFactory.create("digital", "D101", "Photo Editor", 49.90, 100, make_supplier(), 850)
        self.assertIsInstance(product, DigitalProduct)
        self.assertEqual(product.get_download_size(), 850)

    def test_factory_promises_a_product(self) -> None:
        """create() is typed to return Product, not a particular subclass."""
        self.assertIs(inspect.signature(ProductFactory.create).return_annotation, Product)

    def test_unknown_type_raises_value_error(self) -> None:
        """An unknown type raises ValueError with a clear message."""
        with self.assertRaises(ValueError) as caught:
            ProductFactory.create("service", "S001", "Installation", 30.00, 5, make_supplier(), 1.0)

        self.assertEqual(str(caught.exception), "Unknown product type: service")

    def test_program_creates_products_only_through_the_factory(self) -> None:
        """No program file but the factory creates a PhysicalProduct or DigitalProduct."""
        direct = []
        for filename in sorted(os.listdir(PROJECT_FOLDER)):
            if filename.endswith(".py") and filename != "product_factory.py":
                with open(os.path.join(PROJECT_FOLDER, filename)) as file:
                    tree = ast.parse(file.read())

                for node in ast.walk(tree):
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id in ("PhysicalProduct", "DigitalProduct")
                    ):
                        direct.append(f"{filename}, line {node.lineno}")

        self.assertEqual(direct, [])

    def test_loading_inventory_json_uses_the_factory(self) -> None:
        """Products loaded from inventory.json come from ProductFactory.create()."""
        supplier = make_supplier().to_dict()
        records = [
            {"id": "P101", "name": "Desk Lamp", "price": 25.0, "stock": 10,
             "supplier": supplier, "type": "physical", "weight": 1.2},
            {"id": "D101", "name": "Photo Editor", "price": 49.9, "stock": 100,
             "supplier": supplier, "type": "digital", "download_size": 850.0},
        ]
        inventory = Inventory()
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "inventory.json")
            with open(path, "w") as file:
                json.dump(records, file)

            with (
                mock.patch.object(inventory_manager, "INVENTORY_FILE", path),
                mock.patch.object(ProductFactory, "create", wraps=ProductFactory.create) as create,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                inventory_manager.load_inventory(inventory)

        self.assertEqual(create.call_count, 2)
        self.assertIsInstance(inventory.find_product("P101"), PhysicalProduct)
        self.assertIsInstance(inventory.find_product("D101"), DigitalProduct)

    def test_add_product_uses_the_factory(self) -> None:
        """The menu's Add Product asks the factory for the new product."""
        entries = ["1", "P101", "Desk Lamp", "25", "10",
                   "S009", "Nordic Lights", "hello@nordic.example.com", "1.2"]
        inventory = Inventory()
        with (
            mock.patch("builtins.input", side_effect=entries),
            mock.patch.object(ProductFactory, "create", wraps=ProductFactory.create) as create,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            inventory_manager.add_product_menu(inventory)

        create.assert_called_once()
        self.assertIsInstance(inventory.find_product("P101"), PhysicalProduct)