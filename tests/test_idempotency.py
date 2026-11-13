
import csv
import pytest

from app.database import create_connection, initialize_database
from app import pipeline


@pytest.fixture
def isolated_database(tmp_path, monkeypatch):
    db_path = tmp_path / "idempotency_test.db"

    initialize_database(db_path)

    connection = create_connection(db_path)

    connection.execute(
        """
        INSERT INTO customers (customer_id, customer_name, email)
        VALUES (?, ?, ?)
        """,
        ("CUST001", "Test Customer", "test@example.com")
    )

    connection.commit()
    connection.close()

    monkeypatch.setattr(
        pipeline,
        "create_connection",
        lambda: create_connection(db_path)
    )

    monkeypatch.setattr(
        pipeline,
        "publish_run_outputs",
        lambda connection, run_id: {
            "processed_count": connection.execute(
                "SELECT COUNT(*) FROM transactions WHERE run_id = ?",
                (run_id,)
            ).fetchone()[0],
            "rejected_count": connection.execute(
                "SELECT COUNT(*) FROM rejects WHERE run_id = ?",
                (run_id,)
            ).fetchone()[0]
        }
    )

    return db_path


def create_records_csv(file_path, records):
    fields = [
        "transaction_id",
        "customer_id",
        "amount",
        "currency",
        "transaction_ts",
        "status"
    ]

    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def create_test_csv(file_path):
    records = [
        {
            "transaction_id": "TXN1001",
            "customer_id": "CUST001",
            "amount": "500",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN1001",
            "customer_id": "CUST001",
            "amount": "500",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "completed"
        }
    ]

    create_records_csv(file_path, records)


def test_duplicate_transactions_are_skipped(
    tmp_path,
    isolated_database
):
    input_file = tmp_path / "duplicate_transactions.csv"

    create_test_csv(input_file)

    result = pipeline.run_pipeline(input_file, batch_size=1)

    assert result["input_count"] == 2
    assert result["output_count"] == 1
    assert result["duplicate_count"] == 1
    assert result["rejected_count"] == 0

    connection = create_connection(isolated_database)

    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]

        assert count == 1

    finally:
        connection.close()


def test_rerunning_same_file_does_not_insert_duplicates(
    tmp_path,
    isolated_database
):
    input_file = tmp_path / "rerun_transactions.csv"

    create_test_csv(input_file)

    first_result = pipeline.run_pipeline(input_file, batch_size=1)
    second_result = pipeline.run_pipeline(input_file, batch_size=1)

    assert first_result["output_count"] == 1
    assert first_result["duplicate_count"] == 1

    assert second_result["output_count"] == 0
    assert second_result["duplicate_count"] == 2

    connection = create_connection(isolated_database)

    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]

        assert total == 1

    finally:
        connection.close()


def test_unknown_customer_is_rejected(
    tmp_path,
    isolated_database
):
    input_file = tmp_path / "unknown_customer.csv"

    records = [{
        "transaction_id": "TXN2001",
        "customer_id": "CUST999",
        "amount": "500",
        "currency": "INR",
        "transaction_ts": "2026-10-10T10:30:00",
        "status": "completed"
    }]

    create_records_csv(input_file, records)

    result = pipeline.run_pipeline(input_file, batch_size=1)

    assert result["input_count"] == 1
    assert result["output_count"] == 0
    assert result["rejected_count"] == 1

    connection = create_connection(isolated_database)

    try:
        rejected = connection.execute(
            """
            SELECT source_row_number, error_reason
            FROM rejects
            WHERE run_id = ?
            """,
            (result["run_id"],)
        ).fetchone()

        assert rejected is not None
        assert rejected[0] == 2
        assert "Customer does not exist: CUST999" in rejected[1]

        transaction_count = connection.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]

        assert transaction_count == 0

    finally:
        connection.close()


