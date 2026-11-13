
# SmartData Pipeline
### Batch-Based Data Processing and Monitoring Platform

## 1. Project Overview

SmartData Pipeline is a Python-based data engineering application designed to process large transaction datasets efficiently.

It reads CSV files in configurable batches instead of loading the complete dataset into memory. Incoming records are validated, checked for duplicate transaction IDs and customer existence, transformed, and stored in an SQLite database.

Invalid records are stored separately with rejection reasons. The application also exports processed and rejected records as CSV files.

A Streamlit dashboard provides an interface for uploading data, executing pipelines, exploring database records, reviewing execution history, monitoring performance, and downloading results.

## 2. Business Problem

Processing large transaction datasets can introduce several challenges:

- High memory usage when loading entire files.
- Invalid or incomplete transaction records.
- Duplicate transaction processing.
- Missing customer references.
- Difficulty tracking pipeline executions.
- Limited visibility into processing performance.
- Difficulty identifying and investigating rejected records.

SmartData Pipeline addresses these challenges through batch-based ingestion, validation, duplicate detection, relational database storage, monitoring, and reporting.

## 3. Key Features

- Batch-based CSV ingestion.
- Configurable batch size.
- Required-field and data-type validation.
- Positive transaction amount validation.
- Currency and transaction status validation.
- Timestamp validation.
- Customer existence verification.
- Duplicate transaction detection.
- Transaction amount categorization.
- SQLite database integration.
- Rejected record storage with error reasons.
- Processed and rejected CSV exports.
- Pipeline execution history.
- Batch-level database commits.
- Memory and execution-time monitoring.
- Streamlit dashboard.
- Automated testing using Pytest.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and pipeline processing |
| SQLite | Relational database |
| SQL | Database schema and queries |
| Streamlit | Interactive dashboard |
| Pandas | Data presentation and analysis |
| Psutil | System resource monitoring |
| Pytest | Automated testing |
| CSV | Input and output data format |
| Git | Version control |

## 5. Project Architecture

```text
                Input CSV File
                       |
                       v
               Batch Ingestion
                       |
                       v
                Data Validation
                       |
              +--------+--------+
              |                 |
              v                 v
        Invalid Records    Valid Records
              |                 |
              v                 v
         Reject Storage    Customer Check
                                |
                                v
                         Duplicate Check
                                |
                                v
                          Transformation
                                |
                                v
                         SQLite Database
                                |
                                v
                         Result Publishing
                           /          \
                          v            v
                   Processed CSV   Rejected CSV

                 Streamlit Dashboard
                         |
             Monitoring and Run History
```

## 6. Project Structure

```text
smartdata_pipeline/
|
|-- app/
|   |-- database.py
|   |-- ingestion.py
|   |-- main.py
|   |-- monitoring.py
|   |-- pipeline.py
|   |-- publishing.py
|   |-- reporting.py
|   |-- schema.py
|   |-- transformation.py
|   |-- validation.py
|
|-- database/
|   |-- schema.sql
|   |-- sample_queries.sql
|
|-- data/
|   |-- input/
|   |-- output/
|   |-- quarantine/
|
|-- frontend/
|   |-- dashboard.py
|   |-- pages/
|
|-- scripts/
|   |-- create_sample.py
|   |-- generate_data.py
|   |-- seed_customers.py
|   |-- verify_large_run.py
|   |-- export_existing_run.py
|   |-- check_run_ids.py
|   |-- debug_database.py
|   |-- verify_exports.py
|
|-- tests/
|
|-- docs/
|   |-- data_dictionary.md
|   |-- design_decisions.md
|   |-- ai_usage_and_prompt_history.md
|
|-- reports/
|   |-- performance_report.md
|
|-- evidence/
|-- logs/
|
|-- requirements.txt
|-- README.md
|-- .gitignore
```

## 7. Installation

### Prerequisites

- Python 3.10 or higher.
- Git.
- Windows, Linux, or macOS.
- Visual Studio Code (recommended).

### Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd smartdata_pipeline
```

Replace the placeholder with the actual public GitHub repository URL.

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 8. Database Setup

Initialize the SQLite database and create the required tables:

```bash
python -m app.database
```

Insert the sample customer master records:

```bash
python -m scripts.seed_customers
```

The database schema is maintained in:

`database/schema.sql`

The database file is created locally at:

`database/smartdata.db`

The SQLite database file is excluded from Git using `.gitignore`. It is created when the application is initialized.

## 9. Generate Sample Data

Generate a small sample transaction file:

```bash
python -m scripts.create_sample
```

Generate a larger transaction dataset:

```bash
python -m scripts.generate_data
```

The generated input files are stored in:

`data/input/`

The project includes a sample CSV and a larger transaction dataset for testing batch processing.

## 10. Execute the Pipeline

Run the pipeline with the sample dataset:

```bash
python -m app.main --input data/input/sample_transactions.csv --batch-size 1000
```

Run the pipeline with the larger dataset:

```bash
python -m app.main --input data/input/large_transactions.csv --batch-size 1000
```

The batch size can be changed to evaluate different processing configurations.

For example:

```bash
python -m app.main --input data/input/large_transactions.csv --batch-size 500
```

## 11. Launch the Dashboard

Start the Streamlit dashboard:

```bash
python -m streamlit run frontend/dashboard.py
```

The dashboard provides the following sections:

1. Dashboard Overview - Overall pipeline statistics.
2. Data Upload - Upload and preview transaction CSV files.
3. Pipeline Execution - Execute data processing.
4. Database - Explore stored records.
5. Run History - Review pipeline execution history.
6. Performance Monitoring - Analyze execution performance.
7. Download Results - Download processed and rejected CSV files.

## 12. Data Validation

The pipeline validates incoming transaction records for:

- Required transaction fields.
- Positive transaction amounts.
- Supported currencies: INR, USD, and EUR.
- Supported statuses: completed, pending, and refunded.
- Valid transaction timestamps.
- Existing customer references.

Invalid records are rejected and stored with their source information and error reasons.

## 13. Duplicate Handling and Idempotency

The pipeline checks whether a transaction ID already exists before inserting a transaction.

Existing transaction IDs are skipped to prevent duplicate database entries.

The database also enforces transaction ID uniqueness through its primary key.

The pipeline supports replay from the beginning after a partial failure by detecting previously inserted transaction IDs. It does not currently implement checkpoint-based restart.

## 14. Database and SQL Queries

SQLite stores:

- Pipeline execution details.
- Customer master records.
- Successfully processed transactions.
- Rejected transaction records.

The SQL schema and example queries are available in:

- `database/schema.sql`
- `database/sample_queries.sql`

The sample SQL file contains queries for pipeline runs, record reconciliation, transaction summaries, customer activity, rejected records, failed runs, duplicate checks, and recent transactions.

## 15. Performance and Scalability

The application uses configurable batch-based CSV ingestion to avoid loading the entire input file into memory.

It also includes:

- Batch-level database commits.
- Memory usage monitoring.
- Execution time measurement.
- Processed, rejected, and duplicate record counts.
- Pipeline execution tracking.

### Recorded Performance Results

The performance report documents a run using a 100,000-record CSV dataset.

| Metric | Recorded Value |
|---|---:|
| Input records | 100,000 |
| Successfully processed | 99,412 |
| Rejected records | 489 |
| Duplicate records | 99 |
| Batch size | 1,000 |
| Input file size | Approximately 6.28 MB |
| Recorded repeat-run execution time | 4.62 seconds |
| Peak sampled memory | 23.49 MB |
| Memory increase | 4.32 MB |

Record reconciliation:

```text
100,000 = 99,412 + 489 + 99
```

These are recorded results from the documented execution, not guaranteed performance figures for every machine.

More details are available in:

`reports/performance_report.md`

## 16. Automated Testing

Run the complete test suite:

```bash
python -m pytest tests/ -v
```

Latest verified test result:

- Total tests: 44
- Passed: 44
- Failed: 0

The tests cover database operations, ingestion, validation, transformation, reporting, monitoring, pipeline execution, and idempotency.

## 17. Output Files

Processed records are exported to:

`data/output/`

Rejected records are exported to:

`data/quarantine/`

Pipeline execution details are maintained in the SQLite database.

Performance measurements are documented in:

`reports/performance_report.md`

## 18. Current Scope and Limitations

- CSV ingestion is implemented.
- JSON and JSONL ingestion are not currently integrated.
- Processing uses local Python batch execution.
- SQLite is used for relational storage.
- Distributed processing is not implemented.
- Checkpoint-based recovery is not implemented.
- Performance depends on the machine, dataset, and batch size.
- The Streamlit dashboard is intended for local demonstration.

## 19. Future Enhancements

- JSON and JSONL ingestion support.
- MySQL or PostgreSQL integration.
- Checkpoint-based pipeline recovery.
- Scheduled pipeline execution.
- Cloud storage integration.
- API-based pipeline execution.
- Advanced data quality reporting.
- Distributed processing for larger datasets.

## 20. Project Documentation

Additional project documentation:

- `docs/data_dictionary.md` - Database tables, columns, relationships, and constraints.
- `docs/design_decisions.md` - Architecture decisions and implementation trade-offs.
- `docs/ai_usage_and_prompt_history.md` - AI usage disclosure and prompt history.
- `reports/performance_report.md` - Recorded performance and reconciliation results.
- `database/sample_queries.sql` - Example SQL queries.

## 21. Author

Developed as a data engineering project demonstrating batch-based data processing, data validation, relational database integration, monitoring, reporting, and an interactive dashboard.
