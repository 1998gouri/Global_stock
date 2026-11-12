from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.config import settings
from app.models import Quote, SourceHealth, Entitlement

app = FastAPI(title='Global Stock Monitor API', version='0.1.0')
latest_quotes: dict[str, Quote] = {}
source_health = {settings.data_provider: SourceHealth(provider=settings.data_provider, status='DEMO_ONLY' if settings.data_provider == 'demo' else 'NOT_CONNECTED', entitlement=Entitlement.UNKNOWN, notes=['Real provider adapter and entitlement are not configured yet.'])}
clients: set[WebSocket] = set()

@app.get('/health')
async def health():
    return {'status':'ok','environment':settings.app_env,'provider':settings.data_provider,'server_time':datetime.now(timezone.utc)}

@app.get('/quotes')
async def quotes():
    return {'quotes':[q.model_dump(mode='json') for q in latest_quotes.values()], 'count':len(latest_quotes)}

@app.get('/sources/health')
async def sources_health():
    return {k:v.model_dump(mode='json') for k,v in source_health.items()}

@app.post('/internal/quotes', include_in_schema=False)
async def ingest_quote(quote: Quote):
    quote.received_timestamp=datetime.now(timezone.utc)
    latest_quotes[quote.instrument_id]=quote
    stale=[]
    for ws in clients:
        try: await ws.send_json(quote.model_dump(mode='json'))
        except Exception: stale.append(ws)
    for ws in stale: clients.discard(ws)
    return {'accepted':True,'instrument_id':quote.instrument_id}

@app.websocket('/ws/quotes')
async def quote_stream(ws: WebSocket):
    await ws.accept(); clients.add(ws)
    try:
        await ws.send_json({'type':'snapshot','quotes':[q.model_dump(mode='json') for q in latest_quotes.values()]})
        while True: await ws.receive_text()
    except WebSocketDisconnect:
        clients.discard(ws)
