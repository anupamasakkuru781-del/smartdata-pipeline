
import csv
import pytest

from app.ingestion import read_csv_batches


def create_csv(file_path, records, fieldnames=None):
    if fieldnames is None:
        fieldnames = [
            "transaction_id",
            "customer_id",
            "amount",
            "currency",
            "transaction_ts",
            "status"
        ]

    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def test_read_csv_in_batches(tmp_path):
    input_file = tmp_path / "transactions.csv"

    records = [
        {
            "transaction_id": "TXN001",
            "customer_id": "CUST001",
            "amount": "500",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN002",
            "customer_id": "CUST002",
            "amount": "700",
            "currency": "INR",
            "transaction_ts": "2026-10-10T11:30:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN003",
            "customer_id": "CUST003",
            "amount": "900",
            "currency": "USD",
            "transaction_ts": "2026-10-10T12:30:00",
            "status": "pending"
        }
    ]

    create_csv(input_file, records)

    batches = list(read_csv_batches(input_file, batch_size=2))

    assert len(batches) == 2
    assert len(batches[0]) == 2
    assert len(batches[1]) == 1


def test_row_numbers_are_preserved(tmp_path):
    input_file = tmp_path / "row_numbers.csv"

    records = [
        {
            "transaction_id": "TXN001",
            "customer_id": "CUST001",
            "amount": "500",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN002",
            "customer_id": "CUST002",
            "amount": "700",
            "currency": "INR",
            "transaction_ts": "2026-10-10T11:30:00",
            "status": "completed"
        }
    ]

    create_csv(input_file, records)

    batches = list(read_csv_batches(input_file, batch_size=1))

    assert batches[0][0][0] == 2
    assert batches[1][0][0] == 3


def test_missing_file(tmp_path):
    input_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        list(read_csv_batches(input_file))


def test_invalid_batch_size(tmp_path):
    input_file = tmp_path / "transactions.csv"

    records = [{
        "transaction_id": "TXN001",
        "customer_id": "CUST001",
        "amount": "500",
        "currency": "INR",
        "transaction_ts": "2026-10-10T10:30:00",
        "status": "completed"
    }]

    create_csv(input_file, records)

    with pytest.raises(ValueError, match="Batch size must be at least 1"):
        list(read_csv_batches(input_file, batch_size=0))


def test_missing_csv_columns(tmp_path):
    input_file = tmp_path / "missing_columns.csv"

    records = [{
        "transaction_id": "TXN001",
        "customer_id": "CUST001",
        "amount": "500"
    }]

    create_csv(
        input_file,
        records,
        fieldnames=["transaction_id", "customer_id", "amount"]
    )

    with pytest.raises(ValueError, match="Missing CSV columns"):
        list(read_csv_batches(input_file))


def test_empty_csv_file(tmp_path):
    input_file = tmp_path / "empty.csv"
    input_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV file is empty or has no header"):
        list(read_csv_batches(input_file))


def test_header_only_csv_returns_no_batches(tmp_path):
    input_file = tmp_path / "header_only.csv"

    create_csv(input_file, [])

    batches = list(read_csv_batches(input_file))

    assert batches == []


def test_unexpected_csv_column(tmp_path):
    input_file = tmp_path / "unexpected_column.csv"

    fields = [
        "transaction_id",
        "customer_id",
        "amount",
        "currency",
        "transaction_ts",
        "status",
        "extra_column"
    ]

    records = [{
        "transaction_id": "TXN001",
        "customer_id": "CUST001",
        "amount": "500",
        "currency": "INR",
        "transaction_ts": "2026-10-10T10:30:00",
        "status": "completed",
        "extra_column": "unexpected"
    }]

    create_csv(input_file, records, fieldnames=fields)

    with pytest.raises(ValueError, match="Unexpected CSV columns"):
        list(read_csv_batches(input_file))


def test_malformed_csv_row_with_extra_value(tmp_path):
    input_file = tmp_path / "malformed.csv"

    input_file.write_text(
        "transaction_id,customer_id,amount,currency,transaction_ts,status\n"
        "TXN001,CUST001,500,INR,2026-10-10T10:30:00,completed,EXTRA\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Malformed CSV row"):
        list(read_csv_batches(input_file))
