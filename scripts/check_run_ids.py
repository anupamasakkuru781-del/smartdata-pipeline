
from app.database import create_connection


def main():
    connection = create_connection()

    try:
        print("\nPIPELINE RUNS")
        print("=" * 80)

        runs = connection.execute("""
            SELECT
                run_id,
                source_file,
                status,
                input_count,
                output_count,
                rejected_count,
                duplicate_count
            FROM pipeline_runs
            ORDER BY start_time
        """).fetchall()

        for run in runs:
            print("\nRun ID:", run[0])
            print("Source:", run[1])
            print("Status:", run[2])
            print("Input:", run[3])
            print("Inserted:", run[4])
            print("Rejected:", run[5])
            print("Duplicates:", run[6])

        print("\nACTUAL TRANSACTION COUNTS BY RUN ID")
        print("=" * 80)

        counts = connection.execute("""
            SELECT run_id, COUNT(*)
            FROM transactions
            GROUP BY run_id
        """).fetchall()

        for run_id, count in counts:
            print(f"{run_id}: {count} transactions")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
