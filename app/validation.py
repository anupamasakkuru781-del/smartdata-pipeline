
import math
from datetime import datetime

from app.schema import (
    REQUIRED_FIELDS,
    ALLOWED_CURRENCIES,
    ALLOWED_STATUSES
)


def validate_record(record):
    """
    Validate one transaction record.

    Returns:
        cleaned_record: Validated and converted record.
        errors: List of validation error messages.
    """

    errors = []
    cleaned_record = {}

    # 1. Check required fields
    for field in REQUIRED_FIELDS:
        value = record.get(field)

        if value is None or str(value).strip() == "":
            errors.append(f"Missing required field: {field}")
        else:
            cleaned_record[field] = str(value).strip()

    # Stop further checks if required fields are missing.
    if errors:
        return cleaned_record, errors

    # 2. Validate transaction ID
    if not cleaned_record["transaction_id"]:
        errors.append("Transaction ID cannot be empty")

    # 3. Validate customer ID
    if not cleaned_record["customer_id"]:
        errors.append("Customer ID cannot be empty")

    # 4. Validate transaction amount
    try:
        amount = float(cleaned_record["amount"])

        if not math.isfinite(amount):
            errors.append("Amount must be a finite number")
        elif amount <= 0:
            errors.append("Amount must be greater than zero")
        else:
            cleaned_record["amount"] = amount

    except (ValueError, TypeError):
        errors.append("Amount must be a valid number")

    # 5. Validate currency
    if cleaned_record["currency"] not in ALLOWED_CURRENCIES:
        errors.append(
            f"Invalid currency: {cleaned_record['currency']}"
        )

    # 6. Validate transaction status
    if cleaned_record["status"] not in ALLOWED_STATUSES:
        errors.append(
            f"Invalid transaction status: {cleaned_record['status']}"
        )

    # 7. Validate transaction timestamp
    try:
        datetime.fromisoformat(cleaned_record["transaction_ts"])
    except ValueError:
        errors.append("Invalid transaction timestamp")

    return cleaned_record, errors
