
from app.schema import get_amount_category


def transform_record(record, source_file, row_number, run_id):
    """
    Transform a validated transaction into
    the database-ready format.
    """

    transformed_record = {
        "transaction_id": record["transaction_id"],
        "customer_id": record["customer_id"],
        "amount": float(record["amount"]),
        "currency": record["currency"],
        "transaction_ts": record["transaction_ts"],
        "status": record["status"],
        "amount_category": get_amount_category(
            float(record["amount"])
        ),
        "source_file": str(source_file),
        "source_row_number": row_number,
        "run_id": run_id
    }

    return transformed_record
