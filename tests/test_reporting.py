
from app.database import create_connection, initialize_database
from app.reporting import (
    generate_run_id,
    create_pipeline_run,
    update_pipeline_run
)


def test_generate_run_id():
    run_id_1 = generate_run_id()
    run_id_2 = generate_run_id()

    assert run_id_1 != run_id_2
    assert len(run_id_1) == 36


def test_create_pipeline_run(tmp_path):
    db_path = tmp_path / "reporting.db"

    initialize_database(db_path)
    connection = create_connection(db_path)

    try:
        run_id = create_pipeline_run(
            connection,
            "sample_transactions.csv"
        )

        result = connection.execute(
            """
            SELECT run_id, source_file, status
            FROM pipeline_runs
            WHERE run_id = ?
            """,
            (run_id,)
        ).fetchone()

        assert result is not None
        assert result[0] == run_id
        assert result[1] == "sample_transactions.csv"
        assert result[2] == "running"

    finally:
        connection.close()


def test_update_pipeline_run(tmp_path):
    db_path = tmp_path / "reporting.db"

    initialize_database(db_path)
    connection = create_connection(db_path)

    try:
        run_id = create_pipeline_run(
            connection,
            "large_transactions.csv"
        )

        update_pipeline_run(
            connection,
            run_id,
            status="completed",
            input_count=100000,
            output_count=98000,
            rejected_count=1500,
            duplicate_count=500
        )

        result = connection.execute(
            """
            SELECT status, input_count, output_count,
                   rejected_count, duplicate_count, end_time
            FROM pipeline_runs
            WHERE run_id = ?
            """,
            (run_id,)
        ).fetchone()

        assert result[0] == "completed"
        assert result[1] == 100000
        assert result[2] == 98000
        assert result[3] == 1500
        assert result[4] == 500
        assert result[5] is not None

    finally:
        connection.close()
