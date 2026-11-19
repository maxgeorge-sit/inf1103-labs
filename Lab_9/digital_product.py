from product import Product, ProductRecord, check_positive_number
from supplier import Supplier


class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float) -> None:
        # Same pattern as PhysicalProduct: Product's constructor runs first.
        super().__init__(product_id, name, price, stock, supplier)

        # A digital product has no weight; it has a download size in megabytes.
        self.__download_size: float = check_positive_number(download_size, "Download size")

    def get_download_size(self) -> float:
        return self.__download_size

    # Overrides both methods the same way PhysicalProduct does.
    def display_information(self) -> None:
        super().display_information()
        print(f"Download Size: {self.__download_size:.2f} MB")

    def __str__(self) -> str:
        return f"{super().__str__()} | Download Size: {self.__download_size:.2f} MB"

    def to_dict(self) -> ProductRecord:
        record = super().to_dict()
        record["type"] = "digital"
        record["download_size"] = self.__download_size
        return record

    def get_fulfilment_info(self) -> str:
        return "This product is delivered digitally as a download."
