\# SmartData Pipeline — Project Explanation



\## 1. Project Overview



SmartData Pipeline is a Python-based batch data processing application designed to process large CSV transaction datasets without loading the entire dataset into memory.



The application reads records in configurable batches, validates incoming data, identifies duplicates, transforms valid records, stores results in SQLite, and monitors resource usage.



\*\*Main objective:\*\* Demonstrate efficient batch processing, data quality checks, reliable storage, and bounded memory usage.



\## 2. Problem Statement



Processing large datasets by loading the entire file into memory can increase memory consumption.



This project addresses that problem by:

\- Reading CSV files in smaller batches.

\- Validating records before storage.

\- Separating valid and rejected records.

\- Preventing duplicate transaction insertion.

\- Monitoring memory usage.

\- Maintaining processing and reconciliation information.



\## 3. Application Workflow



1\. The user uploads a CSV file through the Streamlit dashboard.

2\. The ingestion module reads the file in batches.

3\. The validation module checks required fields and data values.

4\. Customer IDs and existing transaction IDs are checked.

5\. Valid records are transformed.

6\. Processed records are stored in SQLite.

7\. Invalid records are stored with rejection information.

8\. Monitoring and reporting modules track execution results.

9\. The dashboard displays processing information.



The default batch size is 1,000 records.



\## 4. Technologies Used



| Technology | Purpose |

|---|---|

| Python | Backend implementation |

| Pandas | Structured data handling and CSV batch processing |

| SQLite | Relational database storage |

| Streamlit | Interactive web dashboard |

| psutil | Process memory monitoring |

| pytest | Automated testing |

| SQL | Database schema and queries |

| PowerShell | Windows setup and execution |

| Git and GitHub | Version control and source code hosting |



\## 5. Backend Components



| File | Responsibility |

|---|---|

| `main.py` | Backend entry point |

| `database.py` | Database connection and initialization |

| `ingestion.py` | CSV batch ingestion |

| `validation.py` | Data validation |

| `transformation.py` | Data transformation |

| `pipeline.py` | Coordinates pipeline processing |

| `monitoring.py` | Resource monitoring |

| `reporting.py` | Pipeline execution reporting |

| `schema.py` | Data schema-related definitions |

| `publishing.py` | Processing output publishing |



\## 6. Database Design



The application uses SQLite for persistent storage.



Main tables:



\- `customers`: Stores customer information.

\- `transactions`: Stores successfully processed transactions.

\- `rejects`: Stores rejected records and rejection information.

\- `pipeline\_runs`: Tracks pipeline execution details.



Database constraints help maintain data integrity.



\## 7. Batch Processing



The pipeline reads records in configurable batches rather than loading the complete CSV file into memory.



For a dataset containing 100,000 records and a batch size of 1,000, the pipeline processes approximately 100 batches.



This approach helps control memory consumption as the input dataset grows.



\## 8. Data Validation



The validation logic checks:

\- Required fields.

\- Customer identifiers.

\- Transaction amounts.

\- Currency values.

\- Timestamps.

\- Transaction status.



Invalid records are separated from valid records and stored with rejection information.



\## 9. Duplicate Detection and Idempotency



The pipeline checks transaction IDs before inserting records.



If a transaction ID already exists, the record is skipped instead of being inserted again.



This supports safe replay of the input file from the beginning after a partial failure.



The current implementation uses duplicate detection for replay; it does not implement checkpoint-based recovery.



\## 10. Dashboard



The frontend is built using Streamlit.



The dashboard provides:

\- Overview

\- Data Upload

\- Pipeline Execution

\- Database

\- Run History

\- Performance Monitoring

\- Download Results



The dashboard allows users to interact with the processing workflow and inspect results.



\## 11. Testing



The project uses pytest for automated testing.



The test modules cover:

\- Database operations.

\- CSV ingestion.

\- Data validation.

\- Data transformation.

\- Duplicate detection and replay.

\- Memory monitoring.

\- Pipeline reporting.



\*\*Latest test result:\*\* 44 passed, 0 failed.



All 44 tests passed in 2.73 seconds using the project's `.venv` environment.



\## 12. Performance Results



The project was tested using a CSV dataset containing 100,000 records.



\### Initial processing



| Metric | Result |

|---|---:|

| Input records | 100,000 |

| Processed records | 99,412 |

| Rejected records | 489 |

| Duplicate records | 99 |



Reconciliation:



`100,000 = 99,412 + 489 + 99`



\### Memory monitoring



| Metric | Recorded value |

|---|---:|

| Starting memory | 19.17 MB |

| Peak sampled memory | 23.49 MB |

| Ending memory | 23.49 MB |

| Memory increase | 4.32 MB |



These are recorded measurements from a particular execution. Results may vary depending on the machine and execution conditions.



\### Repeat-run verification



| Metric | Result |

|---|---:|

| Input records | 100,000 |

| Newly inserted records | 0 |

| Rejected records | 489 |

| Duplicate records | 99,511 |



This demonstrates that previously processed transaction IDs were not inserted again.



\## 13. Setup and Execution



\### Install and initialize



```powershell

powershell -ExecutionPolicy Bypass -File .\\setup.ps1

```



The setup script checks Python, creates the virtual environment, installs dependencies, initializes SQLite, and seeds sample customers.



\### Run the dashboard



```powershell

.\\.venv\\Scripts\\python.exe -m streamlit run frontend/dashboard.py

```



\### Run all tests



```powershell

.\\.venv\\Scripts\\python.exe -m pytest tests/ -v

```



\## 14. Current Scope and Limitations



| Feature | Status |

|---|---|

| CSV ingestion | Implemented |

| Batch processing | Implemented |

| Data validation | Implemented |

| Duplicate detection | Implemented |

| SQLite storage | Implemented |

| Memory monitoring | Implemented |

| Streamlit dashboard | Implemented |

| Automated tests | 44 passed |

| JSON/JSONL ingestion | Not implemented |

| Distributed processing | Not implemented |

| LLM integration | Not implemented |

| Checkpoint-based recovery | Not implemented |



\## 15. Conclusion



SmartData Pipeline demonstrates a local batch data engineering workflow using Python, Pandas, SQLite, and Streamlit.



It focuses on processing CSV data in batches, validating records, preventing duplicate insertions, tracking rejected records, monitoring memory usage, and verifying results through automated tests and data reconciliation.

