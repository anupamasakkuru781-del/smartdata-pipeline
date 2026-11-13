
-- Enable foreign key enforcement
PRAGMA foreign_keys = ON;

-- 1. Pipeline execution tracking
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    source_file TEXT NOT NULL,
    file_hash TEXT,
    status TEXT NOT NULL
        CHECK (status IN ('running', 'completed', 'failed')),
    start_time TEXT NOT NULL,
    end_time TEXT,
    input_count INTEGER DEFAULT 0,
    output_count INTEGER DEFAULT 0,
    rejected_count INTEGER DEFAULT 0,
    duplicate_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TEXT DEFAULT (
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    )
);

-- 2. Customer master data
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT,
    created_at TEXT DEFAULT (
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    )
);

-- 3. Successfully processed transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    currency TEXT NOT NULL
        CHECK (currency IN ('INR', 'USD', 'EUR')),
    transaction_ts TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('completed', 'pending', 'refunded')),
    amount_category TEXT NOT NULL
        CHECK (amount_category IN ('small', 'medium', 'large')),
    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    run_id TEXT NOT NULL,

    created_at TEXT DEFAULT (
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    ),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (run_id)
        REFERENCES pipeline_runs(run_id)
);

-- 4. Invalid or rejected records
CREATE TABLE IF NOT EXISTS rejects (
    reject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    raw_record TEXT,
    error_reason TEXT NOT NULL,
    rejected_at TEXT DEFAULT (
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    ),

    FOREIGN KEY (run_id)
        REFERENCES pipeline_runs(run_id)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_transactions_customer
ON transactions(customer_id);

CREATE INDEX IF NOT EXISTS idx_transactions_timestamp
ON transactions(transaction_ts);

CREATE INDEX IF NOT EXISTS idx_transactions_run
ON transactions(run_id);

CREATE INDEX IF NOT EXISTS idx_rejects_run
ON rejects(run_id);
