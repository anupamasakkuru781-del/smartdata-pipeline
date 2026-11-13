
import sys
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from app.pipeline import run_pipeline


INPUT_DIR = BASE_DIR / "data" / "input"


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Pipeline Execution | SmartData",
    page_icon="⚙️",
    layout="wide"
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("📊 SmartData")
    st.caption("DATA ENGINEERING PLATFORM")

    st.divider()

    st.markdown("### Navigation")

    st.page_link(
        "pages/1_Data_Upload.py",
        label="Data Upload",
        icon="📁"
    )

    st.markdown("⚙️ **Pipeline Execution**")

    st.divider()

    st.caption("Version 1.0.0")


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("⚙️ Pipeline Execution")

st.write(
    "Execute the SmartData processing pipeline "
    "on your uploaded transaction files."
)

st.divider()


# --------------------------------------------------
# FIND AVAILABLE CSV FILES
# --------------------------------------------------

st.subheader("Select Input File")

INPUT_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(
    INPUT_DIR.glob("*.csv"),
    key=lambda file: file.stat().st_mtime,
    reverse=True
)

if not csv_files:

    st.warning(
        "No CSV files found in the input folder. "
        "Please upload a file from the Data Upload page first."
    )

    st.page_link(
        "pages/1_Data_Upload.py",
        label="Go to Data Upload →",
        icon="📁"
    )

    st.stop()


# Select the most recently uploaded file by default
saved_path = st.session_state.get("uploaded_file_path")

default_index = 0

if saved_path:
    for index, file in enumerate(csv_files):
        if str(file.resolve()) == str(Path(saved_path).resolve()):
            default_index = index
            break


selected_file = st.selectbox(
    "Choose a CSV file to process",
    options=csv_files,
    index=default_index,
    format_func=lambda file: file.name
)


# --------------------------------------------------
# FILE INFORMATION
# --------------------------------------------------

st.divider()

st.subheader("Input File Details")

col1, col2, col3 = st.columns(3)

col1.metric("File Name", selected_file.name)

col2.metric(
    "File Size",
    f"{selected_file.stat().st_size / 1024:.2f} KB"
)

col3.metric("File Format", "CSV")


# --------------------------------------------------
# PIPELINE SETTINGS
# --------------------------------------------------

st.divider()

st.subheader("Pipeline Configuration")

batch_size = st.selectbox(
    "Select Batch Size",
    options=[100, 500, 1000, 5000, 10000],
    index=2,
    help="Number of records processed in each batch."
)

st.caption(
    "A smaller batch size uses smaller processing batches. "
    "A larger batch size can reduce the number of batch operations."
)


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

st.divider()

st.subheader("Execute Pipeline")

st.write(
    "Click the button below to start ingestion, validation, "
    "transformation, duplicate detection and publishing."
)

if st.button(
    "▶ Run Data Pipeline",
    type="primary",
    use_container_width=True
):

    try:

        with st.spinner(
            "Pipeline is running. Please wait..."
        ):

            result = run_pipeline(
                str(selected_file),
                batch_size
            )

        st.session_state["last_pipeline_result"] = result

        st.success("Pipeline execution completed!")

    except Exception as error:

        st.error(
            f"Pipeline execution failed: {error}"
        )


# --------------------------------------------------
# DISPLAY EXECUTION RESULTS
# --------------------------------------------------

result = st.session_state.get("last_pipeline_result")

if result:

    st.divider()

    st.subheader("Execution Results")

    if isinstance(result, dict):

        run_id = result.get("run_id", "Not provided")

        st.markdown("**Pipeline Run ID**")

        st.code(str(run_id))

        # Display known record counts when available
        result_fields = [
            ("input_count", "Input Records"),
            ("output_count", "Processed Records"),
            ("rejected_count", "Rejected Records"),
            ("duplicate_count", "Duplicate Records")
        ]

        metric_columns = st.columns(4)

        for column, (key, label) in zip(
            metric_columns,
            result_fields
        ):

            value = result.get(key)

            if value is not None:
                column.metric(label, f"{value:,}")

        with st.expander("View complete pipeline result"):

            st.json(result)

    else:

        st.write(result)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SmartData Platform | Pipeline Execution Module"
)
