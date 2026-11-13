
import csv
from pathlib import Path


# Project directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Sample CSV output location
OUTPUT_FILE = BASE_DIR / "data" / "input" / "sample_transactions.csv"


def create_sample_data():

    # Create input folder if it does not exist
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Sample transaction records
    records = [
        {
            "transaction_id": "TXN1001",
            "customer_id": "CUST001",
            "amount": "500.00",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN1002",
            "customer_id": "CUST002",
            "amount": "1500.00",
            "currency": "INR",
            "transaction_ts": "2026-10-10T11:00:00",
            "status": "pending"
        },
        {
            "transaction_id": "TXN1003",
            "customer_id": "CUST003",
            "amount": "12000.00",
            "currency": "INR",
            "transaction_ts": "2026-10-10T12:00:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN1004",
            "customer_id": "CUST001",
            "amount": "-200.00",
            "currency": "INR",
            "transaction_ts": "2026-10-10T13:00:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN1005",
            "customer_id": "CUST002",
            "amount": "",
            "currency": "INR",
            "transaction_ts": "2026-10-10T14:00:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN1006",
            "customer_id": "CUST999",
            "amount": "750.00",
            "currency": "INR",
            "transaction_ts": "2026-10-10T15:00:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN1007",
            "customer_id": "CUST003",
            "amount": "900.00",
            "currency": "GBP",
            "transaction_ts": "2026-10-10T16:00:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN1008",
            "customer_id": "CUST001",
            "amount": "3000.00",
            "currency": "INR",
            "transaction_ts": "invalid-date",
            "status": "completed"
        },
        {
            "transaction_id": "TXN1001",
            "customer_id": "CUST001",
            "amount": "500.00",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "completed"
        }
    ]

    # CSV column names
    fieldnames = [
        "transaction_id",
        "customer_id",
        "amount",
        "currency",
        "transaction_ts",
        "status"
    ]

    # Write records to CSV
    with open(
        OUTPUT_FILE,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)

    print("Sample CSV dataset created successfully!")
    print(f"File location: {OUTPUT_FILE}")
    print(f"Total records created: {len(records)}")


if __name__ == "__main__":
    create_sample_data()
