from fastapi.openapi.models import Schema

from sqlalchemy import MetaData, Column, CheckConstraint, Table, ForeignKey, Integer, DateTime, Text, Interval, Float, \
    Boolean, ForeignKeyConstraint, String, UniqueConstraint
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime, timedelta
from typing import List, Optional
from pytimeparse.timeparse import timeparse
import re


class IndicatorBase(BaseModel):
    name: str
    valid: bool


class Indicator(IndicatorBase):
    signal_id: int


class IndicatorsCreate(BaseModel):
    __root__: List[Indicator]

    @root_validator(pre=True)
    def _set_fields(cls, payload: dict):
        message = payload['__root__']['message']
        signal_id = payload['__root__']['signal_id']
        header_regex = r'🔔 (?P<name>.+) 💱 (?P<symbol>.+) ⏱️ (?P<timeUnit>.+)\n+(?P<operator>\w+)\n'
        header = re.match(header_regex, message).groupdict()
        body = re.sub(header_regex, '', message)
        body_regex = r'\|\s+(?P<name>.+) (?P<valid>.*)'
        indicator_arr = []
        for line in body.split('\n'):
            match = re.match(body_regex, line.strip())
            indicator_arr.append(match.groupdict())
            indicator_arr[-1]['valid'] = indicator_arr[-1]['valid'] in ['✔️', '✔']
            indicator_arr[-1]['signal_id'] = signal_id

        return {'__root__': indicator_arr}


class IndicatorDB(Indicator):
    id: int


class SignalBase(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    type: str
    exchange: Optional[str]
    symbol: str
    price: Optional[float]
    timeUnit: Optional[timedelta]
    operator: Optional[str]
    indicators: Optional[List[IndicatorDB]]


class AuroxSignal(BaseModel):
    message: str
    price: float
    symbol: str
    timeUnit: timedelta | None = None
    timestamp: datetime | None = None
    password: str | None = None

    @validator('timeUnit', pre=True, always=True)
    def _time_unit_to_timedelta(cls, value: str) -> timedelta:
        return timeparse(value)


class SignalCreate(SignalBase):

    @validator('type', pre=True, always=True)
    def convert_type(cls, value: str):
        return value.upper()


class SignalDB(SignalBase):
    id: int


metadata = MetaData()

signals = Table(
    "signals",
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('timestamp', DateTime(timezone=True), nullable=False),
    Column('type', String(length=5), nullable=False),
    CheckConstraint("type LIKE 'LONG' OR type LIKE 'SHORT'", name='type_validator'),
    Column('exchange', String(length=32)),
    Column('symbol', String(length=16), nullable=False),
    CheckConstraint("char_length(symbol) > 1", name='symbol_validator'),
    Column('price', Float),
    Column('timeUnit', Interval),
    Column('operator', String(length=3)),
    CheckConstraint("operator LIKE 'AND' OR operator LIKE 'OR'", name='operator_validator'),
    UniqueConstraint('timestamp', 'type', 'exchange', 'symbol', 'timeUnit', 'operator')
)

indicators = Table(
    "indicators",
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', Text, nullable=False),
    Column('valid', Boolean, nullable=False),
    Column('signal_id', Integer, nullable=False),
    ForeignKeyConstraint(
            ['signal_id'], ['signals.id'], ondelete='CASCADE', onupdate='CASCADE'
        )
)


