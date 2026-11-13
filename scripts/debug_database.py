
from app.database import create_connection


def main():
    expected_run_id = "c0662dae-1b7e-428b-8649-1695b93a01da"

    connection = create_connection()

    try:
        print("Expected ID:", repr(expected_run_id))
        print("Expected ID length:", len(expected_run_id))

        print("\nStored transaction run IDs:")

        rows = connection.execute("""
            SELECT DISTINCT run_id
            FROM transactions
        """).fetchall()

        for row in rows:
            stored_id = row[0]

            print("\nStored ID:", repr(stored_id))
            print("Stored ID length:", len(stored_id))
            print("Exact Python match:", stored_id == expected_run_id)

            count = connection.execute(
                """
                SELECT COUNT(*)
                FROM transactions
                WHERE run_id = ?
                """,
                (stored_id,)
            ).fetchone()[0]

            print("Records using stored ID:", count)

        print("\nDirect comparison:")

        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM transactions
            WHERE run_id = ?
            """,
            (expected_run_id,)
        ).fetchone()[0]

        print("Expected ID query count:", result)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
