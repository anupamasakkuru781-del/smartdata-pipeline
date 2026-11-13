
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = BASE_DIR / "data" / "output"
QUARANTINE_DIR = BASE_DIR / "data" / "quarantine"

BATCH_SIZE = 1000


def export_query_to_csv(connection, query, run_id, output_file):
    cursor = connection.execute(query, (run_id,))

    fieldnames = [column[0] for column in cursor.description]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    exported_count = 0

    with open(
        output_file,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        while True:
            rows = cursor.fetchmany(BATCH_SIZE)

            if not rows:
                break

            for row in rows:
                writer.writerow(dict(zip(fieldnames, row)))
                exported_count += 1

    return exported_count


def publish_run_outputs(connection, run_id):

    processed_file = (
        OUTPUT_DIR / f"processed_{run_id}.csv"
    )

    rejected_file = (
        QUARANTINE_DIR / f"rejected_{run_id}.csv"
    )

    processed_query = """
        SELECT
            transaction_id,
            customer_id,
            amount,
            currency,
            transaction_ts,
            status,
            amount_category,
            source_file,
            source_row_number,
            run_id
        FROM transactions
        WHERE run_id = ?
        ORDER BY source_row_number
    """

    rejected_query = """
        SELECT
            source_file,
            source_row_number,
            raw_record,
            error_reason,
            rejected_at
        FROM rejects
        WHERE run_id = ?
        ORDER BY source_row_number
    """

    processed_count = export_query_to_csv(
        connection,
        processed_query,
        run_id,
        processed_file
    )

    rejected_count = export_query_to_csv(
        connection,
        rejected_query,
        run_id,
        rejected_file
    )

    print("\nPublishing Results")
    print("------------------")
    print(f"Processed CSV: {processed_file}")
    print(f"Processed records exported: {processed_count}")
    print(f"Rejected CSV: {rejected_file}")
    print(f"Rejected records exported: {rejected_count}")

    return {
        "processed_file": str(processed_file),
        "rejected_file": str(rejected_file),
        "processed_count": processed_count,
        "rejected_count": rejected_count
    }
