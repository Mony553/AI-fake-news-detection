from io import StringIO

import streamlit as st

from utils.database import clear_history, load_history
from utils.ui import kpi_card, page_header, section_title


def render() -> None:
    page_header("Review Records")

    session_history = st.session_state.get("session_history", [])
    df = load_history()
    display_df = df.copy()
    if not display_df.empty:
        display_df["prediction"] = display_df["prediction"].replace(
            {
                "Fake News": "High Risk",
                "Suspicious / Needs Review": "Needs Review",
                "Likely Real News": "Low Risk",
            }
        )
        display_df["risk_level"] = display_df["risk_level"].replace({"Medium Risk": "Needs Review"})

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("timer", "Reviewed Now", f"{len(session_history):,}", "Items checked in this session")
    with c2:
        kpi_card("archive", "Saved Reviews", f"{len(df):,}", "Review history records")
    with c3:
        high_risk = int((display_df["risk_level"] == "High Risk").sum()) if not display_df.empty else 0
        kpi_card("alert", "High Concern", f"{high_risk:,}", "Items needing careful review")
    with c4:
        needs_review = int((display_df["prediction"] == "Needs Review").sum()) if not display_df.empty else 0
        kpi_card("shield", "Needs Review", f"{needs_review:,}", "Items needing human review")

    session_tab, saved_tab = st.tabs(["Session reviews", "Saved audit log"])

    with session_tab:
        section_title("🕒", "Session Reviews", "Recent reviews stored in this browser session.")
        if session_history:
            st.dataframe(session_history, use_container_width=True, hide_index=True)
        else:
            st.markdown(
                """
                <div class="data-card">
                    <strong>No session history yet</strong>
                    <p>Run a review to populate recent session records.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with saved_tab:
        section_title("🗄️", "Saved CSV History", "Search, filter, download, and manage saved article reviews.")

        if display_df.empty:
            st.markdown(
                """
                <div class="data-card">
                    <strong>No review history yet</strong>
                    <p>Review an article or run a bulk upload to start building history records.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        col1, col2, col3 = st.columns([2, 1, 1])
        search = col1.text_input("Search title or source", placeholder="Type an article title, source, or keyword")
        prediction_filter = col2.selectbox("Decision", ["All"] + sorted(display_df["prediction"].dropna().unique().tolist()))
        risk_filter = col3.selectbox("Risk level", ["All"] + sorted(display_df["risk_level"].dropna().unique().tolist()))

        filtered = display_df.copy()
        if search:
            search_mask = (
                filtered["title"].astype(str).str.contains(search, case=False, na=False)
                | filtered["source"].astype(str).str.contains(search, case=False, na=False)
                | filtered["explanation_summary"].astype(str).str.contains(search, case=False, na=False)
            )
            filtered = filtered[search_mask]
        if prediction_filter != "All":
            filtered = filtered[filtered["prediction"] == prediction_filter]
        if risk_filter != "All":
            filtered = filtered[filtered["risk_level"] == risk_filter]

        filtered = filtered.sort_values("datetime", ascending=False)
        section_title("🔎", "Filtered Records", f"{len(filtered):,} records match the current filters.")
        display_columns = [
            "datetime",
            "title",
            "source",
            "prediction",
            "fake_probability",
            "real_probability",
            "credibility_score",
            "risk_level",
        ]
        st.dataframe(
            filtered[display_columns],
            use_container_width=True,
            hide_index=True,
            column_config={
                "datetime": "Date",
                "title": "Article",
                "source": "Source",
                "prediction": "Decision",
                "fake_probability": st.column_config.NumberColumn("Risk estimate", format="%.2f%%"),
                "real_probability": st.column_config.NumberColumn("Lower-risk signal", format="%.2f%%"),
                "credibility_score": st.column_config.NumberColumn("Credibility", format="%.2f"),
                "risk_level": "Risk level",
            },
        )

        csv_buffer = StringIO()
        filtered.to_csv(csv_buffer, index=False)
        left, right = st.columns([1, 1])
        left.download_button("Download filtered CSV", csv_buffer.getvalue(), "prediction_history.csv", "text/csv")
        if right.button("Clear saved history"):
            clear_history()
            st.success("History cleared.")
            st.rerun()
