from datetime import datetime
from urllib.parse import urlparse

import streamlit as st

from utils.database import save_prediction
from utils.predictor import predict_news
from utils.ui import (
    add_session_history,
    business_impact_panel,
    insight_cards,
    load_metrics,
    metric_value,
    result_panel,
    section_title,
    source_evidence_panel,
)


def _title_from_url_or_text(url: str, text: str) -> str:
    if url:
        domain = urlparse(url if "://" in url else f"https://{url}").netloc
        return f"Content from {domain or 'submitted link'}"
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return first_line[:120] or "Submitted article"


def _save_result(title: str, text: str, source: str, url: str, result) -> None:
    save_prediction(
        {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "source": source,
            "url": url,
            "prediction": result.prediction,
            "fake_probability": result.fake_probability,
            "real_probability": result.real_probability,
            "credibility_score": result.credibility_score,
            "risk_level": result.risk_level,
            "explanation_summary": result.explanation["summary"],
        }
    )
    add_session_history("Text", result, text, url)


def render_result(title: str, text: str, source: str, url: str, result) -> None:
    left, right = st.columns([2.1, 1], gap="large")
    with left:
        result_panel(result)
        section_title("💡", "Actionable Business Insights")
        insight_cards(result, source=source, url=url)
    with right:
        business_impact_panel(result)
        source_evidence_panel(result, source=source, url=url, text=text)


def _article_metrics(last_result=None) -> None:
    metrics = load_metrics()
    accuracy = metric_value(metrics, "f1", "N/A")
    today = str(st.session_state.get("predictions_today", 0))
    risk = "Pending"
    if last_result is not None:
        risk = getattr(last_result, "risk_level", "Reviewed")
    st.markdown(
        f"""
        <div class="article-metrics-row">
            <div>
                <span>Accuracy</span>
                <strong>{accuracy}</strong>
                <p>Current engine score</p>
            </div>
            <div>
                <span>Today</span>
                <strong>{today}</strong>
                <p>Items analyzed</p>
            </div>
            <div>
                <span>Risk</span>
                <strong>{risk}</strong>
                <p>Analysis status</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render() -> None:
    st.markdown(
        """
        <div class="article-page-shell">
            <div class="article-hero">
                <span>Cambodian social media monitoring</span>
                <h1>Review information credibility instantly.</h1>
                <p>Paste the text of any social post or article to generate a detailed risk assessment and verify claims.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="article-review-card">', unsafe_allow_html=True)
    with st.form("strategic_text_form"):
        title = st.text_input(
            "Article Headline (Optional)",
            placeholder="Add a headline or short title",
            label_visibility="collapsed",
        )
        text = st.text_area(
            "Article text",
            placeholder="Paste the article or social media text you want to review",
            height=430,
            label_visibility="collapsed",
        )
        footer_left, footer_right = st.columns([1.35, 0.65])
        with footer_left:
            st.markdown(
                '<div class="article-classifier-status">Review text is private to this session</div>',
                unsafe_allow_html=True,
            )
        with footer_right:
            submitted = st.form_submit_button("Run Review  →", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    last_result = st.session_state.get("last_result")
    _article_metrics(last_result)

    if not submitted:
        return

    cleaned_text = text.strip()
    url = ""
    source = "Text-only article check"
    cleaned_title = title.strip() or _title_from_url_or_text(url, cleaned_text)
    if not cleaned_text:
        st.error("Please paste article text or extracted content before verification.")
        return

    try:
        with st.spinner("Running credibility review..."):
            result = predict_news(cleaned_title, cleaned_text)
    except RuntimeError as exc:
        st.error(str(exc))
        st.info("Train the transformer first with `python training/train_transformer.py`, then restart the app.")
        return

    st.session_state["last_result"] = result
    _save_result(cleaned_title, cleaned_text, source, url, result)
    render_result(cleaned_title, cleaned_text, source, url, result)
    st.success("Review saved to CSV history and session history.")
