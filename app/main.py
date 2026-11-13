
import argparse
from pathlib import Path

from app.database import initialize_database
from app.pipeline import run_pipeline


BASE_DIR = Path(__file__).resolve().parents[1]


def main():

    parser = argparse.ArgumentParser(
        description="SmartData Pipeline - Large Scale Data Processing"
    )

    parser.add_argument(
        "--input",
        type=str,
        default="data/input/sample_transactions.csv",
        help="Path to the input CSV file"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of records processed per batch"
    )

    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")

    input_file = Path(args.input)

    if not input_file.is_absolute():
        input_file = BASE_DIR / input_file

    print("\n======================================")
    print("       SMARTDATA PIPELINE")
    print("======================================")

    print("\nInitializing database...")

    initialize_database()

    print("\nStarting data processing...")

    summary = run_pipeline(
        input_file=input_file,
        batch_size=args.batch_size
    )

    print("\nPipeline execution finished successfully.")

    return summary


if __name__ == "__main__":
    main()
