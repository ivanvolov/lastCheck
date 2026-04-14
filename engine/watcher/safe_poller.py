"""
Safe Transaction Poller
- Polls the Safe Transaction Service for pending multisig transactions
- Enriches each tx (ETH price, contract check, calldata decode)
- Runs them through the rule engine
- Stores results in TxStore (in-memory)
- Exposes an aiohttp HTTP server on port 8502 for the dashboard
"""

import asyncio
import logging
import time
from typing import Optional

import aiohttp
import yaml
from web3 import AsyncWeb3

from watcher import tenderly

log = logging.getLogger(__name__)

SAFE_API = "https://safe-transaction-arbitrum.safe.global/api/v1"
COINGECKO = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
ERC20_APPROVE_SELECTOR = "0x095ea7b3"


# ── In-memory store ──────────────────────────────────────────────────────────

class TxStore:
    def __init__(self):
        self._txs: dict[str, dict] = {}

    def upsert(self, tx: dict):
        h = tx["hash"]
        if h in self._txs:
            self._txs[h].update(tx)
        else:
            self._txs[h] = tx

    def get(self, tx_hash: str) -> Optional[dict]:
        return self._txs.get(tx_hash)

    def all(self) -> list[dict]:
        return list(reversed(list(self._txs.values())))

    def daily_spent_usd(self, cutoff: float) -> float:
        return sum(
            t.get("value_usd", 0)
            for t in self._txs.values()
            if t.get("status") == "approved" and t.get("timestamp", 0) >= cutoff
        )

    def daily_swap_count(self, cutoff: float) -> int:
        return sum(
            1
            for t in self._txs.values()
            if t.get("is_swap") and t.get("status") == "approved"
            and t.get("timestamp", 0) >= cutoff
        )


# ── ETH price cache ──────────────────────────────────────────────────────────

_eth_price: float = 0.0
_eth_price_ts: float = 0.0

async def get_eth_price_usd(session: aiohttp.ClientSession) -> float:
    global _eth_price, _eth_price_ts
    if time.time() - _eth_price_ts < 60 and _eth_price:
        return _eth_price
    try:
        async with session.get(COINGECKO, timeout=aiohttp.ClientTimeout(total=5)) as r:
            data = await r.json()
            _eth_price = float(data["ethereum"]["usd"])
            _eth_price_ts = time.time()
    except Exception as e:
        log.warning("ETH price fetch failed: %s", e)
    return _eth_price or 1800.0


# ── Calldata helpers ─────────────────────────────────────────────────────────

def decode_erc20_approval(data: str) -> Optional[tuple[str, int]]:
    """Returns (spender, amount) if calldata is an ERC-20 approve(), else None."""
    if not data or not data.startswith(ERC20_APPROVE_SELECTOR):
        return None
    body = data[len(ERC20_APPROVE_SELECTOR):]
    if len(body) < 128:
        return None
    spender = "0x" + body[24:64]
    amount = int(body[64:128], 16)
    return spender.lower(), amount


def is_likely_swap(data: str) -> bool:
    """Heuristic: common swap selectors (Uniswap v2/v3, 1inch)."""
    SWAP_SELECTORS = {
        "0x38ed1739",  # swapExactTokensForTokens
        "0x8803dbee",  # swapTokensForExactTokens
        "0x7ff36ab5",  # swapExactETHForTokens
        "0x4a25d94a",  # swapTokensForExactETH
        "0x18cbafe5",  # swapExactTokensForETH
        "0x414bf389",  # Uniswap v3 exactInputSingle
        "0xc04b8d59",  # Uniswap v3 exactInput
        "0x12aa3caf",  # 1inch swap
        "0xe449022e",  # 1inch uniswapV3Swap
    }
    if not data or len(data) < 10:
        return False
    return data[:10].lower() in SWAP_SELECTORS


# ── Rule engine import ───────────────────────────────────────────────────────

