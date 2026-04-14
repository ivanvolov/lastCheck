# LastCheck

A self-hosted AI agent that co-signs your transactions. The last line of defense between you and a malicious tx.

[👉explore👈](https://ivanvolov.github.io/lastCheck/)

## The Problem

Malicious signing is still the #1 way users lose funds on Ethereum. Wallet warnings are generic, easy to dismiss, and controlled by third parties. Once you click Confirm, there is no second chance.

## Existing Solutions

They optimize for the average user, not your specific usage.

**Hardware wallets** — can flag known malicious txs, but screen space is tiny and rules aren't configurable.

**Browser/mobile wallets** — better warnings, but limited rule logic. You can't say "allow Uniswap up to $5k, block everything else."

**On-chain modules (Zodiac, Safe guards)** — powerful, but painful to use day-to-day. If you want to increase your DeFi spending limit for an afternoon (like raising your card limit to buy plane tickets), you're editing Gnosis module configs.

**Enterprise firewalls** — great for treasuries, but enterprise-priced and enterprise-complex.

## What LastCheck Does Differently

**Invisible by default.** You sign transactions normally. The agent handles everything behind the scenes — no extra UI, no co-signing flow. It blocks the bad stuff and asks you in your preferred channel if you want to proceed.

**Configurable like a spending limit.** Open the dashboard and drag a slider. Or send a voice message to your Telegram bot: "I'm trading memecoins today, raise the limit to $2k." Lower it back tomorrow. The agent learns your patterns over time.

**Easy to adjust when it's wrong.** If the agent rejects too many txs, you tune it in seconds — not by diving into wallet settings or module configs.

## How It Works

1. **Connect wallet** — LastCheck wraps it into a Safe multisig where the agent becomes a mandatory co-signer. EIP-7702 support is in progress for a seamless experience without Safe.
2. **Set rules in plain English** — compiled into deterministic YAML. Hard-enforced at the first layer, the AI cannot override them.
3. **AI reviews what passes** — simulates execution, catches novel attacks and unusual behaviour.
4. **Suspicious? You decide** — alert via Telegram, Signal, or Ledger Trezor. Proceed or reject.

```
Tx proposed
    ↓
Hard Rules ── violates? → REJECTED
    ↓ ok
AI Agent ── suspicious? → Alert (Telegram / Signal / Trezor)
    ↓ clean                    ↓
Agent signs              You approve or reject
    ↓                          ↓
Tx executes              Agent signs (or drops)
```

Self-hosted. Your data never leaves your infrastructure.

## Links

- [ETHGlobal Showcase](https://ethglobal.com/showcase/lastcheck-ig7zw)

---

## Running the Prototype

### Prerequisites

- Node.js 18+
- Docker + Docker Compose
- A Telegram bot token ([create one via @BotFather](https://t.me/BotFather))
- An OpenAI API key (for voice-to-rule transcription)

### Onboarding wizard (app/)

```bash
make app
# opens http://localhost:3000 — redirects to /setup/step1-connect
```

### Marketing site (landing) & GitHub Pages

```bash
make landing
# http://localhost:3001 — “Start setup” links to NEXT_PUBLIC_APP_ORIGIN (default http://localhost:3000)
```

To deploy the landing site to **GitHub Pages**, enable **Settings → Pages → Source: GitHub Actions**, set the repository variable **`NEXT_PUBLIC_APP_ORIGIN`** to your deployed app URL, and push (or run the workflow manually). See [`landing/README.md`](landing/README.md) for details.

### Engine (bot + dashboard + MCP server)

```bash
make setup-engine   # copies engine/.env.example → engine/.env
                    # edit engine/.env with your tokens before continuing
make engine         # starts containers; dashboard at http://localhost:8501
make engine-logs    # tail logs
make engine-down    # stop
```

**Required env vars in `engine/.env`:**

| Variable | Description |
|---|---|
| `TELEGRAM_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your personal or group chat ID |
| `ETH_RPC_URL` | Mainnet/Sepolia RPC endpoint |
| `FIRST_SIGNER` | Your wallet address (Safe owner #1) |
| `OPENAI_API_KEY` | For voice message transcription |

On first start the engine generates an agent keypair and broadcasts the agent's address to your Telegram chat. Use that address as the second owner when creating the Gnosis Safe in step 4 of the wizard.

## Support on Giveth

LastCheck is listed as a public good on Giveth — [support development here](https://giveth.io/project/self-hosted-ai-co-signer-for-your-transactions).