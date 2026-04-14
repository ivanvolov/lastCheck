"""Page 2 — Settings (read-only from .env)."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from _shared import inject_css, page_header

ENV_PATH = Path(__file__).parent.parent.parent / ".env"

inject_css()
page_header("⚙️ Settings", "Runtime configuration · read-only view")
st.markdown(
    "<div class='lc-panel' style='margin-bottom:12px'>"
    "<div class='lc-section-label'>Configuration Source</div>"
    "<div class='lc-card-line'>Read-only snapshot from <code>engine/.env</code>. "
    "Edit the file directly, then restart engine services.</div>"
    "</div>",
    unsafe_allow_html=True,
)


def parse_env(path: Path) -> dict:
    result = {}
    if not path.exists():
        return result
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip()
    return result


def masked_value(value: str) -> str:
    return "•" * 12 if value else "(not set)"


env = parse_env(ENV_PATH)

SENSITIVE = {"TELEGRAM_TOKEN", "OPENAI_API_KEY", "ETH_RPC_URL"}
PRIVATE = {"AGENT_PRIVATE_KEY"}

LABELS = {
    "SAFE_ADDRESS": ("Gnosis Safe address", "Protected Safe on Arbitrum"),
    "FIRST_SIGNER": ("First signer address", "Safe owner #1 wallet"),
    "ETH_RPC_URL": ("Arbitrum RPC endpoint", "Provider URL"),
    "TELEGRAM_TOKEN": ("Telegram bot token", "From @BotFather"),
    "TELEGRAM_CHAT_ID": ("Telegram chat ID", "Personal or group chat"),
    "OPENAI_API_KEY": ("OpenAI API key", "Voice transcription"),
    "DASHBOARD_PORT": ("Dashboard port", "Streamlit server port"),
}

GROUPS = {
    "Core runtime": ["SAFE_ADDRESS", "FIRST_SIGNER", "ETH_RPC_URL"],
    "Bot integration": ["TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"],
    "AI and dashboard": ["OPENAI_API_KEY", "DASHBOARD_PORT"],
}

cols = st.columns(3)
for i, (group_name, keys) in enumerate(GROUPS.items()):
    target = cols[i]
    target.markdown(f"<div class='lc-panel'><div class='lc-section-label'>{group_name}</div>", unsafe_allow_html=True)
    for key in keys:
        val = env.get(key, "")
        label, hint = LABELS.get(key, (key, ""))

        if key in PRIVATE:
            rendered = "Hidden for security"
        elif key in SENSITIVE:
            rendered = masked_value(val)
        else:
            rendered = val or "(not set)"

        target.markdown(
            f"<div class='lc-card'>"
            f"<div class='lc-card-subtle' style='font-weight:700;color:#c5b59d'>{label}</div>"
            f"<div class='lc-card-subtle' style='margin:2px 0 7px'>{hint}</div>"
            f"<div class='lc-card-primary' style='font-family:monospace;font-size:0.78rem;word-break:break-all'>{rendered}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    target.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.markdown(
    "<div class='lc-card-subtle' style='font-size:0.78rem'>"
    "Settings are read-only in the dashboard. Edit <code>engine/.env</code> directly, then restart "
    "with <code>make engine-local</code> or <code>make engine</code>."
    "</div>",
    unsafe_allow_html=True,
)
