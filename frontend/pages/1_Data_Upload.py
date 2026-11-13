
import csv
import io
import uuid
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "data" / "input"
INPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Data Upload | SmartData",
    page_icon="📁",
    layout="wide"
)


# --------------------------------------------------
# REQUIRED CSV COLUMNS
# --------------------------------------------------

REQUIRED_COLUMNS = [
    "transaction_id",
    "customer_id",
    "amount",
    "currency",
    "transaction_ts",
    "status"
]


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("📊 SmartData")
    st.caption("DATA ENGINEERING PLATFORM")
    st.divider()

    st.markdown("### Current Workspace")
    st.markdown("📁 **Data Upload**")
    st.caption("Upload and inspect transaction files.")


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📁 Data Upload")

st.write(
    "Upload transaction data files before sending them "
    "through the SmartData processing pipeline."
)

st.divider()


# --------------------------------------------------
# UPLOAD SECTION
# --------------------------------------------------

st.subheader("Upload Transaction File")

st.info(
    "Supported format: CSV (.csv). "
    "Make sure your file contains all six required columns."
)

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Select a transaction CSV file from your computer."
)


if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()

    st.divider()

    # File information
    st.subheader("File Information")

    col1, col2, col3 = st.columns(3)

    col1.metric("File Name", uploaded_file.name)
    col2.metric("File Size", f"{len(file_bytes) / 1024:.2f} KB")
    col3.metric("File Type", "CSV")

    # Read and inspect CSV
    try:
        decoded_content = file_bytes.decode("utf-8-sig")

        csv_reader = csv.DictReader(
            io.StringIO(decoded_content)
        )

        actual_columns = csv_reader.fieldnames or []

        preview_rows = []

        for row in csv_reader:
            if len(preview_rows) >= 5:
                break
            preview_rows.append(row)

        # Validate columns
        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in actual_columns
        ]

        st.divider()
        st.subheader("Data Preview")

        if preview_rows:
            st.dataframe(
                preview_rows,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("The uploaded CSV contains no data rows.")

        # Column validation
        st.divider()
        st.subheader("Column Validation")

        if missing_columns:

            st.error(
                "Your CSV is missing the following required columns: "
                + ", ".join(missing_columns)
            )

            st.caption("Required columns:")
            st.code(", ".join(REQUIRED_COLUMNS))

        else:

            st.success("All required columns are present.")

            st.write("Detected columns:")
            st.code(", ".join(actual_columns))

            # Save file
            if st.button(
                "⬆️ Upload File",
                type="primary",
                use_container_width=True
            ):

                safe_name = Path(uploaded_file.name).name

                unique_name = (
                    f"{uuid.uuid4().hex[:8]}_{safe_name}"
                )

                destination = INPUT_DIR / unique_name

                destination.write_bytes(file_bytes)

                st.session_state["uploaded_file_path"] = str(
                    destination
                )

                st.session_state["uploaded_file_name"] = unique_name

                st.success("File uploaded successfully!")

                st.write("Saved location:")
                st.code(str(destination))

                st.info(
                    "Your file is ready. You can run it through "
                    "the pipeline from the Pipeline Execution page "
                    "once we build that page."
                )

    except UnicodeDecodeError:

        st.error(
            "Unable to read this file as UTF-8 CSV. "
            "Please upload a valid UTF-8 encoded CSV file."
        )

    except Exception as error:

        st.error(f"Unable to inspect the uploaded file: {error}")


else:

    st.markdown("### Waiting for a file")

    st.caption(
        "Choose a CSV file above to preview and validate its contents."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption("SmartData Platform | Data Upload Module")
