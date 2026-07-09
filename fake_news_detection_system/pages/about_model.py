import pandas as pd
import streamlit as st

from utils.ui import DATASET_PATH, MODEL_DIR, kpi_card, load_metrics, page_header, section_title
from utils.paths import project_path


REPORTS_DIR = project_path("reports")


def _load_metrics() -> dict:
    return load_metrics()


def render() -> None:
    page_header("Model transparency")

    model_name = "Local fine-tuned transformer"
    label_mapping_path = MODEL_DIR / "label_mapping.json"
    if label_mapping_path.exists():
        model_name = "Locally fine-tuned BERT/RoBERTa fake news classifier"

    section_title("🧠", "Model information")
    c1, c2, c3 = st.columns(3)
    c1.metric("Classifier", model_name)
    c2.metric("Labels", "REAL = 0, FAKE = 1")
    c3.metric("Storage", str(MODEL_DIR))

    metrics = _load_metrics()
    if metrics:
        section_title("📈", "Evaluation metrics")
        values = metrics.get("transformer_test") or metrics.get("baseline_test") or metrics.get("test") or metrics
        cols = st.columns(4)
        for col, key in zip(cols, ["accuracy", "precision", "recall", "f1"]):
            value = values.get(key)
            col.metric(key.title(), f"{value:.4f}" if isinstance(value, (int, float)) else "N/A")
    else:
        st.info("No metrics found yet. Run the training and evaluation scripts to generate reports.")

    report_path = REPORTS_DIR / "classification_report.txt"
    if report_path.exists():
        section_title("🧾", "Classification report")
        st.text(report_path.read_text())

    confusion_path = REPORTS_DIR / "confusion_matrix.png"
    if confusion_path.exists():
        section_title("🧮", "Confusion matrix")
        st.image(str(confusion_path))

    section_title("🗄️", "Dataset")
    st.markdown(
        """
        <div class="data-card">
            <strong>Training data format</strong>
            <p>
                Use WELFake Dataset or Kaggle Fake and Real News Dataset. The training scripts standardize data into
                title, text, combined_text, and numeric label columns.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("⚠️", "Limitations")
    st.warning(
        "This system does not prove whether news is 100% true or false. It provides an AI-based credibility prediction to support user verification. Users should still check trusted and official sources before sharing sensitive information."
    )
    st.markdown(
        """
        <div class="data-card">
            <strong>Known model risks</strong>
            <p>
                The model can be affected by dataset bias, outdated training data, short articles, satire, copied content,
                and topics not well represented in the training dataset.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dataset() -> None:
    page_header("Data Overview")
    section_title("🗄️", "Data Overview", "The local article examples used to support the review system.")

    if not DATASET_PATH.exists():
        st.warning("Processed dataset was not found.")
        return

    try:
        sample = pd.read_csv(DATASET_PATH, nrows=500)
        with DATASET_PATH.open() as dataset_file:
            row_count = sum(1 for _ in dataset_file) - 1
    except Exception as exc:
        st.error(f"Unable to load dataset preview: {exc}")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("database", "News Examples", f"{row_count:,}", "Saved examples for review learning")
    with c2:
        kpi_card("table", "Information Fields", str(len(sample.columns)), "Details available for each article")
    with c3:
        label_count = sample["label"].nunique() if "label" in sample.columns else "N/A"
        kpi_card("shield", "Result Types", str(label_count), "Fake and real examples")
    with c4:
        text_ready = "Ready" if {"title", "text"}.intersection(sample.columns) else "Check columns"
        kpi_card("file-text", "Article Text", text_ready, "Content available for review")

    st.markdown(
        """
        <div class="data-card">
            <strong>What this page is for</strong>
            <p>
                Use this view to confirm the training data shape, label balance, and sample rows before discussing
                model behavior or preparing presentation material.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview_tab, labels_tab, columns_tab, preview_tab = st.tabs(
        ["Overview", "Label balance", "Columns", "Preview"]
    )

    with overview_tab:
        st.markdown(
            f"""
            <div class="data-card">
                <strong>Dataset file</strong>
                <p>{DATASET_PATH}</p>
                <strong>Business meaning</strong>
                <p>
                    Each row is one article example. The model learns wording patterns from the article text and the
                    numeric label, then uses that learning to support future credibility reviews.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with labels_tab:
        if "label" in sample.columns:
            section_title("📊", "Class Sample Distribution", "A quick check of fake vs real labels in the preview sample.")
            label_counts = sample["label"].value_counts().rename_axis("label").reset_index(name="count")
            st.bar_chart(label_counts, x="label", y="count", use_container_width=True)
            st.dataframe(label_counts, hide_index=True, use_container_width=True)
        else:
            st.info("No label column was found in the preview sample.")

    with columns_tab:
        column_profile = pd.DataFrame(
            {
                "column": sample.columns,
                "type": [str(sample[column].dtype) for column in sample.columns],
                "missing_in_preview": [int(sample[column].isna().sum()) for column in sample.columns],
            }
        )
        st.dataframe(column_profile, hide_index=True, use_container_width=True)

    with preview_tab:
        section_title("🔎", "Dataset Preview", "First 50 rows from the processed dataset.")
        st.dataframe(sample.head(50), hide_index=True, use_container_width=True)
