
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
    page_title="Run History | SmartData",
    page_icon="📋",
    layout="wide"
)


# --------------------------------------------------
# DATABASE FUNCTIONS
# --------------------------------------------------

def get_run_history():

    connection = create_connection()

    try:
        return pd.read_sql_query("""
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
        """, connection)

    finally:
        connection.close()


def get_run_details(run_id):

    connection = create_connection()

    try:
        return pd.read_sql_query("""
            SELECT
                run_id,
                source_file,
                file_hash,
                status,
                start_time,
                end_time,
                input_count,
                output_count,
                rejected_count,
                duplicate_count,
                error_message,
                created_at
            FROM pipeline_runs
            WHERE run_id = ?
        """, connection, params=(run_id,))

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

    st.page_link(
        "pages/3_Database.py",
        label="Database",
        icon="🗄️"
    )

    st.markdown("📋 **Run History**")

    st.divider()

    st.caption("Version 1.0.0")


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📋 Pipeline Run History")

st.write(
    "Track previous executions and inspect the results "
    "of every recorded pipeline run."
)

st.divider()


# --------------------------------------------------
# LOAD RUN HISTORY
# --------------------------------------------------

try:

    history = get_run_history()

except Exception as error:

    st.error(f"Unable to load run history: {error}")
    st.stop()


if history.empty:

    st.info("No pipeline runs have been recorded yet.")
    st.stop()


# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

st.subheader("Execution Overview")

total_runs = len(history)

completed_runs = int(
    (history["status"] == "completed").sum()
)

failed_runs = int(
    (history["status"] == "failed").sum()
)

running_runs = int(
    (history["status"] == "running").sum()
)

columns = st.columns(4)

columns[0].metric("Total Runs", f"{total_runs:,}")
columns[1].metric("Completed", f"{completed_runs:,}")
columns[2].metric("Failed", f"{failed_runs:,}")
columns[3].metric("Running", f"{running_runs:,}")


st.divider()


# --------------------------------------------------
# RUN HISTORY TABLE
# --------------------------------------------------

st.subheader("All Pipeline Executions")

status_filter = st.selectbox(
    "Filter by status",
    ["All", "completed", "failed", "running"]
)

filtered_history = history.copy()

if status_filter != "All":
    filtered_history = filtered_history[
        filtered_history["status"] == status_filter
    ]


display_columns = [
    "run_id",
    "source_file",
    "status",
    "start_time",
    "input_count",
    "output_count",
    "rejected_count",
    "duplicate_count"
]

st.dataframe(
    filtered_history[display_columns],
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Showing {len(filtered_history):,} of {total_runs:,} pipeline runs."
)


st.download_button(
    "⬇️ Download Run History",
    data=filtered_history.to_csv(index=False).encode("utf-8"),
    file_name="pipeline_run_history.csv",
    mime="text/csv"
)


st.divider()


# --------------------------------------------------
# SELECT A RUN
# --------------------------------------------------

st.subheader("Run Details")

run_ids = filtered_history["run_id"].dropna().tolist()

if not run_ids:

    st.info("No runs are available for the selected status.")

else:

    selected_run = st.selectbox(
        "Select a pipeline run ID",
        options=run_ids
    )

    if selected_run:

        details = get_run_details(selected_run)

        if not details.empty:

            run = details.iloc[0]

            st.markdown("### Selected Execution")

            st.code(str(run["run_id"]))

            status = str(run["status"])

            if status == "completed":
                st.success("Pipeline completed successfully.")

            elif status == "failed":
                st.error("Pipeline execution failed.")

            else:
                st.warning("Pipeline is still running.")

            detail_columns = st.columns(4)

            detail_columns[0].metric(
                "Input Records",
                f"{int(run['input_count'] or 0):,}"
            )

            detail_columns[1].metric(
                "Processed",
                f"{int(run['output_count'] or 0):,}"
            )

            detail_columns[2].metric(
                "Rejected",
                f"{int(run['rejected_count'] or 0):,}"
            )

            detail_columns[3].metric(
                "Duplicates",
                f"{int(run['duplicate_count'] or 0):,}"
            )

            st.markdown("### Execution Information")

            st.write("**Source File:**", run["source_file"])
            st.write("**Start Time:**", run["start_time"])
            st.write("**End Time:**", run["end_time"])
            st.write("**File Hash:**", run["file_hash"])

            if pd.notna(run["error_message"]) and run["error_message"]:
                st.error(
                    f"Error details: {run['error_message']}"
                )

            else:
                st.info("No error message recorded for this run.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SmartData Platform | Run History | SQLite"
)
