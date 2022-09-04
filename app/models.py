from fastapi.openapi.models import Schema
from dateutil.parser import parse, ParserError

from sqlalchemy import MetaData, Column, CheckConstraint, Table, ForeignKey, Integer, DateTime, Text, Interval, Float, \
    Boolean, ForeignKeyConstraint, String, UniqueConstraint
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict
from pytimeparse.timeparse import timeparse
import re


class IndicatorBase(BaseModel):
    name: str
    valid: bool


class Indicator(IndicatorBase):
    signal_id: int


class IndicatorsCreate(BaseModel):
    __root__: Tuple[Dict, List[Indicator]]

    @root_validator(pre=True)
    def _set_fields(cls, payload: dict):
        message = payload['__root__']['message']
        signal_id = payload['__root__']['signal_id']
        header_regex = r'🔔 (?P<name>.+) 💱 (?P<symbol>.+) ⏱️ (?P<timeUnit>.+)\n+(?P<operator>\w+)\n'
        try:
            header = re.match(header_regex, message).groupdict()
        except AttributeError as e:
            raise AttributeError('message is malformed')
        body = re.sub(header_regex, '', message)
        body_regex = r'\|\s+(?P<name>.+) (?P<valid>.*)'
        indicator_arr = []
        for line in body.split('\n'):
            match = re.match(body_regex, line.strip())
            indicator_arr.append(match.groupdict())
            indicator_arr[-1]['valid'] = indicator_arr[-1]['valid'] in ['✔️', '✔']
            indicator_arr[-1]['signal_id'] = signal_id

        return {'__root__': (header, indicator_arr)}


class IndicatorDB(Indicator):
    id: int


class SignalBase(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    type: str
    exchange: Optional[str]
    symbol: str
    price: Optional[float]
    timeUnit: timedelta
    operator: Optional[str]
    indicators: Optional[List[IndicatorDB]]


class AuroxSignal(BaseModel):
    message: str
    price: Optional[float]
    symbol: str
    timeUnit: timedelta
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    password: str | None = None

    @validator('timestamp', pre=True, always=False)
    def _secure_datetime(cls, value: str) -> datetime:
        try:
            return parse(value)
        except ParserError:
            return datetime.now()

    @validator('timeUnit', pre=True, always=True)
    def _time_unit_to_timedelta(cls, value: str) -> timedelta:
        return timeparse(value)

    @validator('price', pre=True, always=False)
    def _money_to_float(cls, text: str) -> float | None:
        m = re.findall(r'([.,])', text)
        try:
            if len(m) >= 1:
                if m[-1] == '.':
                    # comma thousands separator
                    text = text.replace(',', '')
                    return float(text)
                elif m[-1] == ',':
                    # dot thousands separator
                    text = text.replace('.', '')
                    text = text.replace(',', '.')
                    return float(text)
            else:
                return float(text)
        except ValueError:
            return None


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
    Column('timestamp', DateTime(timezone=True)),
    Column('type', String(length=5), nullable=False),
    CheckConstraint("type LIKE 'LONG' OR type LIKE 'SHORT' OR type LIKE 'ALERT' OR type LIKE 'EXIT'", name='type_validator'),
    Column('exchange', String(length=32)),
    Column('symbol', String(length=16), nullable=False),
    CheckConstraint("char_length(symbol) > 1", name='symbol_validator'),
    Column('price', Float, nullable=True),
    Column('timeUnit', Interval, nullable=False),
    Column('operator', String(length=3)),
    CheckConstraint("operator LIKE 'AND' OR operator LIKE 'OR'", name='operator_validator'),
    UniqueConstraint('timestamp', 'type', 'exchange', 'symbol', 'timeUnit', 'operator'),
    Column('source', String(length=128), nullable=False)
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