def _run_rules(tx_fields: dict, rules_doc: dict, store: TxStore) -> tuple[str, str]:
    """Evaluate tx against rules + token caps. Returns (action, rule_id)."""
    from agent.mcp_server import evaluate_tx  # lazy import avoids circular deps

    cutoff_24h = time.time() - 86400

    allowlist  = [c.lower() for c in rules_doc.get("allowlist", {}).get("contracts", [])]
    blocklist  = [a.lower() for a in rules_doc.get("blocklist", {}).get("addresses", [])]

    extra_ctx = {
        "blocklist":         {"addresses": blocklist},
        "token_out_usd":     tx_fields.get("token_out_usd", 0),
        "price_impact_pct":  tx_fields.get("price_impact_pct", 0),
        "daily_spent_usd":   store.daily_spent_usd(cutoff_24h),
        "daily_swap_count":  store.daily_swap_count(cutoff_24h),
    }
    tx_fields["allowlist_contracts"] = allowlist
    action, rule_id = evaluate_tx(tx_fields, rules_doc, extra_ctx=extra_ctx)

    # Token cap checks (after standard rules)
    if action == "approve":
        for cap in rules_doc.get("token_caps", []) or []:
            sym = cap.get("symbol", "")
            addr = (cap.get("address") or "").lower()
            if addr and tx_fields.get("to", "").lower() == addr:
                now = time.time()
                periods = {
                    "hourly":  now - 3600,
                    "daily":   now - 86400,
                    "weekly":  now - 604800,
                    "monthly": now - 2592000,
                }
                for period, cutoff in periods.items():
                    limit = cap.get(period)
                    if not limit:
                        continue
                    spent = sum(
                        t.get("value_usd", 0)
                        for t in store.all()
                        if t.get("status") == "approved"
                        and t.get("timestamp", 0) >= cutoff
                        and (t.get("to", "").lower() == addr)
                    )
                    if spent + tx_fields.get("value_usd", 0) > limit:
                        return "reject", f"token_cap_{sym.lower()}_{period}"

    return action, rule_id


# ── Poller ───────────────────────────────────────────────────────────────────

