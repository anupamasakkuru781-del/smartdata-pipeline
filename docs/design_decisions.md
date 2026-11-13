
# SmartData Pipeline - Design Decisions

## 1. Project Overview

SmartData Pipeline is a batch-oriented data engineering application designed to process transaction CSV files.

The system reads input records in configurable batches, validates data, transforms valid records, stores processed data in SQLite, and exports rejected records separately.

The application also provides pipeline monitoring and a Streamlit dashboard.

## 2. Technology Choices

| Technology | Purpose | Reason for Selection |
|---|---|---|
| Python | Backend processing | Readable, widely used for data engineering |
| CSV module | File ingestion | Supports row-by-row processing |
| SQLite | Data storage | Lightweight, portable relational database |
| Pandas | Data analysis and dashboard support | Convenient tabular data operations |
| Streamlit | Dashboard | Enables a simple interactive interface |
| psutil | Resource monitoring | Measures process memory usage |
| pytest | Automated testing | Supports repeatable validation of application behavior |

## 3. Architecture

The pipeline follows these processing stages:

1. Input file selection
2. Batch-based CSV ingestion
3. Data validation
4. Customer reference validation
5. Duplicate detection
6. Data transformation
7. Database insertion
8. Rejected-record handling
9. Output publishing
10. Monitoring and run reporting

The Streamlit dashboard provides access to upload, execution, database, run history, performance monitoring, and result downloads.

## 4. Batch Processing Strategy

### Decision

The pipeline uses configurable batch-based CSV reading.

### Reason

Loading a complete large file into memory can increase memory consumption.

Processing records in smaller batches helps limit the amount of input data held in memory at one time.

### Current Configuration

- Default batch size: 1,000 records
- Input format: CSV
- CSV reading: Python csv module
- Database: SQLite

The batch size can be changed when executing the pipeline.

## 5. Data Validation

Each input record is checked before it is inserted into the transactions table.

Validation includes:

- Required field checks
- Transaction amount validation
- Currency validation
- Transaction status validation
- Timestamp validation
- Customer reference validation

Invalid records are excluded from successful transaction insertion and recorded with rejection information.

## 6. Data Transformation

Valid records are enriched with processing metadata.

The transformation stage adds:

- Amount category
- Source filename
- Original source row number
- Pipeline run identifier

These fields support analysis and traceability.

## 7. Database Design

SQLite was selected for local relational storage.

The database contains four main tables:

- pipeline_runs
- customers
- transactions
- rejects

Primary keys and foreign keys maintain record identity and relationships.

CHECK constraints enforce supported transaction values and positive amounts.

Indexes are created on frequently queried transaction and rejection columns.

## 8. Duplicate Handling and Idempotency

Transaction IDs are stored as primary keys.

Before inserting a transaction, the pipeline checks whether its transaction ID already exists.

Existing transaction IDs are skipped and counted as duplicates.

This supports safe replay of an input file from the beginning without inserting the same transaction twice.

### Limitation

The current implementation uses duplicate detection for replay. It does not implement checkpoint-based restart or persistent batch offsets.

## 9. Failure Handling

The pipeline records execution status and error information.

When a processing error occurs:

- The current database transaction is rolled back.
- The pipeline run is marked as failed.
- Error information is recorded.
- Previously committed batches remain stored.
- The monitoring process is stopped.

A subsequent replay can skip already inserted transaction IDs and process records that were not committed.

### Limitation

Recovery is based on replay and duplicate detection, not automatic checkpoint recovery.

## 10. Rejected Record Management

Invalid records are stored separately in the rejects table.

The rejection information includes:

- Pipeline run ID
- Source filename
- Original row number
- Raw record, when available
- Error reason
- Rejection timestamp

This makes invalid records traceable and easier to investigate.

## 11. Monitoring and Performance

The application monitors process memory during pipeline execution using psutil.

The performance report records:

- Input record count
- Successfully inserted records
- Rejected records
- Duplicate records
- Execution time where measured
- Sampled memory usage

Resource measurements are environment-dependent and should be interpreted as observations from the recorded test run.

## 12. Testing Strategy

Automated tests are implemented using pytest.

The test suite covers:

- Database operations
- CSV ingestion
- Empty and malformed input
- Required field validation
- Invalid amounts and currencies
- Duplicate handling
- Transformation behavior
- Pipeline execution
- Monitoring behavior
- Failure handling
- Replay after partial failure
- Reporting behavior

The latest recorded full test run completed with 44 passing tests.

## 13. Reconciliation

For completed runs, the pipeline uses the following reconciliation rule:

Input Records = Output Records + Rejected Records + Duplicate Records

This helps verify that input records are accounted for.

## 14. Trade-offs and Limitations

### SQLite Instead of a Distributed Database

SQLite keeps the application simple to install and run locally.

It is suitable for this demonstration but is not intended to provide distributed processing or large-scale concurrent data ingestion.

### CSV Instead of Multiple Input Formats

CSV ingestion is implemented in the current version.

JSON and JSONL ingestion are not currently integrated.

### Local Batch Processing

The application processes data using local Python execution and SQLite.

Distributed frameworks such as Apache Spark are not implemented.

### Replay Instead of Checkpoint Recovery

The pipeline can replay a file from the beginning using transaction ID duplicate detection.

It does not currently store checkpoint offsets for resuming from an exact failed batch.

## 15. Future Improvements

Potential future enhancements include:

- JSON and JSONL ingestion
- Checkpoint-based recovery
- Distributed processing
- Configurable schema evolution
- Improved structured logging
- Production database integration
- Automated scheduled pipeline execution
- More extensive performance benchmarking

## 16. Summary

The implementation demonstrates batch-based CSV processing, validation, transformation, relational storage, duplicate handling, rejection tracking, monitoring, reconciliation, and automated testing.

The design prioritizes reproducibility, traceability, and understandable processing behavior.
