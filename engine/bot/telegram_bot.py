"""
LastCheck Telegram Bot
- Pairs with a single chat via an ephemeral /start <code> handshake.
  The chat id lives in RAM only — not in env, not on disk.
- Sends tx approval requests with inline [Approve] / [Reject] buttons.
- /connect_safe lets the user set the Safe address at runtime.
- Handles voice messages: transcribes → parses intent → patches rules.yaml.
"""

import asyncio
import logging
import os
import secrets
from pathlib import Path

import yaml
from eth_account import Account
from openai import AsyncOpenAI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

ENGINE_ROOT = Path(__file__).parent.parent
RULES_PATH = ENGINE_ROOT / "config" / "rules.yaml"
TMP_DIR = ENGINE_ROOT / "tmp"
KEY_PATH = TMP_DIR / ".agent_key"
ENV_PATH = ENGINE_ROOT / ".env"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ETH_RPC_URL = os.environ.get("ETH_RPC_URL", "")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# ── .env persistence (same format the dashboard uses) ──────────────────────

def _write_env_key(key: str, value: str) -> None:
    """Upsert a single KEY=value line in engine/.env."""
    lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
    out, found = [], False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped == key:
            out.append(f"{key}={value}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(out) + "\n")


# ── Runtime state (seeded from env, persisted back on change) ──────────────

_pending: dict[str, asyncio.Future] = {}

_env_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
_chat_id: int | None = int(_env_chat_id) if _env_chat_id else None

_safe_address: str | None = (os.environ.get("SAFE_ADDRESS", "").strip() or None)
_pairing_code: str = secrets.token_hex(4)
_awaiting_safe_addr: bool = False

_app_instance: Application | None = None


def _get_app() -> Application:
    if _app_instance is None:
        raise RuntimeError("Bot not started")
    return _app_instance


# ── Keypair management ──────────────────────────────────────────────────────

def load_or_create_keypair() -> tuple[str, str]:
    """Returns (private_key, address). Priority: env > file > generate."""
    env_key = os.environ.get("AGENT_PRIVATE_KEY", "").strip()
    if env_key:
        private_key = env_key
    elif KEY_PATH.exists():
        private_key = KEY_PATH.read_text().strip()
    else:
        account = Account.create()
        private_key = account.key.hex()
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        KEY_PATH.write_text(private_key)
        KEY_PATH.chmod(0o600)
        log.info("Generated new agent keypair → %s", KEY_PATH)
    account = Account.from_key(private_key)
    return private_key, account.address


def has_agent_key() -> bool:
    return bool(os.environ.get("AGENT_PRIVATE_KEY", "").strip()) or KEY_PATH.exists()


# ── Pairing / onboarding ────────────────────────────────────────────────────

async def _start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _chat_id
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "Send `/start <pairing-code>` — the code is printed in the agent's startup logs.",
            parse_mode="Markdown",
        )
        return
    if args[0].strip() != _pairing_code:
        await update.message.reply_text("❌ Invalid pairing code.")
        return
    if _chat_id is not None and _chat_id != update.effective_chat.id:
        await update.message.reply_text("Agent is already paired with another chat.")
        return

    _chat_id = update.effective_chat.id
    _write_env_key("TELEGRAM_CHAT_ID", str(_chat_id))
    log.info("Paired with chat_id=%s (persisted to %s)", _chat_id, ENV_PATH.name)
    await update.message.reply_text(
        "✅ Paired. This is now the only chat I'll talk to.\n"
        "_Chat id saved to settings — I won't need pairing on restart._",
        parse_mode="Markdown",
    )
    await _send_key_prompt(context)


async def _send_key_prompt(context: ContextTypes.DEFAULT_TYPE):
    """After pairing: check for an existing agent key and offer next actions."""
    if has_agent_key():
        _, address = load_or_create_keypair()
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Regenerate", callback_data="key:regenerate"),
            InlineKeyboardButton("🔑 Get public key", callback_data="key:pubkey"),
        ]])
        text = (
            "*Agent private key already exists.*\n\n"
            f"Current address:\n`{address}`\n\n"
            "When your Safe is ready, run /connect\\_safe."
        )
        await context.bot.send_message(
            chat_id=_chat_id, text=text,
            parse_mode="Markdown", reply_markup=keyboard,
        )
    else:
        _, address = load_or_create_keypair()
        await context.bot.send_message(
            chat_id=_chat_id,
            text=(
                "*Generated a new agent key.*\n\n"
                f"Address (use as the second Safe signer):\n`{address}`\n\n"
                "When your Safe is ready, run /connect\\_safe."
            ),
            parse_mode="Markdown",
        )