class SafePoller:
    def __init__(
        self,
        safe_address: str,
        rpc_url: str,
        rules_path,
        store: TxStore,
        on_reject=None,
    ):
        # Safe Transaction Service requires a checksummed address in the URL.
        self.safe_address = AsyncWeb3.to_checksum_address(safe_address) if safe_address else ""
        self.rpc_url = rpc_url
        self.rules_path = rules_path
        self.store = store
        self.on_reject = on_reject  # async callback(tx_record)
        self._w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))

    async def run(self):
        log.info("SafePoller starting for %s", self.safe_address)
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    await self.poll(session)
                except Exception as e:
                    log.error("Poll error: %s", e)
                await asyncio.sleep(5)

    async def poll(self, session: aiohttp.ClientSession):
        if not self.safe_address:
            return

        url = f"{SAFE_API}/safes/{self.safe_address}/multisig-transactions/?executed=false&limit=20"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status != 200:
                body = await r.text()
                log.warning("Safe API returned %s: %s", r.status, body[:200])
                return
            data = await r.json()

        eth_price = await get_eth_price_usd(session)
        results = data.get("results", [])

        for raw in results:
            tx_hash = raw.get("safeTxHash") or raw.get("transactionHash", "")
            if not tx_hash:
                continue

            existing = self.store.get(tx_hash)
            # Skip anything the store already has a terminal or in-flight
            # status for. `awaiting_ai` is handled by the MCP client, not
            # the rule engine — don't re-evaluate and overwrite it.
            if existing and existing.get("status") not in ("pending", None):
                continue

            to = (raw.get("to") or "").lower()
            value_wei = int(raw.get("value") or 0)
            value_eth = value_wei / 1e18
            value_usd = value_eth * eth_price
            calldata = raw.get("data") or ""

            is_contract = False
            try:
                code = await self._w3.eth.get_code(AsyncWeb3.to_checksum_address(to))
                is_contract = len(code) > 2  # "0x" = no code
            except Exception:
                pass

            approval = decode_erc20_approval(calldata)
            is_erc20_approval = approval is not None
            spender = approval[0] if approval else ""
            approval_amount = approval[1] if approval else 0
            is_swap = is_likely_swap(calldata)

            # Tenderly simulation — authoritative source for net outflow
            # when configured; falls back to raw ETH value otherwise.
            token_out_usd = value_usd
            sim_success = None
            if tenderly.is_enabled():
                sim = await tenderly.simulate_safe_tx(
                    session, self.safe_address, to, calldata, value_wei,
                )
                if sim is not None:
                    token_out_usd = sim["token_out_usd"] or value_usd
                    sim_success = sim["success"]

            record = {
                "hash":             tx_hash,
                "to":               to,
                "value_eth":        value_eth,
                "value_usd":        value_usd,
                "token_out_usd":    token_out_usd,
                "price_impact_pct": 0,
                "sim_success":      sim_success,
                "data":             calldata[:64] + "…" if len(calldata) > 64 else calldata,
                "is_contract":      is_contract,
                "is_erc20_approval": is_erc20_approval,
                "approval_amount":  approval_amount,
                "spender":          spender,
                "is_swap":          is_swap,
                "nonce":            raw.get("nonce"),
                "status":           "pending",
                "flagged_by":       None,
                "flag_reason":      None,
                "telegram_sent":    False,
                "timestamp":        time.time(),
            }

            self.store.upsert(record)

            # Evaluate rules
            try:
                import yaml as _yaml
                with open(self.rules_path) as f:
                    rules_doc = _yaml.safe_load(f) or {}
                action, rule_id = _run_rules(record, rules_doc, self.store)
            except Exception as e:
                log.error("Rule evaluation failed: %s", e)
                action, rule_id = "approve", "error"

            if action == "reject":
                self.store.upsert({
                    "hash":       tx_hash,
                    "status":     "flagged",
                    "flagged_by": "layer1",
                    "flag_reason": rule_id,
                })
                if self.on_reject and not record.get("telegram_sent"):
                    try:
                        await self.on_reject({**record, "flag_reason": rule_id})
                        self.store.upsert({"hash": tx_hash, "telegram_sent": True})
                    except Exception as e:
                        log.error("Telegram notify failed: %s", e)
            elif action == "confirm":
                # Hand over to the AI / MCP client. The tx sits in
                # `awaiting_ai` until something calls approve/reject
                # on the TxStore HTTP endpoints.
                self.store.upsert({
                    "hash":        tx_hash,
                    "status":      "awaiting_ai",
                    "flagged_by":  "layer1",
                    "flag_reason": rule_id,
                })
            else:
                self.store.upsert({"hash": tx_hash, "status": "approved"})

            log.info("tx %s → %s (rule: %s)", tx_hash[:12], action, rule_id)


# ── HTTP server ──────────────────────────────────────────────────────────────

async def start_http_server(store: TxStore, port: int = 8502):
    from aiohttp import web

    async def handle_transactions(request):
        return web.json_response(store.all())

    async def handle_health(request):
        return web.json_response({"ok": True, "count": len(store.all())})

    async def handle_approve(request):
        tx_hash = request.match_info["hash"]
        if store.get(tx_hash) is None:
            return web.json_response({"error": "tx not found"}, status=404)
        store.upsert({
            "hash": tx_hash,
            "status": "approved",
            "flagged_by": "mcp",
            "flag_reason": None,
        })
        return web.json_response({"ok": True, "hash": tx_hash, "status": "approved"})

    async def handle_reject(request):
        tx_hash = request.match_info["hash"]
        if store.get(tx_hash) is None:
            return web.json_response({"error": "tx not found"}, status=404)
        try:
            body = await request.json() if request.can_read_body else {}
        except Exception:
            body = {}
        reason = (body or {}).get("reason", "mcp-reject")
        store.upsert({
            "hash": tx_hash,
            "status": "flagged",
            "flagged_by": "mcp",
            "flag_reason": reason,
        })
        return web.json_response({"ok": True, "hash": tx_hash, "status": "flagged"})

    app = web.Application()
    app.router.add_get("/transactions", handle_transactions)
    app.router.add_get("/health", handle_health)
    app.router.add_post("/transactions/{hash}/approve", handle_approve)
    app.router.add_post("/transactions/{hash}/reject", handle_reject)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()
    log.info("TX store HTTP server on http://127.0.0.1:%d", port)
    # keep running forever alongside the bot
    await asyncio.Event().wait()
