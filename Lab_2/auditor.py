def main():
    inventory = 0
    rejected_entries = 0

    while True:
        entry = input("Enter stock quantity (or 'quit' to finish): ").strip()

        if entry.lower() == "quit":
            break

        if entry.startswith(("-", "+")):
            digits = entry[1:]
        else:
            digits = entry
            
        if not digits.isdigit():
            print("Error: Enter a whole number.")
            rejected_entries += 1
            continue

        try:
            quantity = int(entry)
        except ValueError:
            print("Error: Enter a valid integer.")
            rejected_entries += 1
            continue

        if quantity < 0:
            print("Error: Enter a positive integer.")
            rejected_entries += 1
            continue

        inventory += quantity
        print(f"Current inventory: {inventory} units")

        if inventory > 500:
            print("OVERSTOCK ALERT: Inventory exceeds 500 units!")
            break

    print(f"Total Units Processed: {inventory}")
    print(f"Number of Failed/Rejected Entries: {rejected_entries}")


if __name__ == "__main__":
    main()
