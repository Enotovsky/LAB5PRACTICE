import csv
import random
import uuid
from pathlib import Path

def generate_big_data():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    file_path = data_dir / "large_data.csv"

    # We want ~1GB file.
    # To keep memory footprint under 50MB for duplicate checking, we generate a small set of unique IDs
    # and repeat them, OR we use large padding in other fields.
    # Let's generate 200,000 unique transactions.
    unique_count = 200000
    transactions = []
    categories = ["food", "transport", "entertainment", "bills", "shopping"]
    
    # Pre-generate the unique records
    for _ in range(unique_count):
        tx_id = f"tx-{uuid.uuid4()}"
        amount = round(random.uniform(1.0, 5000.0), 2)
        category = random.choice(categories)
        date = f"2026-05-{random.randint(1, 28):02d}"
        currency = "RUB"
        # Large padding in the category to inflate file size but keep unique ID count small
        padding = "X" * 1024 # 1 KB per row
        transactions.append({
            "id": tx_id,
            "amount": amount,
            "category": f"{category}_{padding}",
            "date": date,
            "currency": currency
        })

    # 1 KB per row means 1,000,000 rows is ~1 GB
    total_rows = 1_000_000

    print(f"Generating {total_rows} rows to {file_path}...")
    with file_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "amount", "category", "date", "currency"])
        writer.writeheader()
        for i in range(total_rows):
            # Write identical duplicates (which are ignored by the aggregator without error)
            # The aggregator just skips them, so the error isn't raised.
            writer.writerow(transactions[i % unique_count])

    print("Generation complete.")

if __name__ == "__main__":
    generate_big_data()
