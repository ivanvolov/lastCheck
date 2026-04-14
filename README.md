# LastCheck

A self-hosted AI agent that co-signs your transactions. The last line of defense between you and a malicious tx.

[👉explore👈](https://ivanvolov.github.io/lastCheck/)

## The Problem

Malicious signing is still the #1 way users lose funds on Ethereum. Wallet warnings are generic, easy to dismiss, and controlled by third parties. Once you click Confirm, there is no second chance.

User-layer attacks — phishing, malicious approvals, address poisoning, fake dApp frontends — account for a significant share of funds lost each year. These attacks succeed not because wallets lack warnings, but because warnings are not calibrated to how *you* actually use your wallet.

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

**Self-hosted.** Your keys, rules, and transaction history stay on your infrastructure.

## How It Works

1. **Connect wallet** — LastCheck wraps it into a Safe multisig where the agent becomes a mandatory co-signer. EIP-7702 support is in progress for a seamless experience without Safe.
2. **Set rules in plain English** — compiled into deterministic YAML. Hard-enforced at the first layer, the AI cannot override them.
3. **AI reviews what passes** — simulates execution via **Nano Claw**, LastCheck's custom simulator, to catch novel attacks and anomalous behaviour. Protocol-specific skills (MEV, phishing, drainer patterns) plug in alongside it.
4. **Suspicious? You decide** — alert via Telegram, Signal, or Ledger / Trezor. Proceed or reject.

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

## Run it

- **Engine** (bot, dashboard, watcher, Safe poller) — see [`engine/README.md`](engine/README.md)
- **AI layer & MCP tools** for driving approvals from Claude Code — see [`engine/ai/README.md`](engine/ai/README.md)
- **Landing site + onboarding wizard** — see [`landing/README.md`](landing/README.md)

For GitHub Pages project-site deployments, use hash-based onboarding URLs:

- Marketing root: `https://ivanvolov.github.io/lastCheck/`
- Onboarding: `https://ivanvolov.github.io/lastCheck/#/setup/step1-deploy`

## Links

- [ETHGlobal Showcase](https://ethglobal.com/showcase/lastcheck-ig7zw)

## Support on Giveth

LastCheck is listed as a public good on Giveth — [support development here](https://giveth.io/project/self-hosted-ai-co-signer-for-your-transactions).
