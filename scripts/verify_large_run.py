
import sqlite3

DATABASE_FILE = "database/smartdata.db"

RUN_ID = "c0662dae-1b7e-428b-8649-1695b93a01da"

connection = sqlite3.connect(DATABASE_FILE)

try:
    run = connection.execute(
        """
        SELECT input_count, output_count,
               rejected_count, duplicate_count
        FROM pipeline_runs
        WHERE run_id = ?
        """,
        (RUN_ID,)
    ).fetchone()

    print("Large Dataset Pipeline Verification")
    print("-----------------------------------")
    print("Run metrics:", run)

    inserted = connection.execute(
        "SELECT COUNT(*) FROM transactions WHERE run_id = ?",
        (RUN_ID,)
    ).fetchone()[0]

    rejected = connection.execute(
        "SELECT COUNT(*) FROM rejects WHERE run_id = ?",
        (RUN_ID,)
    ).fetchone()[0]

    print("Inserted rows in database:", inserted)
    print("Rejected rows in database:", rejected)

finally:
    connection.close()
