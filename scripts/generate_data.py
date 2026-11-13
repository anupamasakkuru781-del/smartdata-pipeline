
import csv
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BASE_DIR / "data" / "input" / "large_transactions.csv"

CUSTOMER_IDS = ["CUST001", "CUST002", "CUST003"]

def generate_transaction(row_number, rng, previous_record):
    # Introduce a duplicate occasionally.
    if row_number > 1 and row_number % 997 == 0:
        return previous_record.copy()

    transaction_id = f"TXN{row_number:08d}"

    customer_id = rng.choice(CUSTOMER_IDS)
    amount = round(rng.uniform(100, 50000), 2)
    currency = rng.choice(["INR", "INR", "INR", "USD", "EUR"])
    status = rng.choice(["completed", "pending", "refunded"])

    # Generate deterministic dates within October 2026.
    base_date = datetime(2026, 10, 1)
    transaction_date = base_date + timedelta(
        days=rng.randint(0, 30),
        hours=rng.randint(0, 23),
        minutes=rng.randint(0, 59)
    )

    record = {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "amount": f"{amount:.2f}",
        "currency": currency,
        "transaction_ts": transaction_date.isoformat(),
        "status": status
    }

    # Add controlled invalid records for testing.
    if row_number % 500 == 0:
        record["amount"] = "-100"

    elif row_number % 700 == 0:
        record["amount"] = ""

    elif row_number % 900 == 0:
        record["customer_id"] = "CUST999"

    elif row_number % 1100 == 0:
        record["currency"] = "GBP"

    elif row_number % 1300 == 0:
        record["transaction_ts"] = "invalid-date"

    return record


def generate_dataset(total_rows, seed):
    rng = random.Random(seed)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "transaction_id",
        "customer_id",
        "amount",
        "currency",
        "transaction_ts",
        "status"
    ]

    previous_record = None

    with open(
        OUTPUT_FILE,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row_number in range(1, total_rows + 1):
            record = generate_transaction(
                row_number,
                rng,
                previous_record
            )

            writer.writerow(record)

            if row_number % 997 != 0:
                previous_record = record.copy()

            if row_number % 10000 == 0:
                print(f"Generated {row_number:,} records...")

    print("\nDataset generated successfully!")
    print(f"File: {OUTPUT_FILE}")
    print(f"Total records: {total_rows:,}")
    print(f"Random seed: {seed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic transaction data"
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=100000,
        help="Number of records to generate"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible data"
    )

    args = parser.parse_args()

    if args.rows < 1:
        parser.error("--rows must be at least 1")

    generate_dataset(args.rows, args.seed)
