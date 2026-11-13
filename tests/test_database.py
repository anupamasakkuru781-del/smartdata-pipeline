
import pytest

from app.database import (
    create_connection,
    initialize_database,
    customer_exists,
    transaction_exists,
    insert_transaction,
    insert_reject
)


@pytest.fixture
def db_connection(tmp_path):
    db_path = tmp_path / "test_database.db"

    initialize_database(db_path)
    connection = create_connection(db_path)

    # Create a pipeline run because transactions
    # must reference an existing run.
    connection.execute(
        """
        INSERT INTO pipeline_runs (
            run_id, source_file, status, start_time
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            "RUN001",
            "test.csv",
            "running",
            "2026-10-10T10:00:00"
        )
    )

    # Insert a test customer.
    connection.execute(
        """
        INSERT INTO customers (
            customer_id, customer_name, email
        )
        VALUES (?, ?, ?)
        """,
        ("CUST001", "Test Customer", "test@example.com")
    )

    connection.commit()

    yield connection

    connection.close()


def get_transaction():
    return {
        "transaction_id": "TXN1001",
        "customer_id": "CUST001",
        "amount": 500.0,
        "currency": "INR",
        "transaction_ts": "2026-10-10T10:30:00",
        "status": "completed",
        "amount_category": "small",
        "source_file": "test.csv",
        "source_row_number": 2,
        "run_id": "RUN001"
    }


def test_customer_exists(db_connection):
    assert customer_exists(db_connection, "CUST001") is True
    assert customer_exists(db_connection, "CUST999") is False


def test_insert_transaction(db_connection):
    record = get_transaction()

    insert_transaction(db_connection, record)
    db_connection.commit()

    assert transaction_exists(
        db_connection, "TXN1001"
    ) is True


def test_transaction_does_not_exist(db_connection):
    assert transaction_exists(
        db_connection, "TXN9999"
    ) is False


def test_insert_reject(db_connection):
    insert_reject(
        db_connection,
        "RUN001",
        "test.csv",
        5,
        {"transaction_id": "TXN1005", "amount": "-200"},
        "Amount must be greater than zero"
    )

    db_connection.commit()

    result = db_connection.execute(
        "SELECT error_reason FROM rejects"
    ).fetchone()

    assert result[0] == "Amount must be greater than zero"
