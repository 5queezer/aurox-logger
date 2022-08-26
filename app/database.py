import os

from databases import Database
from sqlalchemy import create_engine

assert os.getenv('DATABASE_URL')

database = Database(os.getenv('DATABASE_URL'))
sqlalchemy_engine = create_engine(os.getenv('DATABASE_URL'))


def get_database() -> Database:
    return database
