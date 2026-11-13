
from app.database import create_connection
from app.publishing import publish_run_outputs


def main():
    run_id = "c0662dae-1b7e-428b-8649-1695b93a01da"

    connection = create_connection()

    try:
        print("Exporting existing pipeline results...")
        
        results = publish_run_outputs(
            connection,
            run_id
        )

        print("\nEXPORT VERIFICATION")
        print("=" * 40)
        print("Processed records:", results["processed_count"])
        print("Rejected records:", results["rejected_count"])

        if results["processed_count"] != 99412:
            raise RuntimeError("Processed export count is incorrect.")

        if results["rejected_count"] != 489:
            raise RuntimeError("Rejected export count is incorrect.")

        print("\nAll export checks passed!")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
