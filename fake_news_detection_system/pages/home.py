from html import escape

import streamlit as st

from utils.database import load_history
from utils.ui import (
    icon_svg,
    load_metrics,
    metric_value,
    model_status,
    business_status_label,
    section_title,
)


NAV_TARGETS = {
    "Text Analysis": "Article",
    "Image Analysis": "Image",
    "Link Analysis": "Link",
    "Batch Analysis": "Batch",
    "Performance": "Performance",
}


def _go_to(page: str) -> None:
    st.session_state["nav_page_request"] = NAV_TARGETS[page]
    st.rerun()


def _go_to_target(target: str) -> None:
    st.session_state["nav_page_request"] = target


def _history_count() -> int:
    try:
        return len(load_history())
    except Exception:
        return 0


def _kpi_value(key: str, fallback: int = 0) -> int:
    return int(st.session_state.get(key, fallback) or 0)


def _home_kpi(icon: str, title: str, value: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card friendly-kpi">
            <div class="kpi-icon">{icon_svg(icon)}</div>
            <div>
                <div class="kpi-label">{escape(title)}</div>
                <div class="kpi-value">{escape(value)}</div>
                <div class="kpi-caption">{escape(caption)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _section_header(icon: str, title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="friendly-section-header">
            <span>{icon_svg(icon)}</span>
            <div>
                <strong>{escape(title)}</strong>
                <p>{escape(caption)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _feature_card(icon: str, title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon_svg(icon)}</div>
            <strong>{escape(title)}</strong>
            <p>{escape(text)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _workflow_step(number: int, title: str, text: str, detail: str) -> None:
    step_color = {1: "#0B57D0", 2: "#007A55", 3: "#6D28D9"}.get(number, "#0B57D0")
    step_bg = {1: "#EAF1FF", 2: "#EAF8F2", 3: "#F1E8FF"}.get(number, "#EAF1FF")
    step_icon = {1: "file-text", 2: "scan-search", 3: "badge-check"}.get(number, "circle-check")
    st.markdown(
        f"""
        <div class="timeline-card" style="--step-color:{step_color};--step-bg:{step_bg};">
            <div class="timeline-step">
                <span>{number}</span>
                {icon_svg(step_icon)}
            </div>
            <strong>{escape(title)}</strong>
            <p>{escape(text)}</p>
            <div class="timeline-detail">{escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _action_card(
    icon: str,
    title: str,
    text: str,
    target: str,
    accent: str,
    soft: str,
) -> None:
    st.markdown(
        f"""
        <div class="review-channel-card action-card" style="--card-accent:{accent};--card-soft:{soft};">
            <div class="channel-top">
                <div class="action-icon">{icon_svg(icon)}</div>
                <span>Open review</span>
            </div>
            <div class="channel-title-link">
                {escape(title)}
                <span>{icon_svg("arrow-right")}</span>
            </div>
            <p>{escape(text)}</p>
            <div class="channel-open-button">
                Open {escape(title)}
                <span>{icon_svg("arrow-right")}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        f"Open {title}",
        key=f"review_channel_{target}",
        use_container_width=True,
        on_click=_go_to_target,
        args=(target,),
    )


def _card_button_gap() -> None:
    return None


def _recent_checks_table() -> None:
    rows = [
        ("10:30 AM", "Facebook Post", "Likely Fake", "fake", "82%", "#EF4444", "Needs Review"),
        ("10:10 AM", "News Link", "Likely Real", "real", "76%", "#10B981", "Reviewed"),
        ("09:45 AM", "Image Upload", "Needs Review", "review", "58%", "#8B5CF6", "Verify Source"),
    ]
    history = st.session_state.get("session_history", [])
    if history:
        rows = []
        for item in history[:5]:
            prediction = item.get("prediction", "Needs Review")
            lowered = prediction.lower()
            cls = "fake" if "fake" in lowered else "real" if "real" in lowered else "review"
            color = "#EF4444" if cls == "fake" else "#10B981" if cls == "real" else "#8B5CF6"
            confidence = item.get("confidence", "0%")
            rows.append(
                (
                    item.get("timestamp", "N/A")[-8:-3] or "N/A",
                    item.get("input_type", "Submitted Item"),
                    prediction,
                    cls,
                    confidence,
                    color,
                    "Needs Review" if cls != "real" else "Reviewed",
                )
            )

    table_rows = "".join(
        f"""
        <tr>
            <td>{escape(time)}</td>
            <td>{escape(source)}</td>
            <td><span class="result-pill {cls}">{escape(result)}</span></td>
            <td>{escape(confidence)} <span class="confidence-bar"><span style="width:{escape(confidence)};--bar-color:{color};"></span></span></td>
            <td>{escape(status)}</td>
        </tr>
        """
        for time, source, result, cls, confidence, color, status in rows
    )
    st.markdown(
        f"""
        <div class="home-section recent-section">
            <div class="recent-title-row">
                <strong>Recent Checks</strong>
                <span>Preview only</span>
            </div>
            <table class="recent-table">
                <thead>
                    <tr><th>Time</th><th>Source</th><th>Result</th><th>Confidence</th><th>Status</th></tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>
            <div class="system-note">ⓘ This system is a decision-support tool. Low-confidence results should be verified using trusted sources.</div>
        </div>
        <div class="floating-plus">+</div>
        """,
        unsafe_allow_html=True,
    )


def _model_info() -> None:
    ready = model_status() != "Not loaded"
    deployment = "Yes" if ready else "No"
    review_mode = business_status_label()
    st.markdown(
        f"""
        <div class="model-info-card">
            <strong><span class="heading-icon">{icon_svg("brain")}</span>Review System Details</strong>
            <div class="model-info-grid">
                <div><span>System Status</span><b>{escape(review_mode)}</b></div>
                <div><span>Screenshot Review</span><b>Available</b></div>
                <div><span>Review Result</span><b>Risk and trust signal</b></div>
                <div><span>Supporting Detail</span><b>Source and content summary</b></div>
                <div><span>Saved Records</span><b>Review history</b></div>
                <div><span>Ready for Use</span><b>{deployment}</b></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _recent_predictions() -> None:
    history = st.session_state.get("session_history", [])
    if not history:
        st.markdown(
            """
            <div class="data-card">
                <strong>No recent analyses yet</strong>
                <p>Start by analyzing text, image, link, or batch news. Recent predictions will appear here during this session.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for item in history[:5]:
        st.markdown(
            f"""
            <div class="recent-card">
                <strong>{escape(item.get("preview", "Not available"))}</strong>
                <div class="recent-meta">
                    <span class="mini-pill">{escape(item.get("input_type", "Unknown"))}</span>
                    <span class="mini-pill">{escape(item.get("prediction", "Not available"))}</span>
                    <span class="mini-pill">{escape(item.get("confidence", "N/A"))}</span>
                    <span class="mini-pill">{escape(item.get("timestamp", "N/A"))}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render() -> None:
    metrics = load_metrics()
    saved_count = _history_count()
    total_predictions = _kpi_value("total_predictions", saved_count)
    f1_score = metric_value(metrics, "f1", "Pending")
    status = business_status_label()

    st.markdown(
        f"""
        <div class="home-hero">
            <div>
                <div class="eyebrow">CREDIBILITY REVIEW CENTER</div>
                <h1>Review news before it reaches your audience</h1>
                <p>
                    Check articles, screenshots, social links, and CSV files in one guided workspace.
                    Each review gives a risk signal, source context, and a clear next step.
                </p>
                <div class="hero-mini-grid">
                    <span>{icon_svg("file-text")} Article</span>
                    <span>{icon_svg("image")} Screenshot</span>
                    <span>{icon_svg("link")} Link</span>
                    <span>{icon_svg("folder")} Bulk File</span>
                </div>
            </div>
            <div class="hero-status-card">
                <div class="hero-status-top">
                    <span>{icon_svg("shield-check")}</span>
                    <strong>Review System: {escape(status)}</strong>
                </div>
                <p>Start with one article, upload a screenshot text sample, check a link source, or review many rows from CSV.</p>
                <div class="hero-check-list">
                    <span>{icon_svg("circle-check")} Clear risk signal</span>
                    <span>{icon_svg("circle-check")} Source context</span>
                    <span>{icon_svg("circle-check")} Recommended next step</span>
                </div>
                <div class="status-badges">
                    <span>Guided Review</span>
                    <span>OCR Available</span>
                    <span>Batch Ready</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a1, a2, a3 = st.columns([1, 1, 2.15], gap="medium")
    if a1.button("Start Review", type="primary", use_container_width=True):
        _go_to("Text Analysis")
    if a2.button("View Insights", use_container_width=True):
        _go_to("Performance")
    st.markdown('<div class="home-actions-gap"></div>', unsafe_allow_html=True)

    _section_header("bar-chart", "Review Overview", "Live activity, readiness, and saved review history.")
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        _home_kpi("file-text", "Items Reviewed", str(total_predictions), f"{saved_count} saved records")
    with k2:
        _home_kpi("target", "Review Quality", f1_score, "Latest quality score")
    with k3:
        _home_kpi("link", "Links Checked", str(_kpi_value("link_analyses")), "Current session")
    with k4:
        _home_kpi("shield", "System Status", status, "Ready to check content")

    _section_header("layers", "Review Channels", "Choose how you want to check the content.")
    f1, f2, f3, f4 = st.columns(4, gap="medium")
    with f1:
        _action_card(
            "file-text",
            "Article Review",
            "Best for checking a written news story before publishing or sharing.",
            "Article",
            "#0B57D0",
            "#EAF1FF",
        )
    with f2:
        _action_card(
            "image",
            "Screenshot Review",
            "Use this for posts, image captions, and screenshots from social media.",
            "Image",
            "#007A55",
            "#EAF8F2",
        )
    with f3:
        _action_card(
            "link",
            "Link Review",
            "Check a source URL and review the credibility of its content.",
            "Link",
            "#6D28D9",
            "#F1E8FF",
        )
    with f4:
        _action_card(
            "folder",
            "Bulk Review",
            "Review many news items at once with a CSV upload.",
            "Batch",
            "#1B2941",
            "#EEF1F5",
        )

    st.markdown(
        """
        <div class="home-section">
            <div class="workflow-title-row">
                <div>
                    <strong>Review Workflow</strong>
                    <p>From submitted news content to a clear business review decision.</p>
                </div>
                <span>Content Check / Risk Score / Review Log</span>
            </div>
            <div class="workflow-status-strip">
                <span>Article, image, link, and CSV inputs</span>
                <span>Fake or real prediction with confidence</span>
                <span>Saved review history for follow-up</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    w1, w2, w3 = st.columns(3, gap="large")
    with w1:
        _workflow_step(
            1,
            "Submit Evidence",
            "Choose the review channel and add the news text, screenshot text, source link, or CSV file.",
            "Input is prepared for the local classifier.",
        )
    with w2:
        _workflow_step(
            2,
            "AI Credibility Check",
            "The system reviews the content and returns a fake-or-real signal with confidence and risk level.",
            "Designed as decision support, not automatic publishing.",
        )
    with w3:
        _workflow_step(
            3,
            "Business Decision",
            "Your team checks the result, follows the recommended next step, and keeps the review record.",
            "Use high-risk items for manual verification.",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    _recent_checks_table()
