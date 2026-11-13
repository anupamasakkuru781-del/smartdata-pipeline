
-- ============================================================
-- SmartData Pipeline - Sample SQL Queries
-- Database: SQLite
-- Purpose: Pipeline monitoring, reconciliation and analysis
-- ============================================================


-- 1. View all pipeline runs and their processing results.

SELECT
    run_id,
    source_file,
    status,
    input_count,
    output_count,
    rejected_count,
    duplicate_count,
    start_time,
    end_time
FROM pipeline_runs
ORDER BY start_time DESC;


-- 2. Reconcile completed pipeline runs.
-- Expected:
-- input_count = output_count + rejected_count + duplicate_count

SELECT
    run_id,
    input_count,
    output_count,
    rejected_count,
    duplicate_count,
    (
        output_count + rejected_count + duplicate_count
    ) AS accounted_records,
    CASE
        WHEN input_count =
             output_count + rejected_count + duplicate_count
        THEN 'RECONCILED'
        ELSE 'CHECK REQUIRED'
    END AS reconciliation_status
FROM pipeline_runs
WHERE status = 'completed';


-- 3. Count transactions by currency.

SELECT
    currency,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM transactions
GROUP BY currency
ORDER BY transaction_count DESC;


-- 4. View transaction counts by status.

SELECT
    status,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY status
ORDER BY transaction_count DESC;


-- 5. Find customers with the highest transaction volume.

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_amount
FROM customers AS c
JOIN transactions AS t
    ON c.customer_id = t.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
ORDER BY transaction_count DESC;


-- 6. View rejected records and their error reasons.

SELECT
    reject_id,
    run_id,
    source_file,
    source_row_number,
    error_reason,
    rejected_at
FROM rejects
ORDER BY rejected_at DESC;


-- 7. Summarize rejection reasons.

SELECT
    error_reason,
    COUNT(*) AS rejected_record_count
FROM rejects
GROUP BY error_reason
ORDER BY rejected_record_count DESC;


-- 8. Find failed pipeline runs.

SELECT
    run_id,
    source_file,
    error_message,
    start_time,
    end_time
FROM pipeline_runs
WHERE status = 'failed'
ORDER BY start_time DESC;


-- 9. Check whether any transaction IDs are duplicated.

SELECT
    transaction_id,
    COUNT(*) AS occurrences
FROM transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- 10. View the latest 10 transactions.

SELECT
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
FROM transactions
ORDER BY transaction_ts DESC
LIMIT 10;
