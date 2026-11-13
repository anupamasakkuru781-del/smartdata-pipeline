
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


REPORT_FILE = BASE_DIR / "reports" / "performance_report.md"


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Performance Monitoring | SmartData",
    page_icon="📈",
    layout="wide"
)


# --------------------------------------------------
# DATABASE FUNCTIONS
# --------------------------------------------------

def get_performance_data():

    connection = create_connection()

    try:

        data = pd.read_sql_query("""
            SELECT
                run_id,
                source_file,
                status,
                start_time,
                end_time,
                input_count,
                output_count,
                rejected_count,
                duplicate_count
            FROM pipeline_runs
            ORDER BY start_time DESC
        """, connection)

        return data

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

    st.page_link(
        "pages/4_Run_History.py",
        label="Run History",
        icon="📋"
    )

    st.markdown("📈 **Performance Monitoring**")

    st.divider()

    st.caption("Version 1.0.0")


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📈 Performance Monitoring")

st.write(
    "Analyze pipeline execution time, processing throughput "
    "and available memory measurements."
)

st.divider()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:

    performance_data = get_performance_data()

except Exception as error:

    st.error(f"Unable to load performance data: {error}")
    st.stop()


if performance_data.empty:

    st.info("No pipeline execution records are available yet.")
    st.stop()


# --------------------------------------------------
# CALCULATE EXECUTION TIME
# --------------------------------------------------

performance_data["start_time"] = pd.to_datetime(
    performance_data["start_time"],
    errors="coerce",
    utc=True
)

performance_data["end_time"] = pd.to_datetime(
    performance_data["end_time"],
    errors="coerce",
    utc=True
)

performance_data["execution_seconds"] = (
    performance_data["end_time"] -
    performance_data["start_time"]
).dt.total_seconds()

completed_data = performance_data[
    (performance_data["status"] == "completed") &
    (performance_data["execution_seconds"].notna()) &
    (performance_data["execution_seconds"] >= 0)
].copy()


# --------------------------------------------------
# PERFORMANCE OVERVIEW
# --------------------------------------------------

st.subheader("Performance Overview")

total_runs = len(performance_data)

completed_runs = len(completed_data)

if completed_runs > 0:

    average_execution = completed_data[
        "execution_seconds"
    ].mean()

    latest_execution = completed_data.iloc[0][
        "execution_seconds"
    ]

else:

    average_execution = 0
    latest_execution = 0


columns = st.columns(4)

columns[0].metric(
    "Total Pipeline Runs",
    f"{total_runs:,}"
)

columns[1].metric(
    "Completed Runs",
    f"{completed_runs:,}"
)

columns[2].metric(
    "Average Execution Time",
    f"{average_execution:.2f} sec"
)

columns[3].metric(
    "Latest Execution Time",
    f"{latest_execution:.2f} sec"
)


st.divider()


# --------------------------------------------------
# PROCESSING THROUGHPUT
# --------------------------------------------------

st.subheader("Processing Throughput")

if completed_runs > 0:

    throughput_data = completed_data.copy()

    throughput_data["records_per_second"] = (
        throughput_data["input_count"] /
        throughput_data["execution_seconds"].replace(0, float("nan"))
    )

    latest_throughput = throughput_data.iloc[0][
        "records_per_second"
    ]

    average_throughput = throughput_data[
        "records_per_second"
    ].mean()

    throughput_columns = st.columns(2)

    throughput_columns[0].metric(
        "Latest Throughput",
        (
            f"{latest_throughput:,.2f} records/sec"
            if pd.notna(latest_throughput)
            else "Not available"
        )
    )

    throughput_columns[1].metric(
        "Average Throughput",
        (
            f"{average_throughput:,.2f} records/sec"
            if pd.notna(average_throughput)
            else "Not available"
        )
    )

    st.caption(
        "Throughput is calculated as input records divided by "
        "recorded execution time."
    )

else:

    st.info("Completed runs with valid timestamps are needed for throughput.")


st.divider()


# --------------------------------------------------
# EXECUTION TIME CHART
# --------------------------------------------------

st.subheader("Execution Time Analysis")

if completed_runs > 0:

    chart_data = completed_data[
        ["run_id", "execution_seconds", "input_count"]
    ].copy()

    chart_data["run_label"] = (
        chart_data["run_id"].astype(str).str[:8]
    )

    chart_data = chart_data.head(20).sort_values(
        "execution_seconds"
    )

    st.bar_chart(
        chart_data.set_index("run_label")[
            "execution_seconds"
        ],
        y_label="Execution Time (seconds)"
    )

    st.caption(
        "Showing up to the 20 most recent completed runs. "
        "Run labels show the first eight characters of each run ID."
    )

else:

    st.info("Execution time chart is unavailable.")


st.divider()


# --------------------------------------------------
# MEMORY PERFORMANCE REPORT
# --------------------------------------------------

st.subheader("Memory Monitoring")

if REPORT_FILE.exists():

    report_content = REPORT_FILE.read_text(
        encoding="utf-8"
    )

    if report_content.strip():

        st.markdown("### Performance Report")

        st.markdown(report_content)

    else:

        st.info("The performance report file is currently empty.")

else:

    st.warning(
        "No performance_report.md file was found in the reports folder."
    )

    st.caption(
        "Memory usage is not stored separately for every database run. "
        "The report will display your available memory measurements."
    )


st.divider()


# --------------------------------------------------
# EXECUTION DETAILS
# --------------------------------------------------

st.subheader("Execution Details")

if completed_runs > 0:

    display_data = completed_data[
        [
            "run_id",
            "source_file",
            "execution_seconds",
            "input_count",
            "output_count",
            "rejected_count",
            "duplicate_count"
        ]
    ].copy()

    display_data["execution_seconds"] = (
        display_data["execution_seconds"].round(2)
    )

    display_data.rename(
        columns={
            "run_id": "Run ID",
            "source_file": "Source File",
            "execution_seconds": "Execution Time (sec)",
            "input_count": "Input Records",
            "output_count": "Processed Records",
            "rejected_count": "Rejected Records",
            "duplicate_count": "Duplicate Records"
        },
        inplace=True
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Performance Data",
        data=display_data.to_csv(index=False).encode("utf-8"),
        file_name="performance_data.csv",
        mime="text/csv"
    )

else:

    st.info("No completed execution details are available.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SmartData Platform | Performance Monitoring | Python | SQLite"
)
