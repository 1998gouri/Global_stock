# Market Data and Alert Protocol

## Quote event
Each normalized event carries instrument ID, symbol, exchange/MIC, currency, nullable last/bid/ask/volume, event type, provider, source timestamp, received timestamp, entitlement, freshness, optional provider sequence, and quality flags.

## Freshness and entitlement
Entitlement is realtime, delayed, end-of-day, or unknown. Freshness is LIVE, DELAYED, STALE, CLOSED, UNAVAILABLE, or UNKNOWN. Never infer realtime entitlement from a fast HTTP response. Preserve source time separately from receive time. A delayed entitlement remains DELAYED even if just received. A stale quote must not trigger a live alert unless explicitly enabled.

## Streaming lifecycle
Connect using the provider's documented secure streaming protocol; authenticate without logging secrets; subscribe only to entitled instruments; normalize and validate messages; track sequence numbers; reconnect with exponential backoff and jitter; resubscribe after reconnect; reconcile with provider snapshots/replay when supported. If replay is unavailable, flag a possible data gap.

## REST fallback
Use only provider-approved intervals and batch endpoints. Respect quotas and Retry-After. Back off on 429 and transient 5xx. Never assume one-second polling is permitted. Expose configured and observed polling intervals.

## Alerts
For downward target rules, trigger when last_price <= target_price on accepted market events. Deduplicate by rule/instrument/event and apply a persisted cooldown. Alert payload includes symbol, exchange, observed price, target, currency, provider, entitlement, freshness, and timestamp. Do not generate an alert from missing, stale, or unknown data by default.

## Failures and audit
Missing data is not zero. Timeout is not a price. Closed market is not provider failure. Record provider, product, endpoint, market scope, entitlement, terms/attribution URL, cadence, last success, last error, and coverage limits. Never log API keys or Telegram tokens.
