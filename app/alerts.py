from datetime import datetime, timezone
from app.models import AlertRule, Quote, Freshness

def should_trigger(rule: AlertRule, quote: Quote, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    if not rule.enabled or quote.last_price is None or quote.instrument_id != rule.instrument_id:
        return False
    if quote.freshness in (Freshness.STALE, Freshness.UNAVAILABLE, Freshness.UNKNOWN):
        return False
    if rule.direction != 'below_or_equal' or quote.last_price > rule.target_price:
        return False
    if rule.last_triggered_at is not None:
        if (now - rule.last_triggered_at).total_seconds() < max(0, rule.cooldown_seconds):
            return False
    return True

def mark_triggered(rule: AlertRule, now: datetime | None = None) -> AlertRule:
    rule.last_triggered_at = now or datetime.now(timezone.utc)
    return rule
