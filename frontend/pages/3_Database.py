
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from app.database import create_connection


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Database | SmartData",
    page_icon="🗄️",
    layout="wide"
)


# --------------------------------------------------
# DATABASE HELPER
# --------------------------------------------------

def get_table_data(query, params=()):

    connection = create_connection()

    try:
        return pd.read_sql_query(
            query,
            connection,
            params=params
        )

    finally:
        connection.close()


def get_table_count(table_name):

    allowed_tables = {
        "customers",
        "transactions",
        "rejects",
        "pipeline_runs"
    }

    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")

    connection = create_connection()

    try:
        result = connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()

        return result[0]

    finally:
        connection.close()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("📊 SmartData")
    st.caption("DATA ENGINEERING PLATFORM")

    st.divider()

    st.markdown("### Navigation")

    st.page_link(
        "dashboard.py",
        label="Dashboard",
        icon="🏠"
    )

    st.page_link(
        "pages/1_Data_Upload.py",
        label="Data Upload",
        icon="📁"
    )

    st.page_link(
        "pages/2_Pipeline_Execution.py",
        label="Pipeline Execution",
        icon="⚙️"
    )

    st.markdown("🗄️ **Database**")

    st.divider()

    st.caption("Version 1.0.0")


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("🗄️ Database Explorer")

st.write(
    "Explore customers, processed transactions, "
    "rejected records and pipeline execution data."
)

st.caption("Database: database/smartdata.db")

st.divider()


# --------------------------------------------------
# DATABASE STATISTICS
# --------------------------------------------------

st.subheader("Database Overview")

try:

    customer_count = get_table_count("customers")
    transaction_count = get_table_count("transactions")
    reject_count = get_table_count("rejects")
    run_count = get_table_count("pipeline_runs")

    columns = st.columns(4)

    columns[0].metric(
        "Total Customers",
        f"{customer_count:,}"
    )

    columns[1].metric(
        "Transactions",
        f"{transaction_count:,}"
    )

    columns[2].metric(
        "Rejected Records",
        f"{reject_count:,}"
    )

    columns[3].metric(
        "Pipeline Runs",
        f"{run_count:,}"
    )

except Exception as error:

    st.error(f"Unable to load database statistics: {error}")
    st.stop()


st.divider()


# --------------------------------------------------
# TABLE EXPLORER
# --------------------------------------------------

st.subheader("Explore Database Tables")

customers_tab, transactions_tab, rejects_tab, runs_tab = st.tabs(
    [
        "👥 Customers",
        "💳 Transactions",
        "⚠️ Rejected Records",
        "📋 Pipeline Runs"
    ]
)


# --------------------------------------------------
# CUSTOMERS
# --------------------------------------------------

with customers_tab:

    st.markdown("### Customer Records")

    try:

        customer_data = get_table_data("""
            SELECT
                customer_id,
                customer_name,
                email,
                created_at
            FROM customers
            ORDER BY customer_id
            LIMIT 1000
        """)

        st.caption(
            f"Showing up to 1,000 of {customer_count:,} customer records."
        )

        st.dataframe(
            customer_data,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Customer Data",
            data=customer_data.to_csv(index=False).encode("utf-8"),
            file_name="customers.csv",
            mime="text/csv"
        )

    except Exception as error:

        st.error(f"Unable to load customers: {error}")


# --------------------------------------------------
# TRANSACTIONS
# --------------------------------------------------

with transactions_tab:

    st.markdown("### Processed Transactions")

    try:

        search_id = st.text_input(
            "Search by Transaction ID",
            key="transaction_search"
        )

        if search_id.strip():

            transaction_data = get_table_data("""
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
                WHERE transaction_id LIKE ?
                ORDER BY transaction_ts DESC
                LIMIT 1000
            """, (f"%{search_id.strip()}%",))

        else:

            transaction_data = get_table_data("""
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
                LIMIT 1000
            """)

        st.caption(
            f"Showing {len(transaction_data):,} transaction records "
            "(maximum 1,000 per view)."
        )

        st.dataframe(
            transaction_data,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Transaction Data",
            data=transaction_data.to_csv(index=False).encode("utf-8"),
            file_name="transactions.csv",
            mime="text/csv"
        )

    except Exception as error:

        st.error(f"Unable to load transactions: {error}")


# --------------------------------------------------
# REJECTED RECORDS
# --------------------------------------------------

with rejects_tab:

    st.markdown("### Rejected Records")

    try:

        rejected_data = get_table_data("""
            SELECT
                reject_id,
                run_id,
                source_file,
                source_row_number,
                error_reason,
                rejected_at
            FROM rejects
            ORDER BY reject_id DESC
            LIMIT 1000
        """)

        st.caption(
            f"Showing up to 1,000 of {reject_count:,} rejected records."
        )

        st.dataframe(
            rejected_data,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Rejected Records",
            data=rejected_data.to_csv(index=False).encode("utf-8"),
            file_name="rejected_records.csv",
            mime="text/csv"
        )

    except Exception as error:

        st.error(f"Unable to load rejected records: {error}")


# --------------------------------------------------
# PIPELINE RUNS
# --------------------------------------------------

with runs_tab:

    st.markdown("### Pipeline Execution History")

    try:

        runs_data = get_table_data("""
            SELECT
                run_id,
                source_file,
                status,
                start_time,
                end_time,
                input_count,
                output_count,
                rejected_count,
                duplicate_count,
                error_message
            FROM pipeline_runs
            ORDER BY start_time DESC
            LIMIT 1000
        """)

        st.caption(
            f"Showing up to 1,000 of {run_count:,} pipeline runs."
        )

        st.dataframe(
            runs_data,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Pipeline Runs",
            data=runs_data.to_csv(index=False).encode("utf-8"),
            file_name="pipeline_runs.csv",
            mime="text/csv"
        )

    except Exception as error:

        st.error(f"Unable to load pipeline runs: {error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SmartData Platform | Database Explorer | SQLite"
)
