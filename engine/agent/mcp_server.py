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

import yaml
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

RULES_PATH = Path(__file__).parent.parent / "config" / "rules.yaml"

app = Server("lastcheck")

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
            name="check_transaction",
            description=(
                "Evaluate a pending transaction against LastCheck rules. "
                "Returns 'approve', 'confirm' (escalate to user), or 'reject'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tx_hash": {"type": "string", "description": "Transaction hash"},
                    "to": {"type": "string", "description": "Recipient address"},
                    "value_usd": {"type": "number", "description": "Value in USD"},
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
    if name == "check_transaction":
        rules_doc = load_rules()
        action, rule_id = evaluate_tx(arguments, rules_doc)

        result = {
            "tx_hash": arguments.get("tx_hash"),
            "action": action,
            "matched_rule": rule_id,
        }

        if action == "confirm":
            # Notify Telegram — import lazily to avoid circular deps
            try:
                from bot.telegram_bot import send_approval_request  # type: ignore
                asyncio.create_task(send_approval_request(arguments))
            except Exception as e:
                result["telegram_error"] = str(e)

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
