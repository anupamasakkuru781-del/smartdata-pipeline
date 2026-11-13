
# SmartData Pipeline - Performance Report

## Dataset

- Input file: `large_transactions.csv`
- Total input records: 100,000
- Input file size: approximately 6.28 MB
- Batch size: 1,000
- File format: CSV

## Initial Successful Processing

| Metric | Records |
|---|---:|
| Input records | 100,000 |
| Inserted records | 99,412 |
| Rejected records | 489 |
| Duplicate records | 99 |

### Reconciliation

100,000 = 99,412 + 489 + 99

All input records are accounted for in the processing results.

## Repeat Run - Idempotency Verification

| Metric | Records |
|---|---:|
| Input records | 100,000 |
| Inserted records | 0 |
| Rejected records | 489 |
| Duplicate records | 99,511 |

- Recorded execution time: 4.62 seconds
- No duplicate transactions were inserted during the repeat run.

## Memory Monitoring

| Metric | Recorded Value |
|---|---:|
| Starting memory | 19.17 MB |
| Ending memory | 23.49 MB |
| Peak sampled memory | 23.49 MB |
| Memory increase | 4.32 MB |
| Sampling interval | 0.1 seconds |

These values are from the recorded monitoring run and may vary across machines and executions.

## Automated Tests

- Total tests passed: 44
- Failed tests: 0
- Test framework: pytest

## Implementation Notes

- CSV records are read in configurable batches rather than loading the complete file into memory.
- Invalid records are stored in the rejection output with error information.
- Duplicate transaction IDs are skipped.
- SQLite constraints enforce primary-key and foreign-key relationships.
- The pipeline supports replay from the beginning using duplicate detection. It does not currently implement checkpoint-based recovery.

## Scope and Limitations

- CSV ingestion is implemented.
- JSON/JSONL ingestion is not currently integrated.
- Processing uses SQLite and local batch execution; distributed processing is not implemented.
- Performance measurements depend on the machine and dataset.
