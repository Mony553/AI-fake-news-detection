from __future__ import annotations

from datetime import datetime
from html import escape
import json
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

from utils.paths import PROJECT_ROOT, project_path


REPORTS_DIR = project_path("reports")
DATASET_PATH = project_path("data", "processed", "cleaned_fake_news.csv")
MODEL_DIR = project_path("models", "transformer_fake_news")
BASELINE_MODEL_PATH = project_path("models", "baseline", "logistic_regression_model.pkl")
QWEN_MODEL_DIR = PROJECT_ROOT.parent / "fake-news-detection" / "models" / "qwen_lora_fake_news"
QWEN_REPORTS_DIR = PROJECT_ROOT.parent / "fake-news-detection" / "reports"


DEFAULT_SETTINGS = {
    "confidence_threshold": 0.70,
    "max_extracted_text_length": 500,
    "enable_ai_explanation": True,
    "enable_history": True,
    "theme_mode": "Dark forensic",
}


ICON_PATHS = {
    "activity": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "archive": '<rect width="20" height="5" x="2" y="3" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
    "badge-check": '<path d="m9 12 2 2 4-4"/><path d="M7.5 4.2 12 2l4.5 2.2 4.5.7-.8 4.5L22 13.5l-3.5 3-1 4.5-4.5-1.6L8.5 21l-1-4.5-3.5-3 1.8-4.1L5 4.9l2.5-.7Z"/>',
    "bar-chart": '<line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/>',
    "brain": '<path d="M9.5 2A3.5 3.5 0 0 0 6 5.5v.2A3.5 3.5 0 0 0 4 12a3.5 3.5 0 0 0 2 6.3V19a3 3 0 0 0 6 0V5.5A3.5 3.5 0 0 0 9.5 2Z"/><path d="M14.5 2A3.5 3.5 0 0 1 18 5.5v.2A3.5 3.5 0 0 1 20 12a3.5 3.5 0 0 1-2 6.3V19a3 3 0 0 1-6 0V5.5A3.5 3.5 0 0 1 14.5 2Z"/>',
    "briefcase": '<path d="M10 6V5a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v1"/><rect width="20" height="14" x="2" y="6" rx="2"/><path d="M2 12h20"/><path d="M12 12v2"/>',
    "calendar": '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "circle-check": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "clipboard": '<rect width="16" height="18" x="4" y="3" rx="2"/><path d="M9 3h6v4H9z"/><path d="M8 12h8"/><path d="M8 16h5"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
    "file-text": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/><path d="M8 13h8"/><path d="M8 17h5"/>',
    "folder": '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7l-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2Z"/>',
    "gauge": '<path d="M12 14l4-4"/><path d="M3.3 19a10 10 0 1 1 17.4 0"/><path d="M7 19h10"/>',
    "home": '<path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
    "layers": '<path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1"/><path d="M14 11a5 5 0 0 0-7.1 0l-2 2a5 5 0 0 0 7.1 7.1l1.1-1.1"/>',
    "lightbulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.6A5 5 0 1 0 7.5 11.4C8.3 12.3 8.8 13 9 14"/><path d="M9 18h6"/><path d="M10 22h4"/><path d="M10 14h4v4h-4z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "scan-search": '<path d="M7 3H5a2 2 0 0 0-2 2v2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="11" cy="11" r="3"/><path d="m16 16-2.2-2.2"/>',
    "settings": '<path d="M12 15.5A3.5 3.5 0 1 0 12 8a3.5 3.5 0 0 0 0 7.5Z"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1A2 2 0 1 1 7.1 4l.1.1a1.7 1.7 0 0 0 1.9.3h.1a1.7 1.7 0 0 0 1-1.6V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.6h.1a1.7 1.7 0 0 0 1.9-.3l.1-.1A2 2 0 1 1 20 7.1l-.1.1a1.7 1.7 0 0 0-.3 1.9v.1a1.7 1.7 0 0 0 1.6 1h.1a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.6 1Z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "shield-check": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "table": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "timer": '<path d="M10 2h4"/><path d="M12 14l3-3"/><circle cx="12" cy="14" r="8"/>',
}

ICON_ALIASES = {
    "🎯": "target",
    "🧾": "clipboard",
    "🧭": "gauge",
    "🧠": "brain",
    "🧩": "layers",
    "📣": "alert",
    "✅": "check",
    "🔍": "search",
    "🔎": "search",
    "🌐": "link",
    "📈": "bar-chart",
    "📊": "bar-chart",
    "📅": "calendar",
    "📄": "file-text",
    "📰": "file-text",
    "📝": "file-text",
    "🧮": "table",
    "🗄️": "database",
    "🖼️": "image",
    "📂": "folder",
    "🟢": "shield",
    "⚠️": "alert",
    "💡": "lightbulb",
    "🧪": "activity",
    "🕒": "timer",
    "⚙️": "settings",
}


