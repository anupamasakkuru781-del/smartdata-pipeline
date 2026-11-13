
import sqlite3
from pathlib import Path


# Find the main project directory
BASE_DIR = Path(__file__).resolve().parents[1]

# SQL schema file location
SCHEMA_FILE = BASE_DIR / "database" / "schema.sql"

# SQLite database file location
DATABASE_FILE = BASE_DIR / "database" / "smartdata.db"


def create_connection(db_path=DATABASE_FILE):
    """
    Create and return a SQLite database connection.
    """

    db_path = Path(db_path)

    # Create the parent folder if it does not exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        str(db_path),
        timeout=30
    )

    # Enable foreign key validation
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(db_path=DATABASE_FILE):
    """
    Create database tables using schema.sql.
    """

    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"SQL schema file not found: {SCHEMA_FILE}"
        )

    connection = create_connection(db_path)

    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as sql_file:
            schema = sql_file.read()

        connection.executescript(schema)
        connection.commit()

        print("Database initialized successfully!")
        print(f"Database location: {db_path}")

    finally:
        connection.close()

    
def customer_exists(connection, customer_id):
    query = """
        SELECT 1
        FROM customers
        WHERE customer_id = ?
        LIMIT 1
    """

    result = connection.execute(
        query, (customer_id,)
    ).fetchone()

    return result is not None


def transaction_exists(connection, transaction_id):
    query = """
        SELECT 1
        FROM transactions
        WHERE transaction_id = ?
        LIMIT 1
    """

    result = connection.execute(
        query, (transaction_id,)
    ).fetchone()

    return result is not None


def insert_transaction(connection, record):
    query = """
        INSERT INTO transactions (
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
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    connection.execute(
        query,
        (
            record["transaction_id"],
            record["customer_id"],
            record["amount"],
            record["currency"],
            record["transaction_ts"],
            record["status"],
            record["amount_category"],
            record["source_file"],
            record["source_row_number"],
            record["run_id"]
        )
    )


def insert_reject(
    connection,
    run_id,
    source_file,
    row_number,
    raw_record,
    error_reason
):
    import json

    query = """
        INSERT INTO rejects (
            run_id,
            source_file,
            source_row_number,
            raw_record,
            error_reason
        )
        VALUES (?, ?, ?, ?, ?)
    """

    connection.execute(
        query,
        (
            run_id,
            str(source_file),
            row_number,
            json.dumps(raw_record),
            error_reason
        )
    )



if __name__ == "__main__":
    initialize_database()

    connection = create_connection()

    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    print("\nTables created successfully:")

    for table in tables:
        print(table[0])

    connection.close()

