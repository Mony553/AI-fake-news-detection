import streamlit as st

from utils.ui import DEFAULT_SETTINGS, kpi_card, page_header, section_title


def render() -> None:
    page_header("Workspace Settings")
    st.markdown('<div class="settings-page-marker"></div>', unsafe_allow_html=True)
    section_title("⚙️", "Workspace Settings", "Control how the review workspace behaves for your team.")

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card(
            "gauge",
            "Review Strictness",
            f"{float(st.session_state.get('confidence_threshold', DEFAULT_SETTINGS['confidence_threshold'])):.0%}",
            "How careful the system should be",
        )
    with c2:
        kpi_card(
            "file-text",
            "Article Preview",
            f"{int(st.session_state.get('max_extracted_text_length', DEFAULT_SETTINGS['max_extracted_text_length'])):,}",
            "Amount of article text shown",
        )
    with c3:
        history_status = "On" if st.session_state.get("enable_history", True) else "Off"
        kpi_card("archive", "Recent Reviews", history_status, "Keeps a short review list")

    review_tab, content_tab, display_tab = st.tabs(["Review preferences", "Review records", "Workspace display"])

    with review_tab:
        section_title("🧭", "Review Preferences", "Set how cautious the workspace should be and how much article text users see.")
        st.markdown(
            """
            <div class="settings-control-card">
                <strong>Recommended for business review</strong>
                <p>
                    Keep review strictness near 70% for a balanced workflow. Increase it when sensitive content needs
                    more caution before sharing.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state["confidence_threshold"] = st.slider(
            "Review strictness",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state.get("confidence_threshold", DEFAULT_SETTINGS["confidence_threshold"])),
            step=0.05,
            help="Higher values make the workspace more cautious before showing a strong result.",
        )
        st.session_state["max_extracted_text_length"] = st.slider(
            "Article preview length",
            min_value=200,
            max_value=2000,
            value=int(st.session_state.get("max_extracted_text_length", DEFAULT_SETTINGS["max_extracted_text_length"])),
            step=100,
            help="Controls how much article text is shown in review previews.",
        )
        st.markdown(
            """
            <div class="settings-hint-grid">
                <div><strong>Lower strictness</strong><span>Faster review flow for low-risk work.</span></div>
                <div><strong>Higher strictness</strong><span>More careful review for sensitive content.</span></div>
                <div><strong>Longer preview</strong><span>Shows more article context for human checking.</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with content_tab:
        section_title("🧾", "Review Records", "Choose what supporting context the app keeps and displays.")
        st.session_state["enable_ai_explanation"] = st.toggle(
            "Enable AI explanation",
            value=bool(st.session_state.get("enable_ai_explanation", True)),
            help="Shows the plain-language reason behind a review result.",
        )
        st.session_state["enable_history"] = st.toggle(
            "Enable session history",
            value=bool(st.session_state.get("enable_history", True)),
            help="Stores recent reviews in the current browser session.",
        )
        st.markdown(
            """
            <div class="data-card">
                <strong>Saved CSV history is managed separately</strong>
                <p>
                    This switch controls the short session list. The saved audit log can still be downloaded or cleared
                    from the Review Records page.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with display_tab:
        section_title("🖼️", "Dashboard Display", "Pick the workspace density that feels easiest to use.")
        st.session_state["theme_mode"] = st.selectbox(
            "Theme mode",
            ["Dark forensic", "Dark compact"],
            index=0 if st.session_state.get("theme_mode", "Dark forensic") == "Dark forensic" else 1,
            help="This keeps the same app theme family while changing density preference.",
        )
        st.markdown(
            """
            <div class="data-card">
                <strong>Recommended setup</strong>
                <p>
                    Keep explanations and history enabled for presentations, demos, and business review workflows.
                    Use a higher confidence threshold when decisions must be reviewed carefully.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="settings-reset-area">', unsafe_allow_html=True)
    if st.button("Restore recommended settings"):
        for key, value in DEFAULT_SETTINGS.items():
            st.session_state[key] = value
        st.success("Recommended settings restored.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
