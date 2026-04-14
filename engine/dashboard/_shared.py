"""Shared CSS + helpers injected into every page."""
import streamlit as st

CSS = """
:root {
    --lc-bg: #0a0805;
    --lc-bg-soft: #120e09;
    --lc-panel: rgba(24, 18, 11, 0.92);
    --lc-line: rgba(255, 176, 74, 0.42);
    --lc-line-strong: rgba(255, 188, 92, 0.68);
    --lc-text: #f7efe3;
    --lc-muted: #c5b59d;
    --lc-muted-soft: #7f6f58;
    --lc-accent: #ff9b1f;
    --lc-accent-strong: #ffb04a;
    --lc-danger: #ef4444;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    background:
      radial-gradient(circle at 12% 0%, rgba(255, 176, 74, 0.2), transparent 30%),
      radial-gradient(circle at 88% 0%, rgba(212, 120, 0, 0.18), transparent 26%),
      linear-gradient(180deg, #0b0906 0%, #090705 100%) !important;
    color: var(--lc-text);
}

[data-testid="stSidebar"] { background: #14100b !important; border-right: 1px solid var(--lc-line-strong); }
[data-testid="stSidebarNav"] a { color: #f2e6d4 !important; font-size: 0.96rem; border-radius: 14px; font-weight: 650; padding: 0.35rem 0.55rem !important; }
[data-testid="stSidebarNav"] a:hover { color: #fff5e8 !important; background: rgba(255,155,31,0.2) !important; }
[data-testid="stSidebarNav"] a[aria-current="page"] { color: #fff7ed !important; background: linear-gradient(90deg, rgba(255,176,74,0.28), rgba(212,120,0,0.22)) !important; box-shadow: inset 0 0 0 1px rgba(255,176,74,0.28); }
[data-testid="stSidebarNav"] a span { color: inherit !important; opacity: 1 !important; }

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"],
[data-testid="stHeaderActionElements"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"],
[data-testid="stCodeCopyButton"] { display: none !important; }
#MainMenu, footer { visibility: hidden !important; height: 0 !important; }
[data-testid="stMainBlockContainer"] { max-width: 1320px !important; padding-top: 1rem !important; padding-bottom: 1.2rem !important; }

.lc-header {
    margin-bottom: 14px;
}
.lc-title {
    margin: 0;
    font-size: 1.55rem;
    font-weight: 760;
    letter-spacing: -0.01em;
}
.lc-subtitle {
    margin: 0.25rem 0 0;
    color: var(--lc-muted);
    font-size: 0.84rem;
}

.lc-kpi {
    background: rgba(20, 15, 10, 0.94);
    border: 1px solid var(--lc-line);
    border-radius: 12px;
    padding: 10px 12px;
}
.lc-kpi-label {
    color: var(--lc-muted);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
}
.lc-kpi-value {
    margin-top: 4px;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--lc-text);
}

.lc-panel {
    background: linear-gradient(180deg, rgba(22, 16, 10, 0.94) 0%, rgba(16, 12, 8, 0.94) 100%);
    border: 1px solid var(--lc-line-strong);
    border-radius: 14px;
    padding: 12px;
}
.lc-board {
    min-height: 0;
}
.lc-panel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.lc-panel-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--lc-muted);
    font-weight: 800;
}
.lc-panel-count {
    color: var(--lc-accent-strong);
    font-size: 0.74rem;
    font-weight: 700;
}

.lc-card {
    background: rgba(15, 11, 8, 0.72);
    border: 1px solid rgba(255, 155, 31, 0.18);
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    font-size: 0.8rem;
}
.lc-card:last-child {
    margin-bottom: 0;
}
.lc-card-line {
    color: var(--lc-muted);
    line-height: 1.45;
}
.lc-card-primary {
    color: var(--lc-text);
    font-weight: 600;
}
.lc-card-subtle {
    color: var(--lc-muted-soft);
    font-size: 0.74rem;
}
.lc-pending { border-left: 3px solid var(--lc-accent-strong); }
.lc-ai { border-left: 3px solid var(--lc-accent); }
.lc-flagged { border-left: 3px solid var(--lc-danger); }
.lc-approved { border-left: 3px solid #22c55e; }

.lc-badge {
    border-radius: 999px;
    padding: 2px 7px;
    font-size: 0.64rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-weight: 700;
}
.lc-badge-pending { background: #2d1f0a; color: var(--lc-accent-strong); }
.lc-badge-ai { background: #3a2200; color: var(--lc-accent); }
.lc-badge-flagged { background: #3f1515; color: var(--lc-danger); }
.lc-badge-approved { background: #102616; color: #7ef0a7; }

.lc-section-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--lc-muted);
    font-weight: 800;
    margin-bottom: 6px;
}

.lc-empty {
    text-align: center;
    color: var(--lc-muted-soft);
    padding: 18px 8px 8px;
    font-size: 0.82rem;
}

/* backward-compatible aliases for existing markup */
.card { background: var(--lc-panel); border: 1px solid var(--lc-line); border-radius: 10px; padding: 10px 12px; }
.section-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--lc-muted); font-weight: 800; margin-bottom: 6px; }
.col-header { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--lc-muted); font-weight: 700; }

hr { border-color: var(--lc-line) !important; }
[data-testid="stTextInput"] > div > div > input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] {
    background: #16110b !important;
    border: 1px solid var(--lc-line) !important;
    color: var(--lc-text) !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label {
    color: var(--lc-muted) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--lc-accent-strong) 0%, var(--lc-accent) 55%, #d47800 100%) !important;
    color: #1a1004 !important;
    border: 1px solid rgba(255, 176, 74, 0.35) !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
.stButton > button:hover { background: var(--lc-accent-strong) !important; }
.stButton > button:disabled { background: #252525 !important; color: #6d6d6d !important; }

.stButton > button:focus {
    box-shadow: 0 0 0 2px rgba(255, 176, 74, 0.28) !important;
}
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        "<div class='lc-header'>"
        f"<h1 class='lc-title'>{title}</h1>"
        + (f"<p class='lc-subtitle'>{subtitle}</p>" if subtitle else "")
        + "</div>",
        unsafe_allow_html=True,
    )