# ── /connect_safe ──────────────────────────────────────────────────────────

async def _connect_safe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _awaiting_safe_addr
    if update.effective_chat.id != _chat_id:
        return
    _awaiting_safe_addr = True
    current = f"\n\nCurrently connected: `{_safe_address}`" if _safe_address else ""
    await update.message.reply_text(
        "Send me the Safe wallet address (0x…). I'll start watching it." + current,
        parse_mode="Markdown",
    )


def _looks_like_address(text: str) -> bool:
    return (
        text.startswith("0x")
        and len(text) == 42
        and all(c in "0123456789abcdefABCDEF" for c in text[2:])
    )


async def _text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free-text catcher. Currently only used to receive a Safe address."""
    global _awaiting_safe_addr, _safe_address
    if update.effective_chat.id != _chat_id:
        return
    if not _awaiting_safe_addr:
        return

    text = (update.message.text or "").strip()
    if not _looks_like_address(text):
        await update.message.reply_text(
            "Expecting `0x` + 40 hex chars. Try again or /connect\\_safe to restart.",
            parse_mode="Markdown",
        )
        return

    _safe_address = text.lower()
    _awaiting_safe_addr = False
    _write_env_key("SAFE_ADDRESS", _safe_address)
    await update.message.reply_text(
        f"✅ Safe connected:\n`{_safe_address}`\n\n"
        "_Saved to settings._ Poller will pick it up shortly.",
        parse_mode="Markdown",
    )


# ── Approval flow ──────────────────────────────────────────────────────────

async def send_approval_request(tx: dict) -> bool:
    """Send a tx with Approve/Reject buttons; block until answered or 5-min timeout."""
    if _chat_id is None:
        log.warning("send_approval_request: no paired chat — dropping")
        return False

    app = _get_app()
    tx_hash = tx.get("tx_hash", "unknown")

    text = (
        f"*Transaction requires approval*\n\n"
        f"`{tx_hash}`\n\n"
        f"To: `{tx.get('to', '?')}`\n"
        f"Value: ${tx.get('value_usd', 0):,.2f}\n"
        f"Matched rule: `{tx.get('matched_rule', '?')}`"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve:{tx_hash}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject:{tx_hash}"),
    ]])

    await app.bot.send_message(
        chat_id=_chat_id, text=text,
        parse_mode="Markdown", reply_markup=keyboard,
    )

    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    _pending[tx_hash] = future
    try:
        return await asyncio.wait_for(future, timeout=300)
    except asyncio.TimeoutError:
        _pending.pop(tx_hash, None)
        return False


async def send_rejection_notice(tx: dict):
    """One-way notification when a tx is blocked by rules."""
    if _chat_id is None:
        log.warning("send_rejection_notice: no paired chat — dropping")
        return
    app = _get_app()
    h = tx.get("hash", "unknown")
    short = h[:10] + "…" + h[-6:] if len(h) > 16 else h
    reason = tx.get("flag_reason") or "rule match"
    text = (
        f"⛔ *Transaction blocked*\n\n"
        f"Hash: `{short}`\n"
        f"To: `{tx.get('to', '?')[:20]}…`\n"
        f"Value: ${tx.get('value_usd', 0):,.2f}\n"
        f"Rule: `{reason}`"
    )
    await app.bot.send_message(chat_id=_chat_id, text=text, parse_mode="Markdown")


async def _callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    # Key management buttons
    if data.startswith("key:"):
        action = data.split(":", 1)[1]
        if action == "pubkey":
            _, address = load_or_create_keypair()
            await query.edit_message_text(
                text=f"Agent address:\n`{address}`",
                parse_mode="Markdown",
            )
            return
        if action == "regenerate":
            if os.environ.get("AGENT_PRIVATE_KEY", "").strip():
                await query.edit_message_text(
                    text="Key is supplied via `AGENT_PRIVATE_KEY` env var — cannot regenerate from here.",
                    parse_mode="Markdown",
                )
                return
            if KEY_PATH.exists():
                KEY_PATH.unlink()
            _, address = load_or_create_keypair()
            await query.edit_message_text(
                text=f"🔄 *New agent key generated.*\n\nAddress:\n`{address}`",
                parse_mode="Markdown",
            )
            return
        return

    # Tx approve/reject
    try:
        action, tx_hash = data.split(":", 1)
    except ValueError:
        return
    approved = action == "approve"
    future = _pending.pop(tx_hash, None)
    if future and not future.done():
        future.set_result(approved)

    label = "✅ Approved" if approved else "❌ Rejected"
    await query.edit_message_reply_markup(reply_markup=None)
    await query.edit_message_text(
        text=query.message.text + f"\n\n{label}",
        parse_mode="Markdown",
    )


# ── Voice → rules ──────────────────────────────────────────────────────────

async def _voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if _chat_id is None or update.effective_chat.id != _chat_id:
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    audio_bytes = await file.download_as_bytearray()

    if not openai_client:
        await update.message.reply_text("OpenAI key not configured — cannot transcribe.")
        return

    transcript_resp = await openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=("voice.ogg", bytes(audio_bytes), "audio/ogg"),
    )
    text = transcript_resp.text
    log.info("Transcribed: %s", text)

    rules_yaml = RULES_PATH.read_text()
    system_prompt = (
        "You are a rules engine assistant. The user will describe a change to transaction rules "
        "in natural language. You will respond ONLY with valid YAML for the updated rules.yaml. "
        "Do not include any explanation — just the YAML."
    )
    completion = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current rules:\n{rules_yaml}\n\nRequested change: {text}"},
        ],
    )
    new_yaml = completion.choices[0].message.content.strip()

    try:
        yaml.safe_load(new_yaml)
        RULES_PATH.write_text(new_yaml)
        await update.message.reply_text(
            f"Got it: _{text}_\n\nRules updated.", parse_mode="Markdown"
        )
    except yaml.YAMLError as e:
        await update.message.reply_text(f"Failed to parse updated rules: {e}")


# ── Safe poller task ───────────────────────────────────────────────────────

async def _safe_poller_task():
    """Start Safe poller + in-memory HTTP server alongside the bot."""
    import sys
    engine_root = str(Path(__file__).parent.parent)
    if engine_root not in sys.path:
        sys.path.insert(0, engine_root)

    from watcher.safe_poller import SafePoller, TxStore, start_http_server

    store = TxStore()
    rpc_url = os.environ.get("ETH_RPC_URL", "")

    async def _wait_and_poll():
        while _safe_address is None:
            log.info("Waiting for /connect_safe …")
            await asyncio.sleep(5)
        poller = SafePoller(
            safe_address=_safe_address,
            rpc_url=rpc_url,
            rules_path=RULES_PATH,
            store=store,
            on_reject=send_rejection_notice,
        )
        await poller.run()

    await asyncio.gather(
        _wait_and_poll(),
        start_http_server(store),
    )


# ── Startup ────────────────────────────────────────────────────────────────

async def run_bot():
    global _app_instance

    _app_instance = Application.builder().token(TELEGRAM_TOKEN).build()

    _app_instance.add_handler(CommandHandler("start", _start_handler))
    _app_instance.add_handler(CommandHandler("connect_safe", _connect_safe_handler))
    _app_instance.add_handler(CallbackQueryHandler(_callback_handler))
    _app_instance.add_handler(MessageHandler(filters.VOICE, _voice_handler))
    _app_instance.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, _text_handler)
    )

    log.info("=" * 60)
    if _chat_id is None:
        log.info("LastCheck agent started — no paired chat yet.")
        log.info("Pair your Telegram chat by sending the bot:")
        log.info("    /start %s", _pairing_code)
    else:
        log.info("LastCheck agent started — resumed paired chat %s", _chat_id)
        if _safe_address:
            log.info("Watching Safe: %s", _safe_address)
        else:
            log.info("No Safe configured — run /connect_safe in Telegram.")
    log.info("=" * 60)

    async with _app_instance:
        await _app_instance.start()
        await _app_instance.updater.start_polling()
        asyncio.create_task(_safe_poller_task())
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(run_bot())
