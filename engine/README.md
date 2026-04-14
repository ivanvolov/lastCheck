# LastCheck Engine

The engine is the self-hosted process that watches your Safe on
Arbitrum, evaluates every pending transaction against
`config/rules.yaml`, notifies you via Telegram, and exposes an MCP
server so agents like Claude Code can list / approve / reject
transactions and edit rules.

For the product narrative, see the [root README](../README.md). For
the AI layer and MCP tool reference, see
[`ai/README.md`](ai/README.md). For authoring rules, see
[`config/rules.md`](config/rules.md).

## Prerequisites

One of:

- **Docker + Docker Compose** (for `make engine`), or
- **Python 3.10+** (for `make engine-local` — no containers)

Plus:

- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An Arbitrum RPC URL (Alchemy / Infura / public endpoint)
- *(Optional)* An OpenAI API key — enables voice messages that
  rewrite `rules.yaml` in place
- *(Optional)* Tenderly credentials — enables accurate per-tx USD
  outflow via Nano Claw (see [`ai/README.md`](ai/README.md))

## Quick start

All commands are run from the repo root, not from `engine/`.

```bash
make setup-engine   # copies engine/.env.example → engine/.env
make engine         # Docker: bot + dashboard + watcher + MCP server
make engine-local   # no Docker: pip install + run directly
make engine-logs    # tail container logs
make engine-down    # stop containers
```

After start the Streamlit dashboard is on <http://localhost:8501> and
the TxStore HTTP server (used by the MCP server) is on
<http://127.0.0.1:8502>.

## Environment variables

Fill in `engine/.env`. The file is **read-only at runtime** — the bot
never writes to it. Anything the bot learns at runtime goes to
`engine/tmp/` instead.

### Required

| Variable | Description |
|---|---|
| `TELEGRAM_TOKEN` | Bot token from @BotFather |
| `ETH_RPC_URL` | Arbitrum RPC endpoint |

### Optional

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Enables voice-to-rules. Leave unset to disable the voice path. |
| `AGENT_PRIVATE_KEY` | Supply an existing agent key. If unset, one is generated and saved to `tmp/.agent_key`. |
| `TENDERLY_ACCESS_KEY` | Tenderly Simulation API key |
| `TENDERLY_ACCOUNT_SLUG` | Tenderly account slug |
| `TENDERLY_PROJECT_SLUG` | Tenderly project slug |
| `TENDERLY_NETWORK_ID` | Chain id for simulation (defaults to `42161` / Arbitrum One) |
| `DASHBOARD_PORT` | Streamlit port (defaults to `8501`) |

**Note:** `TELEGRAM_CHAT_ID` and `SAFE_ADDRESS` are **not** required in
`.env`. They are captured interactively at runtime via the pairing
flow below and persisted to `tmp/state.json`.

## First-run pairing flow

The engine doesn't ship with a pre-baked chat id or Safe address.
Both are learned at runtime:

1. **Start the engine.** Watch the logs for a pairing line:

   ```
   Pair your Telegram chat by sending the bot:
       /start 9ceefcaf
   ```

2. **Pair Telegram.** Send that `/start <code>` to your bot in a
   private chat. The bot captures your chat id, persists it to
   `tmp/state.json`, and moves to the next step.

3. **Agent key.**
   - If no agent key exists yet, the bot auto-generates one (saved to
     `tmp/.agent_key`, `chmod 600`) and shows its public address.
   - If a key already exists, the bot shows two inline buttons:
     **🔑 Get public key** (reveal current address) or
     **🔄 Regenerate** (delete and create a fresh one).

   Copy the agent address — you'll use it as the second signer when
   creating your Gnosis Safe (2-of-2: your wallet + agent).

4. **Connect Safe.** Once the Safe is deployed, send `/connect_safe`
   to the bot. It asks for the address, you paste it, and the
   watcher starts polling the Safe Transaction Service immediately.
   The address is persisted to `tmp/state.json`.

On subsequent restarts the engine resumes silently — no pairing code,
no re-entering the Safe address. To force re-pair, delete
`engine/tmp/state.json`.

## Where things live

| Path | What it does |
|---|---|
| `bot/telegram_bot.py` | Telegram handlers, pairing flow, entrypoint |
| `watcher/safe_poller.py` | Safe Transaction Service poller + rule runner + TxStore HTTP server on `:8502` |
| `watcher/tenderly.py` | Tenderly simulation client (Nano Claw backend) |
| `agent/mcp_server.py` | MCP server for Claude Code / Desktop — see [`ai/README.md`](ai/README.md) |
| `config/rules.yaml` | The rulebook |
| `config/rules.md` | Rule authoring reference — variables, wildcards, caveats |
| `dashboard/app.py` | Streamlit dashboard on `:8501` |
| `tmp/state.json` | Paired chat id + Safe address (runtime, gitignored) |
| `tmp/.agent_key` | Generated agent private key (runtime, gitignored) |

## Further reading

- [`ai/README.md`](ai/README.md) — Nano Claw simulator, MCP server,
  Claude Code integration
- [`config/rules.md`](config/rules.md) — rule variables, wildcards,
  default-deny, examples
