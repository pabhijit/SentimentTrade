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
        from ai_trading_agent_with_vwap import fetch_candles
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
        from ai_trading_agent_with_vwap import get_sentiment
        sentiment = get_sentiment("AAPL is rising")
        self.assertGreater(sentiment, 0.5)

    def test_rsi_calculation(self):
        from ai_trading_agent_with_vwap import rsi
        mock_prices = np.linspace(100, 110, 20)
        result = rsi(mock_prices)
        self.assertTrue(0 <= result <= 100)

    def test_macd_calculation(self):
        from ai_trading_agent_with_vwap import macd
        mock_prices = np.linspace(100, 110, 50)
        result = macd(mock_prices)
        self.assertIsInstance(result, float)

    def test_vwap_calculation(self):
        from ai_trading_agent_with_vwap import vwap_from_candles
        candles = [{
            "high": "105",
            "low": "95",
            "close": "100",
            "volume": "1000"
        }]
        vwap = vwap_from_candles(candles)
        self.assertAlmostEqual(vwap, 100.0, places=1)


if __name__ == '__main__':
    unittest.main()
