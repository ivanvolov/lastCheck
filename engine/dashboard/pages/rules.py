"""Page 3 — Rules editor (allowlist, blocklist, token caps, raw YAML)."""
import sys
import time
from pathlib import Path

import streamlit as st
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from _shared import inject_css, page_header

RULES_PATH = Path(__file__).parent.parent.parent / "config" / "rules.yaml"

inject_css()
page_header("📋 Rules", "Firewall configuration · changes are picked up on the next transaction")
st.markdown(
    "<div class='lc-panel' style='margin-bottom:12px'>"
    "<div class='lc-section-label'>Editor</div>"
    "<div class='lc-card-line'>Tune contract allow/block lists, token spend limits, and raw YAML overrides. "
    "Changes apply to the next transaction checks after save.</div></div>",
    unsafe_allow_html=True,
)

# ── common Arbitrum tokens ────────────────────────────────────────────────────

TOKENS = [
    {"symbol": "ETH",    "name": "Ethereum",         "address": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"},
    {"symbol": "WBTC",   "name": "Wrapped Bitcoin",  "address": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"},
    {"symbol": "USDC",   "name": "USD Coin",          "address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"},
    {"symbol": "USDC.e", "name": "Bridged USDC",      "address": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"},
    {"symbol": "USDT",   "name": "Tether",            "address": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"},
    {"symbol": "ARB",    "name": "Arbitrum",          "address": "0x912CE59144191C1204E64559FE8253a0e49E6548"},
    {"symbol": "LINK",   "name": "Chainlink",         "address": "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4"},
    {"symbol": "UNI",    "name": "Uniswap",           "address": "0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0"},
    {"symbol": "AAVE",   "name": "Aave",              "address": "0xba5DdD1f9d7F570dc94a51479a000E3BCE967196"},
    {"symbol": "GMX",    "name": "GMX",               "address": "0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a"},
    {"symbol": "PENDLE", "name": "Pendle",            "address": "0x0c880f6761F1af8d9Aa9C466984b80DAb9a8c9e8"},
    {"symbol": "RDNT",   "name": "Radiant",           "address": "0x3082CC23568eA640225c2467653dB90e9250AaA0"},
    {"symbol": "GNS",    "name": "Gains Network",     "address": "0x18c11FD286C5EC11c3b683Caa813B77f5163A122"},
    {"symbol": "MAGIC",  "name": "Magic",             "address": "0x539bdE0d7Dbd336b79148AA742883198BBF60342"},
    {"symbol": "DPX",    "name": "Dopex",             "address": "0x6C2C06790b3E3E3c38e12Ee22F8183b37a13EE55"},
]
TOKEN_SYMBOLS = [f"{t['symbol']} — {t['name']}" for t in TOKENS]
SYMBOL_MAP    = {f"{t['symbol']} — {t['name']}": t for t in TOKENS}

# ── load / save ───────────────────────────────────────────────────────────────

def load_doc() -> dict:
    raw = RULES_PATH.read_text()
    return yaml.safe_load(raw) or {}, raw

def save_doc(doc: dict):
    with open(RULES_PATH, "w") as f:
        yaml.dump(doc, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

doc, original_yaml = load_doc()


# ── state for change detection ────────────────────────────────────────────────

if "rules_original" not in st.session_state:
    st.session_state.rules_original = original_yaml


# ── allowlist ────────────────────────────────────────────────────────────────

allowlist = doc.get("allowlist", {}).get("contracts", []) or []
al_active = len(allowlist) > 0

st.markdown(
    f"<div class='lc-panel' style='margin-bottom:10px'><div class='lc-section-label'>Allowlist "
    f"<span style='color:{'#ffb04a' if al_active else '#7f6f58'}'>"
    f"{'● active' if al_active else '○ empty — inactive'}</span></div>",
    unsafe_allow_html=True,
)
al_text = st.text_area(
    "Allowlisted contracts",
    value="\n".join(allowlist),
    height=90,
    placeholder="0x… one address per line · leave empty to disable",
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)


# ── blocklist ────────────────────────────────────────────────────────────────

blocklist = doc.get("blocklist", {}).get("addresses", []) or []
bl_active = len(blocklist) > 0

st.markdown(
    f"<div class='lc-panel' style='margin-bottom:10px'><div class='lc-section-label'>Blocklist "
    f"<span style='color:{'#ef4444' if bl_active else '#7f6f58'}'>"
    f"{'● active' if bl_active else '○ empty — inactive'}</span></div>",
    unsafe_allow_html=True,
)
bl_text = st.text_area(
    "Blocklisted addresses",
    value="\n".join(blocklist),
    height=90,
    placeholder="0x… one address per line · leave empty to disable",
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)


# ── token caps ───────────────────────────────────────────────────────────────

st.markdown("<div class='lc-panel' style='margin-bottom:10px'><div class='lc-section-label'>Token caps</div>", unsafe_allow_html=True)

existing_caps: list[dict] = doc.get("token_caps", []) or []

# header row
hc = st.columns([2, 2, 2, 2, 2, 1])
for col, lbl in zip(hc, ["Token", "Hourly ($)", "Daily ($)", "Weekly ($)", "Monthly ($)", ""]):
    col.markdown(f"<div class='col-header'>{lbl}</div>", unsafe_allow_html=True)

# build index of existing caps by symbol for pre-fill
cap_by_symbol = {c["symbol"]: c for c in existing_caps}

if "cap_rows" not in st.session_state:
    st.session_state.cap_rows = [
        {**cap_by_symbol[s], "_sel": f"{s} — {next((t['name'] for t in TOKENS if t['symbol'] == s), s)}"}
        for s in cap_by_symbol
    ] if cap_by_symbol else []

new_cap_rows = []
to_delete = set()

for i, row in enumerate(st.session_state.cap_rows):
    c_tok, c_h, c_d, c_w, c_m, c_del = st.columns([2, 2, 2, 2, 2, 1])
    sel = c_tok.selectbox("Token", TOKEN_SYMBOLS, index=TOKEN_SYMBOLS.index(row["_sel"]) if row.get("_sel") in TOKEN_SYMBOLS else 0, key=f"cap_tok_{i}", label_visibility="collapsed")
    h   = c_h.number_input("Hourly",   min_value=0, value=row.get("hourly")   or 0, step=100, key=f"cap_h_{i}",   label_visibility="collapsed")
    d   = c_d.number_input("Daily",    min_value=0, value=row.get("daily")    or 0, step=100, key=f"cap_d_{i}",   label_visibility="collapsed")
    w   = c_w.number_input("Weekly",   min_value=0, value=row.get("weekly")   or 0, step=100, key=f"cap_w_{i}",   label_visibility="collapsed")
    m   = c_m.number_input("Monthly",  min_value=0, value=row.get("monthly")  or 0, step=100, key=f"cap_m_{i}",   label_visibility="collapsed")
    if c_del.button("✕", key=f"cap_del_{i}"):
        to_delete.add(i)
    else:
        tok_data = SYMBOL_MAP[sel]
        new_cap_rows.append({
            "_sel":    sel,
            "symbol":  tok_data["symbol"],
            "address": tok_data["address"],
            "hourly":  h or None,
            "daily":   d or None,
            "weekly":  w or None,
            "monthly": m or None,
        })

st.session_state.cap_rows = new_cap_rows

# add token button
used_symbols = {r["symbol"] for r in st.session_state.cap_rows}
available = [s for s in TOKEN_SYMBOLS if SYMBOL_MAP[s]["symbol"] not in used_symbols]
if available:
    _, add_col = st.columns([7, 2])
    if add_col.button("Add token cap"):
        first = SYMBOL_MAP[available[0]]
        st.session_state.cap_rows.append({
            "_sel": available[0], "symbol": first["symbol"], "address": first["address"],
            "hourly": None, "daily": None, "weekly": None, "monthly": None,
        })
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# ── raw YAML (always visible) ─────────────────────────────────────────────────

st.markdown("<div class='lc-panel'><div class='lc-section-label'>Raw YAML</div>", unsafe_allow_html=True)
raw_edit = st.text_area(
    "Raw YAML",
    value=RULES_PATH.read_text(),
    height=350,
    label_visibility="collapsed",
    key="raw_yaml",
)
st.markdown("</div>", unsafe_allow_html=True)


# ── save ─────────────────────────────────────────────────────────────────────

save_left, save_col = st.columns([6, 2])
save_left.markdown("<div class='lc-card-subtle'>Save writes structured fields unless raw YAML was edited.</div>", unsafe_allow_html=True)
if save_col.button("Save rules", type="primary"):
    # build new doc from UI state
    new_doc = {
        "allowlist":  {"contracts":  [a.strip() for a in al_text.splitlines() if a.strip()]},
        "blocklist":  {"addresses":  [a.strip() for a in bl_text.splitlines() if a.strip()]},
        "token_caps": [
            {k: v for k, v in row.items() if not k.startswith("_")}
            for row in st.session_state.cap_rows
        ],
        "rules": doc.get("rules", []),
    }

    # if raw YAML was edited, prefer that (validate first)
    current_file = RULES_PATH.read_text()
    if raw_edit.strip() != current_file.strip():
        try:
            parsed = yaml.safe_load(raw_edit)
            RULES_PATH.write_text(raw_edit)
            st.session_state.rules_original = raw_edit
            st.success("Saved from raw YAML.")
            time.sleep(0.4)
            st.rerun()
        except yaml.YAMLError as e:
            st.error(f"Invalid YAML: {e}")
    else:
        save_doc(new_doc)
        st.session_state.rules_original = RULES_PATH.read_text()
        st.success("Saved.")
        time.sleep(0.4)
        st.rerun()
