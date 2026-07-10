from __future__ import annotations

from datetime import datetime
from html import escape
from urllib.parse import urlparse

import streamlit as st

from utils.database import save_prediction
from utils.predictor import PredictionResult, predict_news
from utils.ui import (
    add_session_history,
    business_impact_panel,
    insight_cards,
    result_panel,
    section_title,
    source_evidence_panel,
)


def _normalize_url(url: str) -> str:
    cleaned = url.strip()
    if cleaned and "://" not in cleaned:
        cleaned = f"https://{cleaned}"
    return cleaned


def _domain(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(_normalize_url(url))
    return parsed.netloc or parsed.path


TRUSTED_NEWS_DOMAINS = {
    "apnews.com": "Associated Press",
    "reuters.com": "Reuters",
    "bbc.com": "BBC",
    "bbc.co.uk": "BBC",
    "cnn.com": "CNN",
    "nytimes.com": "The New York Times",
    "washingtonpost.com": "The Washington Post",
    "theguardian.com": "The Guardian",
    "aljazeera.com": "Al Jazeera",
    "npr.org": "NPR",
}


def _trusted_source_name(domain: str) -> str:
    normalized = domain.lower().removeprefix("www.")
    for trusted_domain, source_name in TRUSTED_NEWS_DOMAINS.items():
        if normalized == trusted_domain or normalized.endswith(f".{trusted_domain}"):
            return source_name
    return ""


def _link_only_result(domain: str) -> PredictionResult | None:
    source_name = _trusted_source_name(domain)
    if not source_name:
        return None
    return PredictionResult(
        prediction="Low Risk",
        fake_probability=12.0,
        real_probability=88.0,
        credibility_score=88.0,
        risk_level="Low Risk",
        recommended_action="Trusted source link found. Still read the article details before sharing.",
        explanation={
            "summary": f"This link is from {source_name}, a recognized news source. The link check rates the source as lower risk, but the article details should still be reviewed before sharing.",
            "suspicious_words": [],
            "short_article_warning": False,
            "excessive_punctuation_warning": False,
            "writing_pattern_warning": False,
            "verification_action": "Open the original article and compare key claims with trusted sources if the topic is sensitive.",
        },
    )


def _link_review_text(url: str) -> str:
    domain = _domain(url)
    return (
        f"Submitted source link: {_normalize_url(url)}. "
        f"Domain: {domain or 'not available'}. "
        "This review checks the source link signal only. Verify the page content with trusted official sources."
    )


def render() -> None:
    st.markdown(
        """
        <div class="link-page-shell">
            <div class="link-hero">
                <div>
                    <span>Source link review</span>
                    <h1>Review a source link before sharing.</h1>
                    <p>Paste a news article URL or social post link. The system checks the domain signal and source context.</p>
                </div>
                <div class="link-hero-badge">Link review ready</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.55, 0.9], gap="large")
    with left:
        st.markdown(
            """
            <div class="link-input-panel">
                <div class="link-input-icon">↗</div>
                <strong>Paste Link</strong>
                <p>Use the original article or source URL when possible.</p>
                <div class="link-input-meta">
                    <span>News URL</span>
                    <span>Social post</span>
                    <span>Source page</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        url = st.text_input(
            "News link",
            placeholder="https://example.com/news-story",
            label_visibility="collapsed",
        )

    with right:
        normalized_url = _normalize_url(url) if url else ""
        domain = _domain(url) if url else ""
        if not url:
            st.markdown(
                """
                <div class="link-status-card">
                    <div class="link-status-dot"></div>
                    <strong>Waiting for link</strong>
                    <p>Paste one URL to begin source review.</p>
                    <ul>
                        <li>Use the original source link when possible.</li>
                        <li>Avoid shortened links if you can.</li>
                        <li>Review one source at a time.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="link-status-card ready">
                    <div class="link-status-dot"></div>
                    <strong>Link ready for review</strong>
                    <p>The submitted source link is loaded in the workspace.</p>
                    <div class="link-file-grid">
                        <span>Domain</span><b>{escape(domain or "Not available")}</b>
                        <span>URL</span><b>{escape(normalized_url)}</b>
                        <span>Mode</span><b>Link-only check</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        review_clicked = st.button("Review Link", type="primary", use_container_width=True)
        if review_clicked:
            if not url:
                st.error("Please paste a news link before running review.")
                return
            link_text = _link_review_text(url)
            try:
                with st.spinner("Running link review..."):
                    result = _link_only_result(domain) or predict_news(f"Link review: {domain or normalized_url}", link_text)
            except RuntimeError as exc:
                st.error(str(exc))
                return

            st.session_state["last_result"] = result
            st.session_state["last_link_result"] = result
            st.session_state["last_link_text"] = link_text
            save_prediction(
                {
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "title": f"Link review: {domain or normalized_url}",
                    "source": domain,
                    "url": normalized_url,
                    "prediction": result.prediction,
                    "fake_probability": result.fake_probability,
                    "real_probability": result.real_probability,
                    "credibility_score": result.credibility_score,
                    "risk_level": result.risk_level,
                    "explanation_summary": result.explanation["summary"],
                }
            )
            add_session_history("Link", result, link_text, normalized_url)
            st.success("Link review complete.")

    st.markdown(
        """
        <div class="link-note-card">
            <div class="link-note-icon">↳</div>
            <div>
                <strong>Link-only workflow</strong>
                <p>This page reviews the source URL and domain signal. Use Article Check when you want to review the full article text.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    result = st.session_state.get("last_link_result")
    if result is not None and url:
        link_text = st.session_state.get("last_link_text", _link_review_text(url))
        title = f"Link review: {_domain(url) or _normalize_url(url)}"
        left, right = st.columns([2.1, 1], gap="large")
        with left:
            result_panel(result)
            section_title("💡", "Link Review Insights")
            insight_cards(result, source=_domain(url), url=_normalize_url(url))
        with right:
            business_impact_panel(result)
            source_evidence_panel(
                result,
                source=_domain(url),
                url=_normalize_url(url),
                text=link_text,
                author=_domain(url),
            )
