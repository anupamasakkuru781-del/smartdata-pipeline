
from app.transformation import transform_record


def get_valid_record():
    return {
        "transaction_id": "TXN1001",
        "customer_id": "CUST001",
        "amount": 500.0,
        "currency": "INR",
        "transaction_ts": "2026-10-10T10:30:00",
        "status": "completed"
    }


def test_transform_small_transaction():
    record = get_valid_record()

    result = transform_record(
        record,
        "sample_transactions.csv",
        2,
        "RUN001"
    )

    assert result["amount_category"] == "small"
    assert result["amount"] == 500.0
    assert result["run_id"] == "RUN001"


def test_transform_medium_transaction():
    record = get_valid_record()
    record["amount"] = 5000.0

    result = transform_record(
        record,
        "sample_transactions.csv",
        3,
        "RUN001"
    )

    assert result["amount_category"] == "medium"


def test_transform_large_transaction():
    record = get_valid_record()
    record["amount"] = 15000.0

    result = transform_record(
        record,
        "sample_transactions.csv",
        4,
        "RUN001"
    )

    assert result["amount_category"] == "large"


def test_transform_source_information():
    record = get_valid_record()

    result = transform_record(
        record,
        "sample_transactions.csv",
        5,
        "RUN002"
    )

    assert result["source_file"] == "sample_transactions.csv"
    assert result["source_row_number"] == 5
    assert result["run_id"] == "RUN002"
