# Global Stock Monitor

A streaming-first market-monitoring project with quote provenance, target alerts, Telegram integration planned, and student-focused financial education.

> **Free-tier commitment:** the initial deployment will use free-access sources only. No paid subscription is required by this repository. Free access does not mean every market is real-time. The app must show actual provider entitlement and quote age.

## Live-data expectations

- The UI refresh target can be one second.
- WebSocket updates arrive when a provider emits a market event; a quote is not guaranteed to change every second.
- REST polling must obey each provider's published quota; do not poll every second unless explicitly allowed.
- Free global equity feeds are generally incomplete, delayed, limited, or exchange-specific. We do not claim universal real-time global coverage.
- Every quote must expose provider, exchange, source timestamp, receive timestamp, entitlement, freshness, and quality flags.
- If data is delayed, stale, closed, unavailable, or unknown, show that status prominently rather than calling it live.

## Free provider adapter currently included

The optional `app/providers/alpaca_stream.py` adapter connects to Alpaca's IEX WebSocket endpoint for US-listed instruments, when the user has an eligible free account and API credentials.

**Important limitations:** IEX is one US exchange venue, not the consolidated US market feed and not a global feed. The free plan has limited streaming symbol capacity and coverage. Confirm current limits and terms in the provider's official documentation before relying on it:
https://docs.alpaca.markets/us/v1.1/docs/about-market-data-api

Provider notes and other free/delayed source candidates: [app/providers/README.md](app/providers/README.md).

## Architecture

1. Provider adapters normalize trades and quotes.
2. WebSockets are preferred where a free entitlement allows it.
3. REST fallback is quota-aware and never assumes a one-second interval.
4. A quote cache and WebSocket API distribute received events.
5. Freshness states are LIVE, DELAYED, STALE, CLOSED, UNAVAILABLE, and UNKNOWN.
6. Alert evaluation occurs on accepted market events with cooldown checks.
7. Source-health audit records disconnects, errors, and gaps.

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

## Configuration and secrets

Keep credentials in environment variables or local `.env`; never commit API keys or Telegram tokens. The current default `DATA_PROVIDER=demo` does not provide real prices.

The Alpaca adapter currently exposes a reusable stream function. It is not yet wired into application startup or the quote ingestion lifecycle. Add credentials only in your own deployment environment:
- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`

Telegram variables are reserved for the upcoming notification implementation:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## API

- `GET /health` — service health.
- `GET /quotes` — latest normalized quote snapshots.
- `GET /sources/health` — provider health.
- `POST /internal/quotes` — internal ingestion hook; secure before deployment.
- `WS /ws/quotes` — push ingested quote events.
- `GET /docs` — interactive API documentation.

See [openapi.json](openapi.json) and [PROTOCOL.md](PROTOCOL.md).

## Security and deployment

- Use HTTPS/WSS in deployment.
- Authenticate APIs and protect internal ingestion routes.
- Use persistent storage for watchlists, alerts, idempotency, and audit history.
- Run streaming on an always-on worker; GitHub Actions is not a one-second scheduler.
- Respect exchange/provider licensing, attribution, redistribution restrictions, and API quotas.
- Never scrape private endpoints or evade provider limits.

## Implementation status

Implemented:
- FastAPI starter service, health, quote and source-health endpoints.
- Normalized quote, freshness, entitlement, alert-rule and source-health models.
- Downward target alert evaluator with cooldown check.
- WebSocket broadcast endpoint.
- Optional Alpaca IEX streaming adapter with reconnect backoff.
- Provider coverage notes, protocol, dependency list, environment template, and OpenAPI contract.

Still needed before a usable live deployment:
- Wire the provider adapter into application startup and ingestion.
- Verify current Alpaca account entitlements and test a real IEX subscription.
- Persist quotes/alerts/audit events and add idempotent Telegram delivery.
- Build dashboard, global instrument directory, source audit and student hub.
- Add authentication, automated tests, deployment and monitoring.

## Trade-offs

The project prioritizes truthfulness and traceability over a misleading “live” badge. A one-second UI refresh is inexpensive; a one-second global polling loop is not feasible under most free quotas. The system should degrade visibly rather than silently present stale data as current.
