"""Shared CSS + helpers injected into every page."""
import streamlit as st

CSS = """
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], section.main {
    background-color: #0d0d14 !important;
    color: #e2e2f0;
}
[data-testid="stSidebar"]          { background-color: #0d0d14 !important; }
[data-testid="stSidebarNav"] a     { color: #9999bb !important; font-size: 0.85rem; }
[data-testid="stHeader"]           { background-color: #0d0d14 !important; }

/* cards */
.card {
    background: #16161f;
    border: 1px solid #2a2a3d;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
    font-size: 0.82rem;
}
.card-pending  { border-left: 3px solid #6366f1; }
.card-ai       { border-left: 3px solid #f59e0b; }
.card-flagged  { border-left: 3px solid #ef4444; }
.card-approved { border-left: 3px solid #22c55e; }

/* badges */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 99px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-pending  { background:#1e1e3a; color:#818cf8; }
.badge-ai       { background:#3a2a00; color:#fbbf24; }
.badge-flagged  { background:#3f1515; color:#ef4444; }
.badge-approved { background:#0d2b14; color:#22c55e; }

/* section labels */
.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #55556a;
    margin-bottom: 10px;
}

/* col headers */
.col-header {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #55556a;
    padding-bottom: 4px;
}

/* inputs */
input, textarea {
    background-color: #1c1c2a !important;
    border-color: #2e2e45 !important;
    color: #e2e2f0 !important;
    border-radius: 6px !important;
}

/* buttons */
.stButton > button {
    background: #6366f1 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
.stButton > button:hover { background: #4f46e5 !important; }
.stButton > button:disabled {
    background: #2a2a3d !important;
    color: #55556a !important;
}

/* empty state */
.empty-state {
    text-align: center;
    color: #3a3a55;
    padding: 40px 0;
    font-size: 0.85rem;
}

hr { border-color: #2a2a3d !important; }
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"<h1 style='font-size:1.4rem;font-weight:700;margin-bottom:2px'>{title}</h1>"
        + (f"<p style='color:#55556a;margin-top:0;font-size:0.82rem'>{subtitle}</p>" if subtitle else ""),
        unsafe_allow_html=True,
    )
