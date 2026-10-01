INVENTORY_FILE = "inventory.txt"

def load_inventory():
    try:
        with open(INVENTORY_FILE, "r") as file:
            lines = file.read().splitlines()
    except FileNotFoundError:
        return 0, []

    if not lines:
        return 0, []

    total = int(lines[0])

    history = []
    if len(lines) > 1 and lines[1].strip():
        history = [int(amount) for amount in lines[1].split(",")]

    return total, history


def get_valid_input():
    entry = input(
        "Enter stock quantity (or 'quit' to finish): "
    ).strip()

    if entry.lower() == "quit":
        return "quit"

    if entry.startswith(("-", "+")):
        digits = entry[1:]
    else:
        digits = entry

    if not digits.isdigit():
        raise ValueError("Enter a whole number.")

    try:
        quantity = int(entry)
    except ValueError:
        raise ValueError("Enter a valid integer.") from None

    if quantity < 0:
        raise ValueError("Negative quantities are not allowed.")

    return quantity


def process_delivery(current_total, new_value):
    new_total = current_total + new_value
    return new_total


def calculate_tax(amount):
    tax = amount * 0.10
    return tax


def generate_report(total_units, failed_attempts):
    print(f"Total Units Processed: {total_units}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")


def main():
    inventory, history = load_inventory()
    rejected_entries = 0
    deliveries_processed = 0

    print(f"Loaded inventory: {inventory} units")
    print(f"Loaded history: {history}")

    while True:
        try:
            quantity = get_valid_input()
        except ValueError as error:
            print(f"Error: {error}")
            rejected_entries += 1
            continue

        if quantity == "quit":
            break

        inventory = process_delivery(inventory, quantity)
        delivery_tax = calculate_tax(quantity)
        deliveries_processed += 1

        print(f"Current inventory: {inventory} units")
        print(f"Tax for this delivery: {delivery_tax:.2f}")

        if inventory > 500:
            print("OVERSTOCK ALERT: Inventory exceeds 500 units!")
            break

    print("\nFinal Summary")
    print(f"Total Deliveries Processed: {deliveries_processed}")
    generate_report(inventory, rejected_entries)


if __name__ == "__main__":
    main()