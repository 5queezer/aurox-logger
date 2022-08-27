import os
from typing import Optional, List

import uvicorn
from databases import Database
from fastapi import FastAPI, status, Depends, Request, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware import Middleware

from app.database import get_database, sqlalchemy_engine
from app.models import metadata, SignalCreate, signals as signals_model, indicators as indicators_model, AuroxSignal, \
    IndicatorsCreate, Indicator, \
    IndicatorDB, SignalBase
from app.auth import APIKeyJson
from app.middleware import ProcessTimeMiddleware
from datetime import datetime, timedelta


app = FastAPI(middleware=[Middleware(ProcessTimeMiddleware)])
api_key_json = APIKeyJson(name='password')


@app.on_event('startup')
async def startup():
    await get_database().connect()
    metadata.create_all(sqlalchemy_engine)


@app.on_event("shutdown")
async def shutdown():
    await get_database().disconnect()


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_signal(signal: AuroxSignal = Depends(api_key_json), database: Database = Depends(get_database)):
    try:
        exchange, symbol = signal.symbol.split(':')
    except ValueError:
        exchange = None
        symbol = signal.symbol

    values = {
        'timestamp': signal.timestamp,
        'type': 'LONG',
        'exchange': exchange or None,
        'symbol': symbol,
        'price': signal.price,
        'timeUnit': signal.timeUnit,
        'operator': 'AND'
    }

    insert_query = signals_model.insert().values(values)
    signal_id = await database.execute(insert_query)

    message_create = IndicatorsCreate.parse_obj({'message': signal.message, 'signal_id': signal_id})
    indicators_insert = message_create.dict().get('__root__')
    insert_query = indicators_model.insert().values(indicators_insert)
    await database.execute(insert_query)

    return signal_id


# @app.get("/", status_code=status.HTTP_200_OK)
# async def read_signal(symbol: str,
#                       limit: timedelta,
#                       timeUnit: timedelta = Optional[timedelta],
#                       exchange: str = Optional[str],
#                       operator: str = Optional[str],
#                       indicators: List[IndicatorDB] = Optional[List[IndicatorDB]],
#                       database: Database = Depends(get_database)):
    # session = Session(database)
    # stmt = select(SignalBase).where(SignalBase.symbol.in_([symbol]))
    # return session.scalars(stmt)



if __name__ == '__main__':
    debug = os.getenv('DEBUG').lower() == 'true'
    uvicorn.run("app.main:app", port=8008, host='127.0.0.1', debug=debug)
