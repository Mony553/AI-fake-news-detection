from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

import pandas as pd
import plotly.express as px

from utils.explanation import SUSPICIOUS_PHRASES


CHART_TEMPLATE = "plotly_white"
CHART_COLORS = {
    "High Risk": "#EF4444",
    "Needs Review": "#F59E0B",
    "Low Risk": "#10B981",
    "Fake News": "#EF4444",
    "Likely Real News": "#10B981",
    "Suspicious / Needs Review": "#F59E0B",
    "Medium Risk": "#F59E0B",
}
COLOR_SEQUENCE = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4"]


def _style(fig, title: str = ""):
    fig.update_layout(
        template=CHART_TEMPLATE,
        title=dict(text=title, x=0.02, xanchor="left", font=dict(size=20, color="#111827", family="Inter")),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#334155", family="Inter, system-ui, -apple-system, Segoe UI, sans-serif", size=13),
        colorway=COLOR_SEQUENCE,
        margin=dict(l=44, r=28, t=72, b=52),
        legend=dict(
            title="",
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#475569", size=12),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(bgcolor="#111827", font_size=12, font_color="#FFFFFF"),
        uniformtext_minsize=11,
        uniformtext_mode="hide",
    )
    fig.update_xaxes(
        gridcolor="#E5EAF2",
        zerolinecolor="#CBD5E1",
        linecolor="#CBD5E1",
        title_font=dict(color="#475569", size=13),
        tickfont=dict(color="#64748B", size=12),
    )
    fig.update_yaxes(
        gridcolor="#E5EAF2",
        zerolinecolor="#CBD5E1",
        linecolor="#CBD5E1",
        title_font=dict(color="#475569", size=13),
        tickfont=dict(color="#64748B", size=12),
    )
    return fig


def prediction_pie(df: pd.DataFrame):
    work = df.copy()
    work["prediction"] = work["prediction"].replace(
        {
            "Fake News": "High Risk",
            "Suspicious / Needs Review": "Needs Review",
            "Likely Real News": "Low Risk",
        }
    )
    counts = work["prediction"].value_counts().reset_index()
    counts.columns = ["prediction", "count"]
    fig = px.pie(
        counts,
        names="prediction",
        values="count",
        hole=0.58,
        color="prediction",
        color_discrete_map=CHART_COLORS,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        marker=dict(line=dict(color="#FFFFFF", width=3)),
        hovertemplate="<b>%{label}</b><br>Reviews: %{value}<br>Share: %{percent}<extra></extra>",
    )
    fig.add_annotation(
        text=f"{counts['count'].sum()}<br><span style='font-size:12px;color:#64748B'>reviews</span>",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=24, color="#111827"),
    )
    return _style(fig, "Review Decision Mix")


def risk_bar(df: pd.DataFrame):
    work = df.copy()
    work["risk_level"] = work["risk_level"].replace({"Medium Risk": "Needs Review"})
    order = ["Low Risk", "Needs Review", "High Risk"]
    counts = work["risk_level"].value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ["risk_level", "count"]
    fig = px.bar(
        counts,
        x="risk_level",
        y="count",
        color="risk_level",
        text="count",
        color_discrete_map=CHART_COLORS,
        labels={"risk_level": "Risk level", "count": "Number of reviews"},
    )
    fig.update_traces(
        textposition="outside",
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Reviews: %{y}<extra></extra>",
    )
    fig.update_layout(showlegend=False, bargap=0.42)
    fig.update_yaxes(rangemode="tozero")
    return _style(fig, "Risk Level Summary")


def credibility_histogram(df: pd.DataFrame):
    fig = px.histogram(
        df,
        x="credibility_score",
        nbins=16,
        color_discrete_sequence=["#10B981"],
        labels={"credibility_score": "Credibility score", "count": "Number of reviews"},
    )
    fig.update_traces(hovertemplate="Credibility range: %{x}<br>Reviews: %{y}<extra></extra>")
    fig.update_layout(showlegend=False, bargap=0.08)
    return _style(fig, "Credibility Score Distribution")


def fake_probability_histogram(df: pd.DataFrame):
    fig = px.histogram(
        df,
        x="fake_probability",
        nbins=16,
        color_discrete_sequence=["#EF4444"],
        labels={"fake_probability": "Risk estimate", "count": "Number of reviews"},
    )
    fig.update_traces(hovertemplate="Probability range: %{x}<br>Reviews: %{y}<extra></extra>")
    fig.update_layout(showlegend=False, bargap=0.08)
    return _style(fig, "Risk Estimate Distribution")


def checked_over_time(df: pd.DataFrame):
    work = df.copy()
    work["date"] = pd.to_datetime(work["datetime"], errors="coerce").dt.date
    counts = work.dropna(subset=["date"]).groupby("date").size().reset_index(name="count")
    fig = px.line(
        counts,
        x="date",
        y="count",
        markers=True,
        labels={"date": "Review date", "count": "Number of reviews"},
    )
    fig.update_traces(
        line=dict(color="#2563EB", width=3),
        marker=dict(size=9, color="#FFFFFF", line=dict(color="#2563EB", width=3)),
        hovertemplate="<b>%{x}</b><br>Reviews: %{y}<extra></extra>",
    )
    return _style(fig, "Daily Review Volume")


def flagged_phrase_bar(words: pd.DataFrame):
    fig = px.bar(
        words.sort_values("count"),
        x="count",
        y="word_or_phrase",
        orientation="h",
        text="count",
        color_discrete_sequence=["#8B5CF6"],
        labels={"word_or_phrase": "Flagged phrase", "count": "Times detected"},
    )
    fig.update_traces(
        textposition="outside",
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Detected: %{x}<extra></extra>",
    )
    fig.update_layout(showlegend=False, height=max(420, 34 * len(words) + 150))
    return _style(fig, "Flagged Phrase Signals")


def suspicious_word_counts(texts: Iterable[str]) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    phrase_patterns = {phrase: re.compile(re.escape(phrase), re.IGNORECASE) for phrase in SUSPICIOUS_PHRASES}
    for text in texts:
        for phrase, pattern in phrase_patterns.items():
            if pattern.search(str(text)):
                counter[phrase] += 1
    return pd.DataFrame(counter.most_common(12), columns=["word_or_phrase", "count"])
