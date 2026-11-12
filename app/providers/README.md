# Free provider coverage

## Alpaca Basic (optional)

The adapter in `alpaca_stream.py` targets the Alpaca IEX WebSocket feed. The free Basic equity feed is limited to US stocks/ETFs on IEX and a limited streaming symbol count (currently documented as 30). It is **not** a consolidated all-US feed and does not provide global exchange coverage. Create an account and API keys only if the service is available to you and its terms fit your use. Never share credentials in chat or commit them.

Official documentation: https://docs.alpaca.markets/us/v1.1/docs/about-market-data-api

## Global fallback

No free provider identified so far offers unrestricted, licensed, real-time streaming for every global equity exchange. Global free tiers commonly mean delayed, end-of-day, trial-only, or limited symbol access. Do not relabel those feeds as live. Provider adapters must declare actual exchange coverage and entitlement.

Possible research / delayed sources to evaluate separately:
- Twelve Data: broad symbol/exchange directory; free Basic is limited and international exchange access is plan-dependent. https://twelvedata.com/stocks
- EODHD: global delayed coverage on free tier; verify current quotas and license. https://eodhd.com/financial-apis/new-real-time-data-api-websockets
- Alpha Vantage: useful fundamentals and research endpoints; free request quota is limited and realtime/15-minute US quotes are premium-only. https://www.alphavantage.co/support/

## Policy

The application must show provider, exchange, entitlement, source timestamp, receive timestamp, and freshness for every quote. Do not scrape authenticated/private endpoints or evade quotas. Do not use a source for public redistribution unless its license permits it.
