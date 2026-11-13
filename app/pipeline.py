
import sqlite3
from pathlib import Path

from app.database import (
    create_connection,
    customer_exists,
    transaction_exists,
    insert_transaction,
    insert_reject
)

from app.ingestion import read_csv_batches
from app.validation import validate_record
from app.transformation import transform_record

from app.reporting import (
    create_pipeline_run,
    update_pipeline_run
)

from app.monitoring import PipelineMonitor
from app.publishing import publish_run_outputs


def run_pipeline(input_file, batch_size=1000):

    input_file = Path(input_file)

    connection = create_connection()

    run_id = None

    input_count = 0
    output_count = 0
    rejected_count = 0
    duplicate_count = 0

    monitor = PipelineMonitor()

    try:

        # Step 1: Start performance monitoring.
        monitor.start()

        # Step 2: Create a pipeline run.
        run_id = create_pipeline_run(
            connection,
            input_file
        )

        print(f"\nPipeline Run ID: {run_id}")
        print(f"Input file: {input_file}")

        # Step 3: Read records in batches.
        for batch in read_csv_batches(
            input_file,
            batch_size=batch_size
        ):

            for row_number, record in batch:

                input_count += 1

                # Step 4: Validate the record.
                cleaned_record, errors = validate_record(
                    record
                )

                if errors:

                    insert_reject(
                        connection,
                        run_id,
                        input_file,
                        row_number,
                        record,
                        "; ".join(errors)
                    )

                    rejected_count += 1
                    continue

                customer_id = cleaned_record["customer_id"]
                transaction_id = cleaned_record["transaction_id"]

                # Step 5: Check customer existence.
                if not customer_exists(
                    connection,
                    customer_id
                ):

                    insert_reject(
                        connection,
                        run_id,
                        input_file,
                        row_number,
                        record,
                        f"Customer does not exist: {customer_id}"
                    )

                    rejected_count += 1
                    continue

                # Step 6: Check duplicate transactions.
                if transaction_exists(
                    connection,
                    transaction_id
                ):

                    duplicate_count += 1
                    continue

                # Step 7: Transform the valid record.
                transformed_record = transform_record(
                    cleaned_record,
                    input_file.name,
                    row_number,
                    run_id
                )

                # Step 8: Insert into the database.
                try:

                    insert_transaction(
                        connection,
                        transformed_record
                    )

                    output_count += 1

                except sqlite3.IntegrityError as error:

                    insert_reject(
                        connection,
                        run_id,
                        input_file,
                        row_number,
                        record,
                        str(error)
                    )

                    rejected_count += 1

            # Commit each completed batch.
            connection.commit()

            print(
                f"Processed: {input_count:,} | "
                f"Inserted: {output_count:,} | "
                f"Rejected: {rejected_count:,} | "
                f"Duplicates: {duplicate_count:,}"
            )

        # Step 9: Publish processed and rejected records.
        publishing_results = publish_run_outputs(
            connection,
            run_id
        )

        # Step 10: Stop performance monitoring.
        metrics = monitor.stop()

        # Step 11: Update pipeline run status.
        update_pipeline_run(
            connection,
            run_id,
            status="completed",
            input_count=input_count,
            output_count=output_count,
            rejected_count=rejected_count,
            duplicate_count=duplicate_count
        )

        # Step 12: Create pipeline summary.
        summary = {
            "run_id": run_id,
            "status": "completed",
            "input_count": input_count,
            "output_count": output_count,
            "rejected_count": rejected_count,
            "duplicate_count": duplicate_count,
            "publishing": publishing_results,
            "metrics": metrics
        }

        print("\n========== PIPELINE SUMMARY ==========")

        print(f"Status: {summary['status']}")
        print(f"Input records: {input_count:,}")
        print(f"Inserted records: {output_count:,}")
        print(f"Rejected records: {rejected_count:,}")
        print(f"Duplicate records: {duplicate_count:,}")

        print("======================================")

        return summary

    except Exception as error:

        # Stop monitoring even when pipeline processing fails.
        try:
            monitor.stop()
        except Exception as monitor_error:
            print(
                f"Monitoring cleanup warning: {monitor_error}"
            )

        # Roll back the current uncommitted batch.
        connection.rollback()

        # Record the failed pipeline run.
        if run_id is not None:

            update_pipeline_run(
                connection,
                run_id,
                status="failed",
                input_count=input_count,
                output_count=output_count,
                rejected_count=rejected_count,
                duplicate_count=duplicate_count,
                error_message=str(error)
            )

        # Preserve the original pipeline error.
        raise

    finally:

        connection.close()
