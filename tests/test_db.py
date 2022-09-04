import unittest
from unittest import IsolatedAsyncioTestCase

from sqlalchemy.engine import Inspector
from sqlalchemy import inspect
from app.database import get_database, sqlalchemy_engine
from app.models import metadata, signals, indicators


class DatabaseTests(IsolatedAsyncioTestCase):

    async def test_create_all(self):
        await get_database().connect()
        metadata.create_all(sqlalchemy_engine)
        self.assertTrue(inspect(sqlalchemy_engine).has_table('signals'))
        self.assertTrue(inspect(sqlalchemy_engine).has_table('messages'))
