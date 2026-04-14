# LastCheck rules — how they work

`rules.yaml` is the rulebook the watcher evaluates every pending Safe
transaction against. Rules are processed **top to bottom** and the **first
match wins**. If nothing matches, the default action is **`reject`**
(default-deny): anything the rulebook doesn't explicitly approve is
blocked. You must have at least one `approve` rule or every tx will be
rejected.

The watcher re-reads this file on every poll tick (every 5s), so you can
edit it in place — no restart needed.

## Actions

Each rule has one of two actions:

- `reject` — the watcher will refuse to co-sign and Telegram-notify the user.
- `approve` — the watcher co-signs automatically.

There's no `confirm`/escalate path yet — you either `approve` or `reject`.

## Wildcard: `"all"`

Any list in `rules.yaml` that can be used with the `in` / `not in`
operator accepts the literal string `"all"` as a wildcard that matches
everything. This applies to `allowlist.contracts` and
`blocklist.addresses`. So:

```yaml
allowlist:
  contracts: ["all"]          # every `to` is on the allowlist
```

is equivalent to "match anything" for `to in allowlist.contracts`, and
`to not in allowlist.contracts` will always be false.

## The condition expression

Each rule has a `condition:` — a Python boolean expression that's `eval`'d
in a sandbox (no builtins). It has access to the variables below. A
`SimpleNamespace` wraps `allowlist` and `blocklist` so you can use dot
syntax (`allowlist.contracts`) in conditions.

### Available variables

These come straight from the pending Safe transaction after enrichment.

| Variable | Type | Source | Notes |
|---|---|---|---|
| `to` | `str` | calldata `to` (lowercased) | Target contract / EOA |
| `value_usd` | `float` | `value_wei * ETH_price` | **Native ETH outflow only** — does not include token transfers |
| `is_contract` | `bool` | `eth_getCode(to) != "0x"` | True if `to` has deployed bytecode |
| `is_erc20_approval` | `bool` | calldata selector `0x095ea7b3` | True iff it's a literal `approve()` call |
| `approval_amount` | `int` | decoded from calldata | ERC-20 approval amount (raw, no decimals) |
| `spender` | `str` | decoded from calldata | Spender address in `approve()` (lowercased) |
| `token_out_usd` | `float` | **Tenderly sim** if configured, else `value_usd` | Net USD leaving the Safe |
| `price_impact_pct` | `float` | **not implemented** — always `0` | Slippage for swaps. Rules depending on this will never fire. |
| `daily_spent_usd` | `float` | TxStore (last 24h approved) | Sum of `value_usd` over approved txs in the last 24h. **Counts ETH outflow only.** |
| `daily_swap_count` | `int` | TxStore (last 24h approved) | Number of approved txs where calldata matched a swap selector |
| `max_uint256` | `int` | `2**256 - 1` | Useful for detecting unlimited approvals |
| `allowlist.contracts` | `list[str]` | from `rules.yaml` → `allowlist.contracts` | Lowercased |
| `blocklist.addresses` | `list[str]` | from `rules.yaml` → `blocklist.addresses` | Lowercased |

## Caveats / gotchas

1. **`value_usd` is ETH-only.** Token transfers (USDC, WETH, etc.) don't
   move the Safe's native ETH balance, so `value_usd` stays at 0 for them.
   Rules that should block token outflow must use `token_out_usd`, and
   `token_out_usd` is only accurate when Tenderly is configured
   (`TENDERLY_ACCESS_KEY` + slugs in `.env`). Without Tenderly,
   `token_out_usd` falls back to `value_usd`, meaning token-heavy rules
   silently degrade to ETH-only rules.

2. **`price_impact_pct` is not implemented.** The watcher hard-codes it to
   `0`. Any rule comparing `price_impact_pct > X` will never trigger.
   Leaving the rule in place is harmless but misleading.

3. **Daily counters only look at `approved` txs.** A tx that got rejected
   (by rules or by the user) does not count toward `daily_spent_usd` or
   `daily_swap_count`.

4. **Swap detection is a heuristic.** The watcher matches a small list of
   known selectors (Uniswap v2/v3, 1inch) in `safe_poller.py:is_likely_swap`.
   Unknown DEX aggregators will not set `is_swap`, so they won't count
   toward `daily_swap_count`, but they will still be evaluated by
   `block_large_tx` via `token_out_usd` if Tenderly is on.

5. **`eval` errors are silent.** If a rule's condition raises (typo in a
   variable name, attribute that doesn't exist, etc.) it's logged at
   WARNING and the evaluator moves on. Check the engine logs if a rule
   seems to "not fire".

## Editing rules

### Direct edit

Just edit `rules.yaml`. The watcher reloads on every poll. No restart.

### Via Telegram voice

Send a voice message to the paired bot describing the change in plain
language, e.g. *"block any transfer to an address that isn't on the
allowlist"*. The bot:

1. Transcribes with Whisper.
2. Asks GPT to rewrite `rules.yaml` to reflect the intent.
3. Validates the YAML and writes it back in place.

This requires `OPENAI_API_KEY` in `.env`.

## The shipped ruleset

`rules.yaml` ships with three rules — that's it. Add more only when you
need them.

1. **`block_blocklisted`** — hard-reject anything whose `to` is on
   `blocklist.addresses`.
2. **`block_unlimited_approval_unknown`** — reject `approve(spender,
   max_uint256)` when the spender is not on the allowlist. Classic
   drainer guard.
3. **`approve_allowlisted`** — approve any tx whose `to` is on
   `allowlist.contracts`. Combine with `contracts: ["all"]` for a
   permissive setup, or list specific contracts explicitly.

Anything that doesn't match falls through to default-deny.

## Minimal setups

**Permissive (for testing):**

```yaml
allowlist:
  contracts: ["all"]
```

Every tx is auto-approved, except those matching a blocklisted address.

> ⚠️ **Note:** wildcarding `allowlist.contracts` with `"all"` also
> satisfies the `spender not in allowlist.contracts` check in
> `block_unlimited_approval_unknown` — so unlimited approvals will
> **not** be blocked in this permissive setup. If you want the
> drainer guard, list real contracts explicitly instead of using the
> wildcard.

**Strict allowlist:**

```yaml
allowlist:
  contracts:
    - "0xE592427A0AEce92De3Edee1F18E0157C05861564"   # Uniswap V3 router
blocklist:
  addresses:
    - "0x0000000000000000000000000000000000000bad"
```

Only the Uniswap V3 router is allowed; everything else is denied by
default.

## Adding your own rules

Keep it simple — fewer rules are easier to reason about. A few shapes
that are known to work today:

```yaml
# 24h ETH-outflow cap (requires nothing extra)
- id: cap_daily_eth
  condition: "daily_spent_usd > 2000"
  action: reject

# Per-tx USD cap (accurate only with Tenderly enabled)
- id: cap_per_tx
  condition: "token_out_usd > 1000"
  action: reject
```

Not yet working and intentionally not shipped:

- Anything using `price_impact_pct` — the watcher doesn't compute it,
  so rules comparing it will never fire.
- `token_caps:` (top-level section) — wired in `safe_poller._run_rules`
  but relies on `value_usd` for matching, which is ETH-only. Leave it
  empty until per-token accounting lands.
