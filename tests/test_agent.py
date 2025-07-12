import os
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
import numpy as np

# Load .env for test
load_dotenv()

class TestAIBotConnections(unittest.TestCase):

    def test_env_variables(self):
        self.assertIsNotNone(os.getenv("OPENAI_API_KEY"), "Missing OPENAI_API_KEY")
        self.assertIsNotNone(os.getenv("TWELVE_DATA_API_KEY"), "Missing TWELVE_DATA_API_KEY")
        self.assertIsNotNone(os.getenv("STOCK_SYMBOL"), "Missing STOCK_SYMBOL")

    @patch("requests.get")
    def test_twelve_data_connection(self, mock_get):
        # Mock candle data response
        mock_get.return_value.json.return_value = {
            "values": [{
                "datetime": "2024-07-01 09:30:00",
                "open": "100",
                "high": "105",
                "low": "99",
                "close": "104",
                "volume": "15000"
            }]
        }
        from src.ai_trade_signal import fetch_candles
        candles = fetch_candles("AAPL", "1min", 1)
        self.assertEqual(len(candles), 1)
        self.assertIn("close", candles[0])

    @patch("requests.post")
    def test_openai_sentiment_mock(self, mock_post):
        mock_post.return_value.json.return_value = {
            "choices": [{
                "message": {
                    "content": "0.75"
                }
            }]
        }
        from src.ai_trade_signal import get_sentiment
        sentiment = get_sentiment("AAPL is rising")
        self.assertGreater(sentiment, 0.5)

    def test_rsi_calculation(self):
        from src.ai_trade_signal import rsi
        mock_prices = np.linspace(100, 110, 20)
        result = rsi(mock_prices)
        self.assertTrue(0 <= result <= 100)

    def test_macd_calculation(self):
        from src.ai_trade_signal import macd
        mock_prices = np.linspace(100, 110, 50)
        result = macd(mock_prices)
        self.assertIsInstance(result, float)

    def test_vwap_calculation(self):
        from src.ai_trade_signal import vwap_from_candles
        candles = [{
            "high": "105",
            "low": "95",
            "close": "100",
            "volume": "1000"
        }]
        vwap = vwap_from_candles(candles)
        self.assertAlmostEqual(vwap, 100.0, places=1)

    def test_calculate_atr(self):
        from src.ai_trade_signal import calculate_atr
        mock_candles = [
            {'high': '105', 'low': '95', 'close': '100'},
            {'high': '106', 'low': '96', 'close': '102'},
            {'high': '107', 'low': '97', 'close': '101'},
            {'high': '108', 'low': '98', 'close': '103'},
            {'high': '109', 'low': '99', 'close': '102'},
            {'high': '110', 'low': '100', 'close': '104'},
            {'high': '111', 'low': '101', 'close': '105'},
            {'high': '112', 'low': '102', 'close': '106'},
            {'high': '113', 'low': '103', 'close': '107'},
            {'high': '114', 'low': '104', 'close': '108'},
            {'high': '115', 'low': '105', 'close': '109'},
            {'high': '116', 'low': '106', 'close': '110'},
            {'high': '117', 'low': '107', 'close': '111'},
            {'high': '118', 'low': '108', 'close': '112'},
            {'high': '119', 'low': '109', 'close': '113'}
        ]
        atr = calculate_atr(mock_candles, period=14)
        self.assertIsNotNone(atr)
        self.assertGreater(atr, 0)


if __name__ == '__main__':
    unittest.main()
