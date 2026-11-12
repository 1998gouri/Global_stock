# Global Stock Monitor

A global-market monitoring platform designed around streaming-first market data, fast target-price alerts, transparent source provenance, and student-focused investing education.

> **Important:** “Live” is specific to a provider, exchange, instrument, subscription, and market session. The dashboard must never label a quote real-time unless the provider entitlement confirms it. A one-second screen refresh does not mean a new exchange price arrived in that second.

## Goals

- Global instrument directory with exchange, MIC, and currency identifiers.
- Streaming-first prices through licensed provider WebSockets where available.
- Provider-approved REST fallback with quota-aware scheduling and backoff.
- Telegram target-price alerts with cooldowns and duplicate suppression.
- Per-quote provenance: provider, source timestamp, receive timestamp, entitlement, freshness, and quality flags.
- Source audit for prices, filings, statements, corporate actions, news, and research.
- Student learning hub for all budgets, risk examples, diversification, funds/ETFs/SIPs, and paper trading.
- No fabricated prices, silent substitution of delayed data for live data, or bypassing paywalls/access controls.

## What “every second” means

- **Dashboard refresh:** may run once per second.
- **Streaming quote:** arrives when the provider emits an event; there is no universal one-event-per-second guarantee for every instrument.
- **REST polling:** only at intervals permitted by the provider and exchange rules. One-second polling is not enabled by default.
- **Global coverage:** realtime entitlement, delayed feeds, instrument availability, and exchange coverage vary by provider and subscription.
- **No missed-event guarantee:** recovery depends on provider replay/snapshot features and network conditions.

## Architecture

1. Provider adapters normalize trades, quotes, bars, and connection status.
2. WebSockets are preferred where licensed and available.
3. REST is a fallback, never a reason to exceed quotas.
4. A latest-quote cache supports dashboard snapshots and event streaming.
5. Freshness monitor classifies data as LIVE, DELAYED, STALE, CLOSED, UNAVAILABLE, or UNKNOWN.
6. Alert engine evaluates accepted market events and applies persisted cooldowns.
7. Source-health audit records disconnects, throttling, missing fields, errors, and reconnect attempts.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs`.

## Configuration

Configure secrets only in environment variables or a local `.env` file. Never commit API keys or Telegram bot tokens.

- `DATA_PROVIDER`: currently `demo` by default.
- `DATA_API_KEY`: provider API key when required.
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`: Telegram delivery credentials.
- `QUOTE_STALE_AFTER_SECONDS`: stale threshold.
- `ALERT_COOLDOWN_SECONDS`: minimum repeat alert interval.
- `UI_REFRESH_SECONDS`: UI refresh target (default 1).

**Demo mode is not live market data.** A real provider adapter and a valid exchange-level realtime entitlement must be configured before any quote can be described as live. The current code is a starter service skeleton, not a finished production trading terminal.

## API

- `GET /health` — service health.
- `GET /quotes` — latest normalized snapshots.
- `GET /sources/health` — provider health.
- `POST /internal/quotes` — internal ingestion hook (not public; add authentication before deployment).
- `WS /ws/quotes` — push quote events to clients.
- `GET /docs` — interactive API documentation.

See [openapi.json](openapi.json) and [PROTOCOL.md](PROTOCOL.md).

## Provider strategy

Provider support must be checked for each exchange, asset class, instrument, and entitlement. Examples of official documentation to evaluate:
- EODHD WebSocket API: https://eodhd.com/financial-apis/new-real-time-data-api-websockets
- Alpha Vantage API documentation: https://www.alphavantage.co/documentation/
- Webull market-data streaming documentation: https://developer.webull.com/apis/docs/market-data-api/data-streaming-api/

These examples are not a claim that any one provider supplies realtime prices for every world exchange. Confirm exchange coverage, realtime/delayed status, redistribution rights, request quotas, and subscription cost before selecting a provider.

## Security and deployment

- Keep credentials in environment variables or a secrets manager.
- Use HTTPS/WSS and authentication in deployed environments.
- Protect internal ingestion routes; do not expose the starter internal endpoint publicly.
- Use persistent storage (e.g. PostgreSQL/Redis) for production watchlists, alerts, event IDs, and audit history.
- Use an always-on worker/container for streaming. GitHub Actions is not a reliable one-second scheduler.
- Respect exchange/provider licensing, attribution, redistribution restrictions, and API quotas.

## Current implementation status

Implemented in this initial commit series:
- FastAPI service skeleton and health/quote/source-health endpoints.
- Normalized quote, freshness, entitlement, alert-rule, and source-health models.
- Event-driven downward target rule evaluator with cooldown check.
- WebSocket endpoint for broadcasting ingested quote events.
- Protocol specification, dependency list, and environment template.

Not yet implemented:
- Real provider adapter / verified exchange-level realtime feed.
- Telegram sender and delivery retry persistence.
- Durable database, authentication, production dashboard, global instrument master, and full research/source-audit ingestion.
- Automated tests, deployment, and operational monitoring.

## Reflection and trade-offs

The system prioritizes correctness and traceability over claiming universal realtime coverage. Streaming reduces latency and polling load, but coverage and entitlements differ by venue and may cost money. A one-second UI refresh is inexpensive; one-second REST polling across a large global universe is not. The platform should visibly degrade rather than silently present stale prices as live.
