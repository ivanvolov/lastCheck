"""
LastCheck MCP Server
Exposes a `check_transaction` tool that evaluates a tx against rules.yaml.
Transport: stdio (default) or HTTP via --http flag.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

import aiohttp
import yaml
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

RULES_PATH = Path(__file__).parent.parent / "config" / "rules.yaml"

# Where the bot's TxStore HTTP server is reachable. Override with
# LASTCHECK_STORE_URL if you run the bot on a different host/port.
STORE_URL = os.environ.get("LASTCHECK_STORE_URL", "http://127.0.0.1:8502").rstrip("/")

app = Server("lastcheck")


async def _store_get(path: str) -> Any:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{STORE_URL}{path}") as r:
            return await r.json()


async def _store_post(path: str, body: dict | None = None) -> Any:
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{STORE_URL}{path}", json=body or {}) as r:
            return await r.json()

# ---------------------------------------------------------------------------
# Rule engine
# ---------------------------------------------------------------------------

def load_rules() -> dict:
    with open(RULES_PATH) as f:
        return yaml.safe_load(f)


class _Wildlist(list):
    """list where membership of the string 'all' means everything matches."""

    def __contains__(self, item):  # type: ignore[override]
        if list.__contains__(self, "all"):
            return True
        return list.__contains__(self, item)


def evaluate_tx(tx: dict, rules_doc: dict, extra_ctx: dict | None = None) -> tuple[str, str]:
    """
    Returns (action, rule_id) where action is 'approve' | 'reject'.
    Default-deny: if no rule matches, the tx is rejected.
    extra_ctx: optional dict merged into eval context (blocklist, daily_spent_usd, etc.)
    """
    from types import SimpleNamespace

    allowlist = rules_doc.get("allowlist", {})
    allowed_contracts = _Wildlist(c.lower() for c in allowlist.get("contracts", []))
    blocklist_addrs = _Wildlist()
    if extra_ctx and "blocklist" in extra_ctx:
        blocklist_addrs = _Wildlist(
            a.lower() for a in extra_ctx["blocklist"].get("addresses", [])
        )

    # SimpleNamespace so YAML conditions can use `allowlist.contracts` /
    # `blocklist.addresses` dot syntax instead of `allowlist["contracts"]`.
    ctx = {
        "value_usd":          tx.get("value_usd", 0),
        "to":                 (tx.get("to") or "").lower(),
        "is_contract":        tx.get("is_contract", False),
        "is_erc20_approval":  tx.get("is_erc20_approval", False),
        "approval_amount":    tx.get("approval_amount", 0),
        "spender":            (tx.get("spender") or "").lower(),
        "token_out_usd":      tx.get("token_out_usd", 0),
        "price_impact_pct":   tx.get("price_impact_pct", 0),
        "daily_spent_usd":    0,
        "daily_swap_count":   0,
        "max_uint256":        2**256 - 1,
        "allowlist":          SimpleNamespace(contracts=allowed_contracts),
        "blocklist":          SimpleNamespace(addresses=blocklist_addrs),
    }
    if extra_ctx:
        ctx.update({k: v for k, v in extra_ctx.items() if k != "blocklist"})

    for rule in rules_doc.get("rules", []):
        try:
            if eval(rule["condition"], {"__builtins__": {}}, ctx):  # noqa: S307
                return rule["action"], rule["id"]
        except Exception as e:
            log.warning("Rule %s failed to evaluate: %s", rule.get("id", "?"), e)
            continue

    return "reject", "default_deny"


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_transactions",
            description=(
                "List transactions the watcher has seen in the local TxStore, "
                "with status (pending/approved/flagged). Optional `status` filter."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter: pending | approved | flagged",
                    },
                },
            },
        ),
        Tool(
            name="approve_transaction",
            description="Mark a transaction as approved in the TxStore by hash.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tx_hash": {"type": "string", "description": "Safe tx hash"},
                },
                "required": ["tx_hash"],
            },
        ),
        Tool(
            name="reject_transaction",
            description="Mark a transaction as flagged/rejected in the TxStore by hash.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tx_hash": {"type": "string", "description": "Safe tx hash"},
                    "reason": {"type": "string", "description": "Why you're rejecting"},
                },
                "required": ["tx_hash"],
            },
        ),
        Tool(
            name="check_transaction",
            description=(
                "Dry-run a synthetic transaction through rules.yaml. "
                "Does NOT touch the TxStore — use this to test rules."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tx_hash": {"type": "string"},
                    "to": {"type": "string"},
                    "value_usd": {"type": "number"},
                    "is_contract": {"type": "boolean"},
                    "is_erc20_approval": {"type": "boolean"},
                    "approval_amount": {"type": "number"},
                    "spender": {"type": "string"},
                },
                "required": ["tx_hash", "to", "value_usd"],
            },
        ),
        Tool(
            name="get_rules",
            description="Return the current rules.yaml content.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="update_rules",
            description="Replace rules.yaml with new YAML content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "yaml_content": {"type": "string", "description": "Full YAML to write"},
                },
                "required": ["yaml_content"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "list_transactions":
        try:
            txs = await _store_get("/transactions")
        except Exception as e:
            return [TextContent(type="text", text=f"Failed to reach TxStore at {STORE_URL}: {e}")]
        status_filter = arguments.get("status")
        if status_filter:
            txs = [t for t in txs if t.get("status") == status_filter]
        return [TextContent(type="text", text=json.dumps(txs, indent=2))]

    elif name == "approve_transaction":
        tx_hash = arguments["tx_hash"]
        try:
            result = await _store_post(f"/transactions/{tx_hash}/approve")
        except Exception as e:
            return [TextContent(type="text", text=f"Failed: {e}")]
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "reject_transaction":
        tx_hash = arguments["tx_hash"]
        body = {"reason": arguments.get("reason", "mcp-reject")}
        try:
            result = await _store_post(f"/transactions/{tx_hash}/reject", body)
        except Exception as e:
            return [TextContent(type="text", text=f"Failed: {e}")]
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "check_transaction":
        rules_doc = load_rules()
        action, rule_id = evaluate_tx(arguments, rules_doc)
        result = {
            "tx_hash": arguments.get("tx_hash"),
            "action": action,
            "matched_rule": rule_id,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_rules":
        return [TextContent(type="text", text=RULES_PATH.read_text())]

    elif name == "update_rules":
        yaml_content = arguments["yaml_content"]
        yaml.safe_load(yaml_content)  # validate
        RULES_PATH.write_text(yaml_content)
        return [TextContent(type="text", text="rules.yaml updated")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
