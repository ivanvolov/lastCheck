"""Page 2 — Settings (read from .env; SAFE_ADDRESS is editable)."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from _shared import inject_css, page_header

ENV_PATH = Path(__file__).parent.parent.parent / ".env"

inject_css()
page_header("⚙️ Settings", "Runtime configuration · restart the engine after changes")


# ── parse / write .env ───────────────────────────────────────────────────────

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


def write_env_key(path: Path, key: str, value: str):
    """Update or append a single key in the .env file."""
    lines = path.read_text().splitlines() if path.exists() else []
    found = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped == key:
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{key}={value}")
    path.write_text("\n".join(new_lines) + "\n")


env = parse_env(ENV_PATH)

SENSITIVE = {"TELEGRAM_TOKEN", "OPENAI_API_KEY", "ETH_RPC_URL"}
PRIVATE   = {"AGENT_PRIVATE_KEY"}
EDITABLE  = {"SAFE_ADDRESS"}

LABELS = {
    "TELEGRAM_TOKEN":   ("Telegram bot token",        "From @BotFather"),
    "TELEGRAM_CHAT_ID": ("Telegram chat ID",           "Your personal or group chat"),
    "ETH_RPC_URL":      ("Arbitrum RPC endpoint",      "Infura / Alchemy URL"),
    "SAFE_ADDRESS":     ("Gnosis Safe address",        "Your Safe on Arbitrum — required for tx monitoring"),
    "FIRST_SIGNER":     ("First signer address",       "Your wallet — Safe owner #1"),
    "OPENAI_API_KEY":   ("OpenAI API key",             "Used for voice transcription"),
    "DASHBOARD_PORT":   ("Dashboard port",             "Streamlit server port"),
}

ORDER = ["SAFE_ADDRESS", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID", "ETH_RPC_URL",
         "FIRST_SIGNER", "OPENAI_API_KEY", "DASHBOARD_PORT"]


# ── render ───────────────────────────────────────────────────────────────────

for key in ORDER:
    val = env.get(key, "")
    label, hint = LABELS.get(key, (key, ""))

    is_missing = key in EDITABLE and not val

    st.markdown(
        f"<div style='font-size:0.75rem;font-weight:700;"
        f"color:{'#ef4444' if is_missing else '#9999bb'};margin-bottom:2px'>"
        f"{label} <span style='color:#3a3a55;font-weight:400'>· {hint}</span>"
        f"{'  <span style=\"color:#ef4444\">⚠ not set</span>' if is_missing else ''}"
        f"</div>",
        unsafe_allow_html=True,
    )

    if key in PRIVATE:
        st.markdown(
            "<div class='card' style='color:#3a3a55;font-size:0.8rem'>🔒 Hidden for security</div>",
            unsafe_allow_html=True,
        )

    elif key in EDITABLE:
        col_input, col_btn = st.columns([5, 1])
        new_val = col_input.text_input(
            label,
            value=val,
            placeholder="0x…",
            label_visibility="collapsed",
            key=f"edit_{key}",
        )
        if col_btn.button("Save", key=f"save_{key}"):
            write_env_key(ENV_PATH, key, new_val.strip())
            st.success(f"Saved. Restart the engine for changes to take effect.")
            st.rerun()

    elif key in SENSITIVE:
        visible = st.toggle("Show", key=f"show_{key}", value=False)
        if visible:
            st.code(val or "(not set)", language=None)
        else:
            masked = ("•" * 12) if val else "(not set)"
            st.markdown(
                f"<div class='card' style='font-family:monospace;font-size:0.8rem;color:#55556a'>"
                f"{masked}</div>",
                unsafe_allow_html=True,
            )

    else:
        st.code(val or "(not set)", language=None)

    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)


st.divider()
st.markdown(
    "<div style='color:#3a3a55;font-size:0.78rem'>"
    "Sensitive values (tokens, keys) can be shown with the toggle. "
    "The agent private key is never displayed. "
    "After editing, restart with <code>make engine-local</code>."
    "</div>",
    unsafe_allow_html=True,
)
