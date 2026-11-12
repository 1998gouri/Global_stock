"""Optional Alpaca IEX streaming adapter.

Free Alpaca equity data is IEX-only and US-focused; it is not a global consolidated feed.
Configure ALPACA_API_KEY and ALPACA_API_SECRET before starting this adapter.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Awaitable, Callable

import websockets
from websockets.exceptions import ConnectionClosed

from app.models import Entitlement, Freshness, Quote

log = logging.getLogger(__name__)
IEX_STREAM_URL = "wss://stream.data.alpaca.markets/v2/iex"

async def run_alpaca_iex_stream(
    api_key: str,
    api_secret: str,
    symbols: list[str],
    on_quote: Callable[[Quote], Awaitable[None]],
    stop: asyncio.Event,
) -> None:
    """Connect, authenticate, subscribe and forward trade/quote events.

    Reconnects with bounded exponential backoff. Provider sequence/replay recovery
    is not assumed; callers should mark a gap after an unexpected disconnect.
    """
    if not api_key or not api_secret:
        raise ValueError("Alpaca API credentials are required")
    if not symbols:
        raise ValueError("At least one symbol is required")
    delay = 1
    while not stop.is_set():
        try:
            async with websockets.connect(
                IEX_STREAM_URL,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=5,
                max_size=2**20,
            ) as ws:
                greeting = await ws.recv()
                log.info("Alpaca stream connected: %s", greeting)
                await ws.send(json.dumps({
                    "action": "auth",
                    "key": api_key,
                    "secret": api_secret,
                }))
                auth_reply = json.loads(await ws.recv())
                if any(item.get("msg") == "authenticated" for item in auth_reply if isinstance(item, dict)):
                    pass
                elif any(item.get("T") == "error" for item in auth_reply if isinstance(item, dict)):
                    raise RuntimeError(f"Alpaca authentication failed: {auth_reply}")
                await ws.send(json.dumps({
                    "action": "subscribe",
                    "trades": symbols,
                    "quotes": symbols,
                }))
                delay = 1
                while not stop.is_set():
                    raw = await asyncio.wait_for(ws.recv(), timeout=30)
                    for item in json.loads(raw):
                        if not isinstance(item, dict):
                            continue
                        kind = item.get("T")
                        if kind not in ("t", "q"):
                            continue
                        symbol = item.get("S", "")
                        stamp = item.get("t")
                        source_time = datetime.fromisoformat(stamp.replace("Z", "+00:00")) if stamp else None
                        is_trade = kind == "t"
                        price = item.get("p") if is_trade else None
                        quote = Quote(
                            instrument_id=f"alpaca:US:{symbol}",
                            symbol=symbol,
                            exchange="IEX",
                            mic="IEXG",
                            currency="USD",
                            last_price=float(price) if price is not None else None,
                            bid=float(item["bp"]) if item.get("bp") is not None else None,
                            ask=float(item["ap"]) if item.get("ap") is not None else None,
                            volume=float(item["s"]) if is_trade and item.get("s") is not None else None,
                            event_type="trade" if is_trade else "quote",
                            provider="alpaca_iex",
                            source_timestamp=source_time,
                            received_timestamp=datetime.now(timezone.utc),
                            entitlement=Entitlement.REALTIME,
                            freshness=Freshness.LIVE,
                            sequence=str(item.get("i")) if item.get("i") is not None else None,
                        )
                        await on_quote(quote)
        except (ConnectionClosed, asyncio.TimeoutError, OSError, RuntimeError) as exc:
            log.warning("Alpaca IEX stream interrupted: %s", exc)
            try:
                await asyncio.wait_for(stop.wait(), timeout=delay)
            except asyncio.TimeoutError:
                pass
            delay = min(delay * 2, 60)
