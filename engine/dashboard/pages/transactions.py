"""Page 1 — Transaction monitor."""
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from _shared import inject_css, page_header

TX_API = "http://127.0.0.1:8502/transactions"

inject_css()
page_header("⚡ Transactions", "Live transaction pipeline · auto-refreshes every 3 s")


# ── fetch ────────────────────────────────────────────────────────────────────

def load_txs() -> tuple[list, bool]:
    """Returns (txs, engine_online)."""
    try:
        resp = requests.get(TX_API, timeout=1.5)
        return resp.json(), True
    except Exception:
        return [], False


def fmt_addr(addr: str) -> str:
    if not addr or len(addr) < 10:
        return addr or "—"
    return addr[:8] + "…" + addr[-4:]


def fmt_time(ts) -> str:
    try:
        return datetime.fromtimestamp(float(ts)).strftime("%H:%M:%S")
    except Exception:
        return "—"


def tx_card_html(tx: dict, border_class: str, badge_class: str, badge_label: str) -> str:
    h = tx.get("hash", "")
    extra = ""
    if tx.get("flag_reason"):
        extra += f"<div class='lc-card-subtle' style='color:#ef4444;margin-top:6px'>⛔ {tx['flag_reason']}</div>"
    if tx.get("flagged_by"):
        extra += f"<div class='lc-card-subtle'>Flagged by: {tx['flagged_by'].replace('_',' ').title()}</div>"
    if tx.get("telegram_sent"):
        extra += "<div class='lc-card-subtle' style='color:#ffb04a'>Telegram alert sent</div>"
    if tx.get("is_erc20_approval"):
        spender = fmt_addr(tx.get("spender", ""))
        amt = tx.get("approval_amount", 0)
        amt_str = "unlimited" if amt >= 2**255 else f"{amt:.0f}"
        extra += f"<div class='lc-card-subtle' style='color:#ff9b1f'>ERC-20 approve · spender {spender} · {amt_str}</div>"

    return f"""
    <div class="lc-card {border_class}">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
        <span class="lc-card-subtle" style="font-family:monospace">{fmt_addr(h)}</span>
        <span class="lc-badge {badge_class}">{badge_label}</span>
      </div>
      <div class="lc-card-line" style="margin-top:8px">
        To: <span class="lc-card-primary" style="font-family:monospace">{fmt_addr(tx.get('to',''))}</span>
        {"<span class='lc-card-subtle'> · contract</span>" if tx.get('is_contract') else ""}
      </div>
      <div class="lc-card-line">
        Value: <b class="lc-card-primary">${tx.get('value_usd', 0):,.2f}</b>
        &nbsp;·&nbsp; {fmt_time(tx.get('timestamp'))}
      </div>
      {extra}
    </div>
    """


def render_lane(column, title: str, count: int, cards_html: str, empty_text: str):
    content = cards_html or f"<div class='lc-empty'>{empty_text}</div>"
    column.markdown(
        f"""
        <div class="lc-panel lc-board">
          <div class="lc-panel-head">
            <span class="lc-panel-title">{title}</span>
            <span class="lc-panel-count">{count}</span>
          </div>
          {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── load + status banner ─────────────────────────────────────────────────────

txs, online = load_txs()

if not online:
    st.markdown(
        "<div class='lc-panel' style='border-color:#5a1a1a;color:#ef4444;margin-bottom:16px'>"
        "Engine offline - start the bot with <code>make engine-local</code></div>",
        unsafe_allow_html=True,
    )


# ── columns ──────────────────────────────────────────────────────────────────

pending   = [t for t in txs if t.get("status") == "pending"]
ai_review = [t for t in txs if t.get("status") == "ai_review"]
flagged   = [t for t in txs if t.get("status") in ("flagged", "rejected")]
approved  = [t for t in txs if t.get("status") == "approved"]

# overview strip
k1, k2, k3, k4 = st.columns(4)
k1.markdown(
    f"<div class='lc-kpi'><div class='lc-kpi-label'>Incoming</div><div class='lc-kpi-value'>{len(pending)}</div></div>",
    unsafe_allow_html=True,
)
k2.markdown(
    f"<div class='lc-kpi'><div class='lc-kpi-label'>AI Review</div><div class='lc-kpi-value'>{len(ai_review)}</div></div>",
    unsafe_allow_html=True,
)
k3.markdown(
    f"<div class='lc-kpi'><div class='lc-kpi-label'>Blocked</div><div class='lc-kpi-value'>{len(flagged)}</div></div>",
    unsafe_allow_html=True,
)
k4.markdown(
    f"<div class='lc-kpi'><div class='lc-kpi-label'>Approved</div><div class='lc-kpi-value'>{len(approved)}</div></div>",
    unsafe_allow_html=True,
)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

render_lane(
    col1,
    "Incoming",
    len(pending),
    "".join(tx_card_html(t, "lc-pending", "lc-badge-pending", "pending") for t in pending[:20]),
    "No pending transactions",
)
render_lane(
    col2,
    "AI Review",
    len(ai_review),
    "".join(tx_card_html(t, "lc-ai", "lc-badge-ai", "in review") for t in ai_review[:20]),
    "Nothing in review",
)
render_lane(
    col3,
    "Blocked",
    len(flagged),
    "".join(tx_card_html(t, "lc-flagged", "lc-badge-flagged", t.get("flagged_by") or "blocked") for t in flagged[:20]),
    "No blocked transactions",
)


# ── approved summary bar ─────────────────────────────────────────────────────

if approved:
    st.markdown(
        f"<div class='lc-card-subtle' style='text-align:center;margin-top:10px;color:#ffb04a'>"
        f"{len(approved)} transaction{'s' if len(approved) != 1 else ''} approved this session</div>",
        unsafe_allow_html=True,
    )


# ── auto-refresh ─────────────────────────────────────────────────────────────

ctrl_l, ctrl_r = st.columns([7, 1])
ctrl_l.markdown("<div class='lc-card-subtle'>Auto refresh interval: 3 seconds</div>", unsafe_allow_html=True)
auto = ctrl_r.toggle("Auto", value=True, key="auto_refresh")
if auto:
    time.sleep(3)
    st.rerun()
