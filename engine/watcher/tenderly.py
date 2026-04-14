"""
Tenderly simulation client.

Simulates a Safe's queued transaction against an Arbitrum fork and returns
the net USD outflow from the Safe (sum of dollar values of asset_changes
where `from == safe_address`). Used by the watcher to populate
`token_out_usd` / `price_impact_pct` before rule evaluation.

Env:
  TENDERLY_ACCESS_KEY     — API access key (required to enable)
  TENDERLY_ACCOUNT_SLUG   — account slug
  TENDERLY_PROJECT_SLUG   — project slug
  TENDERLY_NETWORK_ID     — defaults to 42161 (Arbitrum One)
"""

import logging
import os
from typing import Optional

import aiohttp

log = logging.getLogger(__name__)

_API = "https://api.tenderly.co/api/v1/account/{acc}/project/{proj}/simulate"


def _cfg() -> Optional[tuple[str, str, str, str]]:
    key = os.getenv("TENDERLY_ACCESS_KEY", "").strip()
    acc = os.getenv("TENDERLY_ACCOUNT_SLUG", "").strip()
    proj = os.getenv("TENDERLY_PROJECT_SLUG", "").strip()
    net = os.getenv("TENDERLY_NETWORK_ID", "42161").strip()
    if not (key and acc and proj):
        return None
    return key, acc, proj, net


def is_enabled() -> bool:
    return _cfg() is not None


async def simulate_safe_tx(
    session: aiohttp.ClientSession,
    safe_address: str,
    to: str,
    data: str,
    value: int,
) -> Optional[dict]:
    """
    Simulate a Safe-initiated call via Tenderly.

    Returns a dict with:
      - token_out_usd: float  (sum of dollar values of outbound asset_changes)
      - asset_changes: list   (raw passthrough, may be empty)
      - success: bool
    Or None if Tenderly isn't configured / the request failed.
    """
    cfg = _cfg()
    if not cfg:
        return None
    key, acc, proj, net = cfg

    payload = {
        "network_id": net,
        "from": safe_address,
        "to": to,
        "input": data or "0x",
        "value": str(value),
        "gas": 8_000_000,
        "gas_price": "0",
        "save": False,
        "save_if_fails": False,
        "simulation_type": "quick",
    }
    headers = {"X-Access-Key": key, "Content-Type": "application/json"}
    url = _API.format(acc=acc, proj=proj)

    try:
        async with session.post(
            url,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as r:
            if r.status != 200:
                body = await r.text()
                log.warning("Tenderly %s: %s", r.status, body[:200])
                return None
            result = await r.json()
    except Exception as e:
        log.warning("Tenderly request failed: %s", e)
        return None

    tx = result.get("transaction") or {}
    info = tx.get("transaction_info") or {}
    changes = info.get("asset_changes") or []

    safe_lc = safe_address.lower()
    token_out_usd = 0.0
    for ch in changes:
        frm = (ch.get("from") or "").lower()
        if frm != safe_lc:
            continue
        dv = ch.get("dollar_value")
        try:
            token_out_usd += float(dv) if dv is not None else 0.0
        except (TypeError, ValueError):
            pass

    return {
        "token_out_usd": token_out_usd,
        "asset_changes": changes,
        "success": tx.get("status", True),
    }
