"""LastCheck Dashboard — entry point."""
from pathlib import Path

import streamlit as st

ICON_PATH = Path(__file__).parent / "iconLC.png"

st.set_page_config(page_title="LastCheck", page_icon=str(ICON_PATH), layout="wide")

pg = st.navigation([
    st.Page("pages/transactions.py", title="Transactions", icon="⚡", default=True),
    st.Page("pages/settings.py",     title="Settings",     icon="⚙️"),
    st.Page("pages/rules.py",        title="Rules",        icon="📋"),
])
pg.run()