def icon_svg(name: str) -> str:
    icon_name = ICON_ALIASES.get(name, name)
    path = ICON_PATHS.get(icon_name, ICON_PATHS["shield"])
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f"{path}</svg>"
    )


def init_session_state() -> None:
    st.session_state.setdefault("session_history", [])
    st.session_state.setdefault("predictions_today", 0)
    st.session_state.setdefault("total_predictions", 0)
    st.session_state.setdefault("text_analyses", 0)
    st.session_state.setdefault("image_analyses", 0)
    st.session_state.setdefault("link_analyses", 0)
    st.session_state.setdefault("batch_analyses", 0)
    for key, value in DEFAULT_SETTINGS.items():
        st.session_state.setdefault(key, value)


def load_metrics() -> dict:
    paths = [
        QWEN_REPORTS_DIR / "qwen_metrics.json",
        REPORTS_DIR / "metrics.json",
        REPORTS_DIR / "baseline_metrics.json",
    ]
    for path in paths:
        if path.exists():
            try:
                return json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
    return {}


def metric_values(metrics: dict) -> dict:
    return (
        metrics.get("eval_metrics")
        or metrics.get("transformer_test")
        or metrics.get("baseline_test")
        or metrics.get("test")
        or metrics
    )


def metric_value(metrics: dict, key: str, fallback: str = "N/A") -> str:
    values = metric_values(metrics)
    aliases = {"f1": ["f1", "f1_score", "eval_f1", "weighted_f1"]}
    keys = aliases.get(key, [key])
    value = None
    if isinstance(values, dict):
        for candidate in keys:
            if candidate in values:
                value = values[candidate]
                break
    if isinstance(value, (int, float)):
        return f"{value * 100:.0f}%" if value <= 1 else f"{value:.0f}%"
    return fallback


def model_status() -> str:
    old_model_ready = (MODEL_DIR / "config.json").exists()
    baseline_ready = BASELINE_MODEL_PATH.exists()
    qwen_ready = (QWEN_MODEL_DIR / "adapter_config.json").exists() or (QWEN_MODEL_DIR / "adapter_model.safetensors").exists()
    if qwen_ready or old_model_ready or baseline_ready:
        return "Ready"
    return "Not loaded"


def business_status_label(status: str | None = None) -> str:
    current_status = status or model_status()
    if current_status == "Not loaded":
        return "Setup Needed"
    return "Ready"


def risk_score(fake_probability: float) -> float:
    return max(0.0, min(100.0, float(fake_probability)))


def approximate_risk_score(score: float) -> int:
    return int(max(5, min(95, round(float(score) / 5) * 5)))


def risk_band(score: float) -> str:
    if score < 45:
        return "Low Risk"
    if score < 75:
        return "Needs Review"
    return "High Risk"


def risk_label(score: float) -> str:
    return risk_band(score)


def risk_class(score: float) -> str:
    if score < 45:
        return "risk-low"
    if score < 75:
        return "risk-medium"
    return "risk-high"


def add_session_history(input_type: str, result, preview: str, url: str = "") -> None:
    if not st.session_state.get("enable_history", True):
        return
    st.session_state["predictions_today"] = st.session_state.get("predictions_today", 0) + 1
    st.session_state["total_predictions"] = st.session_state.get("total_predictions", 0) + 1
    counter_key = {
        "Text": "text_analyses",
        "Image": "image_analyses",
        "Link": "link_analyses",
        "Batch": "batch_analyses",
    }.get(input_type)
    if counter_key:
        st.session_state[counter_key] = st.session_state.get(counter_key, 0) + 1
    st.session_state["session_history"].insert(
        0,
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input_type": input_type,
            "prediction": result.prediction,
            "confidence": risk_band(result.fake_probability),
            "url": url or "Not available",
            "preview": preview[:140] if preview else "Not available",
        },
    )
    st.session_state["session_history"] = st.session_state["session_history"][:20]


