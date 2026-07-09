from __future__ import annotations

from html import escape
from io import StringIO

import pandas as pd
import streamlit as st

from utils.database import save_batch
from utils.predictor import predict_news
from utils.ui import add_session_history, section_title


REQUIRED_COLUMNS = {"title", "text"}
SAMPLE_CSV = (
    "title,text,source,date,url\n"
    "Example title,Example article text,Example source,2026-01-01,https://example.com\n"
)


def _file_size_label(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    return f"{size / 1024:.1f} KB"


def _load_csv(uploaded_file) -> tuple[pd.DataFrame | None, str]:
    try:
        return pd.read_csv(uploaded_file), ""
    except Exception as exc:
        return None, f"Could not read this CSV file: {exc}"


def _column_status(df: pd.DataFrame) -> tuple[set[str], dict[str, str]]:
    normalized_columns = {str(column).lower(): column for column in df.columns}
    missing = REQUIRED_COLUMNS - set(normalized_columns)
    return missing, normalized_columns


def render() -> None:
    st.markdown(
        """
        <div class="batch-page-shell">
            <div class="batch-hero">
                <span>CSV batch review</span>
                <h1>Upload one CSV file for bulk checking.</h1>
                <p>This page focuses only on file upload review. Use it when you need to check many news items at once.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.55, 0.9], gap="large")
    with left:
        st.markdown(
            """
            <div class="batch-upload-panel">
                <div class="batch-upload-icon">CSV</div>
                <strong>Upload File</strong>
                <p>CSV file only. Required columns: title and text.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=["csv"],
            label_visibility="collapsed",
        )

    df = None
    missing: set[str] = set()
    normalized_columns: dict[str, str] = {}
    load_error = ""
    if uploaded_file is not None:
        df, load_error = _load_csv(uploaded_file)
        if df is not None:
            missing, normalized_columns = _column_status(df)

    with right:
        if uploaded_file is None:
            st.markdown(
                """
                <div class="batch-status-card">
                    <div class="batch-status-dot"></div>
                    <strong>Waiting for CSV</strong>
                    <p>Upload one CSV file to begin batch review.</p>
                    <ul>
                        <li>Required columns: title, text.</li>
                        <li>Optional columns: source, url.</li>
                        <li>Each row is reviewed separately.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="batch-template-action">', unsafe_allow_html=True)
            st.download_button(
                "Download CSV Template",
                data=SAMPLE_CSV,
                file_name="sample_batch_template.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        elif load_error:
            st.error(load_error)
        else:
            status_text = "Ready for review" if not missing else "Missing required columns"
            status_class = "ready" if not missing else "warning"
            st.markdown(
                f"""
                <div class="batch-status-card {status_class}">
                    <div class="batch-status-dot"></div>
                    <strong>{escape(status_text)}</strong>
                    <p>Your uploaded CSV is loaded in the workspace.</p>
                    <div class="batch-file-grid">
                        <span>File name</span><b>{escape(uploaded_file.name)}</b>
                        <span>File size</span><b>{_file_size_label(uploaded_file.size)}</b>
                        <span>Rows</span><b>{len(df) if df is not None else 0}</b>
                        <span>Columns</span><b>{len(df.columns) if df is not None else 0}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if missing:
                st.error(f"Missing required columns: {', '.join(sorted(missing))}")

    st.markdown(
        """
        <div class="batch-note-card">
            <strong>Upload-file workflow</strong>
            <p>Upload a CSV, confirm the required columns, then run batch review. Link, image, and article checks stay on their own pages.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if uploaded_file is None or df is None or missing:
        return

    st.markdown(
        f"""
        <div class="batch-preview-card">
            <strong>File Preview</strong>
            <p>{len(df)} rows loaded from {escape(uploaded_file.name)}.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(df.head(8), use_container_width=True)

    if st.button("Review Uploaded CSV", type="primary", use_container_width=True):
        title_col = normalized_columns["title"]
        text_col = normalized_columns["text"]
        source_col = normalized_columns.get("source")
        url_col = normalized_columns.get("url")
        results = []
        history_records = []
        progress = st.progress(0, text="Reviewing rows")

        try:
            for index, row in df.iterrows():
                title = str(row.get(title_col, "") or "")
                text = str(row.get(text_col, "") or "")
                if not title.strip() or not text.strip():
                    result_row = {
                        "prediction": "Skipped",
                        "fake_probability": None,
                        "real_probability": None,
                        "credibility_score": None,
                        "risk_level": "Missing Text",
                        "explanation_summary": "Title or article content is missing.",
                    }
                else:
                    prediction = predict_news(title, text)
                    result_row = {
                        "prediction": prediction.prediction,
                        "fake_probability": prediction.fake_probability,
                        "real_probability": prediction.real_probability,
                        "credibility_score": prediction.credibility_score,
                        "risk_level": prediction.risk_level,
                        "explanation_summary": prediction.explanation["summary"],
                    }
                    history_records.append(
                        {
                            "title": title,
                            "source": row.get(source_col, "") if source_col else "",
                            "url": row.get(url_col, "") if url_col else "",
                            **result_row,
                        }
                    )
                    st.session_state["last_result"] = prediction
                    add_session_history(
                        "Batch",
                        prediction,
                        text,
                        str(row.get(url_col, "") if url_col else ""),
                    )
                results.append(result_row)
                progress.progress((index + 1) / len(df), text=f"Reviewed {index + 1} of {len(df)} rows")
        except RuntimeError as exc:
            st.error(str(exc))
            return

        output = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
        save_batch(history_records)
        st.success("Batch review complete.")
        section_title("📊", "Batch Review Results")
        st.dataframe(output, use_container_width=True)

        csv_buffer = StringIO()
        output.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download Results CSV",
            data=csv_buffer.getvalue(),
            file_name="fake_news_batch_results.csv",
            mime="text/csv",
            use_container_width=True,
        )
