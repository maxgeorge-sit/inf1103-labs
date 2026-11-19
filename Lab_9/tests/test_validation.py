import unittest

from order import Order
from order_line import OrderLine
from product import Product
from product_factory import ProductFactory
from supplier import Supplier


def make_product(product_type: str, price: float = 25.00, stock: int = 10) -> Product:
    supplier = Supplier("S001", "Acme Components", "sales@acme.example.com")
    return ProductFactory.create(product_type, "X001", "Test Item", price, stock, supplier, 1.5)


class TestProductValidation(unittest.TestCase):
    # Every rule is checked on both kinds of product: under LSP, a subclass
    # keeps its parent's rules.
    PRODUCT_TYPES = ["physical", "digital"]

    def test_price_must_be_greater_than_zero(self) -> None:
        """A price of 0 or less is refused, with a clear message."""
        for product_type in self.PRODUCT_TYPES:
            for price in [0, -5]:
                with self.subTest(product_type=product_type, price=price):
                    with self.assertRaises(ValueError) as caught:
                        make_product(product_type, price=price)
                    self.assertEqual(str(caught.exception), "Price must be greater than zero.")

    def test_price_must_be_a_number(self) -> None:
        """A price that isn't a usable number is refused."""
        for product_type in self.PRODUCT_TYPES:
            for price in ["abc", None, float("nan"), float("inf")]:
                with self.subTest(product_type=product_type, price=price):
                    with self.assertRaises(ValueError):
                        make_product(product_type, price=price)

    def test_smallest_prices_are_accepted(self) -> None:
        """A price just above zero is accepted."""
        for product_type in self.PRODUCT_TYPES:
            with self.subTest(product_type=product_type):
                self.assertEqual(make_product(product_type, price=0.01).get_price(), 0.01)

    def test_stock_cannot_start_negative(self) -> None:
        """A product can't be created with negative stock."""
        for product_type in self.PRODUCT_TYPES:
            with self.subTest(product_type=product_type):
                with self.assertRaises(ValueError) as caught:
                    make_product(product_type, stock=-1)
                self.assertEqual(str(caught.exception), "Stock cannot be negative.")

    def test_stock_cannot_be_updated_below_zero(self) -> None:
        """update_stock(-1) is refused, and the stock stays as it was."""
        for product_type in self.PRODUCT_TYPES:
            with self.subTest(product_type=product_type):
                product = make_product(product_type, stock=10)
                with self.assertRaises(ValueError):
                    product.update_stock(-1)
                self.assertEqual(product.get_stock(), 10)

    def test_zero_stock_is_accepted(self) -> None:
        """A stock of 0 is allowed: the product is just sold out."""
        for product_type in self.PRODUCT_TYPES:
            with self.subTest(product_type=product_type):
                self.assertEqual(make_product(product_type, stock=0).get_stock(), 0)


class TestOrderLineValidation(unittest.TestCase):
    def test_quantity_must_be_greater_than_zero(self) -> None:
        """An order line refuses a quantity of 0 or less, with a clear message."""
        for quantity in [0, -3]:
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError) as caught:
                    OrderLine(make_product("physical"), quantity)
                self.assertEqual(str(caught.exception), "Quantity must be greater than zero.")

    def test_quantity_must_be_a_whole_number(self) -> None:
        """An order line refuses a quantity that isn't a whole number."""
        for quantity in [2.5, "2", True]:
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    OrderLine(make_product("physical"), quantity)

    def test_order_is_protected_by_its_lines(self) -> None:
        """The OrderLine owns the rule, so an Order can't add a line of 0."""
        order = Order("O001")
        with self.assertRaises(ValueError):
            order.add_order_line(make_product("digital"), 0)
        self.assertEqual(order.get_order_lines(), [])

    def test_quantity_of_one_is_accepted(self) -> None:
        """A quantity of 1 is the smallest allowed."""
        self.assertEqual(OrderLine(make_product("physical"), 1).get_quantity(), 1)
