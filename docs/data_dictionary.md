
# SmartData Pipeline - Data Dictionary

## 1. Overview

This document describes the database structure used by the SmartData Pipeline project.

The application uses SQLite to store pipeline execution details, customer information, successfully processed transactions, and rejected records.

The database contains four main tables:

1. `pipeline_runs`
2. `customers`
3. `transactions`
4. `rejects`

---

## 2. Database Relationships

### Entity Relationship Overview

- One pipeline run can process multiple transactions.
- One pipeline run can generate multiple rejected records.
- One customer can have multiple transactions.
- Each transaction belongs to one customer.
- Each transaction is associated with one pipeline run.

### Relationship Summary

| Parent Table | Child Table | Relationship |
|---|---|---|
| pipeline_runs | transactions | One-to-Many |
| pipeline_runs | rejects | One-to-Many |
| customers | transactions | One-to-Many |

---

## 3. Table: pipeline_runs

### Purpose

Stores information about each pipeline execution, including processing status, record counts, execution timestamps, and error details.

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| run_id | TEXT | Primary Key | Unique identifier for each pipeline execution |
| source_file | TEXT | NOT NULL | Name of the input file |
| file_hash | TEXT | Optional | Field reserved for source file hash information |
| status | TEXT | NOT NULL, CHECK | Execution status: running, completed, or failed |
| start_time | TEXT | NOT NULL | Pipeline start timestamp |
| end_time | TEXT | Optional | Pipeline completion timestamp |
| input_count | INTEGER | DEFAULT 0 | Number of input records |
| output_count | INTEGER | DEFAULT 0 | Number of successfully processed records |
| rejected_count | INTEGER | DEFAULT 0 | Number of rejected records |
| duplicate_count | INTEGER | DEFAULT 0 | Number of duplicate records skipped |
| error_message | TEXT | Optional | Error details if execution fails |
| created_at | TEXT | DEFAULT | Record creation timestamp in UTC |

---

## 4. Table: customers

### Purpose

Stores customer master data used to validate transaction references.

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| customer_id | TEXT | Primary Key | Unique customer identifier |
| customer_name | TEXT | NOT NULL | Customer name |
| email | TEXT | Optional | Customer email address |
| created_at | TEXT | DEFAULT | Customer record creation timestamp in UTC |

---

## 5. Table: transactions

### Purpose

Stores successfully validated and transformed transaction records.

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| transaction_id | TEXT | Primary Key | Unique transaction identifier |
| customer_id | TEXT | NOT NULL, Foreign Key | References customers.customer_id |
| amount | REAL | NOT NULL, CHECK amount > 0 | Transaction amount |
| currency | TEXT | NOT NULL, CHECK | Supported currencies: INR, USD, EUR |
| transaction_ts | TEXT | NOT NULL | Original transaction timestamp |
| status | TEXT | NOT NULL, CHECK | Transaction status: completed, pending, refunded |
| amount_category | TEXT | NOT NULL, CHECK | Derived category: small, medium, large |
| source_file | TEXT | NOT NULL | Original input filename |
| source_row_number | INTEGER | NOT NULL | Original CSV row number |
| run_id | TEXT | NOT NULL, Foreign Key | References pipeline_runs.run_id |
| created_at | TEXT | DEFAULT | Record insertion timestamp in UTC |

### Data Validation Rules

- Transaction ID must be unique.
- Customer ID must reference an existing customer.
- Transaction amount must be greater than zero.
- Currency must be INR, USD, or EUR.
- Transaction status must be completed, pending, or refunded.
- Amount category must be small, medium, or large.
- Source file and source row number are retained for traceability.

---

## 6. Table: rejects

### Purpose

Stores invalid records that cannot be processed successfully, along with their source information and rejection reasons.

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| reject_id | INTEGER | Primary Key, AUTOINCREMENT | Unique rejection record identifier |
| run_id | TEXT | NOT NULL, Foreign Key | References pipeline_runs.run_id |
| source_file | TEXT | NOT NULL | Original input filename |
| source_row_number | INTEGER | NOT NULL | Original CSV row number |
| raw_record | TEXT | Optional | Original rejected record content |
| error_reason | TEXT | NOT NULL | Reason for rejection |
| rejected_at | TEXT | DEFAULT | Rejection timestamp in UTC |

### Rejection Handling

Rejected records are stored separately from successfully processed transactions.

The source filename, row number, and error reason help identify and investigate invalid input records.

---

## 7. Indexes

The database defines the following indexes to improve query performance.

| Index Name | Table | Column | Purpose |
|---|---|---|---|
| idx_transactions_customer | transactions | customer_id | Faster customer-based transaction queries |
| idx_transactions_timestamp | transactions | transaction_ts | Faster timestamp-based queries |
| idx_transactions_run | transactions | run_id | Faster run-specific transaction queries |
| idx_rejects_run | rejects | run_id | Faster run-specific rejection queries |

---

## 8. Data Integrity

The database uses the following integrity mechanisms:

- Primary keys prevent duplicate identifiers.
- Foreign keys maintain relationships between customers, transactions, pipeline runs, and rejects.
- CHECK constraints restrict invalid values.
- NOT NULL constraints enforce required fields.
- Default timestamps record database insertion times.

Foreign-key enforcement is enabled through SQLite's `PRAGMA foreign_keys = ON` setting.

---

## 9. Record Reconciliation

For a successfully completed pipeline run, the expected reconciliation is:

Input Records = Output Records + Rejected Records + Duplicate Records

This provides a way to verify that all input records have been accounted for.

---

## 10. Timestamp Convention

Database-generated creation and rejection timestamps use UTC ISO-style timestamps.

The transaction_ts field stores the source transaction timestamp.

---

## 11. Database Technology

- Database: SQLite
- Schema definition: database/schema.sql
- Sample SQL queries: database/sample_queries.sql
- Database file: database/smartdata.db (local runtime file, excluded from Git)

The database schema can be recreated using the project's schema initialization process.
