
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.database import create_connection


st.set_page_config(
    page_title="SmartData Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_dashboard_metrics():
    connection = create_connection()

    try:
        result = connection.execute("""
            SELECT
                COALESCE(SUM(input_count), 0),
                COALESCE(SUM(output_count), 0),
                COALESCE(SUM(rejected_count), 0),
                COALESCE(SUM(duplicate_count), 0)
            FROM pipeline_runs
            WHERE status = 'completed'
        """).fetchone()

        return result

    finally:
        connection.close()


with st.sidebar:
    st.title("📊 SmartData")
    st.caption("DATA ENGINEERING PLATFORM")

    st.divider()

    st.markdown("### Navigation")

    st.page_link("dashboard.py", label="Dashboard", icon="🏠")

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

    st.page_link(
        "pages/5_Performance_Monitoring.py",
        label="Performance Monitoring",
        icon="📈"
    )

    st.page_link(
        "pages/6_Download_Results.py",
        label="Download Results",
        icon="📥"
    )

    st.divider()

    st.markdown("### Platform")

    st.write(
        "Process, validate and monitor large-scale transaction data."
    )

    st.divider()

    st.caption("Version 1.0.0")
    st.caption("Python | SQLite | Streamlit")


st.title("SmartData Platform")

st.write(
    "Monitor, process and manage large-scale transaction data "
    "through a unified data engineering workspace."
)

st.divider()

st.subheader("Pipeline Overview")

st.caption(
    "Aggregated statistics from all completed pipeline runs."
)

try:
    metrics = get_dashboard_metrics()

    labels = [
        "Total Input Records",
        "Processed Records",
        "Rejected Records",
        "Duplicate Records"
    ]

    columns = st.columns(4)

    for column, label, value in zip(columns, labels, metrics):
        column.metric(label, f"{value:,}")

except Exception as error:
    st.error(f"Unable to load dashboard metrics: {error}")


st.divider()

st.subheader("Workspace")

st.write(
    "Select a workspace to manage your data pipeline."
)


features = [
    {
        "icon": "📁",
        "title": "Data Upload",
        "description": "Upload transaction CSV files and preview input data.",
        "page": "pages/1_Data_Upload.py"
    },
    {
        "icon": "⚙️",
        "title": "Pipeline Execution",
        "description": "Execute the pipeline and process transaction records.",
        "page": "pages/2_Pipeline_Execution.py"
    },
    {
        "icon": "🗄️",
        "title": "Database",
        "description": "Explore customers and processed transaction records.",
        "page": "pages/3_Database.py"
    },
    {
        "icon": "📋",
        "title": "Run History",
        "description": "Review previous pipeline executions and summaries.",
        "page": "pages/4_Run_History.py"
    },
    {
        "icon": "📈",
        "title": "Performance Monitoring",
        "description": "Monitor execution time and pipeline performance.",
        "page": "pages/5_Performance_Monitoring.py"
    },
    {
        "icon": "📥",
        "title": "Download Results",
        "description": "Preview and download processed and rejected CSV files.",
        "page": "pages/6_Download_Results.py"
    }
]


for start in range(0, len(features), 3):

    columns = st.columns(3)

    for column, feature in zip(columns, features[start:start + 3]):

        with column:

            with st.container(border=True):

                st.markdown(f"## {feature['icon']}")

                st.markdown(f"### {feature['title']}")

                st.write(feature["description"])

                st.page_link(
                    feature["page"],
                    label="Open Workspace →",
                    use_container_width=True
                )


st.divider()

st.caption(
    "SmartData Platform | Data Engineering | Python | SQLite | Streamlit"
)
