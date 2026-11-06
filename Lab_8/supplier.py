# The shape of a supplier's record in inventory.json.
SupplierRecord = dict[str, str]


# A supplier exists on its own: products refer to it (association), but a
# supplier is not part of a product, and a product is not part of it.
class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        if not isinstance(supplier_id, str) or not supplier_id.strip():
            raise ValueError("Supplier ID must be non-empty text.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Supplier name must be non-empty text.")

        if not isinstance(contact_email, str):
            raise ValueError("Contact email must be text.")

        # An email address needs text on both sides of the @ sign.
        user, at_sign, domain = contact_email.strip().partition("@")
        if not user or not at_sign or not domain:
            raise ValueError("Contact email must look like name@example.com.")

        self.__supplier_id: str = supplier_id.strip().upper()
        self.__name: str = name.strip()
        self.__contact_email: str = contact_email.strip()

    def get_supplier_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    def display_information(self) -> None:
        print(f"Supplier ID: {self.__supplier_id}")
        print(f"Name: {self.__name}")
        print(f"Contact Email: {self.__contact_email}")

    # The supplier's details as they are saved in inventory.json.
    def to_dict(self) -> SupplierRecord:
        return {
            "supplier_id": self.__supplier_id,
            "name": self.__name,
            "contact_email": self.__contact_email,
        }
