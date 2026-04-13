"""
LastCheck Telegram Bot
- Sends tx approval requests with inline [Approve] / [Reject] buttons
- Handles voice messages: transcribes → parses intent → patches rules.yaml
- On startup: generates/loads agent keypair and broadcasts public key
"""

import asyncio
import json
import logging
import os
from pathlib import Path

import yaml
from eth_account import Account
from openai import AsyncOpenAI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

RULES_PATH = Path(__file__).parent.parent / "config" / "rules.yaml"
KEY_PATH = Path(__file__).parent.parent / ".agent_key"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SAFE_ADDRESS = os.environ.get("SAFE_ADDRESS", "").strip()
ETH_RPC_URL = os.environ.get("ETH_RPC_URL", "")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# In-memory pending approvals: tx_hash → asyncio.Future
_pending: dict[str, asyncio.Future] = {}

# ---------------------------------------------------------------------------
# Keypair management
# ---------------------------------------------------------------------------

def load_or_create_keypair() -> tuple[str, str]:
    """Returns (private_key, address).

    Priority:
    1. AGENT_PRIVATE_KEY env var (user-supplied)
    2. .agent_key file (previously auto-generated)
    3. Generate a new key, persist it to .agent_key
    """
    env_key = os.environ.get("AGENT_PRIVATE_KEY", "").strip()
    if env_key:
        private_key = env_key
    elif KEY_PATH.exists():
        private_key = KEY_PATH.read_text().strip()
    else:
        account = Account.create()
        private_key = account.key.hex()
        KEY_PATH.write_text(private_key)
        KEY_PATH.chmod(0o600)
        log.info("Generated new agent keypair, saved to %s", KEY_PATH)
    account = Account.from_key(private_key)
    return private_key, account.address


# ---------------------------------------------------------------------------
# Approval flow
# ---------------------------------------------------------------------------

async def send_approval_request(tx: dict) -> bool:
    """
    Send a Telegram message with Approve/Reject buttons.
    Blocks until the user responds or times out (5 min).
    Returns True if approved.
    """
    app = _get_app()
    tx_hash = tx.get("tx_hash", "unknown")

    text = (
        f"*Transaction requires approval*\n\n"
        f"`{tx_hash}`\n\n"
        f"To: `{tx.get('to', '?')}`\n"
        f"Value: ${tx.get('value_usd', 0):,.2f}\n"
        f"Matched rule: `{tx.get('matched_rule', '?')}`"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve:{tx_hash}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject:{tx_hash}"),
        ]
    ])

    await app.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    _pending[tx_hash] = future

    try:
        return await asyncio.wait_for(future, timeout=300)
    except asyncio.TimeoutError:
        _pending.pop(tx_hash, None)
        return False


async def _callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, tx_hash = query.data.split(":", 1)
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


# ---------------------------------------------------------------------------
# Voice → rules
# ---------------------------------------------------------------------------

async def _voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != TELEGRAM_CHAT_ID:
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    audio_bytes = await file.download_as_bytearray()

    if not openai_client:
        await update.message.reply_text("OpenAI key not configured — cannot transcribe.")
        return

    # Transcribe
    transcript_resp = await openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=("voice.ogg", bytes(audio_bytes), "audio/ogg"),
    )
    text = transcript_resp.text
    log.info("Transcribed: %s", text)

    # Parse intent into rule patch via GPT
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

    # Validate and write
    try:
        yaml.safe_load(new_yaml)
        RULES_PATH.write_text(new_yaml)
        await update.message.reply_text(
            f"Got it: _{text}_\n\nRules updated.", parse_mode="Markdown"
        )
    except yaml.YAMLError as e:
        await update.message.reply_text(f"Failed to parse updated rules: {e}")


# ---------------------------------------------------------------------------
# App singleton & startup
# ---------------------------------------------------------------------------

_app_instance: Application | None = None

def _get_app() -> Application:
    global _app_instance
    if _app_instance is None:
        raise RuntimeError("Bot not started")
    return _app_instance


async def send_rejection_notice(tx: dict):
    """Send a one-way Telegram notification when a tx is rejected by rules."""
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
    await app.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=text,
        parse_mode="Markdown",
    )


async def _safe_poller_task():
    """Start Safe poller + in-memory HTTP server alongside the bot."""
    import importlib
    import sys

    # Ensure engine root is on path
    engine_root = str(Path(__file__).parent.parent)
    if engine_root not in sys.path:
        sys.path.insert(0, engine_root)

    from watcher.safe_poller import SafePoller, TxStore, start_http_server

    store = TxStore()

    safe_addr = os.environ.get("SAFE_ADDRESS", "").strip()
    rpc_url = os.environ.get("ETH_RPC_URL", "")

    if not safe_addr:
        log.warning("SAFE_ADDRESS not set — poller will wait until it is configured")

    async def _wait_for_safe_address_and_poll():
        nonlocal safe_addr
        while True:
            safe_addr = os.environ.get("SAFE_ADDRESS", "").strip()
            if safe_addr:
                break
            log.info("Waiting for SAFE_ADDRESS to be configured…")
            await asyncio.sleep(10)

        poller = SafePoller(
            safe_address=safe_addr,
            rpc_url=rpc_url,
            rules_path=RULES_PATH,
            store=store,
            on_reject=send_rejection_notice,
        )
        await poller.run()

    await asyncio.gather(
        _wait_for_safe_address_and_poll(),
        start_http_server(store),
    )


async def run_bot():
    global _app_instance

    private_key, address = load_or_create_keypair()
    log.info("Agent address: %s", address)

    _app_instance = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    _app_instance.add_handler(CallbackQueryHandler(_callback_handler))
    _app_instance.add_handler(MessageHandler(filters.VOICE, _voice_handler))

    async with _app_instance:
        await _app_instance.start()

        safe_info = f"\nWatching Safe: `{SAFE_ADDRESS}`" if SAFE_ADDRESS else "\n⚠️ No Safe address configured yet — add `SAFE_ADDRESS` in settings."

        # Broadcast public key on startup
        await _app_instance.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=(
                f"*LastCheck agent started*\n\n"
                f"Agent address (second signer):\n`{address}`\n"
                f"{safe_info}"
            ),
            parse_mode="Markdown",
        )

        await _app_instance.updater.start_polling()

        # Start Safe poller + HTTP store server in same event loop
        asyncio.create_task(_safe_poller_task())

        await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(run_bot())
