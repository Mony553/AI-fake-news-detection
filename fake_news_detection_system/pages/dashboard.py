import pandas as pd
import streamlit as st

from utils.charts import (
    checked_over_time,
    credibility_histogram,
    flagged_phrase_bar,
    fake_probability_histogram,
    prediction_pie,
    risk_bar,
    suspicious_word_counts,
)
from utils.database import load_history
from utils.ui import DATASET_PATH, business_status_label, kpi_card, load_metrics, metric_values, page_header, section_title


def _format_metric(value) -> str:
    if isinstance(value, (int, float)):
        return f"{value * 100:.1f}%" if value <= 1 else f"{value:.1f}%"
    return "Awaiting report"


def _metric_lookup(metrics: dict, key: str):
    aliases = {
        "accuracy": ["accuracy", "eval_accuracy"],
        "precision": ["precision", "eval_precision", "weighted_precision"],
        "recall": ["recall", "eval_recall", "weighted_recall"],
        "f1": ["f1", "f1_score", "eval_f1", "weighted_f1"],
    }
    for candidate in aliases.get(key, [key]):
        if isinstance(metrics, dict) and candidate in metrics:
            return metrics[candidate]
    return None


def render() -> None:
    page_header("Insights")

    metrics = metric_values(load_metrics())
    system_status = business_status_label()
    reference_label = "Cloud demo"
    reference_caption = "Training data is kept local to keep deployment fast"
    if DATASET_PATH.exists():
        try:
            reference_label = f"{sum(1 for _ in DATASET_PATH.open()) - 1:,} rows"
            reference_caption = "Examples used to prepare the system"
        except OSError:
            reference_label = "Cloud demo"

    section_title("📈", "Review Quality Snapshot", "A plain-language view of how well the review system is performing.")
    cols = st.columns(4)
    labels = {
        "accuracy": ("Overall Quality", "How often reviews matched the test data"),
        "precision": ("Fake Alert Trust", "How reliable fake-news alerts are"),
        "recall": ("High Risk Found", "How well high-risk examples were caught"),
        "f1": ("Balanced Score", "Overall balance of alert quality and coverage"),
    }
    for col, key in zip(cols, ["accuracy", "precision", "recall", "f1"]):
        label, caption = labels[key]
        with col:
            kpi_card("bar-chart", label, _format_metric(_metric_lookup(metrics, key)), caption)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("brain", "System Status", system_status, "Ready to check content")
    with c2:
        kpi_card("database", "Reference Mode", reference_label, reference_caption)
    with c3:
        kpi_card("shield", "Review Outcomes", "Fake or Real", "Main result shown to users")

    df = load_history()

    if df.empty:
        st.markdown(
            """
            <div class="data-card">
                <strong>No saved review analytics yet</strong>
                <p>Review one article or upload a CSV batch to populate dashboard charts.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    numeric_cols = ["fake_probability", "real_probability", "credibility_score"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["prediction"] = df["prediction"].replace(
        {
            "Fake News": "High Risk",
            "Suspicious / Needs Review": "Needs Review",
            "Likely Real News": "Low Risk",
        }
    )
    df["risk_level"] = df["risk_level"].replace({"Medium Risk": "Needs Review"})

    total = len(df)
    high_count = int((df["prediction"] == "High Risk").sum())
    real_count = int((df["prediction"] == "Low Risk").sum())
    review_count = int((df["prediction"] == "Needs Review").sum())
    avg_credibility = df["credibility_score"].mean()
    high_risk_count = int((df["risk_level"] == "High Risk").sum())

    section_title("🧭", "Review Activity", "What the saved review history says about recent content risk.")
    cols = st.columns(5)
    with cols[0]:
        kpi_card("clipboard", "Total Reviewed", f"{total:,}", "Saved review records")
    with cols[1]:
        kpi_card("alert", "High Risk", f"{high_count:,}", "Do not share without verification")
    with cols[2]:
        kpi_card("badge-check", "Low Risk", f"{real_count:,}", "Items with stronger trust signals")
    with cols[3]:
        kpi_card("search", "Needs Review", f"{review_count:,}", "Items needing human review")
    with cols[4]:
        kpi_card("gauge", "High Concern", f"{high_risk_count:,}", f"Average trust score {avg_credibility:.1f}")

    overview_tab, trend_tab, signal_tab, queue_tab = st.tabs(
        ["Decision mix", "Score trends", "Risk signals", "High-risk queue"]
    )

    with overview_tab:
        left, right = st.columns(2)
        left.plotly_chart(prediction_pie(df), use_container_width=True)
        right.plotly_chart(risk_bar(df), use_container_width=True)

    with trend_tab:
        section_title("📅", "Review Volume", "How many articles were reviewed over time.")
        st.plotly_chart(checked_over_time(df), use_container_width=True)
        left, right = st.columns(2)
        left.plotly_chart(credibility_histogram(df), use_container_width=True)
        right.plotly_chart(fake_probability_histogram(df), use_container_width=True)

    words = suspicious_word_counts(df.get("explanation_summary", []))
    with signal_tab:
        if not words.empty:
            st.plotly_chart(flagged_phrase_bar(words), use_container_width=True)
        else:
            st.info("No suspicious words found in saved explanations.")

    with queue_tab:
        high_risk = df[df["risk_level"] == "High Risk"].sort_values("datetime", ascending=False).head(10)
        if high_risk.empty:
            st.success("No high-risk saved reviews are currently in the queue.")
        else:
            st.dataframe(
                high_risk[["datetime", "title", "source", "prediction", "fake_probability", "credibility_score"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "datetime": "Date",
                    "title": "Article",
                    "source": "Source",
                    "prediction": "Decision",
                    "fake_probability": st.column_config.NumberColumn("Risk estimate", format="%.2f%%"),
                    "credibility_score": st.column_config.NumberColumn("Credibility", format="%.2f"),
                },
            )
