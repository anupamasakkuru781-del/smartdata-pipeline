
import csv
from pathlib import Path

from app.schema import REQUIRED_FIELDS


def read_csv_batches(file_path, batch_size=1000):
    """
    Read a CSV file in batches without loading
    the entire file into memory.

    Each batch contains:
        (row_number, record)
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    if batch_size < 1:
        raise ValueError("Batch size must be at least 1")

    with open(
        file_path,
        mode="r",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header")

        missing_fields = [
            field for field in REQUIRED_FIELDS
            if field not in reader.fieldnames
        ]

        if missing_fields:
            raise ValueError(
                f"Missing CSV columns: {missing_fields}"
            )

        unexpected_fields = [
            field for field in reader.fieldnames
            if field not in REQUIRED_FIELDS
        ]

        if unexpected_fields:
            raise ValueError(
                f"Unexpected CSV columns: {unexpected_fields}"
            )

        batch = []

        for record in reader:
            row_number = reader.line_num

            # Detect rows containing more values than the header.
            if None in record:
                raise ValueError(
                    f"Malformed CSV row at line {row_number}: "
                    "too many values"
                )

            batch.append((row_number, record))

            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch
