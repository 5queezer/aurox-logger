import os
import uvicorn
from typing import Optional, List

from databases import Database
from fastapi import FastAPI, status, Depends, Request, Header
from fastapi.responses import FileResponse
from starlette.middleware import Middleware
from starlette.responses import JSONResponse

from app.database import get_database, sqlalchemy_engine
from app.models import metadata, SignalCreate, signals as signals_model, indicators as indicators_model, AuroxSignal, \
    IndicatorsCreate, Indicator, \
    IndicatorDB, SignalBase
from app.auth import APIKeyJson
from app.middleware import ProcessTimeMiddleware, CatchAllExceptionsMiddleWare
from datetime import timedelta

import logging


##loging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=os.getenv('DEBUG', None) and 'DEBUG' or 'INFO',
                    format='%(levelname)6s | %(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log/log.txt',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger = logging.getLogger()


app = FastAPI(
    middleware=[
        Middleware(CatchAllExceptionsMiddleWare),
        Middleware(ProcessTimeMiddleware),
    ],
)


@app.on_event('startup')
async def startup():
    await get_database().connect()
    metadata.create_all(sqlalchemy_engine)


@app.on_event("shutdown")
async def shutdown():
    await get_database().disconnect()


@app.get('/')
async def index():
    return JSONResponse({'status': 'success'}, status_code=status.HTTP_200_OK)


@app.get('/favicon.ico')
async def favicon():
    try:
        return FileResponse('./app/favicon.ico')
    except RuntimeError:
        return JSONResponse({'status': 'error'}, status_code=status.HTTP_404_NOT_FOUND)


@app.post("/long", status_code=status.HTTP_201_CREATED)
@app.post("/short", status_code=status.HTTP_201_CREATED)
@app.post("/alert", status_code=status.HTTP_201_CREATED)
@app.post("/exit", status_code=status.HTTP_201_CREATED)
async def create_signal(request: Request, real_ip: str = Header(None, alias='X-Real-IP'),
                        signal: AuroxSignal = Depends(APIKeyJson(name='password')),
                        database: Database = Depends(get_database)):
    long_or_short = request.scope['path'].lstrip('/')
    try:
        exchange, symbol = signal.symbol.split(':')
    except ValueError:
        exchange = None
        symbol = signal.symbol

    values = {
        'timestamp': signal.timestamp,
        'type': long_or_short.upper(),
        'exchange': exchange or None,
        'symbol': symbol,
        'price': signal.price,
        'timeUnit': signal.timeUnit,
        'source': real_ip or request.client.host
    }

    # insert signal
    insert_query = signals_model.insert().values(values)
    signal_id = await database.execute(insert_query)

    # insert indicators
    indicators_create = IndicatorsCreate.parse_obj({'message': signal.message, 'signal_id': signal_id})
    indicators_insert = indicators_create.dict().get('__root__')
    for indicator in indicators_insert[1]:
        insert_query = indicators_model.insert().values(indicator)
        await database.execute(insert_query)

    # update signal operator
    operator = indicators_insert[0]['operator']
    update_query = signals_model.update().where(signals_model.c.id == signal_id).values(operator=operator)
    await database.execute(update_query)

    info = {
        'type': long_or_short,
        'exchange': values['exchange'],
        'symbol': values['symbol'],
        'price': values['price'],
        'timestamp': str(values['timestamp']),
        'signal_id': signal_id
    }
    logger.info(f'signal {long_or_short} {info}')
    return JSONResponse({'status': 'success', **info})


@app.get("/get", status_code=status.HTTP_200_OK)
async def read_signal(symbol: str,
                      limit: timedelta,
                      timeUnit: timedelta = Optional[timedelta],
                      exchange: str = Optional[str],
                      indicators: List[IndicatorDB] = Optional[List[IndicatorDB]],
                      database: Database = Depends(get_database)):
    pass


if __name__ == '__main__':
    debug = os.getenv('DEBUG', '').lower() in ['true', 'yes', '1']
    uvicorn.run("app.main:app", port=8008, host='127.0.0.1', debug=debug)
