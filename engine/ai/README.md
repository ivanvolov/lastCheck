# AI Layer

The AI layer is the second pass after the deterministic rule engine.
Hard rules from `config/rules.yaml` run first and are authoritative —
the AI **cannot** override them. Rules with the `confirm` action park
their tx in `awaiting_ai` status; the AI layer (an MCP client like
Claude Code) then decides via simulation, protocol-specific heuristics,
and human-in-the-loop overrides via Telegram.

For running the engine itself, see [`../README.md`](../README.md).
For authoring rules, see [`../config/rules.md`](../config/rules.md).

---

## Nano Claw — the simulation engine

**Nano Claw** is LastCheck's custom transaction simulator. It
re-executes each pending Safe transaction against a forked state of
the chain and reads back the resulting asset changes, so the rule
engine sees the real USD outflow instead of guessing from calldata.

**Current status:** the build ships a Tenderly-backed implementation.
It POSTs the queued Safe tx to Tenderly's Simulation API with
`from = safe_address`, parses `transaction_info.asset_changes`, and
sums the dollar values of outbound transfers into `token_out_usd`.
Without Tenderly configured, `token_out_usd` falls back to the native
ETH value — rules that depend on it silently degrade to ETH-only
checks, which is the current prototype limitation.

Enable it by setting these in `engine/.env`:

```
TENDERLY_ACCESS_KEY=tly_...
TENDERLY_ACCOUNT_SLUG=your-account
TENDERLY_PROJECT_SLUG=your-project
TENDERLY_NETWORK_ID=42161
```

A **fully custom** Nano Claw implementation (no third-party dependency)
is planned for a future release so simulation runs entirely inside the
self-hosted engine, with no tx payloads leaving your infrastructure.

Source: [`../watcher/tenderly.py`](../watcher/tenderly.py) and its
call site in [`../watcher/safe_poller.py`](../watcher/safe_poller.py).

## Custom skills

Protocol-specific heuristics — MEV detection, phishing templates,
drainer patterns, address-poisoning detection. **Status: planned.**
These will plug in alongside Nano Claw as recommendations the rule
layer can reference but never be overridden by.

---

## MCP server

The engine ships an MCP (Model Context Protocol) server at
[`../agent/mcp_server.py`](../agent/mcp_server.py) that exposes the
running engine to any MCP client — Claude Code, Claude Desktop, or any
other agent that speaks MCP. You can drive approvals, rejections, and
rule edits from natural-language prompts.

The MCP server runs as a stdio subprocess spawned by the client. It
talks to the already-running bot over HTTP on `127.0.0.1:8502` (the
TxStore HTTP server started by `make engine-local` or `make engine`).
It only works while the engine is up.

### Wire it up in Claude Code

The repo ships with a project-scoped [`.mcp.json`](../../.mcp.json) at
the root, so you don't have to copy-paste JSON — just launch Claude
Code from the repo root:

```bash
cd /path/to/lastCheck
claude
```

Claude Code auto-detects `.mcp.json`, prompts you once to approve the
`lastcheck` server, and the tools below become available.

If you prefer to wire it up manually, or you want to add it from a
different working directory, run:

```bash
claude mcp add --scope project lastcheck python ./engine/agent/mcp_server.py \
  -e LASTCHECK_STORE_URL=http://127.0.0.1:8502
```

from the repo root. This writes the same `.mcp.json` file.

The `.mcp.json` uses a **relative path** (`./engine/agent/mcp_server.py`)
so it travels with the repo and works for anyone who clones it. If
your engine runs on a different host or port, override
`LASTCHECK_STORE_URL` in that file.

### Tools

| Tool | What it does |
|---|---|
| `list_transactions` | Return everything the watcher has in the TxStore, with status. Optional `status` filter: `pending` / `awaiting_ai` / `approved` / `flagged`. |
| `approve_transaction` | Mark a tx by hash as approved in the TxStore. |
| `reject_transaction` | Mark a tx by hash as flagged, with an optional `reason`. |
| `check_transaction` | Dry-run a synthetic tx through `rules.yaml`. Does **not** touch the TxStore — use this to test new rules. |
| `get_rules` | Return the current `rules.yaml` content. |
| `update_rules` | Validate and overwrite `rules.yaml`. |

### Example prompts

- *"List transactions awaiting AI review."*
- *"Show me pending transactions and summarize what each one does."*
- *"Approve 0xce9cccae1e…"*
- *"Reject 0xdead… — it's an unlimited approval to an unknown spender."*
- *"Add a rule that blocks any transfer over $500."*

When you approve or reject from MCP, the bot also fires a Telegram
notification with **`✅ Approve anyway`** / **`⛔ Ultimately reject`**
inline buttons so you have the final say on the AI's decision.

### Caveat

The current approve/reject flow updates TxStore state only — the bot
does **not** yet propagate approvals into an on-chain Safe co-signature.
On-chain co-signing is work in progress; the MCP tools are the
interface the agent will drive once that lands. In the meantime the
tools are useful for dashboard-state control and for testing the
rule-authoring loop (`get_rules` / `update_rules` / `check_transaction`).
