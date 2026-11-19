from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


# The Factory pattern: the one place that decides which Product subclass to
# create. The rest of the program asks the factory and gets back a Product,
# so it never needs to name PhysicalProduct or DigitalProduct itself.
class ProductFactory:
    # products.csv has no weight or download size, so a product created
    # without a size gets this one. If that rule changes, it changes here.
    DEFAULT_SIZE: float = 1.0

    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock_quantity: int, supplier: Supplier,
               size: float = DEFAULT_SIZE) -> Product:
        # size is the weight in kg for a physical product, and the download
        # size in MB for a digital one.
        if product_type == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity, supplier, size)
        elif product_type == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity, supplier, size)
        else:
            raise ValueError(f"Unknown product type: {product_type}")