from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

def utc_now():
    return datetime.now(timezone.utc)

class Freshness(str, Enum):
    LIVE='LIVE'; DELAYED='DELAYED'; STALE='STALE'; CLOSED='CLOSED'; UNAVAILABLE='UNAVAILABLE'; UNKNOWN='UNKNOWN'

class Entitlement(str, Enum):
    REALTIME='realtime'; DELAYED='delayed'; END_OF_DAY='end_of_day'; UNKNOWN='unknown'

class Quote(BaseModel):
    instrument_id: str
    symbol: str
    exchange: str = ''
    mic: str = ''
    currency: str = ''
    last_price: float | None = None
    bid: float | None = None
    ask: float | None = None
    volume: float | None = None
    event_type: str = 'snapshot'
    provider: str = 'unknown'
    source_timestamp: datetime | None = None
    received_timestamp: datetime = Field(default_factory=utc_now)
    entitlement: Entitlement = Entitlement.UNKNOWN
    freshness: Freshness = Freshness.UNKNOWN
    sequence: str | None = None
    quality_flags: list[str] = Field(default_factory=list)

class AlertRule(BaseModel):
    id: str
    instrument_id: str
    symbol: str
    exchange: str = ''
    target_price: float
    currency: str = ''
    direction: str = 'below_or_equal'
    cooldown_seconds: int = 300
    enabled: bool = True
    last_triggered_at: datetime | None = None

class SourceHealth(BaseModel):
    provider: str
    status: str
    entitlement: Entitlement = Entitlement.UNKNOWN
    markets: list[str] = Field(default_factory=list)
    last_event_at: datetime | None = None
    last_success_at: datetime | None = None
    last_error: str | None = None
    configured_interval_seconds: float | None = None
    observed_interval_seconds: float | None = None
    notes: list[str] = Field(default_factory=list)
