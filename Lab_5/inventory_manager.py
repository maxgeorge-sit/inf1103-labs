DIVIDER = "-" * 48


def search_product(inventory, product_id):
    product_id = product_id.strip().upper()

    for product in inventory:
        if product["id"] == product_id:
            return product

    return None


def add_product(inventory, product_id, name, price, stock):
    
    product_id = product_id.strip().upper()

    if search_product(inventory, product_id) is not None:
        return False

    product = {
        "id": product_id,
        "name": name.strip(),
        "price": price,
        "stock": stock,
    }
    inventory.append(product)
    return True


def update_stock(inventory, product_id, new_stock):

    product = search_product(inventory, product_id)

    if product is None:
        return False

    product["stock"] = new_stock
    return True


def display_product(product):
    print(DIVIDER)
    print(f"ID: {product['id']}")
    print(f"Name: {product['name']}")
    print(f"Price: ${product['price']:.2f}")
    print(f"Stock: {product['stock']}")
    print(DIVIDER)


def display_all(inventory):
    print("\nCurrent Inventory")
    print(DIVIDER)

    if not inventory:
        print("No products in inventory.")

    for product in inventory:
        print(
            f"ID: {product['id']} | Name: {product['name']} | "
            f"Price: ${product['price']:.2f} | Stock: {product['stock']}"
        )

    print(DIVIDER)


def main():
    inventory = []

    add_product(inventory, "P001", "Laptop", 1200.00, 15)
    add_product(inventory, "P002", "Mouse", 25.50, 40)
    add_product(inventory, "P003", "Keyboard", 45.00, 25)
    display_all(inventory)

    add_product(inventory, "P004", "Monitor", 299.99, 10)
    update_stock(inventory, "P002", 50)
    display_all(inventory)

    product = search_product(inventory, "P004")
    if product is not None:
        print("\nProduct Found")
        display_product(product)


if __name__ == "__main__":
    main()