def page_header(kicker: str = "AI forensic dashboard") -> None:
    st.markdown(
        f"""
        <div class="dashboard-header">
            <div>
                <div class="eyebrow">{escape(kicker)}</div>
                <h1>Credibility Review Center</h1>
                <p class="lead">
                    Check news content with clear risk scoring, evidence context, and next-step guidance for business review.
                </p>
            </div>
            <div class="header-status">
                <span class="status-dot"></span>
                Ready for Review
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(icon: str, title: str, caption: str = "") -> None:
    caption_html = f"<p>{escape(caption)}</p>" if caption else ""
    st.markdown(
        f"""
        <div class="section-heading">
            <span class="section-icon">{icon_svg(icon)}</span>
            <div><strong>{escape(title)}</strong>{caption_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, label: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon_svg(icon)}</div>
            <div>
                <div class="kpi-label">{escape(label)}</div>
                <div class="kpi-value">{escape(str(value))}</div>
                <div class="kpi-caption">{escape(caption)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(last_result=None) -> None:
    metrics = load_metrics()
    f1 = metric_value(metrics, "f1", "Pending")
    scanned = str(st.session_state.get("predictions_today", 0))
    avg_risk = "Pending"
    if last_result is not None:
        avg_risk = risk_label(risk_score(last_result.fake_probability))
    status = business_status_label()

    cols = st.columns(4)
    with cols[0]:
        kpi_card("🎯", "Review Quality", f1, "Latest quality score")
    with cols[1]:
        kpi_card("🧾", "Checked Today", scanned, "Items reviewed this session")
    with cols[2]:
        kpi_card("🧭", "Latest Result", avg_risk, "Most recent review outcome")
    with cols[3]:
        kpi_card("🧠", "System Status", status, "Ready to check content")


def result_panel(result) -> None:
    score = risk_score(result.fake_probability)
    display_score = approximate_risk_score(score)
    label = risk_label(score)
    status = "Low Risk to Share" if score < 45 else "Needs Human Review" if score < 75 else "High Risk - Do Not Share"
    badge_class = "badge-good" if score < 45 else "badge-danger"
    result_class = risk_class(score)
    meter_class = "risk-meter-low" if score < 45 else "risk-meter-warning" if score < 75 else "risk-meter-high"
    explanation = result.explanation.get("summary", "Not available")

    st.markdown(
        f"""
        <div class="analysis-result {result_class}">
            <div class="result-topline">
                <div>
                    <span class="status-badge {badge_class}">Review Complete</span>
                    <h2>{escape(status)}</h2>
                    <p>{escape(explanation)}</p>
                </div>
                <div class="risk-ring" style="--score:{display_score};">
                    <div>{display_score}<span>%</span></div>
                </div>
            </div>
            <div class="result-grid">
                <div><span>Decision</span><strong>{escape(result.prediction)}</strong></div>
                <div><span>Confidence Band</span><strong>{escape(label)}</strong></div>
                <div><span>Approx. Risk Score</span><strong>About {display_score}/100</strong></div>
                <div><span>Review Guidance</span><strong>{escape(result.recommended_action)}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="risk-meter {meter_class}" style="--score:{display_score}%;">
            <div class="risk-meter-header">
                <div>
                    <span>Confidence Band</span>
                    <strong>{escape(label)}</strong>
                </div>
                <b>About {display_score}/100</b>
            </div>
            <div class="risk-meter-track">
                <div class="risk-meter-fill"></div>
            </div>
            <div class="risk-meter-scale">
                <span>Lower risk</span>
                <span>Needs review</span>
                <span>High risk</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def business_impact_panel(result) -> None:
    is_fake = result.fake_probability >= 75
    items = (
        [
            ("Reputation Risk", "Elevated exposure if shared publicly"),
            ("Public Misinformation Risk", "Narrative may spread misleading claims"),
            ("Financial / Market Influence Risk", "Review before business decisions"),
            ("Fact-check Required", "Verify with official and trusted sources"),
        ]
        if is_fake
        else [
            ("Lower misinformation risk", "Model found stronger reliability signals"),
            ("Source appears more reliable", "Still confirm source and date"),
            ("Manual review recommended", "Use extra care for sensitive news"),
        ]
    )
    rows = "".join(f"<li><strong>{escape(title)}</strong><span>{escape(text)}</span></li>" for title, text in items)
    st.markdown(
        f"""
        <div class="side-card">
            <h3><span class="heading-icon">{icon_svg("bar-chart")}</span>Business Impact</h3>
            <ul class="impact-list">{rows}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_cards(result, source: str = "", url: str = "") -> None:
    suspicious = result.explanation.get("suspicious_words", [])
    keyword_text = ", ".join(suspicious) if suspicious else "No flagged phrases detected"
    cards = [
        ("alert", "Reputational Risk", risk_label(risk_score(result.fake_probability))),
        ("check", "Fact-Check Required", result.recommended_action),
        ("brain", "Review Summary", result.explanation.get("summary", "Not available")),
        ("search", "Flagged Phrases", keyword_text),
        ("link", "Source Review", source or domain_from_url(url) or "Not available"),
    ]
    columns = st.columns(2)
    for index, (icon, title, text) in enumerate(cards):
        with columns[index % 2]:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-icon">{icon_svg(icon)}</div>
                    <strong>{escape(title)}</strong>
                    <p>{escape(str(text))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def domain_from_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    return parsed.netloc or "Not available"


def _official_url_status(url: str) -> tuple[bool, str]:
    domain = domain_from_url(url)
    if not domain or domain == "Not available":
        return False, "No URL provided"
    trusted_news_domains = (
        "apnews.com",
        "reuters.com",
        "bbc.com",
        "bbc.co.uk",
        "npr.org",
        "aljazeera.com",
        "theguardian.com",
        "nytimes.com",
        "washingtonpost.com",
    )
    trusted_suffixes = (".gov", ".edu", ".org")
    official_terms = ("official", "news", "press", "ministry", "government", "gov")
    normalized = domain.lower()
    normalized = normalized.removeprefix("www.")
    if any(normalized == item or normalized.endswith(f".{item}") for item in trusted_news_domains):
        return True, "Trusted news source"
    if normalized.endswith(trusted_suffixes) or any(term in normalized for term in official_terms):
        return True, "Looks official"
    return False, "Review domain"


def source_trust_checklist(source: str = "", url: str = "", author: str = "", published: str = "") -> None:
    domain = domain_from_url(url)
    official_ok, official_text = _official_url_status(url)
    checks = [
        ("Source name found?", bool(source or (domain and domain != "Not available")), source or domain or "Not provided"),
        ("Date found?", bool(published), published or "Not provided"),
        ("Author found?", bool(author), author or "Not provided"),
        ("URL looks official?", official_ok, official_text),
    ]
    rows = "".join(
        f"""
        <li class="{'trust-ok' if passed else 'trust-warn'}">
            <span>{icon_svg('circle-check' if passed else 'alert')}</span>
            <div><strong>{escape(label)}</strong><p>{escape(detail)}</p></div>
        </li>
        """
        for label, passed, detail in checks
    )
    st.markdown(
        f"""
        <div class="side-card source-trust-card">
            <h3><span class="heading-icon">{icon_svg("shield-check")}</span>Source Trust Checklist</h3>
            <ul class="source-trust-list">{rows}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _article_length_quality(text: str) -> tuple[bool, str]:
    word_count = len((text or "").split())
    if word_count >= 120:
        return True, f"Strong context ({word_count} words)"
    if word_count >= 40:
        return True, f"Usable context ({word_count} words)"
    if word_count > 0:
        return False, f"Limited context ({word_count} words)"
    return False, "No article text provided"


def source_evidence_panel(
    result,
    source: str = "",
    url: str = "",
    text: str = "",
    author: str = "",
    published: str = "",
) -> None:
    domain = domain_from_url(url)
    official_ok, official_text = _official_url_status(url)
    suspicious = result.explanation.get("suspicious_words", []) if result is not None else []
    length_ok, length_text = _article_length_quality(text)
    risk_score_value = float(getattr(result, "fake_probability", 0.0))
    display_score = approximate_risk_score(risk_score_value)
    risk_ok = risk_score_value < 45
    source_name = source or (domain if domain and domain != "Not available" else "")
    checks = [
        ("Source domain", bool(domain and domain != "Not available"), domain or "Not provided"),
        ("Date found", bool(published), published or "Not provided"),
        ("Author found", bool(author), author or "Not provided"),
        ("Trusted source match", official_ok, official_text if source_name or url else "No trusted source match"),
        (
            "Suspicious wording found",
            not bool(suspicious),
            ", ".join(suspicious) if suspicious else "No flagged wording",
        ),
        ("Article length quality", length_ok, length_text),
        ("Model risk band", risk_ok, f"{risk_band(risk_score_value)} - about {display_score}/100"),
    ]
    rows = "".join(
        f"""
        <li class="{'trust-ok' if passed else 'trust-warn'}">
            <span>{icon_svg('circle-check' if passed else 'alert')}</span>
            <div><strong>{escape(label)}</strong><p>{escape(detail)}</p></div>
        </li>
        """
        for label, passed, detail in checks
    )
    st.markdown(
        f"""
        <div class="side-card source-evidence-card">
            <h3><span class="heading-icon">{icon_svg("shield-check")}</span>Source Evidence</h3>
            <ul class="source-trust-list">{rows}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
