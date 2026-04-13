"""LastCheck Dashboard — entry point."""
import streamlit as st

st.set_page_config(page_title="LastCheck", page_icon="🛡️", layout="wide")

pg = st.navigation([
    st.Page("pages/transactions.py", title="Transactions", icon="⚡", default=True),
    st.Page("pages/settings.py",     title="Settings",     icon="⚙️"),
    st.Page("pages/rules.py",        title="Rules",        icon="📋"),
])
pg.run()
