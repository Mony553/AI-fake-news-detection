import importlib

import streamlit as st

from pages import about_model, batch_upload, check_news, dashboard, history, home
from pages import image_analysis, link_analysis, settings
from utils.ui import business_status_label, init_session_state, model_status


APP_TITLE = "Credibility Review Center"


def _load_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --background: #070A0F;
            --sidebar: #F5F8FF;
            --sidebar-panel: #FFFFFF;
            --sidebar-panel-soft: #EFF6FF;
            --card: #101722;
            --card-secondary: #162033;
            --card-hover: #1B2940;
            --primary: #38BDF8;
            --primary-hover: #7DD3FC;
            --violet: #A78BFA;
            --pink: #F472B6;
            --teal: #2DD4BF;
            --orange: #F97316;
            --success: #22C55E;
            --warning: #F59E0B;
            --danger: #EF4444;
            --text: #F8FAFC;
            --muted: #A7B2C3;
            --border: #263244;
            --panel-shadow: 0 18px 46px rgba(0, 0, 0, 0.34), 0 6px 16px rgba(0, 0, 0, 0.20);
            --panel-shadow-soft: 0 12px 30px rgba(0, 0, 0, 0.24), 0 3px 10px rgba(0, 0, 0, 0.16);
            --panel-shadow-strong: 0 24px 58px rgba(0, 0, 0, 0.42), 0 10px 24px rgba(56, 189, 248, 0.10);
        }

        .stApp {
            background:
                radial-gradient(circle at 12% -8%, rgba(167, 139, 250, 0.18), transparent 24rem),
                radial-gradient(circle at 88% 4%, rgba(244, 114, 182, 0.14), transparent 24rem),
                radial-gradient(circle at 42% 16%, rgba(45, 212, 191, 0.11), transparent 26rem),
                linear-gradient(180deg, rgba(56, 189, 248, 0.08), rgba(7, 10, 15, 0) 22rem),
                var(--background);
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            background: rgba(7, 10, 15, 0.84);
            backdrop-filter: blur(14px);
        }

        .block-container {
            max-width: none;
            width: 100%;
            padding: calc(4.25rem + env(safe-area-inset-top)) clamp(1rem, 2.1vw, 2.25rem) 2.4rem;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 35% 2%, rgba(37, 99, 235, 0.10), transparent 14rem),
                linear-gradient(180deg, #F8FAFF 0%, #F3F7FF 48%, #F8FAFC 100%),
                var(--sidebar);
            border-right: 1px solid rgba(191, 219, 254, 0.78);
            min-width: 278px !important;
            width: 278px !important;
        }

        section[data-testid="stSidebar"] > div {
            margin: 0.85rem 0.75rem;
            padding: 1rem 0.85rem 1rem;
            min-height: calc(100vh - 1.7rem);
            border: 1px solid rgba(219, 234, 254, 0.78);
            border-radius: 18px;
            background:
                radial-gradient(circle at 50% 0%, rgba(37, 99, 235, 0.08), transparent 11rem),
                linear-gradient(180deg, rgba(255, 255, 255, 0.68), rgba(248, 250, 252, 0.42));
            box-shadow:
                0 22px 42px rgba(37, 99, 235, 0.08),
                inset 0 1px 0 rgba(255, 255, 255, 0.86);
            overflow: hidden;
            position: relative;
        }

        section[data-testid="stSidebar"] > div::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            border-radius: inherit;
            background:
                linear-gradient(90deg, rgba(37, 99, 235, 0.26), transparent 0.28rem),
                radial-gradient(circle at 88% 3%, rgba(14, 165, 233, 0.12), transparent 8rem);
        }

        section[data-testid="stSidebar"] > div > div {
            position: relative;
            z-index: 1;
        }

        section[data-testid="stSidebar"] * {
            color: #0F172A;
        }

        section[data-testid="stSidebarNav"],
        div[data-testid="stSidebarNav"] {
            display: none !important;
        }

        h1, h2, h3, h4, p, label, span, div {
            letter-spacing: 0;
        }

        h1 {
            color: var(--text);
            font-size: clamp(1.9rem, 2.8vw, 3rem);
            line-height: 1.05;
            text-align: left;
            margin: 0;
            font-weight: 900;
        }

        h2, h3 {
            color: var(--text);
        }

        .sidebar-brand {
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(148, 163, 184, 0.32);
            border-radius: 16px;
            background:
                radial-gradient(circle at 86% 0%, rgba(37, 99, 235, 0.15), transparent 8rem),
                linear-gradient(180deg, rgba(30, 41, 59, 0.98), rgba(17, 24, 39, 0.96));
            box-shadow:
                0 18px 36px rgba(15, 23, 42, 0.18),
                inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }

        .sidebar-brand h2 {
            color: #FFFFFF;
            font-size: 1.6rem;
            margin: 0 0 0.55rem;
            font-weight: 900;
        }

        .sidebar-brand p {
            color: #CBD5E1;
            margin: 0.25rem 0;
            font-size: 0.88rem;
        }

        .status-line {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #FFFFFF;
        }

        .status-dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 999px;
            background: #57ff7a;
            display: inline-block;
            box-shadow: 0 0 18px rgba(34, 197, 94, 0.65);
        }

        div[role="radiogroup"] {
            gap: 0.28rem;
            display: grid;
        }

        div[role="radiogroup"] label {
            min-height: 3.05rem;
            border-radius: 12px;
            padding: 0.55rem 0.75rem;
            border: 1px solid rgba(191, 219, 254, 0.82);
            transition: all 160ms ease;
            display: flex !important;
            align-items: center;
            gap: 0.9rem;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: 0 10px 24px rgba(37, 99, 235, 0.06);
        }

        div[role="radiogroup"] label:hover {
            background: #EFF6FF;
            border-color: rgba(96, 165, 250, 0.72);
            box-shadow: 0 14px 28px rgba(37, 99, 235, 0.12);
        }

        div[role="radiogroup"] label > div:first-child,
        div[role="radiogroup"] label input {
            display: none !important;
        }

        div[role="radiogroup"] label p {
            color: #123B7A !important;
            font-size: 0.94rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
        }

        div[role="radiogroup"] label::before {
            width: 2.55rem;
            height: 2.55rem;
            border-radius: 10px;
            display: grid;
            place-items: center;
            background:
                linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(14, 165, 233, 0.10)),
                var(--sidebar-panel-soft);
            border: 1px solid rgba(191, 219, 254, 0.78);
            color: #123B7A;
            font-size: 1.45rem;
            flex: 0 0 auto;
            box-shadow: 0 10px 22px rgba(37, 99, 235, 0.08);
        }

        div[role="radiogroup"] label:nth-child(1)::before {content: "⌂";}
        div[role="radiogroup"] label:nth-child(2)::before {content: "T";}
        div[role="radiogroup"] label:nth-child(3)::before {content: "◫";}
        div[role="radiogroup"] label:nth-child(4)::before {content: "⛓";}
        div[role="radiogroup"] label:nth-child(5)::before {content: "CSV";}
        div[role="radiogroup"] label:nth-child(6)::before {content: "↗";}
        div[role="radiogroup"] label:nth-child(7)::before {content: "DB";}
        div[role="radiogroup"] label:nth-child(8)::before {content: "◷";}
        div[role="radiogroup"] label:nth-child(9)::before {content: "⚙";}

        div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, #2563EB, #0EA5E9);
            border-color: rgba(125, 211, 252, 0.62);
            box-shadow: 0 14px 34px rgba(37, 99, 235, 0.28), 0 8px 22px rgba(14, 165, 233, 0.15);
        }

        div[role="radiogroup"] label:has(input:checked) p,
        div[role="radiogroup"] label:has(input:checked) span {
            color: #FFFFFF !important;
            font-weight: 900;
        }

        div[role="radiogroup"] label:has(input:checked)::before {
            background: rgba(255, 255, 255, 0.14);
            border-color: rgba(255, 255, 255, 0.22);
            color: #FFFFFF;
        }

        .sidebar-bottom {
            border-top: 1px solid rgba(191, 219, 254, 0.72);
            margin-top: 1.25rem;
            padding: 1rem 0.55rem 0;
            display: grid;
            gap: 0.65rem;
            color: var(--muted);
        }

        .sidebar-bottom div {
            color: #334155;
            font-weight: 700;
            font-size: 0.88rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        .sidebar-chip {
            border: 1px solid rgba(203, 213, 225, 0.92);
            background:
                linear-gradient(135deg, rgba(239, 246, 255, 0.88), rgba(255, 255, 255, 0.98)),
                var(--sidebar-panel);
            border-radius: 10px;
            padding: 0.7rem;
            margin-top: 0.25rem;
        }

        .sidebar-icon {
            width: 2.55rem;
            height: 2.55rem;
            border-radius: 13px;
            display: inline-grid;
            place-items: center;
            background: var(--sidebar-panel-soft);
            color: #2563EB;
            flex: 0 0 auto;
            font-size: 1.18rem;
        }

        .dashboard-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.05rem;
            padding: 1rem 1.1rem;
            border: 1px solid var(--border);
            border-radius: 12px;
            background:
                radial-gradient(circle at 86% 0%, rgba(244, 114, 182, 0.12), transparent 15rem),
                radial-gradient(circle at 12% 16%, rgba(45, 212, 191, 0.10), transparent 14rem),
                rgba(16, 23, 34, 0.90);
            box-shadow: var(--panel-shadow);
        }

        .dashboard-header .lead {
            max-width: 920px;
            text-align: left;
            margin: 0.35rem 0 0;
        }

        .eyebrow {
            color: var(--primary);
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 900;
            letter-spacing: 0;
            text-align: left;
            margin-bottom: 0.45rem;
        }

        .lead {
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.55;
        }

        .header-status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--muted);
            border: 1px solid var(--border);
            background:
                linear-gradient(135deg, rgba(56, 189, 248, 0.10), rgba(167, 139, 250, 0.07)),
                var(--card);
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            font-size: 0.88rem;
            white-space: nowrap;
        }

        .input-card,
        .kpi-card,
        .analysis-result,
        .side-card,
        .insight-card,
        .data-card {
            background:
                radial-gradient(circle at 92% 0%, rgba(56, 189, 248, 0.10), transparent 8rem),
                linear-gradient(180deg, rgba(22,32,51,0.97), rgba(16,23,34,0.97));
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: var(--panel-shadow);
            transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
        }

        .kpi-card::before,
        .insight-card::before,
        .feature-card::before,
        .timeline-card::before,
        .model-info-card::before,
        .data-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--violet), var(--pink));
            opacity: 0.95;
        }

        div[data-testid="column"]:nth-of-type(1) .kpi-card::before,
        div[data-testid="column"]:nth-of-type(1) .insight-card::before,
        div[data-testid="column"]:nth-of-type(1) .feature-card::before,
        div[data-testid="column"]:nth-of-type(1) .timeline-card::before {
            background: linear-gradient(90deg, var(--primary), #60A5FA);
        }

        div[data-testid="column"]:nth-of-type(2) .kpi-card::before,
        div[data-testid="column"]:nth-of-type(2) .insight-card::before,
        div[data-testid="column"]:nth-of-type(2) .feature-card::before,
        div[data-testid="column"]:nth-of-type(2) .timeline-card::before {
            background: linear-gradient(90deg, var(--violet), #C084FC);
        }

        div[data-testid="column"]:nth-of-type(3) .kpi-card::before,
        div[data-testid="column"]:nth-of-type(3) .insight-card::before,
        div[data-testid="column"]:nth-of-type(3) .feature-card::before,
        div[data-testid="column"]:nth-of-type(3) .timeline-card::before {
            background: linear-gradient(90deg, var(--teal), var(--success));
        }

        div[data-testid="column"]:nth-of-type(4) .kpi-card::before,
        div[data-testid="column"]:nth-of-type(4) .insight-card::before,
        div[data-testid="column"]:nth-of-type(4) .feature-card::before,
        div[data-testid="column"]:nth-of-type(4) .timeline-card::before {
            background: linear-gradient(90deg, var(--pink), #FB7185);
        }

        div[data-testid="column"]:nth-of-type(5) .kpi-card::before,
        div[data-testid="column"]:nth-of-type(5) .timeline-card::before {
            background: linear-gradient(90deg, var(--orange), var(--warning));
        }

        div[data-testid="column"]:nth-of-type(1) .kpi-icon,
        div[data-testid="column"]:nth-of-type(1) .insight-icon,
        div[data-testid="column"]:nth-of-type(1) .feature-icon {
            color: var(--primary);
            background: rgba(56, 189, 248, 0.18);
        }

        div[data-testid="column"]:nth-of-type(2) .kpi-icon,
        div[data-testid="column"]:nth-of-type(2) .insight-icon,
        div[data-testid="column"]:nth-of-type(2) .feature-icon {
            color: var(--violet);
            background: rgba(167, 139, 250, 0.18);
        }

        div[data-testid="column"]:nth-of-type(3) .kpi-icon,
        div[data-testid="column"]:nth-of-type(3) .insight-icon,
        div[data-testid="column"]:nth-of-type(3) .feature-icon {
            color: var(--teal);
            background: rgba(45, 212, 191, 0.17);
        }

        div[data-testid="column"]:nth-of-type(4) .kpi-icon,
        div[data-testid="column"]:nth-of-type(4) .insight-icon,
        div[data-testid="column"]:nth-of-type(4) .feature-icon {
            color: var(--pink);
            background: rgba(244, 114, 182, 0.18);
        }

        div[data-testid="column"]:nth-of-type(5) .kpi-icon {
            color: var(--orange);
            background: rgba(249, 115, 22, 0.17);
        }

        .input-card:hover,
        .kpi-card:hover,
        .analysis-result:hover,
        .side-card:hover,
        .insight-card:hover,
        .data-card:hover,
        .feature-card:hover,
        .model-info-card:hover,
        .notice-card:hover,
        .timeline-card:hover,
        .recent-card:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.38);
            box-shadow: var(--panel-shadow-strong);
        }

        .input-card {
            padding: 0;
            margin: 0;
            max-width: none;
        }

        .home-search {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 118px;
            gap: 0.85rem;
            align-items: center;
            max-width: 100%;
            margin: 0 auto 1.45rem;
        }

        .input-card .stTextInput input {
            background: transparent;
            border: 0;
            color: var(--text);
            min-height: 3.1rem;
            font-size: 1rem;
        }

        .input-card .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        .stTextInput input::placeholder {
            color: #737373;
            opacity: 1;
        }

        .kpi-card {
            min-height: 132px;
            padding: 1.18rem;
            margin: 0 0 1.35rem;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: stretch;
            gap: 1rem;
            position: relative;
            overflow: hidden;
        }

        div[data-testid="stHorizontalBlock"]:has(.kpi-card) {
            column-gap: clamp(1.35rem, 2.1vw, 2.1rem) !important;
            row-gap: clamp(1.1rem, 1.8vw, 1.65rem) !important;
            margin-bottom: clamp(1.15rem, 1.9vw, 1.65rem);
            align-items: stretch;
        }

        div[data-testid="column"]:has(.kpi-card) {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        .kpi-icon,
        .insight-icon {
            width: 46px;
            height: 46px;
            border-radius: 10px;
            display: grid;
            place-items: center;
            color: var(--primary);
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(167, 139, 250, 0.12));
            font-size: 1.45rem;
            flex: 0 0 auto;
            box-shadow: var(--panel-shadow-soft);
        }

        .kpi-icon svg,
        .insight-icon svg,
        .section-icon svg,
        .heading-icon svg,
        .feature-icon svg {
            width: 1.42rem;
            height: 1.42rem;
            stroke-width: 2.55;
        }

        .kpi-card .kpi-icon {
            position: absolute;
            top: 1.05rem;
            right: 1.05rem;
        }

        .kpi-label {
            color: var(--muted);
            font-size: 0.92rem;
            text-transform: none;
            font-weight: 850;
            letter-spacing: 0;
            margin: 0 3.45rem 1.35rem 0;
            min-height: 2rem;
        }

        .kpi-value {
            color: var(--text);
            font-size: clamp(1.65rem, 2.2vw, 2.35rem);
            font-weight: 900;
            line-height: 1;
            overflow-wrap: anywhere;
        }

        .kpi-caption {
            color: var(--muted);
            margin-top: auto;
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .section-heading {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: var(--text);
            margin: 1.15rem 0 0.75rem;
        }

        .section-heading > span {
            color: var(--primary);
            width: 2.8rem;
            height: 2.8rem;
            border-radius: 11px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(167, 139, 250, 0.12));
            box-shadow: var(--panel-shadow-soft);
            flex: 0 0 auto;
        }

        .section-heading strong {
            color: var(--text);
            font-size: 1.35rem;
        }

        .section-heading p {
            color: var(--muted);
            margin: 0.15rem 0 0;
        }

        .analysis-result {
            padding: 1.65rem;
            border-color: rgba(239, 68, 68, 0.40);
            background:
                radial-gradient(circle at 84% 26%, rgba(239,68,68,0.20), transparent 26%),
                radial-gradient(circle at 8% 0%, rgba(244, 114, 182, 0.12), transparent 20rem),
                linear-gradient(135deg, #172033, #0B1018);
        }

        .analysis-result.risk-low {
            border-color: rgba(34,197,94,0.48);
            background:
                radial-gradient(circle at 84% 26%, rgba(34,197,94,0.18), transparent 26%),
                radial-gradient(circle at 10% 0%, rgba(45, 212, 191, 0.12), transparent 18rem),
                linear-gradient(135deg, #0F1A12, #0D0D0D);
        }

        .result-topline {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 150px;
            gap: 1.5rem;
            align-items: center;
        }

        .analysis-result h2 {
            font-size: clamp(1.9rem, 3.4vw, 2.8rem);
            line-height: 1.1;
            margin: 1rem 0 0.8rem;
            max-width: 580px;
        }

        .analysis-result p {
            color: var(--muted);
            font-size: 0.98rem;
            line-height: 1.5;
            max-width: 620px;
        }

        .status-badge {
            display: inline-flex;
            border-radius: 999px;
            padding: 0.38rem 0.85rem;
            font-size: 0.78rem;
            font-weight: 900;
            color: var(--text);
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.08);
        }

        .badge-danger {border-color: rgba(255,77,77,0.55);}
        .badge-good {border-color: rgba(34,197,94,0.55);}

        .risk-ring {
            width: 124px;
            height: 124px;
            border-radius: 999px;
            display: grid;
            place-items: center;
            justify-self: center;
            background:
                radial-gradient(circle, var(--card) 55%, transparent 56%),
                conic-gradient(var(--primary) calc(var(--score) * 1%), rgba(255,255,255,0.13) 0);
        }

        .risk-low .risk-ring {
            background:
                radial-gradient(circle, var(--card) 55%, transparent 56%),
                conic-gradient(var(--success) calc(var(--score) * 1%), rgba(255,255,255,0.13) 0);
        }

        .risk-ring div {
            color: var(--text);
            font-size: 1.7rem;
            font-weight: 900;
            text-align: center;
        }

        .risk-ring span {
            font-size: 0.9rem;
        }

        .risk-meter {
            margin: 1rem 0 1.35rem;
            padding: 1rem 1.1rem;
            border: 1px solid var(--border);
            border-radius: 14px;
            background:
                linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)),
                rgba(7, 10, 15, 0.42);
            box-shadow: var(--panel-shadow-soft);
        }

        .risk-meter-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.85rem;
        }

        .risk-meter-header span {
            display: block;
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 850;
            letter-spacing: 0;
            margin-bottom: 0.2rem;
        }

        .risk-meter-header strong {
            color: var(--text);
            font-size: 1.08rem;
            line-height: 1.2;
        }

        .risk-meter-header b {
            flex: 0 0 auto;
            border-radius: 999px;
            padding: 0.38rem 0.72rem;
            color: var(--text);
            background: rgba(255,255,255,0.08);
            border: 1px solid var(--border);
            font-size: 0.9rem;
        }

        .risk-meter-track {
            height: 0.72rem;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(148, 163, 184, 0.24);
        }

        .risk-meter-fill {
            width: var(--score);
            height: 100%;
            min-width: 0.55rem;
            border-radius: inherit;
            background: linear-gradient(90deg, #22C55E, #84CC16);
        }

        .risk-meter-warning .risk-meter-fill {
            background: linear-gradient(90deg, #F59E0B, #F97316);
        }

        .risk-meter-high .risk-meter-fill {
            background: linear-gradient(90deg, #FB7185, #EF4444);
        }

        .risk-meter-scale {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.65rem;
            margin-top: 0.65rem;
            color: var(--muted);
            font-size: 0.76rem;
            font-weight: 760;
        }

        .risk-meter-scale span:nth-child(2) {
            text-align: center;
        }

        .risk-meter-scale span:nth-child(3) {
            text-align: right;
        }

        .result-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            column-gap: clamp(1rem, 1.8vw, 1.45rem);
            row-gap: clamp(1rem, 1.8vw, 1.45rem);
            margin: 1.35rem 0 0.75rem;
        }

        .result-grid div,
        .mini-panel {
            border: 1px solid var(--border);
            border-radius: 12px;
            background:
                linear-gradient(135deg, rgba(56, 189, 248, 0.06), rgba(244, 114, 182, 0.04)),
                rgba(7,10,15,0.44);
            padding: 1.12rem;
            box-shadow: var(--panel-shadow-soft);
        }

        .result-grid span {
            display: block;
            color: var(--muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            font-weight: 800;
            margin-bottom: 0.4rem;
        }

        .result-grid strong {
            color: var(--text);
        }

        .side-card {
            padding: 1.5rem;
            margin-bottom: 1.2rem;
        }

        .side-card h3 {
            margin: 0 0 1.1rem;
            font-size: 1.35rem;
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }

        .heading-icon {
            width: 2.75rem;
            height: 2.75rem;
            border-radius: 10px;
            display: inline-grid;
            place-items: center;
            color: var(--primary);
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(244, 114, 182, 0.12));
            box-shadow: var(--panel-shadow-soft);
            flex: 0 0 auto;
        }

        .impact-list {
            display: grid;
            gap: 1rem;
            margin: 0;
            padding: 0;
            list-style: none;
        }

        .impact-list li {
            border-left: 4px solid var(--primary);
            border-radius: 10px;
            padding: 1rem;
            background:
                linear-gradient(135deg, rgba(56, 189, 248, 0.06), rgba(45, 212, 191, 0.05)),
                rgba(7,10,15,0.40);
            box-shadow: var(--panel-shadow-soft);
        }

        .impact-list strong,
        .impact-list span {
            display: block;
        }

        .impact-list span {
            color: var(--muted);
            margin-top: 0.4rem;
            line-height: 1.45;
        }

        .insight-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: clamp(1.15rem, 1.8vw, 1.65rem);
        }

        .insight-card {
            position: relative;
            overflow: hidden;
            padding: 1.25rem;
            min-height: 160px;
            margin-bottom: clamp(1.1rem, 1.75vw, 1.55rem);
        }

        .insight-card strong {
            display: block;
            color: var(--text);
            margin: 0.8rem 0 0.35rem;
            font-size: 1.02rem;
        }

        .insight-card p {
            color: var(--muted);
            line-height: 1.42;
            margin: 0;
        }

        .source-trust-list {
            display: grid;
            gap: 0.75rem;
            margin: 0;
            padding: 0;
            list-style: none;
        }

        .source-trust-list li {
            display: grid;
            grid-template-columns: 2.35rem minmax(0, 1fr);
            gap: 0.75rem;
            align-items: start;
            border: 1px solid var(--border);
            border-radius: 10px;
            background:
                linear-gradient(135deg, rgba(56, 189, 248, 0.06), rgba(45, 212, 191, 0.05)),
                rgba(7,10,15,0.40);
            padding: 0.85rem;
            box-shadow: var(--panel-shadow-soft);
        }

        .source-trust-list li > span {
            width: 2.35rem;
            height: 2.35rem;
            display: grid;
            place-items: center;
            border-radius: 10px;
            color: var(--success);
            background: rgba(34, 197, 94, 0.12);
        }

        .source-trust-list li.trust-warn > span {
            color: var(--warning);
            background: rgba(245, 158, 11, 0.13);
        }

        .source-trust-list svg {
            width: 1.25rem;
            height: 1.25rem;
            stroke-width: 2.6;
        }

        .source-trust-list strong {
            display: block;
            color: var(--text);
            font-size: 0.95rem;
            font-weight: 900;
            line-height: 1.25;
        }

        .source-trust-list p {
            margin: 0.28rem 0 0;
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.35;
            overflow-wrap: anywhere;
        }

        .data-card {
            position: relative;
            overflow: hidden;
            padding: 1.3rem;
            margin-bottom: 1rem;
        }

        .data-card p {
            color: var(--muted);
            line-height: 1.5;
            margin: 0.45rem 0 0;
        }

        .home-hero {
            border: 1px solid rgba(56, 189, 248, 0.28);
            border-radius: 12px;
            padding: clamp(1.25rem, 2.4vw, 2rem);
            margin-bottom: 1.35rem;
            background:
                radial-gradient(circle at 88% 18%, rgba(56,189,248,0.16), transparent 30%),
                radial-gradient(circle at 8% 0%, rgba(244,114,182,0.12), transparent 28%),
                linear-gradient(135deg, rgba(22,32,51,0.98), rgba(7,10,15,0.98));
            box-shadow: var(--panel-shadow);
        }

        .home-hero h1 {
            text-align: left;
            max-width: 820px;
            margin-bottom: 0.8rem;
        }

        .home-hero p {
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.58;
            max-width: 860px;
            margin: 0;
        }

        .home-hero .eyebrow {
            text-align: left;
        }

        .hero-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 1.35rem;
        }

        .home-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 0.9rem;
            margin-bottom: 1rem;
        }

        .feature-card,
        .model-info-card,
        .notice-card,
        .timeline-card,
        .recent-card {
            background:
                radial-gradient(circle at 92% 0%, rgba(56, 189, 248, 0.09), transparent 7rem),
                linear-gradient(180deg, rgba(22,32,51,0.96), rgba(16,23,34,0.96));
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: var(--panel-shadow);
        }

        .feature-card {
            position: relative;
            overflow: hidden;
            padding: 1.15rem;
            min-height: 168px;
        }

        .feature-icon {
            width: 3.05rem;
            height: 3.05rem;
            border-radius: 10px;
            display: grid;
            place-items: center;
            color: var(--primary);
            background: linear-gradient(135deg, rgba(56,189,248,0.18), rgba(167,139,250,0.12));
            font-size: 1.55rem;
            margin-bottom: 0.9rem;
            box-shadow: var(--panel-shadow-soft);
        }

        .feature-card strong,
        .model-info-card strong,
        .notice-card strong,
        .timeline-card strong,
        .recent-card strong {
            color: var(--text);
            font-size: 1.05rem;
        }

        .model-info-card > strong,
        .notice-card > strong {
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }

        .feature-card p,
        .timeline-card p,
        .notice-card p,
        .recent-card p {
            color: var(--muted);
            line-height: 1.48;
            margin: 0.45rem 0 0;
        }

        .timeline-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 0.8rem;
        }

        .timeline-card {
            overflow: hidden;
            padding: 1rem;
            position: relative;
            min-height: 126px;
        }

        .timeline-step {
            width: 2.25rem;
            height: 2.25rem;
            border-radius: 999px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, var(--primary), var(--teal));
            color: #04111D;
            font-weight: 900;
            margin-bottom: 0.75rem;
        }

        .model-info-card {
            position: relative;
            overflow: hidden;
            padding: 1.15rem;
        }

        .model-info-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 0.9rem;
        }

        .model-info-grid div {
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.8rem;
            background:
                linear-gradient(135deg, rgba(56, 189, 248, 0.06), rgba(167, 139, 250, 0.05)),
                rgba(7,10,15,0.38);
            box-shadow: var(--panel-shadow-soft);
        }

        .model-info-grid span {
            display: block;
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .model-info-grid b {
            color: var(--text);
        }

        .notice-card {
            padding: 1.05rem 1.15rem;
            border-color: rgba(245,158,11,0.34);
            background:
                linear-gradient(90deg, rgba(245,158,11,0.14), rgba(244,114,182,0.08), transparent),
                rgba(16,23,34,0.95);
        }

        .recent-card {
            padding: 0.95rem;
            margin-bottom: 0.6rem;
        }

        .recent-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.65rem;
        }

        .mini-pill {
            border: 1px solid var(--border);
            background:
                linear-gradient(135deg, rgba(56,189,248,0.08), rgba(244,114,182,0.06)),
                rgba(7,10,15,0.42);
            color: var(--muted);
            border-radius: 999px;
            padding: 0.25rem 0.6rem;
            font-size: 0.78rem;
            font-weight: 800;
        }

        .stTabs [data-baseweb="tab-list"] {
            justify-content: flex-start;
            gap: 0.45rem;
            overflow-x: auto;
            padding-bottom: 0.2rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.35rem 1rem;
            color: var(--muted);
            background:
                linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(167, 139, 250, 0.06)),
                var(--card);
            border: 1px solid var(--border);
        }

        .stTabs [aria-selected="true"] {
            color: var(--text);
            background: linear-gradient(135deg, var(--primary), var(--violet));
            border-color: var(--primary);
        }

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stSlider,
        div[data-testid="stFileUploader"] section {
            background: var(--card);
            color: var(--text);
            border-color: var(--border);
            border-radius: 10px;
            box-shadow: var(--panel-shadow-soft);
        }

        .stTextArea textarea {
            color: var(--text);
        }

        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 10px;
            min-height: 3rem;
            font-weight: 900;
            border: 1px solid var(--primary);
            background: var(--primary);
            color: #04111D;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            border-color: var(--primary-hover);
            background: var(--primary-hover);
            color: #04111D;
        }

        div[data-testid="stMetric"] {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: var(--panel-shadow-soft);
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--muted);
        }

        div[data-testid="stMetricValue"] {
            color: var(--text);
        }

        /* Stitch-inspired business workspace refresh */
        :root {
            --background: #F6F8FB;
            --sidebar: #FFFFFF;
            --sidebar-panel: #FFFFFF;
            --sidebar-panel-soft: #F1F5F9;
            --card: #FFFFFF;
            --card-secondary: #F8FAFC;
            --card-hover: #F1F5F9;
            --primary: #2563EB;
            --primary-hover: #1D4ED8;
            --violet: #7C3AED;
            --pink: #DB2777;
            --teal: #0F766E;
            --orange: #D97706;
            --success: #16A34A;
            --warning: #D97706;
            --danger: #DC2626;
            --text: #0F172A;
            --muted: #64748B;
            --border: #E2E8F0;
            --panel-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
            --panel-shadow-soft: 0 10px 24px rgba(15, 23, 42, 0.06);
            --panel-shadow-strong: 0 24px 58px rgba(15, 23, 42, 0.12);
        }

        .stApp {
            background:
                linear-gradient(90deg, rgba(37, 99, 235, 0.06), transparent 34rem),
                linear-gradient(180deg, #FFFFFF 0%, #F6F8FB 18rem, #F8FAFC 100%);
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.82);
            border-bottom: 1px solid rgba(226, 232, 240, 0.78);
        }

        .block-container {
            padding: calc(3.75rem + env(safe-area-inset-top)) clamp(1rem, 2vw, 2.1rem) 2rem;
        }

        h1, h2, h3, h4, p, label, span, div {
            color: inherit;
        }

        h1, h2, h3 {
            color: var(--text);
        }

        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid var(--border);
            min-width: 286px !important;
            width: 286px !important;
        }

        section[data-testid="stSidebar"] > div {
            margin: 0;
            padding: 1rem 0.9rem;
            min-height: 100vh;
            border: 0;
            border-radius: 0;
            background: #FFFFFF;
            box-shadow: none;
        }

        section[data-testid="stSidebar"] > div::before {
            display: none;
        }

        section[data-testid="stSidebar"] * {
            color: #0F172A;
        }

        .sidebar-brand {
            border: 1px solid #DBEAFE;
            border-radius: 14px;
            background:
                linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 58%, #F8FAFC 100%);
            box-shadow: var(--panel-shadow-soft);
        }

        .sidebar-brand h2 {
            color: #0F172A;
            font-size: 1.28rem;
        }

        .sidebar-brand p {
            color: #475569;
        }

        .status-dot {
            background: #16A34A;
            box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.12);
        }

        div[role="radiogroup"] {
            gap: 0.38rem;
        }

        div[role="radiogroup"] label {
            min-height: 2.85rem;
            border-radius: 10px;
            background: transparent;
            border-color: transparent;
            box-shadow: none;
        }

        div[role="radiogroup"] label:hover {
            background: #F8FAFC;
            border-color: #E2E8F0;
            box-shadow: none;
        }

        div[role="radiogroup"] label p {
            color: #334155 !important;
            font-weight: 750 !important;
        }

        div[role="radiogroup"] label::before {
            width: 2.25rem;
            height: 2.25rem;
            border-radius: 9px;
            background: #F1F5F9;
            border-color: #E2E8F0;
            color: #475569;
            box-shadow: none;
            font-size: 1.1rem;
        }

        div[role="radiogroup"] label:has(input:checked) {
            background: #EEF2FF;
            border-color: #C7D2FE;
            box-shadow: none;
        }

        div[role="radiogroup"] label:has(input:checked) p,
        div[role="radiogroup"] label:has(input:checked) span {
            color: #1D4ED8 !important;
        }

        div[role="radiogroup"] label:has(input:checked)::before {
            background: #2563EB;
            border-color: #2563EB;
            color: #FFFFFF;
        }

        .sidebar-bottom {
            border-top: 1px solid var(--border);
        }

        .sidebar-bottom div {
            color: #475569;
        }

        .sidebar-chip {
            background: #F8FAFC;
            border-color: var(--border);
        }

        .sidebar-icon {
            background: #EEF2FF;
            color: #2563EB;
        }

        .dashboard-header,
        .home-hero {
            border: 1px solid var(--border);
            border-radius: 16px;
            background:
                linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 58%, #EEF2FF 100%);
            box-shadow: var(--panel-shadow);
        }

        .dashboard-header {
            padding: 1.15rem 1.25rem;
        }

        .home-hero {
            padding: clamp(1.4rem, 2.8vw, 2.4rem);
        }

        .home-hero h1,
        .dashboard-header h1 {
            color: #0F172A;
            font-size: clamp(2rem, 3.1vw, 3.15rem);
            line-height: 1.04;
        }

        .lead,
        .home-hero p,
        .section-heading p,
        .kpi-caption,
        .feature-card p,
        .timeline-card p,
        .notice-card p,
        .recent-card p,
        .data-card p,
        .analysis-result p,
        .impact-list span,
        .insight-card p {
            color: var(--muted);
        }

        .eyebrow {
            color: #2563EB;
        }

        .header-status {
            color: #166534;
            border-color: #BBF7D0;
            background: #F0FDF4;
        }

        .input-card,
        .kpi-card,
        .analysis-result,
        .side-card,
        .insight-card,
        .data-card,
        .feature-card,
        .model-info-card,
        .notice-card,
        .timeline-card,
        .recent-card,
        div[data-testid="stMetric"],
        [data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 14px;
            box-shadow: var(--panel-shadow-soft);
        }

        .kpi-card::before,
        .insight-card::before,
        .feature-card::before,
        .timeline-card::before,
        .model-info-card::before,
        .data-card::before {
            height: 0;
        }

        .input-card:hover,
        .kpi-card:hover,
        .analysis-result:hover,
        .side-card:hover,
        .insight-card:hover,
        .data-card:hover,
        .feature-card:hover,
        .model-info-card:hover,
        .notice-card:hover,
        .timeline-card:hover,
        .recent-card:hover {
            transform: translateY(-1px);
            border-color: #CBD5E1;
            box-shadow: var(--panel-shadow-strong);
        }

        .kpi-icon,
        .insight-icon,
        .feature-icon,
        .heading-icon,
        .section-heading > span {
            color: #2563EB;
            background: #EEF2FF;
            box-shadow: none;
        }

        .kpi-label,
        .result-grid span,
        .model-info-grid span {
            color: #64748B;
        }

        .kpi-value,
        .feature-card strong,
        .model-info-card strong,
        .notice-card strong,
        .timeline-card strong,
        .recent-card strong,
        .section-heading strong,
        .insight-card strong,
        .side-card h3,
        .model-info-grid b,
        .result-grid strong,
        div[data-testid="stMetricValue"] {
            color: #0F172A;
        }

        .source-trust-list li {
            border-color: #DCE6F4;
            background: #F8FAFC;
            box-shadow: none;
        }

        .source-trust-list strong {
            color: #111827;
        }

        .source-trust-list p {
            color: #64748B;
        }

        .analysis-result {
            border-color: #FECACA;
            background:
                linear-gradient(135deg, #FFFFFF 0%, #FFF7ED 52%, #FEF2F2 100%);
        }

        .analysis-result.risk-low {
            border-color: #BBF7D0;
            background:
                linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 62%, #ECFDF5 100%);
        }

        .status-badge {
            color: #1E293B;
            background: #F8FAFC;
            border-color: #E2E8F0;
        }

        .risk-ring {
            background:
                radial-gradient(circle, #FFFFFF 55%, transparent 56%),
                conic-gradient(var(--danger) calc(var(--score) * 1%), #E2E8F0 0);
        }

        .risk-low .risk-ring {
            background:
                radial-gradient(circle, #FFFFFF 55%, transparent 56%),
                conic-gradient(var(--success) calc(var(--score) * 1%), #E2E8F0 0);
        }

        .risk-ring div {
            color: #0F172A;
        }

        .risk-meter {
            border-color: #DCE6F4;
            background: #FFFFFF;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
        }

        .risk-meter-header span,
        .risk-meter-scale {
            color: #64748B;
        }

        .risk-meter-header strong {
            color: #0F172A;
        }

        .risk-meter-header b {
            color: #0F172A;
            border-color: #DCE6F4;
            background: #F8FAFC;
        }

        .risk-meter-track {
            background: #E8EEF7;
        }

        .result-grid div,
        .mini-panel,
        .model-info-grid div,
        .impact-list li,
        .mini-pill {
            background: #F8FAFC;
            border-color: var(--border);
            box-shadow: none;
        }

        .impact-list li {
            border-left-color: #2563EB;
        }

        .notice-card {
            border-color: #FED7AA;
            background: #FFFBEB;
        }

        .timeline-step {
            background: #2563EB;
            color: #FFFFFF;
        }

        .mini-pill {
            color: #475569;
        }

        .stTabs [data-baseweb="tab"] {
            color: #475569;
            background: #FFFFFF;
            border-color: var(--border);
        }

        .stTabs [aria-selected="true"] {
            color: #FFFFFF;
            background: #2563EB;
            border-color: #2563EB;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stSlider,
        div[data-testid="stFileUploader"] section {
            background: #FFFFFF;
            color: #0F172A;
            border-color: var(--border);
        }

        .input-card .stTextInput input {
            color: #0F172A;
        }

        .input-card .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        .stTextInput input::placeholder {
            color: #94A3B8;
        }

        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 10px;
            border-color: #2563EB;
            background: #2563EB;
            color: #FFFFFF;
            box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            border-color: #1D4ED8;
            background: #1D4ED8;
            color: #FFFFFF;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--panel-shadow-soft);
        }

        div[data-testid="stAlert"] {
            border-radius: 10px;
            box-shadow: var(--panel-shadow-soft);
        }

        [data-testid="stExpander"] {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: var(--panel-shadow-soft);
        }

        /* Reference-match layer: clean light app, compact mono labels, and action cards. */
        :root {
            --background: #F4F6F8;
            --surface: #FFFFFF;
            --surface-soft: #F7F8FA;
            --ink: #111827;
            --ink-soft: #2F3441;
            --muted: #6B7280;
            --line: #DCE1EA;
            --blue: #0B57D0;
            --blue-soft: #EAF1FF;
            --green: #007A55;
            --green-soft: #EAF8F2;
            --purple: #6D28D9;
            --purple-soft: #F1E8FF;
            --navy: #18233A;
            --danger: #EF4444;
            --text: var(--ink);
            --border: var(--line);
            --card: var(--surface);
            --primary: var(--blue);
            --primary-hover: #0848B2;
            --panel-shadow: 0 16px 34px rgba(15, 23, 42, 0.08);
            --panel-shadow-soft: 0 8px 20px rgba(15, 23, 42, 0.05);
            --panel-shadow-strong: 0 18px 38px rgba(15, 23, 42, 0.12);
        }

        html, body, .stApp, [class*="css"] {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .stApp {
            background: #F4F6F8;
            color: var(--ink);
        }

        header[data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }

        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        div[data-testid="stDeployButton"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
        }

        div[data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
        }

        div[data-testid="stAppViewBlockContainer"] {
            padding-top: 0 !important;
        }

        .block-container {
            max-width: 1180px;
            padding: 0 1.5rem 2rem;
        }

        section[data-testid="stSidebar"] {
            background: #EEF1F5;
            border-right: 1px solid #D7DCE5;
            width: 278px !important;
            min-width: 278px !important;
        }

        section[data-testid="stSidebar"] > div {
            background: #EEF1F5;
            padding: 0.9rem 1rem 1rem;
            min-height: 100vh;
        }

        .sidebar-brand {
            min-height: 98px;
            border: 0;
            border-radius: 18px;
            padding: 0.95rem;
            background: #1B2941;
            box-shadow: 0 14px 28px rgba(21, 32, 51, 0.24);
        }

        .sidebar-brand::before {
            content: "";
            width: 38px;
            height: 38px;
            border-radius: 11px;
            display: grid;
            place-items: center;
            margin-bottom: 0.7rem;
            background: #0B57D0;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z'/%3E%3Cpath d='m9 12 2 2 4-4'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: center;
            background-size: 22px 22px;
        }

        .sidebar-brand h2 {
            color: #FFFFFF;
            font-size: 0.96rem;
            line-height: 1.15;
            margin: 0;
            font-weight: 900;
        }

        .sidebar-brand p {
            color: #D8E1F0;
            margin: 0.15rem 0 0;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .sidebar-brand .status-line {
            display: none;
        }

        div[role="radiogroup"] {
            gap: 0.45rem;
            margin-top: 1.35rem;
        }

        div[role="radiogroup"] label {
            min-height: 3.05rem;
            padding: 0.58rem 0.8rem;
            border-radius: 18px;
            background: transparent;
            border: 0;
            box-shadow: none;
        }

        div[role="radiogroup"] label:hover {
            background: #F8FAFC;
            border: 0;
            box-shadow: none;
        }

        div[role="radiogroup"] label p {
            color: #3C4352 !important;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
        }

        div[role="radiogroup"] label::before {
            content: "";
            width: 2rem;
            height: 2rem;
            display: grid;
            place-items: center;
            border-radius: 11px;
            border: 0;
            background-color: #3D4656;
            box-shadow: none;
            font-size: 0;
            -webkit-mask-repeat: no-repeat;
            mask-repeat: no-repeat;
            -webkit-mask-position: center;
            mask-position: center;
            -webkit-mask-size: 18px 18px;
            mask-size: 18px 18px;
        }

        div[role="radiogroup"] label:has(input:checked) {
            background: #0B57D0;
            border: 0;
            box-shadow: 0 12px 22px rgba(11, 87, 208, 0.22);
        }

        div[role="radiogroup"] label:has(input:checked) p,
        div[role="radiogroup"] label:has(input:checked) span {
            color: #FFFFFF !important;
        }

        div[role="radiogroup"] label:has(input:checked)::before {
            background-color: #FFFFFF;
            box-shadow: 0 0 0 10px rgba(255, 255, 255, 0.13);
        }

        .sidebar-bottom {
            border-top: 0;
            margin-top: 2rem;
            padding: 0;
            gap: 0.9rem;
        }

        .sidebar-group-label {
            margin: 2.4rem 0 0.75rem 0.9rem;
            color: #777D8E;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.22em;
        }

        .sidebar-group-label.admin {
            margin-top: 2.2rem;
        }

        .sidebar-bottom div {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.82rem;
            color: #1F2937;
            font-weight: 700;
        }

        .sidebar-chip {
            border: 1px solid #D7DDE8;
            border-radius: 20px;
            padding: 0.85rem;
            background: #FFFFFF;
        }

        .workspace-card {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 1.35rem 0 0.9rem;
            border: 1px solid #CAD2E0;
            border-radius: 22px;
            padding: 0.85rem;
            background: #F8FAFC;
        }

        .workspace-card small {
            display: block;
            color: #777D8E;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.72rem;
            font-weight: 900;
            letter-spacing: 0.08em;
        }

        .workspace-card strong {
            color: #111827;
            font-size: 0.86rem;
        }

        .workspace-avatar {
            width: 34px;
            height: 34px;
            display: grid;
            place-items: center;
            border-radius: 999px;
            background: #BFF3D7;
            color: transparent;
            font-size: 0;
            position: relative;
        }

        .workspace-avatar::before {
            content: "";
            width: 18px;
            height: 18px;
            background: #007A55;
            -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3C/svg%3E") center / contain no-repeat;
            mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3C/svg%3E") center / contain no-repeat;
        }

        .sidebar-ready-card {
            display: grid;
            gap: 0.45rem;
            border-radius: 18px;
            padding: 0.9rem;
            background: #E4E8ED;
        }

        .sidebar-ready-card span::before {
            content: "";
            width: 0.42rem;
            height: 0.42rem;
            display: inline-block;
            border-radius: 999px;
            margin-right: 0.45rem;
            background: #46916F;
        }

        .top-shell {
            min-height: 74px;
            display: grid;
            grid-template-columns: minmax(220px, 1fr) auto auto auto;
            gap: 1.1rem;
            align-items: center;
            margin: 0 -1.5rem 1.4rem;
            padding: 0.7rem 1.5rem;
            border-bottom: 1px solid #DCE1EA;
            background: #FFFFFF;
        }

        .top-brand {
            display: flex;
            align-items: center;
            gap: 0.95rem;
        }

        .top-logo {
            width: 54px;
            height: 54px;
            border-radius: 15px;
            display: grid;
            place-items: center;
            background:
                linear-gradient(135deg, rgba(37, 99, 235, 0.14), rgba(45, 212, 191, 0.12)),
                #EEF4FF;
            color: #0B57D0;
            font-weight: 900;
            box-shadow: 0 12px 24px rgba(11, 87, 208, 0.12);
        }

        .top-logo svg {
            width: 1.9rem;
            height: 1.9rem;
            stroke-width: 2.35;
        }

        .top-brand strong {
            display: block;
            color: #111827;
            font-size: 1.18rem;
            line-height: 1.1;
            font-weight: 900;
        }

        .top-brand span {
            display: block;
            margin-top: 0.28rem;
            color: #667085;
            font-size: 0.78rem;
            font-weight: 750;
            text-transform: none;
        }

        .top-pill {
            min-height: 2.55rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            border-radius: 999px;
            padding: 0 1.25rem;
            background: #ECEEF1;
            color: #374151;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-weight: 800;
            font-size: 0.95rem;
        }

        .top-pill.available {
            min-width: 220px;
            background: #CFF7E6;
            color: #006B4A;
        }

        .top-icons {
            color: #4B5563;
            font-size: 1.2rem;
            letter-spacing: 0.5rem;
            white-space: nowrap;
        }

        .home-hero,
        .dashboard-header,
        .home-section,
        .data-card,
        .analysis-result,
        .side-card,
        .insight-card,
        .kpi-card,
        .feature-card,
        .timeline-card,
        .recent-card,
        .model-info-card,
        .notice-card,
        div[data-testid="stMetric"],
        [data-testid="stExpander"] {
            border: 1px solid #DCE1EA;
            border-radius: 22px;
            background: #FFFFFF;
            box-shadow: none;
        }

        .home-hero {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 380px;
            gap: 2rem;
            align-items: center;
            min-height: 260px;
            padding: 3.1rem 4rem;
            margin-bottom: 1.4rem;
        }

        .home-hero .eyebrow {
            display: inline-flex;
            width: fit-content;
            border-radius: 999px;
            padding: 0.45rem 0.95rem;
            background: #EAF1FF;
            color: #0B57D0;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.86rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }

        .home-hero h1,
        .dashboard-header h1 {
            color: #111827;
            font-size: 1rem;
            font-weight: 850;
            margin: 1.1rem 0 0.8rem;
        }

        .home-hero p,
        .lead {
            color: #252A36;
            font-size: 1rem;
            line-height: 1.5;
            max-width: 520px;
        }

        .hero-status-card {
            border: 1px solid #D5F0E4;
            border-radius: 22px;
            padding: 1.45rem;
            background: #F4FCF8;
        }

        .hero-status-card strong {
            color: #007A55;
            font-weight: 900;
        }

        .hero-status-card p {
            color: #4D866F;
            margin: 1rem 0;
        }

        .status-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
        }

        .status-badges span {
            border-radius: 6px;
            padding: 0.35rem 0.55rem;
            background: #BFF3D7;
            color: #007A55;
            font-size: 0.65rem;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-weight: 900;
            text-transform: uppercase;
        }

        .action-card {
            min-height: 255px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border: 1px solid #DCE1EA;
            border-top: 4px solid var(--card-accent, #0B57D0);
            border-radius: 22px;
            padding: 1.55rem 1.45rem;
            background: #FFFFFF;
        }

        .action-icon {
            width: 44px;
            height: 44px;
            display: grid;
            place-items: center;
            border-radius: 999px;
            color: var(--card-accent, #0B57D0);
            background: var(--card-soft, #EAF1FF);
        }

        .action-card strong {
            display: block;
            margin: 1.35rem 0 0.65rem;
            color: #111827;
            font-weight: 850;
        }

        .action-card p {
            min-height: 4.5rem;
            margin: 0;
            color: #303643;
            line-height: 1.45;
        }

        .home-section {
            padding: 1.35rem 1.45rem;
            margin: 1.35rem 0;
        }

        .workflow-title-row,
        .recent-title-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .workflow-title-row strong,
        .recent-title-row strong {
            color: #111827;
            font-weight: 850;
        }

        .workflow-title-row span,
        .recent-title-row span {
            color: #777D8E;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-weight: 800;
        }

        .timeline-card {
            min-height: 170px;
            border-radius: 18px;
            background: #FAFAFB;
            padding: 1.35rem;
        }

        .timeline-step {
            width: 30px;
            height: 30px;
            color: var(--step-color, #0B57D0);
            background: var(--step-bg, #EAF1FF);
        }

        .timeline-card strong {
            font-size: 1rem;
            color: #111827;
        }

        .timeline-card p {
            color: #333946;
        }

        .recent-table {
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
            border-radius: 0 0 18px 18px;
            font-size: 0.95rem;
        }

        .recent-table th {
            padding: 1.1rem 1.45rem;
            background: #F5F6F8;
            color: #3F4655;
            text-align: left;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.78rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
        }

        .recent-table td {
            padding: 1.15rem 1.45rem;
            border-top: 1px solid #DCE1EA;
            color: #111827;
        }

        .result-pill {
            border-radius: 999px;
            padding: 0.35rem 0.65rem;
            font-size: 0.72rem;
            font-weight: 900;
        }

        .result-pill.fake { background: #FFE8EA; color: #D21F3C; }
        .result-pill.real { background: #E5FAEF; color: #007A55; }
        .result-pill.review { background: #F1E8FF; color: #6D28D9; }

        .confidence-bar {
            width: 120px;
            height: 6px;
            display: inline-block;
            border-radius: 99px;
            background: #DDE3EA;
            vertical-align: middle;
            overflow: hidden;
            margin-left: 0.75rem;
        }

        .confidence-bar span {
            height: 100%;
            display: block;
            background: var(--bar-color, #0B57D0);
        }

        .system-note {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.75rem 1rem;
            color: #0B57D0;
            background: #F4F8FF;
            font-weight: 800;
        }

        .floating-plus {
            position: fixed;
            right: 1.45rem;
            bottom: 1.35rem;
            width: 56px;
            height: 56px;
            display: grid;
            place-items: center;
            border-radius: 999px;
            background: #0B57D0;
            color: #FFFFFF;
            font-size: 2rem;
            line-height: 1;
            box-shadow: 0 18px 32px rgba(11, 87, 208, 0.28);
            z-index: 99;
        }

        .dashboard-header {
            padding: 1.45rem;
            margin-bottom: 1.25rem;
        }

        .header-status {
            color: #007A55;
            background: #EAF8F2;
            border-color: #BFEBD8;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-weight: 800;
        }

        .section-heading strong,
        .kpi-value,
        .feature-card strong,
        .model-info-card strong,
        .notice-card strong,
        .recent-card strong,
        .insight-card strong,
        .side-card h3,
        .result-grid strong {
            color: #111827;
        }

        .section-heading {
            display: flex;
        }

        .kpi-card {
            display: flex;
        }

        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            min-height: 3rem;
            border-radius: 8px;
            border: 0;
            background: #0B57D0;
            color: #FFFFFF;
            font-weight: 900;
            box-shadow: none;
        }

        div[data-testid="column"]:has(.action-card[style*="#007A55"]) .stButton > button {
            background: #007A55;
        }

        div[data-testid="column"]:has(.action-card[style*="#6D28D9"]) .stButton > button {
            background: #6D28D9;
        }

        div[data-testid="column"]:has(.action-card[style*="#1B2941"]) .stButton > button {
            background: #1B2941;
        }

        /* Organization and motion polish */
        @keyframes fadeSlideUp {
            from {
                opacity: 0;
                transform: translateY(18px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes softPulse {
            0%, 100% {
                box-shadow: 0 0 0 0 rgba(0, 122, 85, 0.18);
            }
            50% {
                box-shadow: 0 0 0 8px rgba(0, 122, 85, 0);
            }
        }

        @keyframes floatInPlace {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-4px);
            }
        }

        .block-container > div {
            animation: fadeSlideUp 520ms ease both;
        }

        .top-shell {
            position: sticky;
            top: 0;
            z-index: 50;
            animation: fadeSlideUp 420ms ease both;
        }

        .sidebar-brand,
        div[role="radiogroup"] label,
        .workspace-card,
        .sidebar-ready-card,
        .home-hero,
        .home-section,
        .action-card,
        .timeline-card,
        .recent-section,
        .dashboard-header,
        .kpi-card,
        .data-card,
        .analysis-result,
        .side-card,
        .insight-card {
            animation: fadeSlideUp 560ms ease both;
        }

        div[role="radiogroup"] label:nth-child(1) { animation-delay: 40ms; }
        div[role="radiogroup"] label:nth-child(2) { animation-delay: 70ms; }
        div[role="radiogroup"] label:nth-child(3) { animation-delay: 100ms; }
        div[role="radiogroup"] label:nth-child(4) { animation-delay: 130ms; }
        div[role="radiogroup"] label:nth-child(5) { animation-delay: 160ms; }
        div[role="radiogroup"] label:nth-child(6) { animation-delay: 190ms; }
        div[role="radiogroup"] label:nth-child(7) { animation-delay: 220ms; }
        div[role="radiogroup"] label:nth-child(8) { animation-delay: 250ms; }
        div[role="radiogroup"] label:nth-child(9) { animation-delay: 280ms; }

        div[data-testid="column"]:nth-of-type(1) .action-card { animation-delay: 80ms; }
        div[data-testid="column"]:nth-of-type(2) .action-card { animation-delay: 140ms; }
        div[data-testid="column"]:nth-of-type(3) .action-card { animation-delay: 200ms; }
        div[data-testid="column"]:nth-of-type(4) .action-card { animation-delay: 260ms; }

        div[role="radiogroup"] label:nth-child(1)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 11 9-8 9 8'/%3E%3Cpath d='M5 10v10h14V10'/%3E%3Cpath d='M9 20v-6h6v6'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 11 9-8 9 8'/%3E%3Cpath d='M5 10v10h14V10'/%3E%3Cpath d='M9 20v-6h6v6'/%3E%3C/svg%3E");
        }
        div[role="radiogroup"] label:nth-child(2)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z'/%3E%3Cpath d='M14 2v6h6'/%3E%3Cpath d='M8 13h8'/%3E%3Cpath d='M8 17h5'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z'/%3E%3Cpath d='M14 2v6h6'/%3E%3Cpath d='M8 13h8'/%3E%3Cpath d='M8 17h5'/%3E%3C/svg%3E");
        }
        div[role="radiogroup"] label:nth-child(3)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='18' height='18' rx='2'/%3E%3Ccircle cx='9' cy='9' r='2'/%3E%3Cpath d='m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='18' height='18' rx='2'/%3E%3Ccircle cx='9' cy='9' r='2'/%3E%3Cpath d='m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21'/%3E%3C/svg%3E");
        }
        div[role="radiogroup"] label:nth-child(4)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1'/%3E%3Cpath d='M14 11a5 5 0 0 0-7.1 0l-2 2a5 5 0 0 0 7.1 7.1l1.1-1.1'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1'/%3E%3Cpath d='M14 11a5 5 0 0 0-7.1 0l-2 2a5 5 0 0 0 7.1 7.1l1.1-1.1'/%3E%3C/svg%3E");
        }
        div[role="radiogroup"] label:nth-child(5)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7l-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2Z'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7l-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2Z'/%3E%3C/svg%3E");
        }
        div[role="radiogroup"] label:nth-child(6)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 3v18h18'/%3E%3Cpath d='m19 9-5 5-4-4-3 3'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 3v18h18'/%3E%3Cpath d='m19 9-5 5-4-4-3 3'/%3E%3C/svg%3E");
        }
        div[role="radiogroup"] label:nth-child(7)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cellipse cx='12' cy='5' rx='9' ry='3'/%3E%3Cpath d='M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5'/%3E%3Cpath d='M3 12c0 1.7 4 3 9 3s9-1.3 9-3'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cellipse cx='12' cy='5' rx='9' ry='3'/%3E%3Cpath d='M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5'/%3E%3Cpath d='M3 12c0 1.7 4 3 9 3s9-1.3 9-3'/%3E%3C/svg%3E");
        }
        div[role="radiogroup"] label:nth-child(8)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 3v5h5'/%3E%3Cpath d='M3.05 13A9 9 0 1 0 6 5.3L3 8'/%3E%3Cpath d='M12 7v5l4 2'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 3v5h5'/%3E%3Cpath d='M3.05 13A9 9 0 1 0 6 5.3L3 8'/%3E%3Cpath d='M12 7v5l4 2'/%3E%3C/svg%3E");
        }
        div[role="radiogroup"] label:nth-child(9)::before {
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 15.5A3.5 3.5 0 1 0 12 8a3.5 3.5 0 0 0 0 7.5Z'/%3E%3Cpath d='M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 13h-.1a2 2 0 1 1 0-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1A2 2 0 1 1 7 3.2l.1.1a1.7 1.7 0 0 0 1.9.3h.1a1.7 1.7 0 0 0 1-1.6V2a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.6h.1a1.7 1.7 0 0 0 1.9-.3l.1-.1A2 2 0 1 1 20 6.1l-.1.1a1.7 1.7 0 0 0-.3 1.9v.1a1.7 1.7 0 0 0 1.6 1h.1a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.6 1Z'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 15.5A3.5 3.5 0 1 0 12 8a3.5 3.5 0 0 0 0 7.5Z'/%3E%3Cpath d='M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 13h-.1a2 2 0 1 1 0-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1A2 2 0 1 1 7 3.2l.1.1a1.7 1.7 0 0 0 1.9.3h.1a1.7 1.7 0 0 0 1-1.6V2a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.6h.1a1.7 1.7 0 0 0 1.9-.3l.1-.1A2 2 0 1 1 20 6.1l-.1.1a1.7 1.7 0 0 0-.3 1.9v.1a1.7 1.7 0 0 0 1.6 1h.1a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.6 1Z'/%3E%3C/svg%3E");
        }

        div[role="radiogroup"] label:nth-child(6) {
            margin-top: 2.3rem;
            position: relative;
        }

        div[role="radiogroup"] label:nth-child(6)::after {
            content: "ADMIN / REPORTS";
            position: absolute;
            left: 0.95rem;
            top: -1.8rem;
            color: #111827;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.22em;
        }

        div[role="radiogroup"] label {
            display: grid !important;
            grid-template-columns: 2rem minmax(0, 1fr);
            align-items: center;
            column-gap: 0.65rem;
        }

        div[role="radiogroup"] label::before {
            justify-self: center;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
            font-size: 0.95rem;
            line-height: 1;
        }

        div[role="radiogroup"] label p {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .status-dot,
        .workspace-avatar,
        .hero-status-card strong::before,
        .sidebar-ready-card span::before {
            animation: softPulse 2200ms ease-in-out infinite;
        }

        .sidebar-brand::before,
        .top-logo,
        .action-icon,
        .section-heading > span,
        .kpi-icon,
        .timeline-step,
        .heading-icon {
            display: grid;
            place-items: center;
            flex: 0 0 auto;
        }

        .top-shell {
            backdrop-filter: blur(16px);
            box-shadow: 0 1px 0 rgba(220, 225, 234, 0.9);
        }

        .home-hero {
            align-items: center;
            row-gap: 1.25rem;
        }

        .hero-status-card {
            transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
        }

        .hero-status-card:hover {
            transform: translateY(-3px);
            border-color: #AFE3CE;
            box-shadow: 0 16px 30px rgba(0, 122, 85, 0.10);
        }

        .stHorizontalBlock {
            gap: 1rem;
        }

        div[data-testid="column"]:has(.action-card) {
            display: flex;
            flex-direction: column;
        }

        .action-card {
            min-height: 248px;
            margin-bottom: 0;
            transition: transform 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
        }

        .action-card:hover {
            transform: translateY(-6px);
            border-color: var(--card-accent, #0B57D0);
            box-shadow: 0 18px 34px rgba(15, 23, 42, 0.10);
        }

        .action-card:hover .action-icon {
            animation: floatInPlace 1300ms ease-in-out infinite;
        }

        div[data-testid="column"]:has(.action-card) .stButton {
            margin-top: 0;
        }

        div[data-testid="column"]:has(.action-card) .stButton > button {
            border-radius: 0 0 14px 14px;
            margin-top: -1px;
            min-height: 3.35rem;
            transition: transform 180ms ease, filter 180ms ease, box-shadow 180ms ease;
        }

        div[data-testid="column"]:has(.action-card) .stButton > button:hover {
            transform: translateY(-2px);
            filter: brightness(1.04);
            box-shadow: 0 12px 24px rgba(11, 87, 208, 0.16);
        }

        .home-section {
            padding: 1.55rem;
        }

        .workflow-title-row,
        .recent-title-row {
            gap: 1rem;
        }

        .timeline-card {
            min-height: 176px;
            transition: transform 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
        }

        .timeline-card:hover {
            transform: translateY(-4px);
            border-color: #C8D2E1;
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
        }

        .timeline-card:hover .timeline-step {
            animation: floatInPlace 1300ms ease-in-out infinite;
        }

        .recent-table tr {
            transition: background 160ms ease;
        }

        .recent-table tbody tr:hover {
            background: #F8FBFF;
        }

        .confidence-bar span {
            animation: fadeSlideUp 700ms ease both;
        }

        .floating-plus {
            transition: transform 200ms ease, box-shadow 200ms ease;
            animation: floatInPlace 2400ms ease-in-out infinite;
        }

        .floating-plus:hover {
            transform: translateY(-4px) scale(1.04);
            box-shadow: 0 22px 38px rgba(11, 87, 208, 0.34);
        }

        .dashboard-header,
        .data-card,
        .analysis-result,
        .side-card,
        .insight-card,
        .kpi-card {
            transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
        }

        .dashboard-header:hover,
        .data-card:hover,
        .analysis-result:hover,
        .side-card:hover,
        .insight-card:hover,
        .kpi-card:hover {
            transform: translateY(-3px);
            border-color: #C8D2E1;
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
        }

        /* Friendlier dashboard organization */
        .home-hero {
            grid-template-columns: minmax(0, 1.08fr) minmax(300px, 0.72fr);
            min-height: 250px;
            padding: clamp(2rem, 4vw, 3.4rem);
            gap: clamp(1.5rem, 3vw, 3rem);
        }

        .home-hero h1 {
            font-size: clamp(1.55rem, 2.2vw, 2.35rem);
            line-height: 1.12;
            max-width: 560px;
            margin: 1.1rem 0 1rem;
        }

        .home-hero p {
            max-width: 620px;
            color: #3F4654;
            font-size: 1.02rem;
        }

        .hero-mini-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 1.35rem;
        }

        .hero-mini-grid span {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border: 1px solid #DDE5F2;
            border-radius: 999px;
            padding: 0.5rem 0.75rem;
            background: #F8FAFF;
            color: #334155;
            font-weight: 800;
            font-size: 0.82rem;
        }

        .hero-mini-grid svg {
            width: 1rem;
            height: 1rem;
            color: #0B57D0;
        }

        .hero-status-card {
            align-self: stretch;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background:
                linear-gradient(135deg, #F4FCF8 0%, #FFFFFF 72%);
        }

        .hero-status-card strong {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            color: #006B4A;
            font-size: 1rem;
        }

        .hero-status-card strong svg {
            width: 1.25rem;
            height: 1.25rem;
        }

        .friendly-section-header {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin: 2rem 0 0.85rem;
        }

        .friendly-section-header > span {
            width: 3rem;
            height: 3rem;
            display: grid;
            place-items: center;
            border-radius: 14px;
            color: #0B57D0;
            background: #EAF1FF;
            flex: 0 0 auto;
        }

        .friendly-section-header svg {
            width: 1.35rem;
            height: 1.35rem;
        }

        .friendly-section-header strong {
            display: block;
            color: #111827;
            font-size: 1.35rem;
            line-height: 1.15;
        }

        .friendly-section-header p {
            margin: 0.25rem 0 0;
            color: #6B7280;
            font-size: 0.98rem;
        }

        .friendly-kpi {
            min-height: 142px;
            padding: 1.15rem;
            border-radius: 18px;
            display: grid;
            grid-template-columns: minmax(0, 1fr) 3rem;
            gap: 0.85rem;
            align-items: start;
        }

        .friendly-kpi .kpi-icon {
            position: static;
            grid-column: 2;
            grid-row: 1 / span 2;
            width: 3rem;
            height: 3rem;
            border-radius: 14px;
            color: #0B57D0;
            background: #EAF1FF;
            box-shadow: none;
        }

        .friendly-kpi .kpi-label {
            min-height: auto;
            margin: 0;
            grid-column: 1;
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.35;
            text-transform: none !important;
            letter-spacing: 0 !important;
        }

        .friendly-kpi .kpi-value {
            grid-column: 1;
            margin-top: 0.35rem;
            font-size: clamp(1.7rem, 2.6vw, 2.25rem);
            line-height: 0.95;
            letter-spacing: 0;
            overflow-wrap: anywhere;
        }

        .friendly-kpi .kpi-caption {
            grid-column: 1 / -1;
            margin: 0.1rem 0 0;
            color: #64748B;
            font-size: 0.9rem;
        }

        .action-card {
            min-height: 188px;
            border-top: 0;
            border-radius: 20px 20px 0 0;
            padding: 1.15rem 1.3rem 1rem;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,1)),
                var(--card-soft, #EAF1FF);
        }

        .action-icon {
            width: 2.8rem;
            height: 2.8rem;
            border-radius: 13px;
        }

        .action-icon svg {
            width: 1.3rem;
            height: 1.3rem;
        }

        .action-card strong {
            font-size: 1.05rem;
            margin: 0.9rem 0 0.45rem;
        }

        .action-card p {
            min-height: 3.45rem;
            color: #5B6473;
        }

        .action-hint {
            display: inline-flex;
            width: fit-content;
            margin-top: 1rem;
            border-radius: 999px;
            padding: 0.35rem 0.65rem;
            background: var(--card-soft, #EAF1FF);
            color: var(--card-accent, #0B57D0);
            font-size: 0.72rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        div[data-testid="column"]:has(.action-card) .stButton > button {
            border-radius: 0 0 20px 20px;
        }

        .workflow-title-row strong,
        .recent-title-row strong {
            font-size: 1.15rem;
        }

        /* Home page spacing rhythm */
        .home-hero {
            margin-bottom: 1.4rem;
        }

        .home-actions-gap {
            height: 1.55rem;
        }

        .friendly-section-header {
            margin: 2.35rem 0 1.05rem;
        }

        .friendly-section-header + div[data-testid="stHorizontalBlock"] {
            margin-bottom: 2.2rem;
        }

        div[data-testid="column"]:has(.friendly-kpi) {
            padding-bottom: 0.2rem;
        }

        .friendly-kpi {
            min-height: 150px;
        }

        div[data-testid="column"]:has(.action-card) {
            gap: 0;
            padding-bottom: 0.35rem;
            display: flex !important;
            flex-direction: column !important;
            align-self: stretch !important;
            height: 100% !important;
        }

        div[data-testid="column"]:has(.action-card) > div,
        div[data-testid="column"]:has(.action-card) div[data-testid="stVerticalBlock"] {
            display: flex !important;
            flex-direction: column !important;
            height: 100% !important;
        }

        .action-card {
            height: 176px !important;
            min-height: 176px !important;
            max-height: 176px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            overflow: hidden !important;
            border-radius: 20px !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.action-card),
        div[data-testid="stMarkdown"]:has(.action-card) {
            height: auto !important;
            min-height: 176px !important;
            max-height: none !important;
            overflow: visible !important;
            margin-bottom: 26px !important;
        }

        .action-hint {
            margin-top: 1.2rem;
        }

        .action-card p {
            min-height: 2.7rem !important;
            max-height: 3.1rem !important;
            margin-bottom: 0 !important;
            overflow: hidden !important;
        }

        .review-action-spacer {
            height: 6px !important;
            min-height: 6px !important;
            display: block !important;
            flex: 0 0 6px !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.action-card) {
            align-items: stretch !important;
            margin-bottom: 4rem !important;
        }

        div[data-testid="column"]:has(.action-card) .stButton,
        div[data-testid="column"]:has(.action-card) div[data-testid="stButton"] {
            margin-top: 0 !important;
            flex: 0 0 auto !important;
            clear: both !important;
        }

        div[data-testid="column"]:has(.action-card) .stButton > button,
        div[data-testid="column"]:has(.action-card) div[data-testid="stButton"] > button {
            width: 100% !important;
            min-height: 3.05rem !important;
            margin-top: 0 !important;
            border-radius: 16px !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.friendly-kpi) {
            margin-bottom: 2.6rem;
        }

        .home-section {
            margin: 3rem 0 2.2rem;
            padding: 1.7rem;
        }

        .workflow-title-row,
        .recent-title-row {
            margin-bottom: 1.25rem;
        }

        .timeline-card {
            min-height: 185px;
        }

        div[data-testid="stHorizontalBlock"]:has(.timeline-card) {
            margin-bottom: 2.2rem;
        }

        div[data-testid="stHorizontalBlock"]:has(.model-info-card),
        div[data-testid="stHorizontalBlock"]:has(.recent-card),
        div[data-testid="stHorizontalBlock"]:has(.data-card) {
            margin-top: 2.1rem;
            margin-bottom: 2.2rem;
            align-items: flex-start;
        }

        .model-info-card,
        .notice-card,
        .recent-card,
        .data-card {
            margin-bottom: 1.35rem;
        }

        .notice-card {
            margin-top: 2rem;
        }

        .recent-section {
            margin-top: 3rem;
        }

        /* Final homepage polish layer */
        @keyframes homeFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }

        @keyframes homeFadeRise {
            from { opacity: 0; transform: translateY(14px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes statusGlow {
            0%, 100% { box-shadow: 0 0 0 0 rgba(0, 122, 85, 0.18); }
            50% { box-shadow: 0 0 0 8px rgba(0, 122, 85, 0); }
        }

        .home-hero {
            position: relative;
            grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.75fr) !important;
            gap: clamp(1.8rem, 3vw, 3rem) !important;
            align-items: center !important;
            min-height: 0 !important;
            margin: 1.35rem 0 1.6rem !important;
            padding: clamp(2rem, 4vw, 3.3rem) !important;
            border-color: #D8E0EC !important;
            border-radius: 26px !important;
            background:
                linear-gradient(135deg, rgba(234, 241, 255, 0.9), rgba(255,255,255,0.96) 38%, rgba(244,252,248,0.92)) !important;
            overflow: hidden !important;
            animation: homeFadeRise 520ms ease both !important;
        }

        .home-hero::after {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(90deg, transparent, rgba(255,255,255,0.42), transparent);
            transform: translateX(-120%);
            animation: heroSweep 5200ms ease-in-out infinite;
        }

        @keyframes heroSweep {
            0%, 58% { transform: translateX(-120%); }
            100% { transform: translateX(120%); }
        }

        .home-hero > * {
            position: relative;
            z-index: 1;
        }

        .home-hero .eyebrow {
            padding: 0.5rem 0.95rem !important;
            border: 1px solid #D8E6FF !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.75);
        }

        .home-hero h1 {
            max-width: 680px !important;
            margin: 1.25rem 0 1rem !important;
            color: #0F172A !important;
            font-size: clamp(2rem, 4.2vw, 3.45rem) !important;
            line-height: 1.05 !important;
            letter-spacing: 0 !important;
        }

        .home-hero p {
            max-width: 720px !important;
            color: #4B5563 !important;
            font-size: clamp(1rem, 1.5vw, 1.12rem) !important;
            line-height: 1.65 !important;
        }

        .hero-mini-grid {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 0.7rem !important;
            margin-top: 1.35rem !important;
        }

        .hero-mini-grid span {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            min-height: 2.55rem !important;
            padding: 0.45rem 0.85rem !important;
            border: 1px solid #DCE5F3 !important;
            border-radius: 999px !important;
            background: rgba(255,255,255,0.78) !important;
            color: #334155 !important;
            font-weight: 850 !important;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
        }

        .hero-mini-grid svg {
            width: 1.05rem !important;
            height: 1.05rem !important;
            color: #0B57D0 !important;
        }

        .hero-status-card {
            min-height: 0 !important;
            padding: 1.55rem !important;
            border-radius: 24px !important;
            background: rgba(244, 252, 248, 0.88) !important;
            box-shadow: 0 18px 40px rgba(0, 122, 85, 0.08) !important;
        }

        .hero-status-top {
            display: flex !important;
            align-items: center !important;
            gap: 0.75rem !important;
            color: #007A55 !important;
        }

        .hero-status-top > span {
            width: 2.55rem !important;
            height: 2.55rem !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 14px !important;
            background: #DDF8EA !important;
            animation: statusGlow 2300ms ease-in-out infinite;
        }

        .hero-status-top svg {
            width: 1.25rem !important;
            height: 1.25rem !important;
        }

        .hero-status-card strong {
            font-size: 1.1rem !important;
        }

        .hero-check-list {
            display: grid !important;
            gap: 0.55rem !important;
            margin: 1rem 0 1.1rem !important;
        }

        .hero-check-list span {
            display: flex !important;
            align-items: center !important;
            gap: 0.55rem !important;
            color: #245A45 !important;
            font-size: 0.92rem !important;
            font-weight: 800 !important;
        }

        .hero-check-list svg {
            width: 1rem !important;
            height: 1rem !important;
            color: #007A55 !important;
        }

        .status-badges {
            gap: 0.6rem !important;
        }

        .status-badges span {
            border-radius: 999px !important;
            padding: 0.45rem 0.7rem !important;
            background: #BFF3D7 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.home-hero) {
            margin-bottom: 1.2rem !important;
        }

        .home-actions-gap {
            height: 1.8rem !important;
        }

        .friendly-section-header {
            margin: 2.6rem 0 1.15rem !important;
            gap: 1rem !important;
        }

        .friendly-section-header > span {
            width: 3.25rem !important;
            height: 3.25rem !important;
            border-radius: 18px !important;
            box-shadow: 0 10px 24px rgba(11, 87, 208, 0.08);
        }

        .friendly-section-header strong {
            font-size: 1.45rem !important;
            letter-spacing: 0 !important;
        }

        .friendly-section-header p {
            max-width: 760px !important;
            line-height: 1.45 !important;
        }

        .friendly-kpi {
            min-height: 160px !important;
            border-radius: 20px !important;
            padding: 1.25rem !important;
            transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease !important;
        }

        .friendly-kpi:hover {
            transform: translateY(-4px) !important;
            border-color: #BFD0EA !important;
            box-shadow: 0 18px 34px rgba(15, 23, 42, 0.08) !important;
        }

        .friendly-kpi .kpi-icon {
            width: 3.2rem !important;
            height: 3.2rem !important;
            border-radius: 16px !important;
        }

        .friendly-kpi .kpi-value {
            font-size: clamp(2rem, 3vw, 2.6rem) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.friendly-kpi) {
            column-gap: clamp(1.35rem, 2vw, 2rem) !important;
            row-gap: 1.35rem !important;
            margin-bottom: 2rem !important;
        }

        div[data-testid="column"]:has(.action-card) {
            padding-bottom: 0 !important;
        }

        .action-card {
            height: 205px !important;
            min-height: 205px !important;
            max-height: 205px !important;
            padding: 1.25rem !important;
            border-radius: 22px !important;
            border: 1px solid #DCE4F0 !important;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,255,255,1)),
                var(--card-soft, #EAF1FF) !important;
            transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease !important;
        }

        .action-card:hover {
            transform: translateY(-5px) !important;
            border-color: color-mix(in srgb, var(--card-accent, #0B57D0) 45%, #DCE4F0) !important;
            box-shadow: 0 18px 34px rgba(15, 23, 42, 0.09) !important;
        }

        .action-card-body {
            min-height: 138px !important;
        }

        .action-icon {
            width: 3.1rem !important;
            height: 3.1rem !important;
            border-radius: 16px !important;
        }

        .action-card strong {
            margin: 0.95rem 0 0.45rem !important;
            font-size: 1.08rem !important;
        }

        .action-card p {
            min-height: 0 !important;
            max-height: none !important;
            color: #5F6B7A !important;
            font-size: 0.96rem !important;
            line-height: 1.42 !important;
        }

        .action-card-foot {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            margin-top: 0.8rem !important;
            padding-top: 0.75rem !important;
            border-top: 1px solid #EEF2F7 !important;
            color: var(--card-accent, #0B57D0) !important;
            font-size: 0.78rem !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
        }

        .action-card-foot svg {
            width: 1rem !important;
            height: 1rem !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.action-card),
        div[data-testid="stMarkdown"]:has(.action-card) {
            margin-bottom: 18px !important;
            overflow: visible !important;
        }

        .review-action-spacer {
            height: 0 !important;
            min-height: 0 !important;
            flex-basis: 0 !important;
        }

        div[data-testid="column"]:has(.action-card) .stButton > button,
        div[data-testid="column"]:has(.action-card) div[data-testid="stButton"] > button {
            min-height: 3.25rem !important;
            border-radius: 16px !important;
            font-weight: 850 !important;
            box-shadow: 0 10px 22px rgba(11, 87, 208, 0.13) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.action-card) {
            margin-bottom: 3.2rem !important;
        }

        .home-section {
            margin: 2.6rem 0 2.3rem !important;
            padding: 1.65rem !important;
            border-radius: 24px !important;
            background: rgba(255,255,255,0.92) !important;
        }

        .workflow-title-row,
        .recent-title-row {
            gap: 1rem !important;
            margin-bottom: 1.35rem !important;
        }

        .timeline-card {
            min-height: 180px !important;
            padding: 1.35rem !important;
            border-radius: 20px !important;
            transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease !important;
        }

        .timeline-card:hover {
            transform: translateY(-4px) !important;
            border-color: #CBD8EA !important;
            box-shadow: 0 16px 30px rgba(15, 23, 42, 0.07) !important;
        }

        .timeline-step {
            width: auto !important;
            min-width: 3.15rem !important;
            height: 2rem !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.35rem !important;
            border-radius: 999px !important;
            margin-bottom: 1rem !important;
            font-weight: 900 !important;
        }

        .timeline-step svg {
            width: 0.95rem !important;
            height: 0.95rem !important;
        }

        .timeline-card strong {
            display: block !important;
            margin-bottom: 0.65rem !important;
        }

        .timeline-card p {
            color: #4B5563 !important;
            line-height: 1.55 !important;
        }

        .recent-section {
            margin-top: 2.6rem !important;
            overflow: hidden !important;
        }

        .recent-table {
            border-collapse: separate !important;
            border-spacing: 0 !important;
        }

        .recent-table thead th {
            background: #F3F6FA !important;
        }

        .recent-table tbody tr {
            transition: background 180ms ease !important;
        }

        .recent-table tbody tr:hover {
            background: #F8FAFF !important;
        }

        /* Review channel function blocks */
        div[data-testid="column"]:has(.action-card),
        div[data-testid="column"]:has(.action-card) > div,
        div[data-testid="column"]:has(.action-card) div[data-testid="stVerticalBlock"],
        div[data-testid="column"]:has(.action-card) div[data-testid="stElementContainer"] {
            height: auto !important;
            min-height: 0 !important;
            align-self: flex-start !important;
        }

        div[data-testid="column"]:has(.action-card) div[data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        .action-card {
            height: 188px !important;
            min-height: 188px !important;
            max-height: 188px !important;
            padding: 1.15rem 1.2rem !important;
            border-radius: 20px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
        }

        .action-card-body {
            min-height: 0 !important;
        }

        .action-icon {
            width: 2.85rem !important;
            height: 2.85rem !important;
            border-radius: 15px !important;
        }

        .action-card strong {
            margin: 0.85rem 0 0.4rem !important;
            font-size: 1.02rem !important;
        }

        .action-card p {
            font-size: 0.91rem !important;
            line-height: 1.42 !important;
        }

        .action-card-foot {
            margin-top: 0.6rem !important;
            padding-top: 0.55rem !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.action-card),
        div[data-testid="stMarkdown"]:has(.action-card) {
            margin-bottom: 12px !important;
            height: auto !important;
            min-height: 0 !important;
        }

        .review-action-spacer {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="column"]:has(.action-card) .stButton,
        div[data-testid="column"]:has(.action-card) div[data-testid="stButton"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        div[data-testid="column"]:has(.action-card) .stButton > button,
        div[data-testid="column"]:has(.action-card) div[data-testid="stButton"] > button {
            min-height: 3rem !important;
            border-radius: 14px !important;
            margin-top: 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.action-card) {
            align-items: flex-start !important;
            margin-bottom: 2.6rem !important;
        }

        /* Business-friendly review channel cards */
        .review-channel-card {
            height: 236px !important;
            min-height: 236px !important;
            max-height: 236px !important;
            padding: 1.15rem 1.2rem !important;
            border-radius: 20px !important;
            border-color: #D8E2F0 !important;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,1)),
                var(--card-soft, #EAF1FF) !important;
        }

        .review-channel-link-card,
        .review-channel-link-card:visited,
        .review-channel-link-card:active,
        .review-channel-link-card:focus {
            color: inherit !important;
            text-decoration: none !important;
            cursor: pointer !important;
        }

        .review-channel-link-card:hover,
        .review-channel-link-card:focus {
            border-color: var(--card-accent, #0B57D0) !important;
            box-shadow: 0 18px 34px rgba(15, 23, 42, 0.09) !important;
            transform: translateY(-3px) !important;
            text-decoration: none !important;
        }

        .review-channel-card .channel-top {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            margin-bottom: 1rem !important;
        }

        .review-channel-card .channel-top > span {
            border-radius: 999px !important;
            padding: 0.3rem 0.55rem !important;
            background: var(--card-soft, #EAF1FF) !important;
            color: var(--card-accent, #0B57D0) !important;
            font-size: 0.68rem !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.03em !important;
            white-space: nowrap !important;
        }

        .review-channel-card .action-icon {
            width: 2.85rem !important;
            height: 2.85rem !important;
            border-radius: 15px !important;
            background: var(--card-soft, #EAF1FF) !important;
            color: var(--card-accent, #0B57D0) !important;
        }

        .channel-title-link {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.45rem !important;
            width: fit-content !important;
            margin: 0 0 0.55rem !important;
            color: #111827 !important;
            font-size: 1.08rem !important;
            font-weight: 900 !important;
            line-height: 1.2 !important;
            text-decoration: none !important;
            transition: color 180ms ease, transform 180ms ease !important;
        }

        .review-channel-link-card:hover .channel-title-link {
            color: var(--card-accent, #0B57D0) !important;
            transform: translateX(2px) !important;
        }

        .review-channel-link-card:hover .channel-title-link svg {
            transform: translateX(3px) !important;
        }

        .channel-title-link svg {
            width: 1rem !important;
            height: 1rem !important;
            color: var(--card-accent, #0B57D0) !important;
            transition: transform 180ms ease !important;
        }

        .channel-title-link:hover {
            color: var(--card-accent, #0B57D0) !important;
            transform: translateX(2px) !important;
        }

        .channel-title-link:hover svg {
            transform: translateX(3px) !important;
        }

        .review-channel-card p {
            min-height: 3.9rem !important;
            margin: 0 0 0.9rem !important;
            color: #5F6B7A !important;
            font-size: 0.92rem !important;
            line-height: 1.4 !important;
        }

        .channel-info-grid {
            display: none !important;
        }

        .channel-click-hint {
            display: inline-flex !important;
            align-items: center !important;
            width: fit-content !important;
            margin-top: auto !important;
            border-radius: 999px !important;
            padding: 0.42rem 0.7rem !important;
            background: var(--card-soft, #EAF1FF) !important;
            color: var(--card-accent, #0B57D0) !important;
            font-size: 0.72rem !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.03em !important;
        }

        .channel-open-button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.45rem !important;
            width: 100% !important;
            min-height: 2.6rem !important;
            margin-top: auto !important;
            border-radius: 13px !important;
            background: var(--card-accent, #0B57D0) !important;
            color: #FFFFFF !important;
            font-size: 0.82rem !important;
            font-weight: 900 !important;
            line-height: 1.1 !important;
            text-align: center !important;
            text-decoration: none !important;
            text-transform: uppercase !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 10px 20px rgba(11, 87, 208, 0.14) !important;
            transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease !important;
            visibility: hidden !important;
        }

        .channel-open-button svg {
            width: 1rem !important;
            height: 1rem !important;
            stroke-width: 2.6 !important;
            flex: 0 0 auto !important;
        }

        .channel-open-button:hover,
        .channel-open-button:focus {
            color: #FFFFFF !important;
            filter: saturate(1.08) brightness(0.97) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 14px 24px rgba(11, 87, 208, 0.20) !important;
            text-decoration: none !important;
        }

        /* Review workflow: system-specific, compact decision path. */
        .home-section:has(.workflow-title-row) {
            margin-top: 1.45rem !important;
            padding: 1.35rem !important;
            border: 1px solid #D8E2F0 !important;
            border-radius: 20px !important;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.94)),
                #F8FAFC !important;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.05) !important;
        }

        .workflow-title-row {
            display: flex !important;
            align-items: flex-start !important;
            justify-content: space-between !important;
            gap: 1.25rem !important;
            margin-bottom: 0.85rem !important;
        }

        .workflow-title-row strong {
            display: block !important;
            color: #111827 !important;
            font-size: 1.2rem !important;
            font-weight: 900 !important;
            line-height: 1.2 !important;
            margin-bottom: 0.25rem !important;
        }

        .workflow-title-row p {
            margin: 0 !important;
            color: #667085 !important;
            font-size: 0.94rem !important;
            line-height: 1.35 !important;
        }

        .workflow-title-row > span {
            flex: 0 0 auto !important;
            max-width: 360px !important;
            border-radius: 999px !important;
            padding: 0.5rem 0.7rem !important;
            background: #EEF4FF !important;
            color: #0B57D0 !important;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            font-size: 0.76rem !important;
            font-weight: 900 !important;
            letter-spacing: 0 !important;
            text-align: center !important;
            white-space: normal !important;
        }

        .workflow-status-strip {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 0.65rem !important;
            margin: 0 0 1rem !important;
        }

        .workflow-status-strip span {
            min-height: 2.45rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 1px solid #E3EAF5 !important;
            border-radius: 12px !important;
            background: #FFFFFF !important;
            color: #4B5563 !important;
            font-size: 0.82rem !important;
            font-weight: 800 !important;
            line-height: 1.25 !important;
            text-align: center !important;
            padding: 0.45rem 0.65rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.timeline-card) {
            gap: 0.9rem !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        .timeline-card {
            min-height: 176px !important;
            height: 176px !important;
            padding: 1rem !important;
            border: 1px solid #E1E8F2 !important;
            border-radius: 16px !important;
            background: #FFFFFF !important;
            box-shadow: none !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
        }

        .timeline-step {
            width: fit-content !important;
            min-width: 4.35rem !important;
            height: 2.75rem !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.5rem !important;
            border-radius: 16px !important;
            margin-bottom: 0.9rem !important;
            color: var(--step-color, #0B57D0) !important;
            background: var(--step-bg, #EAF1FF) !important;
            font-size: 1rem !important;
            font-weight: 900 !important;
            padding: 0 0.85rem !important;
        }

        .timeline-step svg {
            width: 1.35rem !important;
            height: 1.35rem !important;
            stroke-width: 2.65 !important;
        }

        .timeline-card strong {
            display: block !important;
            color: #111827 !important;
            font-size: 1rem !important;
            font-weight: 900 !important;
            line-height: 1.2 !important;
            margin: 0 0 0.4rem !important;
        }

        .timeline-card p {
            color: #5F6B7A !important;
            font-size: 0.88rem !important;
            line-height: 1.35 !important;
            margin: 0 !important;
        }

        .timeline-detail {
            margin-top: auto !important;
            border-top: 1px solid #EEF2F7 !important;
            padding-top: 0.65rem !important;
            color: var(--step-color, #0B57D0) !important;
            font-size: 0.74rem !important;
            font-weight: 900 !important;
            line-height: 1.25 !important;
        }

        div[data-testid="stMarkdownContainer"]:has(.review-channel-card),
        div[data-testid="stMarkdown"]:has(.review-channel-card) {
            margin-bottom: 0 !important;
        }

        div[data-testid="column"]:has(.review-channel-card) .stButton > button,
        div[data-testid="column"]:has(.review-channel-card) div[data-testid="stButton"] > button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 2.6rem !important;
            width: 100% !important;
            border: 0 !important;
            border-radius: 13px !important;
            background: #0B57D0 !important;
            color: #FFFFFF !important;
            font-size: 0.82rem !important;
            font-weight: 900 !important;
            line-height: 1.1 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 10px 20px rgba(11, 87, 208, 0.14) !important;
        }

        div[data-testid="column"]:has(.review-channel-card) div[data-testid="stButton"] {
            position: relative !important;
            z-index: 5 !important;
            margin: -3.45rem 1.2rem 0 !important;
            width: auto !important;
        }

        div[data-testid="column"]:has(.review-channel-card) .stButton > button:hover,
        div[data-testid="column"]:has(.review-channel-card) div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 14px 26px rgba(11, 87, 208, 0.18) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.review-channel-card) {
            gap: 1.15rem !important;
            align-items: flex-start !important;
            margin-bottom: 2.2rem !important;
        }

        /* Home spacing: bring Review Channels closer to Review Overview. */
        div[data-testid="stHorizontalBlock"]:has(.friendly-kpi) {
            margin-bottom: 0.85rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.friendly-kpi) + div[data-testid="stMarkdownContainer"]:has(.friendly-section-header) .friendly-section-header,
        div[data-testid="stHorizontalBlock"]:has(.friendly-kpi) + div[data-testid="stMarkdown"]:has(.friendly-section-header) .friendly-section-header {
            margin-top: 0.65rem !important;
        }

        .friendly-section-header + div[data-testid="stHorizontalBlock"]:has(.review-channel-card),
        div[data-testid="stMarkdownContainer"]:has(.friendly-section-header) + div[data-testid="stHorizontalBlock"]:has(.review-channel-card),
        div[data-testid="stMarkdown"]:has(.friendly-section-header) + div[data-testid="stHorizontalBlock"]:has(.review-channel-card) {
            margin-top: 0.45rem !important;
        }

        /* Final home rhythm: organize Overview, Channels, Workflow, and Recent Checks. */
        .home-actions-gap {
            height: 0.85rem !important;
        }

        .friendly-section-header {
            margin: 1.35rem 0 0.8rem !important;
        }

        .friendly-section-header > span {
            width: 3rem !important;
            height: 3rem !important;
            border-radius: 16px !important;
        }

        .friendly-section-header strong {
            font-size: 1.32rem !important;
            line-height: 1.18 !important;
        }

        .friendly-section-header p {
            margin-top: 0.25rem !important;
            line-height: 1.35 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.friendly-kpi) {
            margin-bottom: 1.15rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.review-channel-card) {
            margin-bottom: 1.15rem !important;
        }

        .home-section:has(.workflow-title-row) {
            margin: 1.15rem 0 1.45rem !important;
        }

        .home-section:has(.workflow-title-row) + div[data-testid="stHorizontalBlock"]:has(.timeline-card) {
            margin-top: 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.timeline-card) {
            margin-bottom: 1.4rem !important;
        }

        .recent-section {
            margin-top: 1.45rem !important;
        }

        @media (max-width: 900px) {
            .friendly-section-header {
                margin: 1.15rem 0 0.7rem !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.friendly-kpi),
            div[data-testid="stHorizontalBlock"]:has(.review-channel-card),
            div[data-testid="stHorizontalBlock"]:has(.timeline-card) {
                margin-bottom: 1rem !important;
            }

            .home-section:has(.workflow-title-row) {
                margin: 1rem 0 1.2rem !important;
            }

            .workflow-title-row {
                flex-direction: column !important;
                gap: 0.65rem !important;
            }

            .workflow-title-row > span {
                width: 100% !important;
                max-width: none !important;
            }

            .workflow-status-strip {
                grid-template-columns: 1fr !important;
            }
        }

        /* Final navigation layer: keep the app menu visible above older theme rules. */
        section[data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            min-width: 380px !important;
            width: 380px !important;
            background: #F1F4F8 !important;
        }

        section[data-testid="stSidebar"] > div {
            display: flex !important;
            flex-direction: column !important;
            gap: 0 !important;
            padding: 1.05rem 1.25rem !important;
            overflow-y: auto !important;
        }

        .sidebar-brand {
            min-height: auto !important;
            margin-bottom: 0.8rem !important;
            padding: 1.15rem !important;
            border-radius: 14px !important;
            background: #172033 !important;
            color: #FFFFFF !important;
        }

        .sidebar-brand::before {
            width: 34px !important;
            height: 34px !important;
            border-radius: 9px !important;
            margin-bottom: 0.65rem !important;
        }

        .sidebar-brand h2 {
            color: #FFFFFF !important;
            font-size: 1.12rem !important;
            line-height: 1.2 !important;
            margin: 0 !important;
            white-space: normal !important;
        }

        .sidebar-brand p {
            color: #C9D4E5 !important;
            font-size: 0.72rem !important;
            letter-spacing: 0.08em !important;
        }

        .sidebar-group-label {
            margin: 1rem 0 0.55rem 0.15rem !important;
            color: #5B6472 !important;
            font-size: 0.74rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.12em !important;
            text-transform: uppercase !important;
        }

        .custom-nav-menu {
            display: grid !important;
            gap: 0.38rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .custom-nav-link {
            display: grid !important;
            grid-template-columns: 2.65rem minmax(0, 1fr) !important;
            align-items: center !important;
            min-height: 3.25rem !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0.62rem 0.95rem !important;
            border: 1px solid transparent !important;
            border-radius: 10px !important;
            background: transparent !important;
            color: #273142 !important;
            text-decoration: none !important;
            box-shadow: none !important;
            cursor: pointer !important;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            font-size: 0.98rem !important;
            font-weight: 780 !important;
            line-height: 1.2 !important;
        }

        .custom-nav-link:hover {
            background: #FFFFFF !important;
            border-color: #DCE4F0 !important;
            color: #273142 !important;
            text-decoration: none !important;
        }

        .custom-nav-link.active {
            background: #0B57D0 !important;
            border-color: #0B57D0 !important;
            color: #FFFFFF !important;
            box-shadow: 0 10px 20px rgba(11, 87, 208, 0.18) !important;
        }

        .custom-nav-icon {
            display: grid !important;
            place-items: center !important;
            width: 2.35rem !important;
            height: 2.35rem !important;
            color: currentColor !important;
            font-size: 1.22rem !important;
            line-height: 1 !important;
        }

        .custom-nav-label {
            min-width: 0 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] {
            margin: 0 0 0.46rem !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button {
            justify-content: flex-start !important;
            align-items: center !important;
            min-height: 3.35rem !important;
            width: 100% !important;
            padding: 0.68rem 1rem !important;
            border-radius: 10px !important;
            border: 1px solid transparent !important;
            background: transparent !important;
            color: #273142 !important;
            box-shadow: none !important;
            gap: 1.05rem !important;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            font-size: 0.98rem !important;
            font-weight: 780 !important;
            line-height: 1.2 !important;
            text-align: left !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button > div,
        section[data-testid="stSidebar"] div[data-testid="stButton"] button div[data-testid="stBaseButton-secondary"],
        section[data-testid="stSidebar"] div[data-testid="stButton"] button div[data-testid="stBaseButton-primary"] {
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 1.05rem !important;
            text-align: left !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button div[data-testid="stMarkdownContainer"] {
            width: auto !important;
            min-width: 0 !important;
            flex: 1 1 auto !important;
            display: block !important;
            text-align: left !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button [data-testid="stIconMaterial"],
        section[data-testid="stSidebar"] div[data-testid="stButton"] button svg {
            color: currentColor !important;
            flex: 0 0 1.75rem !important;
            font-size: 1.42rem !important;
            width: 1.75rem !important;
            height: 1.42rem !important;
            text-align: center !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
            width: 100% !important;
            margin: 0 !important;
            color: inherit !important;
            font-size: 0.98rem !important;
            font-weight: 820 !important;
            line-height: 1.2 !important;
            text-align: left !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
            background: #FFFFFF !important;
            border-color: #DCE4F0 !important;
            color: #273142 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
            background: #0B57D0 !important;
            border-color: #0B57D0 !important;
            color: #FFFFFF !important;
            box-shadow: 0 10px 20px rgba(11, 87, 208, 0.18) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] p {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] {
            display: grid !important;
            gap: 0.38rem !important;
            margin-top: 0 !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            display: grid !important;
            grid-template-columns: 2.65rem minmax(0, 1fr) !important;
            align-items: center !important;
            min-height: 3.25rem !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0.62rem 0.95rem !important;
            border: 1px solid transparent !important;
            border-radius: 10px !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
        }

        /* Streamlit Cloud can render the native radio indicator differently
           from local Streamlit. Hide that marker so the custom menu stays clean. */
        section[data-testid="stSidebar"] div[role="radiogroup"] label input,
        section[data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"],
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child,
        section[data-testid="stSidebar"] div[role="radiogroup"] label > span:first-child,
        section[data-testid="stSidebar"] div[role="radiogroup"] label [role="radio"],
        section[data-testid="stSidebar"] div[role="radiogroup"] label [data-testid="stRadioIcon"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            min-width: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: #FFFFFF !important;
            border-color: #DCE4F0 !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:not(:first-child),
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            grid-column: 2 !important;
            min-width: 0 !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            display: block !important;
            color: #273142 !important;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            font-size: 0.98rem !important;
            font-weight: 780 !important;
            line-height: 1.2 !important;
            margin: 0 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: #0B57D0 !important;
            border-color: #0B57D0 !important;
            box-shadow: 0 10px 20px rgba(11, 87, 208, 0.18) !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(6) {
            margin-top: 1.55rem !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(6)::after {
            content: "Reports" !important;
            top: -1.22rem !important;
            left: 0.15rem !important;
            color: #5B6472 !important;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
            font-size: 0.74rem !important;
            letter-spacing: 0.12em !important;
            text-transform: uppercase !important;
        }

        .workspace-card,
        .sidebar-ready-card {
            border-radius: 12px !important;
            border: 1px solid #DCE4F0 !important;
            background: #FFFFFF !important;
            box-shadow: none !important;
        }

        .top-shell {
            display: grid !important;
            grid-template-columns: minmax(0, 1fr) auto auto auto !important;
            align-items: center !important;
            gap: clamp(0.9rem, 1.4vw, 1.35rem) !important;
            min-height: 4.9rem !important;
            padding-top: 0.75rem !important;
            padding-bottom: 0.75rem !important;
        }

        .top-shell .top-logo {
            width: 56px !important;
            height: 56px !important;
            border-radius: 16px !important;
        }

        .top-shell .top-brand strong {
            font-size: clamp(1.18rem, 1.5vw, 1.42rem) !important;
            line-height: 1.05 !important;
        }

        .top-shell .top-brand span {
            font-size: clamp(0.78rem, 0.92vw, 0.9rem) !important;
            margin-top: 0.32rem !important;
            color: #667085 !important;
            font-weight: 760 !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
        }

        .top-shell .top-pill {
            min-height: 2.75rem !important;
            padding: 0 1.35rem !important;
            font-size: 0.98rem !important;
        }

        /* Final page width: use more horizontal space while staying readable. */
        .block-container,
        div[data-testid="stAppViewBlockContainer"] {
            max-width: 1540px !important;
            width: min(100%, 1540px) !important;
            padding-left: clamp(1.25rem, 2.4vw, 2.2rem) !important;
            padding-right: clamp(1.25rem, 2.4vw, 2.2rem) !important;
        }

        .top-shell,
        .home-hero,
        .dashboard-header,
        .home-section,
        div[data-testid="stHorizontalBlock"]:has(.friendly-kpi),
        div[data-testid="stHorizontalBlock"]:has(.review-channel-card),
        div[data-testid="stHorizontalBlock"]:has(.timeline-card) {
            width: 100% !important;
            max-width: none !important;
        }

        .home-hero {
            grid-template-columns: minmax(0, 1.18fr) minmax(360px, 0.82fr) !important;
            padding-left: clamp(2rem, 4.2vw, 4.5rem) !important;
            padding-right: clamp(2rem, 4.2vw, 4.5rem) !important;
        }

        .home-hero h1 {
            max-width: 780px !important;
            font-size: clamp(2.15rem, 3.6vw, 4.05rem) !important;
        }

        .home-hero p {
            max-width: 820px !important;
        }

        /* Article review workspace */
        .article-focus-panel {
            display: grid !important;
            grid-template-columns: auto minmax(0, 1.35fr) minmax(320px, 0.6fr) !important;
            gap: 1.4rem !important;
            align-items: center !important;
            margin: 1rem 0 1.2rem !important;
            border: 1px solid #D8E2F0 !important;
            border-radius: 20px !important;
            background:
                radial-gradient(circle at 92% 12%, rgba(191, 235, 216, 0.45), transparent 18rem),
                linear-gradient(135deg, #FFFFFF 0%, #F7FAFF 100%) !important;
            padding: 1.35rem 1.45rem !important;
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06) !important;
        }

        .article-focus-icon {
            width: 4.35rem !important;
            height: 4.35rem !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 20px !important;
            background: #EEF4FF !important;
            color: #0B57D0 !important;
            font-size: 2rem !important;
            box-shadow: 0 12px 24px rgba(11, 87, 208, 0.10) !important;
        }

        .article-focus-panel > div:nth-child(2) > span {
            display: inline-flex !important;
            width: fit-content !important;
            border-radius: 999px !important;
            background: #EEF4FF !important;
            color: #0B57D0 !important;
            padding: 0.35rem 0.65rem !important;
            font-size: 0.72rem !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
            margin-bottom: 0.75rem !important;
        }

        .article-focus-panel strong {
            display: block !important;
            color: #0F172A !important;
            font-size: clamp(1.35rem, 2vw, 2rem) !important;
            line-height: 1.1 !important;
            font-weight: 950 !important;
            margin-bottom: 0.55rem !important;
        }

        .article-focus-panel p {
            max-width: 760px !important;
            margin: 0 !important;
            color: #526173 !important;
            font-size: 0.98rem !important;
            line-height: 1.5 !important;
        }

        .article-focus-steps {
            display: grid !important;
            gap: 0.6rem !important;
            align-self: stretch !important;
        }

        .article-focus-steps span {
            display: flex !important;
            align-items: center !important;
            min-height: 2.7rem !important;
            border: 1px solid #E0E8F3 !important;
            border-radius: 12px !important;
            background: #FFFFFF !important;
            color: #334155 !important;
            font-size: 0.88rem !important;
            font-weight: 850 !important;
            padding: 0.6rem 0.75rem !important;
        }

        .review-tab-note {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.7rem !important;
            margin: 0.25rem 0 0.75rem !important;
            border: 1px solid #DCE6F5 !important;
            border-radius: 12px !important;
            background: #FFFFFF !important;
            padding: 0.75rem 0.9rem !important;
            color: #475569 !important;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04) !important;
        }

        .review-tab-note strong {
            color: #0F172A !important;
            font-size: 0.92rem !important;
            font-weight: 900 !important;
        }

        .review-tab-note span {
            color: #64748B !important;
            font-size: 0.9rem !important;
            font-weight: 750 !important;
        }

        .review-tab-note.muted {
            color: #64748B !important;
            font-weight: 750 !important;
        }

        .review-workspace-heading {
            display: flex !important;
            align-items: flex-start !important;
            justify-content: space-between !important;
            gap: 1rem !important;
            margin: 1rem 0 0.9rem !important;
        }

        .review-workspace-heading strong {
            display: block !important;
            color: #0F172A !important;
            font-size: 1.25rem !important;
            font-weight: 900 !important;
            line-height: 1.2 !important;
            margin-bottom: 0.25rem !important;
        }

        .review-workspace-heading p {
            margin: 0 !important;
            color: #64748B !important;
            font-size: 0.95rem !important;
            line-height: 1.4 !important;
        }

        .review-workspace-heading > span {
            flex: 0 0 auto !important;
            border-radius: 999px !important;
            background: #EEF4FF !important;
            color: #0B57D0 !important;
            padding: 0.45rem 0.75rem !important;
            font-size: 0.76rem !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.02em !important;
        }

        .review-form-card {
            padding: 1.35rem !important;
            border: 1px solid #D8E2F0 !important;
            border-radius: 18px !important;
            background: #FFFFFF !important;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05) !important;
        }

        .form-section-heading {
            display: flex !important;
            align-items: center !important;
            gap: 0.75rem !important;
            margin: 0 0 0.85rem !important;
        }

        .form-section-heading.second {
            margin-top: 1.15rem !important;
            padding-top: 1.15rem !important;
            border-top: 1px solid #EEF2F7 !important;
        }

        .form-section-heading > span {
            width: 2.45rem !important;
            height: 2.45rem !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 12px !important;
            background: #EEF4FF !important;
            color: #0B57D0 !important;
            font-size: 1.1rem !important;
            flex: 0 0 auto !important;
        }

        .form-section-heading strong {
            display: block !important;
            color: #0F172A !important;
            font-size: 1rem !important;
            font-weight: 900 !important;
            line-height: 1.2 !important;
        }

        .form-section-heading p {
            margin: 0.12rem 0 0 !important;
            color: #64748B !important;
            font-size: 0.84rem !important;
            font-weight: 700 !important;
            line-height: 1.3 !important;
        }

        .review-form-card label,
        .review-form-card label p,
        .review-form-card [data-testid="stWidgetLabel"] p,
        .review-form-card div[data-testid="stWidgetLabel"] p {
            color: #1E293B !important;
            font-size: 0.9rem !important;
            font-weight: 900 !important;
            opacity: 1 !important;
        }

        .review-form-card .stTextInput input,
        .review-form-card .stTextArea textarea {
            border: 1px solid #D8E2F0 !important;
            border-radius: 12px !important;
            background: #FFFFFF !important;
            color: #0F172A !important;
            box-shadow: none !important;
            font-size: 0.95rem !important;
        }

        .review-form-card .stTextInput input:focus,
        .review-form-card .stTextArea textarea:focus {
            border-color: #0B57D0 !important;
            box-shadow: 0 0 0 3px rgba(11, 87, 208, 0.12) !important;
        }

        .review-form-card div[data-testid="stFormSubmitButton"] button {
            min-height: 3rem !important;
            border-radius: 12px !important;
            background: #0B57D0 !important;
            color: #FFFFFF !important;
            border-color: #0B57D0 !important;
            box-shadow: 0 10px 20px rgba(11, 87, 208, 0.16) !important;
        }

        .text-only-review-card {
            padding: 1.45rem !important;
        }

        .text-only-review-card .stTextArea textarea {
            min-height: 360px !important;
            line-height: 1.55 !important;
        }

        .text-only-review-card div[data-testid="stFormSubmitButton"] button {
            min-height: 3.25rem !important;
            margin-top: 0.8rem !important;
            font-size: 0.95rem !important;
        }

        .text-review-footer {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 0.6rem !important;
            margin: 0.85rem 0 0.25rem !important;
        }

        .text-review-footer span {
            display: inline-flex !important;
            align-items: center !important;
            border-radius: 999px !important;
            background: #F1F5F9 !important;
            color: #475569 !important;
            padding: 0.38rem 0.65rem !important;
            font-size: 0.78rem !important;
            font-weight: 850 !important;
        }

        /* Reference-style article text review page */
        .article-page-shell {
            max-width: 920px !important;
            margin: 3.2rem auto 2.4rem !important;
            text-align: center !important;
        }

        .article-hero > span {
            display: inline-flex !important;
            color: #2563EB !important;
            font-size: 0.8rem !important;
            font-weight: 950 !important;
            letter-spacing: 0.32em !important;
            text-transform: uppercase !important;
            margin-bottom: 1.35rem !important;
        }

        .article-hero h1 {
            max-width: 640px !important;
            margin: 0 auto 1.25rem !important;
            color: #111827 !important;
            font-size: clamp(2.3rem, 4.6vw, 4rem) !important;
            line-height: 1.03 !important;
            font-weight: 950 !important;
            text-align: center !important;
        }

        .article-hero p {
            max-width: 650px !important;
            margin: 0 auto !important;
            color: #6B7280 !important;
            font-size: 1.08rem !important;
            line-height: 1.55 !important;
            font-weight: 650 !important;
            text-align: center !important;
        }

        .article-review-card {
            max-width: 880px !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 auto !important;
            padding: 0 !important;
            border: 0 !important;
            overflow: visible !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) {
            max-width: 880px !important;
            min-height: 620px !important;
            margin: 0 auto 3.2rem !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 28px !important;
            background: #FFFFFF !important;
            box-shadow: 0 28px 70px rgba(15, 23, 42, 0.08) !important;
            padding: 3.2rem 3.4rem 2rem !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) .stTextInput input {
            min-height: 3.35rem !important;
            border: 1px solid #DCE6F4 !important;
            border-radius: 12px !important;
            background: #F8FAFC !important;
            color: #111827 !important;
            font-size: 1.05rem !important;
            font-weight: 750 !important;
            box-shadow: none !important;
            padding: 0.25rem 1rem !important;
            outline: none !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) .stTextInput input::placeholder {
            color: #94A3B8 !important;
            opacity: 1 !important;
            font-size: 0.98rem !important;
            font-weight: 750 !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) .stTextArea textarea {
            min-height: 390px !important;
            border: 1px solid #DCE6F4 !important;
            border-radius: 16px !important;
            background: #F8FAFC !important;
            color: #111827 !important;
            font-size: 1rem !important;
            line-height: 1.65 !important;
            box-shadow: none !important;
            padding: 1.25rem 1rem !important;
            resize: vertical !important;
            outline: none !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) .stTextArea textarea::placeholder {
            color: #94A3B8 !important;
            opacity: 1 !important;
            font-size: 0.98rem !important;
            font-weight: 750 !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) .stTextInput input:focus,
        div[data-testid="stForm"]:has(.article-classifier-status) .stTextArea textarea:focus {
            border-color: #2563EB !important;
            background: #FFFFFF !important;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12) !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) .stTextInput input:invalid,
        div[data-testid="stForm"]:has(.article-classifier-status) .stTextArea textarea:invalid {
            border-color: #DCE6F4 !important;
            box-shadow: none !important;
        }

        .article-classifier-status {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.45rem !important;
            min-height: 3rem !important;
            color: #64748B !important;
            font-size: 0.82rem !important;
            font-weight: 850 !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) div[data-testid="stFormSubmitButton"] button {
            min-height: 3.8rem !important;
            border: 0 !important;
            border-radius: 14px !important;
            background: #2563EB !important;
            color: #FFFFFF !important;
            font-size: 1rem !important;
            font-weight: 900 !important;
            box-shadow: 0 16px 30px rgba(37, 99, 235, 0.24) !important;
        }

        div[data-testid="stForm"]:has(.article-classifier-status) div[data-testid="stFormSubmitButton"] button:hover {
            background: #1D4ED8 !important;
            color: #FFFFFF !important;
            transform: translateY(-1px) !important;
        }

        .article-metrics-row {
            max-width: 1020px !important;
            margin: 0 auto 3rem !important;
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 0 !important;
        }

        .article-metrics-row > div {
            padding: 0 2.2rem !important;
            border-left: 1px solid #EEF2F7 !important;
        }

        .article-metrics-row > div:first-child {
            border-left: 0 !important;
        }

        .article-metrics-row span {
            display: block !important;
            color: #A0A8B8 !important;
            font-size: 0.72rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            margin-bottom: 0.55rem !important;
        }

        .article-metrics-row strong {
            display: block !important;
            color: #111827 !important;
            font-size: 2rem !important;
            line-height: 1 !important;
            font-weight: 950 !important;
        }

        .article-metrics-row strong:not(:first-child) {
            overflow-wrap: anywhere !important;
        }

        .article-metrics-row p {
            margin: 0.7rem 0 0 !important;
            color: #9CA3AF !important;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
        }

        .image-page-shell {
            max-width: 1320px !important;
            margin: 0.75rem auto 1.55rem !important;
            padding: 0 0.2rem !important;
        }

        .image-hero {
            display: grid !important;
            grid-template-columns: minmax(0, 1fr) auto !important;
            align-items: center !important;
            gap: 1.25rem !important;
            text-align: left !important;
            padding: 1.35rem 1.45rem !important;
            border: 1px solid #DCE6F4 !important;
            border-radius: 22px !important;
            background:
                radial-gradient(circle at 90% 5%, rgba(191, 235, 216, 0.45), transparent 18rem),
                linear-gradient(135deg, #FFFFFF 0%, #F7FAFF 100%) !important;
            box-shadow: 0 16px 34px rgba(15, 23, 42, 0.06) !important;
        }

        .image-hero span {
            display: inline-block !important;
            color: #2563EB !important;
            font-size: 0.72rem !important;
            font-weight: 950 !important;
            letter-spacing: 0.16em !important;
            text-transform: uppercase !important;
            margin-bottom: 0.45rem !important;
        }

        .image-hero h1 {
            max-width: 820px !important;
            margin: 0 !important;
            color: #111827 !important;
            font-size: clamp(1.85rem, 2.8vw, 3.25rem) !important;
            line-height: 1.05 !important;
            font-weight: 950 !important;
            letter-spacing: 0 !important;
        }

        .image-hero p {
            max-width: 760px !important;
            margin: 0.85rem 0 0 !important;
            color: #64748B !important;
            font-size: 1rem !important;
            line-height: 1.55 !important;
            font-weight: 650 !important;
        }

        .image-hero-badge {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.45rem !important;
            min-height: 2.65rem !important;
            padding: 0 1rem !important;
            border-radius: 999px !important;
            border: 1px solid #BFEBD8 !important;
            background: #ECFDF5 !important;
            color: #047857 !important;
            font-size: 0.86rem !important;
            font-weight: 900 !important;
            white-space: nowrap !important;
        }

        .image-hero-badge::before {
            content: "";
            width: 0.55rem !important;
            height: 0.55rem !important;
            border-radius: 999px !important;
            background: #10B981 !important;
            box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.12) !important;
        }

        .image-upload-panel,
        .image-status-card,
        .image-note-card {
            border: 1px solid #DCE6F4 !important;
            border-radius: 26px !important;
            background: #FFFFFF !important;
            box-shadow: 0 22px 56px rgba(15, 23, 42, 0.07) !important;
        }

        .image-upload-panel {
            min-height: 285px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            padding: 2rem !important;
            margin-bottom: 1rem !important;
            background:
                radial-gradient(circle at 86% 8%, rgba(37, 99, 235, 0.10), transparent 16rem),
                linear-gradient(135deg, rgba(37, 99, 235, 0.055), rgba(16, 185, 129, 0.055)),
                #FFFFFF !important;
        }

        .image-upload-icon {
            width: 4.75rem !important;
            height: 4.75rem !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 20px !important;
            background: #EAF1FF !important;
            color: #2563EB !important;
            font-size: 2rem !important;
            font-weight: 950 !important;
            margin-bottom: 1rem !important;
        }

        .image-upload-panel strong,
        .image-status-card strong,
        .image-note-card strong {
            display: block !important;
            color: #111827 !important;
            font-size: 1.2rem !important;
            font-weight: 950 !important;
            margin-bottom: 0.45rem !important;
        }

        .image-upload-panel p,
        .image-status-card p,
        .image-note-card p {
            margin: 0 !important;
            color: #64748B !important;
            line-height: 1.55 !important;
            font-weight: 650 !important;
        }

        .image-upload-meta {
            display: flex !important;
            gap: 0.55rem !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
            margin-top: 1rem !important;
        }

        .image-upload-meta span {
            display: inline-flex !important;
            align-items: center !important;
            min-height: 2rem !important;
            padding: 0 0.72rem !important;
            border-radius: 999px !important;
            background: #F1F5F9 !important;
            color: #475569 !important;
            font-size: 0.82rem !important;
            font-weight: 850 !important;
        }

        div[data-testid="stFileUploader"] {
            max-width: 100% !important;
        }

        div[data-testid="stFileUploader"] section {
            border: 1px solid #DCE6F4 !important;
            border-radius: 14px !important;
            background: #FFFFFF !important;
        }

        div[data-testid="stFileUploader"] button {
            border: 0 !important;
            border-radius: 10px !important;
            background: #2563EB !important;
            color: #FFFFFF !important;
            font-weight: 850 !important;
            box-shadow: none !important;
        }

        div[data-testid="stFileUploader"] button:hover {
            background: #1D4ED8 !important;
            color: #FFFFFF !important;
        }

        div[data-testid="stFileUploader"] small,
        div[data-testid="stFileUploader"] span {
            color: #64748B !important;
            font-weight: 650 !important;
        }

        .image-status-card {
            min-height: 285px !important;
            padding: 1.6rem !important;
        }

        .image-status-card.ready {
            border-color: #BFEBD8 !important;
            background: linear-gradient(180deg, #F3FCF8 0%, #FFFFFF 100%) !important;
        }

        .image-status-dot {
            width: 0.75rem !important;
            height: 0.75rem !important;
            border-radius: 999px !important;
            background: #94A3B8 !important;
            margin-bottom: 1rem !important;
        }

        .image-status-card.ready .image-status-dot {
            background: #10B981 !important;
            box-shadow: 0 0 0 7px rgba(16, 185, 129, 0.12) !important;
        }

        .image-status-card ul {
            margin: 1rem 0 0 !important;
            padding-left: 0 !important;
            color: #475569 !important;
            font-weight: 650 !important;
            line-height: 1.7 !important;
            list-style: none !important;
        }

        .image-status-card li {
            position: relative !important;
            padding-left: 1.45rem !important;
            margin: 0.45rem 0 !important;
        }

        .image-status-card li::before {
            content: "";
            position: absolute !important;
            left: 0 !important;
            top: 0.72rem !important;
            width: 0.42rem !important;
            height: 0.42rem !important;
            border-radius: 999px !important;
            background: #2563EB !important;
        }

        .image-file-grid {
            display: grid !important;
            grid-template-columns: 90px minmax(0, 1fr) !important;
            gap: 0.75rem 1rem !important;
            margin-top: 1.2rem !important;
            align-items: start !important;
        }

        .image-file-grid span {
            color: #94A3B8 !important;
            font-size: 0.72rem !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
        }

        .image-file-grid b {
            color: #111827 !important;
            font-size: 0.9rem !important;
            overflow-wrap: anywhere !important;
        }

        .image-note-card {
            max-width: 1320px !important;
            margin: 1.6rem auto 2rem !important;
            padding: 1.2rem 1.35rem !important;
            display: grid !important;
            grid-template-columns: auto minmax(0, 1fr) !important;
            gap: 0.9rem !important;
            align-items: center !important;
        }

        .image-note-icon {
            width: 2.75rem !important;
            height: 2.75rem !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 14px !important;
            background: #EEF4FF !important;
            color: #2563EB !important;
            font-size: 1.45rem !important;
        }

        .text-from-image-card {
            border: 1px solid #DCE6F4 !important;
            border-radius: 22px !important;
            background: #FFFFFF !important;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.06) !important;
            padding: 1.35rem !important;
            margin: 1.2rem 0 1.4rem !important;
        }

        .text-from-image-header {
            display: flex !important;
            align-items: center !important;
            gap: 0.85rem !important;
            margin-bottom: 1rem !important;
        }

        .text-from-image-icon {
            width: 3rem !important;
            height: 3rem !important;
            display: grid !important;
            place-items: center !important;
            flex: 0 0 auto !important;
            border-radius: 14px !important;
            background: #EAF1FF !important;
            color: #2563EB !important;
            font-size: 0.76rem !important;
            font-weight: 950 !important;
            letter-spacing: 0.04em !important;
        }

        .text-from-image-header strong {
            display: block !important;
            color: #111827 !important;
            font-size: 1.15rem !important;
            font-weight: 950 !important;
            margin: 0 0 0.2rem !important;
        }

        .text-from-image-header p {
            margin: 0 !important;
            color: #64748B !important;
            font-size: 0.9rem !important;
            font-weight: 700 !important;
        }

        .text-from-image-body {
            max-height: 320px !important;
            overflow: auto !important;
            white-space: pre-wrap !important;
            border: 1px solid #EEF2F7 !important;
            border-radius: 16px !important;
            background: #F8FAFC !important;
            color: #111827 !important;
            font-size: 0.96rem !important;
            line-height: 1.62 !important;
            font-weight: 650 !important;
            padding: 1rem !important;
        }

        .link-page-shell,
        .batch-page-shell {
            max-width: 1180px !important;
            margin: 2.4rem auto 2rem !important;
            padding: 0 0.2rem !important;
        }

        .link-hero,
        .batch-hero {
            text-align: center !important;
            padding: 2.2rem 1rem 1.6rem !important;
        }

        .link-hero span,
        .batch-hero span {
            display: inline-block !important;
            color: #2563EB !important;
            font-size: 0.76rem !important;
            font-weight: 950 !important;
            letter-spacing: 0.22em !important;
            text-transform: uppercase !important;
            margin-bottom: 1rem !important;
        }

        .link-hero h1,
        .batch-hero h1 {
            max-width: 820px !important;
            margin: 0 auto !important;
            color: #111827 !important;
            font-size: clamp(2.2rem, 4vw, 4.1rem) !important;
            line-height: 1.04 !important;
            font-weight: 950 !important;
            letter-spacing: 0 !important;
        }

        .link-hero p,
        .batch-hero p {
            max-width: 640px !important;
            margin: 1.05rem auto 0 !important;
            color: #64748B !important;
            font-size: 1.05rem !important;
            line-height: 1.6 !important;
            font-weight: 650 !important;
        }

        .link-input-panel,
        .batch-upload-panel,
        .link-status-card,
        .batch-status-card,
        .link-note-card,
        .batch-note-card,
        .batch-preview-card {
            border: 1px solid #DCE6F4 !important;
            border-radius: 26px !important;
            background: #FFFFFF !important;
            box-shadow: 0 22px 56px rgba(15, 23, 42, 0.07) !important;
        }

        .link-input-panel,
        .batch-upload-panel {
            min-height: 240px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            padding: 2rem !important;
            margin-bottom: 1rem !important;
            background:
                linear-gradient(135deg, rgba(37, 99, 235, 0.06), rgba(16, 185, 129, 0.06)),
                #FFFFFF !important;
        }

        .link-input-icon,
        .batch-upload-icon {
            width: 4.25rem !important;
            height: 4.25rem !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 20px !important;
            background: #EAF1FF !important;
            color: #2563EB !important;
            font-size: 1rem !important;
            font-weight: 950 !important;
            margin-bottom: 1rem !important;
        }

        .link-input-panel strong,
        .batch-upload-panel strong,
        .link-status-card strong,
        .batch-status-card strong,
        .link-note-card strong,
        .batch-note-card strong,
        .batch-preview-card strong {
            display: block !important;
            color: #111827 !important;
            font-size: 1.2rem !important;
            font-weight: 950 !important;
            margin-bottom: 0.45rem !important;
        }

        .link-input-panel p,
        .batch-upload-panel p,
        .link-status-card p,
        .batch-status-card p,
        .link-note-card p,
        .batch-note-card p,
        .batch-preview-card p {
            margin: 0 !important;
            color: #64748B !important;
            line-height: 1.55 !important;
            font-weight: 650 !important;
        }

        .link-status-card,
        .batch-status-card {
            min-height: 240px !important;
            padding: 1.45rem !important;
        }

        .batch-template-action {
            margin-top: 1.15rem !important;
        }

        .batch-template-action div[data-testid="stDownloadButton"] > button {
            min-height: 3.25rem !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
        }

        .link-status-card.ready,
        .batch-status-card.ready {
            border-color: #BFEBD8 !important;
            background: linear-gradient(180deg, #F3FCF8 0%, #FFFFFF 100%) !important;
        }

        .batch-status-card.warning {
            border-color: #FED7AA !important;
            background: linear-gradient(180deg, #FFF7ED 0%, #FFFFFF 100%) !important;
        }

        .link-status-dot,
        .batch-status-dot {
            width: 0.75rem !important;
            height: 0.75rem !important;
            border-radius: 999px !important;
            background: #94A3B8 !important;
            margin-bottom: 1rem !important;
        }

        .link-status-card.ready .link-status-dot,
        .batch-status-card.ready .batch-status-dot {
            background: #10B981 !important;
            box-shadow: 0 0 0 7px rgba(16, 185, 129, 0.12) !important;
        }

        .batch-status-card.warning .batch-status-dot {
            background: #F97316 !important;
            box-shadow: 0 0 0 7px rgba(249, 115, 22, 0.12) !important;
        }

        .link-status-card ul,
        .batch-status-card ul {
            margin: 1rem 0 0 !important;
            padding-left: 1.2rem !important;
            color: #475569 !important;
            font-weight: 650 !important;
            line-height: 1.7 !important;
        }

        .link-file-grid,
        .batch-file-grid {
            display: grid !important;
            grid-template-columns: 90px minmax(0, 1fr) !important;
            gap: 0.75rem 1rem !important;
            margin-top: 1.2rem !important;
            align-items: start !important;
        }

        .link-file-grid span,
        .batch-file-grid span {
            color: #94A3B8 !important;
            font-size: 0.72rem !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
        }

        .link-file-grid b,
        .batch-file-grid b {
            color: #111827 !important;
            font-size: 0.9rem !important;
            overflow-wrap: anywhere !important;
        }

        .link-note-card,
        .batch-note-card,
        .batch-preview-card {
            max-width: 1180px !important;
            margin: 2rem auto 2rem !important;
            padding: 1.2rem 1.4rem !important;
        }

        .link-page-shell {
            max-width: 1320px !important;
            margin: 0.75rem auto 1.55rem !important;
            padding: 0 0.2rem !important;
        }

        .link-hero {
            display: grid !important;
            grid-template-columns: minmax(0, 1fr) auto !important;
            align-items: center !important;
            gap: 1.25rem !important;
            text-align: left !important;
            padding: 1.35rem 1.45rem !important;
            border: 1px solid #DCE6F4 !important;
            border-radius: 22px !important;
            background:
                radial-gradient(circle at 90% 5%, rgba(191, 235, 216, 0.42), transparent 18rem),
                linear-gradient(135deg, #FFFFFF 0%, #F7FAFF 100%) !important;
            box-shadow: 0 16px 34px rgba(15, 23, 42, 0.06) !important;
        }

        .link-hero span {
            display: inline-block !important;
            color: #2563EB !important;
            font-size: 0.72rem !important;
            font-weight: 950 !important;
            letter-spacing: 0.16em !important;
            text-transform: uppercase !important;
            margin-bottom: 0.45rem !important;
        }

        .link-hero h1 {
            max-width: 820px !important;
            margin: 0 !important;
            color: #111827 !important;
            font-size: clamp(1.85rem, 2.8vw, 3.25rem) !important;
            line-height: 1.05 !important;
            font-weight: 950 !important;
            letter-spacing: 0 !important;
        }

        .link-hero p {
            max-width: 760px !important;
            margin: 0.85rem 0 0 !important;
            color: #64748B !important;
            font-size: 1rem !important;
            line-height: 1.55 !important;
            font-weight: 650 !important;
        }

        .link-hero-badge {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.45rem !important;
            min-height: 2.65rem !important;
            padding: 0 1rem !important;
            border-radius: 999px !important;
            border: 1px solid #BFEBD8 !important;
            background: #ECFDF5 !important;
            color: #047857 !important;
            font-size: 0.86rem !important;
            font-weight: 900 !important;
            white-space: nowrap !important;
        }

        .link-hero-badge::before {
            content: "";
            width: 0.55rem !important;
            height: 0.55rem !important;
            border-radius: 999px !important;
            background: #10B981 !important;
            box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.12) !important;
        }

        .link-input-panel,
        .link-status-card {
            min-height: 285px !important;
        }

        .link-input-panel {
            background:
                radial-gradient(circle at 86% 8%, rgba(37, 99, 235, 0.10), transparent 16rem),
                linear-gradient(135deg, rgba(37, 99, 235, 0.055), rgba(16, 185, 129, 0.055)),
                #FFFFFF !important;
        }

        .link-input-icon {
            width: 4.75rem !important;
            height: 4.75rem !important;
            font-size: 1.55rem !important;
        }

        .link-input-meta {
            display: flex !important;
            gap: 0.55rem !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
            margin-top: 1rem !important;
        }

        .link-input-meta span {
            display: inline-flex !important;
            align-items: center !important;
            min-height: 2rem !important;
            padding: 0 0.72rem !important;
            border-radius: 999px !important;
            background: #F1F5F9 !important;
            color: #475569 !important;
            font-size: 0.82rem !important;
            font-weight: 850 !important;
        }

        .link-status-card ul {
            padding-left: 0 !important;
            list-style: none !important;
        }

        .link-status-card li {
            position: relative !important;
            padding-left: 1.45rem !important;
            margin: 0.45rem 0 !important;
        }

        .link-status-card li::before {
            content: "";
            position: absolute !important;
            left: 0 !important;
            top: 0.72rem !important;
            width: 0.42rem !important;
            height: 0.42rem !important;
            border-radius: 999px !important;
            background: #2563EB !important;
        }

        .link-note-card {
            max-width: 1320px !important;
            margin: 1.6rem auto 2rem !important;
            padding: 1.2rem 1.35rem !important;
            display: grid !important;
            grid-template-columns: auto minmax(0, 1fr) !important;
            gap: 0.9rem !important;
            align-items: center !important;
        }

        .link-note-icon {
            width: 2.75rem !important;
            height: 2.75rem !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 14px !important;
            background: #EEF4FF !important;
            color: #2563EB !important;
            font-size: 1.45rem !important;
        }

        .batch-preview-card {
            margin-bottom: 1rem !important;
        }

        .review-guide-card {
            height: 100% !important;
            min-height: 360px !important;
            border: 1px solid #BFEBD8 !important;
            border-radius: 18px !important;
            background: linear-gradient(180deg, #F2FCF7 0%, #FFFFFF 100%) !important;
            padding: 1.2rem !important;
            color: #315B49 !important;
            box-shadow: 0 12px 28px rgba(0, 122, 85, 0.06) !important;
        }

        .review-guide-card .guide-icon {
            width: 2.75rem !important;
            height: 2.75rem !important;
            display: grid !important;
            place-items: center !important;
            border-radius: 14px !important;
            background: #DDF8EA !important;
            color: #007A55 !important;
            font-weight: 900 !important;
            margin-bottom: 0.9rem !important;
        }

        .review-guide-card strong {
            color: #006B4A !important;
            display: block !important;
            font-size: 1.08rem !important;
            font-weight: 900 !important;
            margin-bottom: 0.5rem !important;
        }

        .review-guide-card p,
        .review-guide-card li {
            color: #426555 !important;
            font-size: 0.92rem !important;
            line-height: 1.45 !important;
        }

        .review-guide-card ul {
            margin: 1rem 0 0 !important;
            padding-left: 1.1rem !important;
        }

        .review-guide-card li + li {
            margin-top: 0.55rem !important;
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 1ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
                transition-duration: 1ms !important;
            }
        }

        @media (max-width: 900px) {
            .block-container {padding: 0 1rem 2rem;}
            section[data-testid="stSidebar"] {min-width: 330px !important; width: 330px !important;}
            .top-shell {grid-template-columns: 1fr; height: auto; padding-top: 0.8rem; padding-bottom: 0.8rem;}
            .home-hero {grid-template-columns: 1fr; padding: 1.5rem;}
            .home-actions-gap {height: 1.1rem;}
            .friendly-section-header {margin: 1.8rem 0 0.85rem;}
            .friendly-section-header + div[data-testid="stHorizontalBlock"] {margin-bottom: 1.5rem;}
            div[data-testid="stHorizontalBlock"]:has(.friendly-kpi) {
                row-gap: 1.1rem !important;
                margin-bottom: 1.05rem !important;
            }
            .home-section {margin: 1.8rem 0 1.35rem; padding: 1.25rem;}
            .dashboard-header {align-items: flex-start; flex-direction: column;}
            .result-topline {grid-template-columns: 1fr;}
            .result-grid {
                grid-template-columns: 1fr 1fr;
                gap: 1.05rem !important;
            }
            .review-workspace-heading {
                flex-direction: column !important;
            }
            .review-workspace-heading > span {
                width: fit-content !important;
            }
            .article-focus-panel {
                grid-template-columns: 1fr !important;
            }
            .article-page-shell {
                margin: 2rem auto 1.5rem !important;
            }
            .article-review-card {
                padding: 0 !important;
                min-height: 540px !important;
                border-radius: 20px !important;
            }
            div[data-testid="stForm"]:has(.article-classifier-status) {
                padding: 2rem 1.25rem 1.5rem !important;
                min-height: 540px !important;
                border-radius: 20px !important;
            }
            .article-metrics-row {
                grid-template-columns: 1fr !important;
                gap: 1.2rem !important;
            }
            .article-metrics-row > div {
                border-left: 0 !important;
                border-top: 1px solid #EEF2F7 !important;
                padding: 1rem 0 0 !important;
            }
            .article-metrics-row > div:first-child {
                border-top: 0 !important;
            }
        }

        @media (max-width: 560px) {
            .block-container {padding-left: 0.75rem; padding-right: 0.75rem;}
            .result-grid,
            .model-info-grid,
            .home-search {grid-template-columns: 1fr;}
            .header-status {white-space: normal;}
            section[data-testid="stSidebar"] {min-width: 292px !important; width: 292px !important;}
            section[data-testid="stSidebar"] div[role="radiogroup"] label p {font-size: 0.88rem !important;}
        }

        div[data-testid="stHorizontalBlock"]:has(.kpi-card):not(:has(.friendly-kpi)) {
            column-gap: clamp(1.45rem, 2.2vw, 2.25rem) !important;
            row-gap: 1.45rem !important;
            margin-bottom: 1.65rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.kpi-card):not(:has(.friendly-kpi)) + div[data-testid="stHorizontalBlock"]:has(.kpi-card):not(:has(.friendly-kpi)) {
            margin-top: 0.65rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.kpi-card):not(:has(.friendly-kpi)) .kpi-card {
            margin-bottom: 0 !important;
        }

        .result-grid {
            column-gap: clamp(1.15rem, 1.9vw, 1.6rem) !important;
            row-gap: clamp(1.15rem, 1.9vw, 1.6rem) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.insight-card) {
            column-gap: clamp(1.45rem, 2.2vw, 2.25rem) !important;
            row-gap: 1.45rem !important;
            margin-top: 0.35rem !important;
            margin-bottom: 0.45rem !important;
            align-items: stretch !important;
        }

        div[data-testid="column"]:has(.insight-card) {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        div[data-testid="column"]:has(.insight-card) .insight-card:last-child {
            margin-bottom: 0 !important;
        }

        .settings-control-card {
            border: 1px solid #DCE6F4 !important;
            border-radius: 18px !important;
            background:
                linear-gradient(135deg, rgba(37, 99, 235, 0.06), rgba(16, 185, 129, 0.06)),
                #FFFFFF !important;
            padding: 1.15rem 1.25rem !important;
            margin: 0.25rem 0 1.25rem !important;
            box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06) !important;
        }

        .settings-control-card strong {
            display: block !important;
            color: #111827 !important;
            font-size: 1.08rem !important;
            font-weight: 900 !important;
            margin-bottom: 0.35rem !important;
        }

        .settings-control-card p {
            max-width: 840px !important;
            margin: 0 !important;
            color: #64748B !important;
            line-height: 1.55 !important;
            font-weight: 650 !important;
        }

        .settings-page-marker ~ div[data-testid="stVerticalBlock"] div[data-testid="stSlider"],
        div[data-testid="stSlider"] {
            border: 1px solid #DCE6F4 !important;
            border-radius: 18px !important;
            background: #FFFFFF !important;
            padding: 1.1rem 1.25rem 1.25rem !important;
            margin: 0 0 1rem !important;
            box-shadow: 0 14px 32px rgba(15, 23, 42, 0.055) !important;
        }

        div[data-testid="stSlider"] label,
        div[data-testid="stSlider"] label p {
            color: #334155 !important;
            font-size: 0.98rem !important;
            font-weight: 850 !important;
            opacity: 1 !important;
            margin-bottom: 0.6rem !important;
        }

        div[data-testid="stSlider"] [data-testid="stTickBar"] {
            display: none !important;
        }

        div[data-testid="stSlider"] [role="slider"] {
            border-color: #2563EB !important;
            background: #2563EB !important;
            box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.12) !important;
        }

        div[data-testid="stCheckbox"],
        div[data-testid="stCheckbox"] label,
        div[data-testid="stCheckbox"] label p,
        div[data-testid="stCheckbox"] span,
        div[data-testid="stToggle"],
        div[data-testid="stToggle"] label,
        div[data-testid="stToggle"] label p,
        div[data-testid="stToggle"] span {
            color: #111827 !important;
            opacity: 1 !important;
        }

        div[data-testid="stCheckbox"] label p,
        div[data-testid="stToggle"] label p {
            font-size: 0.98rem !important;
            font-weight: 850 !important;
            line-height: 1.35 !important;
        }

        div[data-testid="stCheckbox"] [data-testid="stTooltipIcon"],
        div[data-testid="stToggle"] [data-testid="stTooltipIcon"],
        div[data-testid="stCheckbox"] svg,
        div[data-testid="stToggle"] svg {
            color: #64748B !important;
            fill: #64748B !important;
            opacity: 1 !important;
        }

        .settings-hint-grid {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 0.85rem !important;
            margin: 0.25rem 0 1.35rem !important;
        }

        .settings-hint-grid > div {
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            background: #F8FAFC !important;
            padding: 0.95rem !important;
        }

        .settings-hint-grid strong {
            display: block !important;
            color: #111827 !important;
            font-size: 0.95rem !important;
            font-weight: 900 !important;
            margin-bottom: 0.3rem !important;
        }

        .settings-hint-grid span {
            display: block !important;
            color: #64748B !important;
            font-size: 0.88rem !important;
            line-height: 1.4 !important;
            font-weight: 650 !important;
        }

        .settings-reset-area {
            margin-top: 1.2rem !important;
            padding-top: 1rem !important;
            border-top: 1px solid #E2E8F0 !important;
        }

        .settings-reset-area + div[data-testid="stButton"] button,
        div[data-testid="stButton"]:has(button[kind="secondary"]) button {
            min-height: 3.1rem !important;
            border-radius: 12px !important;
        }

        @media (max-width: 800px) {
            .settings-hint-grid {
                grid-template-columns: 1fr !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> str:
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <h2>AI Fake News Detection</h2>
            <p class="status-line"><span class="status-dot"></span>System Ready</p>
            <p>FACT-CHECKING TEAM</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    pages = [
        "Home",
        "Article",
        "Image",
        "Link",
        "Batch",
        "Performance",
        "Data",
        "History",
        "Settings",
    ]
    page_labels = {
        "Home": "Overview",
        "Article": "Article Check",
        "Image": "Image Check",
        "Link": "Link Check",
        "Batch": "Batch Upload",
        "Performance": "Insights",
        "Data": "Data Overview",
        "History": "Review Records",
        "Settings": "Workspace Settings",
    }
    page_icons = {
        "Home": ":material/home:",
        "Article": ":material/article:",
        "Image": ":material/image:",
        "Link": ":material/link:",
        "Batch": ":material/folder:",
        "Performance": ":material/monitoring:",
        "Data": ":material/database:",
        "History": ":material/history:",
        "Settings": ":material/settings:",
    }
    if st.session_state.get("nav_page_selected") not in pages:
        st.session_state["nav_page_selected"] = pages[0]
    selected = st.session_state["nav_page_selected"]

    def render_nav_button(page: str) -> None:
        clicked = st.sidebar.button(
            page_labels.get(page, page),
            key=f"nav_btn_{page}",
            type="primary" if page == selected else "secondary",
            icon=page_icons[page],
            use_container_width=True,
        )
        if clicked:
            st.session_state["nav_page_selected"] = page
            st.rerun()

    st.sidebar.markdown('<div class="sidebar-group-label">MAIN</div>', unsafe_allow_html=True)
    for page in ["Home", "Article", "Image", "Link", "Batch"]:
        render_nav_button(page)

    st.sidebar.markdown('<div class="sidebar-group-label">REPORTS</div>', unsafe_allow_html=True)
    for page in ["Performance", "Data", "History", "Settings"]:
        render_nav_button(page)

    selected = st.session_state["nav_page_selected"]
    status = business_status_label(model_status())
    st.sidebar.markdown(
        f"""
        <div class="workspace-card">
            <span class="workspace-avatar">⌾</span>
            <div><small>WORKSPACE</small><strong>Fact-Checking ...</strong></div>
        </div>
        <div class="sidebar-ready-card">
            <span>Review System {status}</span>
            <span>OCR Available</span>
            <span>Batch Ready</span>
        </div>
        <div class="sidebar-bottom">
            <div><span class="sidebar-icon">?</span><span>Help Center</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return selected


def _render_topbar() -> None:
    st.markdown(
        """
        <div class="top-shell">
            <div class="top-brand">
                <div class="top-logo" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 3 5 6v5c0 4.8 3 8.4 7 10 4-1.6 7-5.2 7-10V6l-7-3Z"/>
                        <path d="m9 12 2 2 4-4"/>
                    </svg>
                </div>
                <div>
                    <strong>Credibility Review Center</strong>
                    <span>News and social media risk screening</span>
                </div>
            </div>
            <div class="top-pill">AI review workspace</div>
            <div class="top-pill available">Ready for review</div>
            <div class="top-icons">♧ ⚙</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    for page_module in (about_model, batch_upload, check_news, dashboard, history, home, image_analysis, link_analysis, settings):
        importlib.reload(page_module)
    init_session_state()
    _load_theme()
    try:
        nav_target = st.query_params.get("nav")
    except Exception:
        nav_target = None

    if st.session_state.get("nav_page_request"):
        st.session_state["nav_page_selected"] = st.session_state.pop("nav_page_request")
    elif nav_target in {"Home", "Article", "Image", "Link", "Batch", "Performance", "Data", "History", "Settings"}:
        st.session_state["nav_page_selected"] = nav_target
        try:
            st.query_params.clear()
        except Exception:
            pass

    selected = _render_sidebar()
    _render_topbar()
    routes = {
        "Home": home.render,
        "Article": check_news.render,
        "Image": image_analysis.render,
        "Link": link_analysis.render,
        "Batch": batch_upload.render,
        "Performance": dashboard.render,
        "Data": about_model.render_dataset,
        "History": history.render,
        "Settings": settings.render,
    }
    routes[selected]()


if __name__ == "__main__":
    main()