def test_invalid_amount_and_status_are_rejected(
    tmp_path,
    isolated_database
):
    input_file = tmp_path / "invalid_transactions.csv"

    records = [
        {
            "transaction_id": "TXN2002",
            "customer_id": "CUST001",
            "amount": "-100",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN2003",
            "customer_id": "CUST001",
            "amount": "500",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "unknown"
        }
    ]

    create_records_csv(input_file, records)

    result = pipeline.run_pipeline(input_file, batch_size=2)

    assert result["input_count"] == 2
    assert result["output_count"] == 0
    assert result["rejected_count"] == 2

    connection = create_connection(isolated_database)

    try:
        reasons = connection.execute(
            """
            SELECT error_reason
            FROM rejects
            WHERE run_id = ?
            """,
            (result["run_id"],)
        ).fetchall()

        combined_reasons = " ".join(row[0] for row in reasons)

        assert "Amount must be greater than zero" in combined_reasons
        assert "Invalid transaction status" in combined_reasons

    finally:
        connection.close()


def test_valid_and_invalid_records_in_same_batch(
    tmp_path,
    isolated_database
):
    input_file = tmp_path / "mixed_records.csv"

    records = [
        {
            "transaction_id": "TXN2004",
            "customer_id": "CUST001",
            "amount": "750",
            "currency": "INR",
            "transaction_ts": "2026-10-10T10:30:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN2005",
            "customer_id": "CUST999",
            "amount": "900",
            "currency": "INR",
            "transaction_ts": "2026-10-10T11:30:00",
            "status": "completed"
        }
    ]

    create_records_csv(input_file, records)

    result = pipeline.run_pipeline(input_file, batch_size=2)

    assert result["input_count"] == 2
    assert result["output_count"] == 1
    assert result["rejected_count"] == 1
    assert result["duplicate_count"] == 0

    connection = create_connection(isolated_database)

    try:
        inserted = connection.execute(
            """
            SELECT transaction_id
            FROM transactions
            WHERE run_id = ?
            """,
            (result["run_id"],)
        ).fetchall()

        assert [row[0] for row in inserted] == ["TXN2004"]

        rejected = connection.execute(
            """
            SELECT source_row_number
            FROM rejects
            WHERE run_id = ?
            """,
            (result["run_id"],)
        ).fetchall()

        assert [row[0] for row in rejected] == [3]

    finally:
        connection.close()


def test_pipeline_failure_preserves_committed_batch_and_stops_monitoring(
    isolated_database,
    tmp_path,
    monkeypatch
):
    import pytest
    from app import pipeline

    # Create two valid records for the same existing customer.
    records = [
        {
            "transaction_id": "TXN_FAILURE_001",
            "customer_id": "CUST001",
            "amount": "500",
            "currency": "INR",
            "transaction_ts": "2026-11-12T10:00:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN_FAILURE_002",
            "customer_id": "CUST001",
            "amount": "750",
            "currency": "INR",
            "transaction_ts": "2026-11-12T10:05:00",
            "status": "completed"
        }
    ]

    input_file = tmp_path / "failure_test.csv"
    create_records_csv(input_file, records)

    # Keep the original insert function.
    original_insert = pipeline.insert_transaction
    insert_calls = 0

    # Simulate a failure during the second transaction.
    def insert_with_failure(connection, record):

        nonlocal insert_calls
        insert_calls += 1

        if insert_calls == 2:
            raise RuntimeError(
                "Simulated failure during second batch"
            )

        return original_insert(connection, record)

    monkeypatch.setattr(
        pipeline,
        "insert_transaction",
        insert_with_failure
    )

    # Capture the monitor instance to verify cleanup.
    original_monitor = pipeline.PipelineMonitor
    monitor_instances = []

    def monitor_factory():
        monitor = original_monitor()
        monitor_instances.append(monitor)
        return monitor

    monkeypatch.setattr(
        pipeline,
        "PipelineMonitor",
        monitor_factory
    )

    # Run the pipeline with one record per batch.
    with pytest.raises(
        RuntimeError,
        match="Simulated failure during second batch"
    ):
        pipeline.run_pipeline(
            input_file,
            batch_size=1
        )

    # Check database results.
    connection = pipeline.create_connection()

    try:
        transactions = connection.execute(
            """
            SELECT transaction_id
            FROM transactions
            WHERE transaction_id IN (
                'TXN_FAILURE_001',
                'TXN_FAILURE_002'
            )
            """
        ).fetchall()

        assert [row[0] for row in transactions] == [
            "TXN_FAILURE_001"
        ]

        failed_run = connection.execute(
            """
            SELECT status, input_count, output_count, error_message
            FROM pipeline_runs
            WHERE source_file = ?
            ORDER BY start_time DESC
            LIMIT 1
            """,
            (str(input_file),)
        ).fetchone()

        assert failed_run is not None
        assert failed_run[0] == "failed"
        assert failed_run[1] == 2
        assert failed_run[2] == 1
        assert (
            failed_run[3]
            == "Simulated failure during second batch"
        )

    finally:
        connection.close()

    # Verify that the monitoring thread was stopped.
    assert len(monitor_instances) == 1

    monitor = monitor_instances[0]

    assert monitor.stop_event.is_set()
    assert monitor.monitor_thread is not None
    assert not monitor.monitor_thread.is_alive()


