
from datetime import datetime, timezone
import uuid


def generate_run_id():
    """Generate a unique ID for every pipeline execution."""
    return str(uuid.uuid4())


def get_current_timestamp():
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def create_pipeline_run(connection, source_file):
    """Create a new pipeline run in the database."""

    run_id = generate_run_id()
    start_time = get_current_timestamp()

    query = """
        INSERT INTO pipeline_runs (
            run_id,
            source_file,
            status,
            start_time
        )
        VALUES (?, ?, ?, ?)
    """

    connection.execute(
        query,
        (
            run_id,
            str(source_file),
            "running",
            start_time
        )
    )

    connection.commit()

    return run_id


def update_pipeline_run(
    connection,
    run_id,
    status,
    input_count=0,
    output_count=0,
    rejected_count=0,
    duplicate_count=0,
    error_message=None
):
    """Update pipeline execution details."""

    end_time = get_current_timestamp()

    query = """
        UPDATE pipeline_runs
        SET
            status = ?,
            end_time = ?,
            input_count = ?,
            output_count = ?,
            rejected_count = ?,
            duplicate_count = ?,
            error_message = ?
        WHERE run_id = ?
    """

    connection.execute(
        query,
        (
            status,
            end_time,
            input_count,
            output_count,
            rejected_count,
            duplicate_count,
            error_message,
            run_id
        )
    )

    connection.commit()
