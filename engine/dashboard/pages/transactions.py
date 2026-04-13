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


def tx_card(tx: dict, border_class: str, badge_class: str, badge_label: str):
    h = tx.get("hash", "")
    extra = ""
    if tx.get("flag_reason"):
        extra += f"<div style='color:#ef4444;margin-top:6px;font-size:0.75rem'>⛔ {tx['flag_reason']}</div>"
    if tx.get("flagged_by"):
        extra += f"<div style='color:#55556a;font-size:0.72rem'>Flagged by: {tx['flagged_by'].replace('_',' ').title()}</div>"
    if tx.get("telegram_sent"):
        extra += "<div style='color:#818cf8;font-size:0.72rem'>📨 Sent to Telegram</div>"
    if tx.get("is_erc20_approval"):
        spender = fmt_addr(tx.get("spender", ""))
        amt = tx.get("approval_amount", 0)
        amt_str = "unlimited" if amt >= 2**255 else f"{amt:.0f}"
        extra += f"<div style='color:#f59e0b;font-size:0.72rem'>ERC-20 approve · spender {spender} · {amt_str}</div>"

    st.markdown(
        f"""
        <div class="card {border_class}">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-family:monospace;font-size:0.78rem;color:#9999cc">{fmt_addr(h)}</span>
            <span class="badge {badge_class}">{badge_label}</span>
          </div>
          <div style="margin-top:8px;color:#9999bb">
            To: <span style="font-family:monospace">{fmt_addr(tx.get('to',''))}</span>
            {"<span style='color:#55556a'> · contract</span>" if tx.get('is_contract') else ""}
          </div>
          <div style="color:#9999bb">
            Value: <b style="color:#e2e2f0">${tx.get('value_usd', 0):,.2f}</b>
            &nbsp;·&nbsp; {fmt_time(tx.get('timestamp'))}
          </div>
          {extra}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── load + status banner ─────────────────────────────────────────────────────

txs, online = load_txs()

if not online:
    st.markdown(
        "<div style='background:#2a0a0a;border:1px solid #5a1a1a;border-radius:8px;"
        "padding:10px 16px;color:#ef4444;font-size:0.82rem;margin-bottom:16px'>"
        "🔴 Engine offline — start the bot with <code>make engine-local</code></div>",
        unsafe_allow_html=True,
    )


# ── columns ──────────────────────────────────────────────────────────────────

pending   = [t for t in txs if t.get("status") == "pending"]
ai_review = [t for t in txs if t.get("status") == "ai_review"]
flagged   = [t for t in txs if t.get("status") in ("flagged", "rejected")]
approved  = [t for t in txs if t.get("status") == "approved"]

col1, col2, col3 = st.columns(3)

with col1:
    count = len(pending)
    cnt_html = f'<span style="color:#818cf8">({count})</span>' if count else ""
    st.markdown(f"<div class='section-label'>🔵 Incoming {cnt_html}</div>", unsafe_allow_html=True)
    if pending:
        for t in pending[:20]:
            tx_card(t, "card-pending", "badge-pending", "pending")
    else:
        st.markdown("<div class='empty-state'>No pending transactions</div>", unsafe_allow_html=True)

with col2:
    count = len(ai_review)
    cnt_html = f'<span style="color:#fbbf24">({count})</span>' if count else ""
    st.markdown(f"<div class='section-label'>🟡 AI Review {cnt_html}</div>", unsafe_allow_html=True)
    if ai_review:
        for t in ai_review[:20]:
            tx_card(t, "card-ai", "badge-ai", "AI review")
    else:
        st.markdown("<div class='empty-state'>Nothing in review</div>", unsafe_allow_html=True)

with col3:
    count = len(flagged)
    cnt_html = f'<span style="color:#ef4444">({count})</span>' if count else ""
    st.markdown(f"<div class='section-label'>🔴 Blocked {cnt_html}</div>", unsafe_allow_html=True)
    if flagged:
        for t in flagged[:20]:
            tx_card(t, "card-flagged", "badge-flagged", t.get("flagged_by") or "blocked")
    else:
        st.markdown("<div class='empty-state'>No blocked transactions</div>", unsafe_allow_html=True)


# ── approved summary bar ─────────────────────────────────────────────────────

if approved:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='color:#22c55e;font-size:0.78rem;text-align:center'>"
        f"✅ {len(approved)} transaction{'s' if len(approved) != 1 else ''} approved this session</div>",
        unsafe_allow_html=True,
    )


# ── auto-refresh ─────────────────────────────────────────────────────────────

_, rc = st.columns([8, 1])
auto = rc.toggle("Auto", value=True, key="auto_refresh")
if auto:
    time.sleep(3)
    st.rerun()
