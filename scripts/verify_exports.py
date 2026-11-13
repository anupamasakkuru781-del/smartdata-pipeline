
import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

RUN_ID = "c0662dae-1b7e-428b-8649-1695b93a01da"

FILES = {
    "Processed": (
        BASE_DIR / "data" / "output"
        / f"processed_{RUN_ID}.csv"
    ),
    "Rejected": (
        BASE_DIR / "data" / "quarantine"
        / f"rejected_{RUN_ID}.csv"
    )
}


def verify_csv(label, file_path):

    print(f"\n{label} CSV")
    print("-" * 40)

    if not file_path.exists():
        print("File not found!")
        return False

    with open(
        file_path,
        mode="r",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        reader = csv.reader(csv_file)

        header = next(reader, None)

        row_count = sum(1 for _ in reader)

    print("File:", file_path.name)
    print("File size:", round(file_path.stat().st_size / 1024, 2), "KB")
    print("Columns:", header)
    print("Data rows:", row_count)

    return True


def main():

    print("EXPORT FILE VERIFICATION")
    print("=" * 50)

    all_files_exist = True

    for label, file_path in FILES.items():

        result = verify_csv(label, file_path)

        if not result:
            all_files_exist = False

    if all_files_exist:
        print("\nBoth export files exist!")
    else:
        print("\nOne or more export files are missing.")


if __name__ == "__main__":
    main()
