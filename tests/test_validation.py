
from app.validation import validate_record


def get_valid_record():
    return {
        "transaction_id": "TXN1001",
        "customer_id": "CUST001",
        "amount": "500.00",
        "currency": "INR",
        "transaction_ts": "2026-10-10T10:30:00",
        "status": "completed"
    }


def test_valid_record():
    record = get_valid_record()

    cleaned_record, errors = validate_record(record)

    assert errors == []
    assert cleaned_record["amount"] == 500.0


def test_negative_amount():
    record = get_valid_record()
    record["amount"] = "-200"

    cleaned_record, errors = validate_record(record)

    assert any("greater than zero" in error for error in errors)


def test_zero_amount():
    record = get_valid_record()
    record["amount"] = "0"

    cleaned_record, errors = validate_record(record)

    assert any("greater than zero" in error for error in errors)


def test_non_finite_amount():
    for invalid_amount in ["NaN", "inf", "-inf"]:
        record = get_valid_record()
        record["amount"] = invalid_amount

        cleaned_record, errors = validate_record(record)

        assert any("finite number" in error for error in errors)


def test_null_amount():
    record = get_valid_record()
    record["amount"] = None

    cleaned_record, errors = validate_record(record)

    assert any("Missing required field: amount" in error for error in errors)


def test_invalid_currency():
    record = get_valid_record()
    record["currency"] = "GBP"

    cleaned_record, errors = validate_record(record)

    assert any("Invalid currency" in error for error in errors)


def test_invalid_timestamp():
    record = get_valid_record()
    record["transaction_ts"] = "invalid-date"

    cleaned_record, errors = validate_record(record)

    assert any("Invalid transaction timestamp" in error for error in errors)


def test_missing_amount():
    record = get_valid_record()
    record["amount"] = ""

    cleaned_record, errors = validate_record(record)

    assert any("Missing required field: amount" in error for error in errors)


def test_invalid_status():
    record = get_valid_record()
    record["status"] = "unknown"

    cleaned_record, errors = validate_record(record)

    assert any("Invalid transaction status" in error for error in errors)


def test_empty_record():
    cleaned_record, errors = validate_record({})

    assert len(errors) == 6
    assert cleaned_record == {}


def test_whitespace_only_customer_id():
    record = get_valid_record()
    record["customer_id"] = "   "

    cleaned_record, errors = validate_record(record)

    assert any("Missing required field: customer_id" in error for error in errors)


def test_boundary_amount_one():
    record = get_valid_record()
    record["amount"] = "1"

    cleaned_record, errors = validate_record(record)

    assert errors == []
    assert cleaned_record["amount"] == 1.0
