import unittest
from app.models import SignalCreate, IndicatorsCreate

txt = """🔔 BTC Long 💱 Binance Futures:BTCUSDT ⏱️ 5 Minutes

AND
|  AI BGMCv1/Signal <None> became TRUE ✔️
|  Volume Osc(5,10) <> is less than <> ❌"""

expected_header = {'name': 'BTC Long',
                   'operator': 'AND',
                   'symbol': 'Binance Futures:BTCUSDT',
                   'timeUnit': '5 Minutes'}

expected_indicators = [{'name': 'AI BGMCv1/Signal <None> became TRUE', 'valid': True},
                       {'name': 'Volume Osc(5,10) <> is less than <>', 'valid': False}]


class MessageTests(unittest.TestCase):

    def test_parse_message(self):
        header, indicators = IndicatorsCreate(txt)
        self.assertEqual(header, expected_header)
        self.assertEqual(indicators, expected_indicators)