def test_rerun_after_partial_failure_completes_without_duplicates(
    isolated_database,
    tmp_path,
    monkeypatch
):
    import pytest
    from app import pipeline

    records = [
        {
            "transaction_id": "TXN_RECOVERY_001",
            "customer_id": "CUST001",
            "amount": "500",
            "currency": "INR",
            "transaction_ts": "2026-11-12T10:00:00",
            "status": "completed"
        },
        {
            "transaction_id": "TXN_RECOVERY_002",
            "customer_id": "CUST001",
            "amount": "750",
            "currency": "INR",
            "transaction_ts": "2026-11-12T10:05:00",
            "status": "completed"
        }
    ]

    input_file = tmp_path / "recovery_test.csv"
    create_records_csv(input_file, records)

    original_insert = pipeline.insert_transaction
    insert_calls = 0

    def insert_with_one_failure(connection, record):
        nonlocal insert_calls
        insert_calls += 1

        if insert_calls == 2:
            raise RuntimeError("Simulated recovery test failure")

        return original_insert(connection, record)

    # First execution: deliberately fail on the second insert.
    monkeypatch.setattr(
        pipeline,
        "insert_transaction",
        insert_with_one_failure
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated recovery test failure"
    ):
        pipeline.run_pipeline(input_file, batch_size=1)

    # Restore normal insertion before rerunning.
    monkeypatch.setattr(
        pipeline,
        "insert_transaction",
        original_insert
    )

    # Second execution: replay the same input file.
    summary = pipeline.run_pipeline(
        input_file,
        batch_size=1
    )

    assert summary["status"] == "completed"
    assert summary["input_count"] == 2
    assert summary["output_count"] == 1
    assert summary["duplicate_count"] == 1

    connection = pipeline.create_connection()

    try:
        transaction_rows = connection.execute(
            """
            SELECT transaction_id, COUNT(*)
            FROM transactions
            WHERE transaction_id IN (
                'TXN_RECOVERY_001',
                'TXN_RECOVERY_002'
            )
            GROUP BY transaction_id
            """
        ).fetchall()

        assert sorted(transaction_rows) == [
            ("TXN_RECOVERY_001", 1),
            ("TXN_RECOVERY_002", 1)
        ]

        run_statuses = connection.execute(
            """
            SELECT status
            FROM pipeline_runs
            WHERE source_file = ?
            ORDER BY start_time
            """,
            (str(input_file),)
        ).fetchall()

        assert [row[0] for row in run_statuses] == [
            "failed",
            "completed"
        ]

    finally:
        connection.close()
