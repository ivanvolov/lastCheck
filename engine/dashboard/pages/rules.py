"""Page 3 — Rules editor."""
import sys
import time
from pathlib import Path

import streamlit as st
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from _shared import inject_css, page_header

RULES_PATH = Path(__file__).parent.parent.parent / "config" / "rules.yaml"

inject_css()
page_header("📋 Rules", "Edit the raw rules text and save to update the engine configuration")

st.markdown(
    "<div class='lc-panel' style='margin-bottom:12px'>"
    "<div class='lc-section-label'>Rules file</div>"
    "<div class='lc-card-line'>This editor writes directly to <code>engine/config/rules.yaml</code>. "
    "Paste or edit the full text, then click save.</div>"
    "</div>",
    unsafe_allow_html=True,
)

info_col, save_col = st.columns([5, 2])
info_col.markdown(
    "<div class='lc-card-subtle' style='padding-top:10px'>Review the YAML carefully before saving.</div>",
    unsafe_allow_html=True,
)
save_clicked = save_col.button("Save rules", type="primary", use_container_width=True)

raw_edit = st.text_area(
    "Rules YAML",
    value=RULES_PATH.read_text(),
    height=520,
    label_visibility="collapsed",
    key="raw_yaml",
)

st.markdown(
    "<div class='lc-card-subtle' style='margin-top:10px'>When you save, the full text replaces the current rules file immediately.</div>",
    unsafe_allow_html=True,
)

if save_clicked:
    try:
        yaml.safe_load(raw_edit)
        RULES_PATH.write_text(raw_edit)
        st.success("Rules updated.")
        time.sleep(0.4)
        st.rerun()
    except yaml.YAMLError as e:
        st.error(f"Invalid YAML: {e}")
