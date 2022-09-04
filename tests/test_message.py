import unittest
from textwrap import dedent

from app.models import SignalCreate, IndicatorsCreate


class MessageTests(unittest.TestCase):

    def test_parse_message(self):
        txt = dedent("""
        🔔 BTC Long 💱 Binance Futures:BTCUSDT ⏱️ 5 Minutes

        OR
        |  AI BGMCv1/Signal <None> became TRUE ✔️
        |  Volume Osc(5,10) <> is less than <> ❌""").lstrip()

        indicators_create = IndicatorsCreate.parse_obj({'message': txt, 'signal_id': 0})
        indicators_insert = indicators_create.dict().get('__root__')
        self.assertEqual(indicators_insert[0], {'name': 'BTC Long', 'symbol': 'Binance Futures:BTCUSDT', 'timeUnit': '5 Minutes', 'operator': 'OR'})
        self.assertEqual(indicators_insert[1], [
            {'name': 'AI BGMCv1/Signal <None> became TRUE', 'valid': True, 'signal_id': 0},
            {'name': 'Volume Osc(5,10) <> is less than <>', 'valid': False, 'signal_id': 0}
        ])
