import os
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "binance")
SYMBOL = os.getenv("SYMBOL", "BTC/USDT")
TIMEFRAME = os.getenv("TIMEFRAME", "5m")

START_USD = float(os.getenv("START_USD", "1000"))
FAST = int(os.getenv("FAST", "20"))
SLOW = int(os.getenv("SLOW", "50"))
LIMIT = int(os.getenv("LIMIT", "500"))

STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "0.0"))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "0.0"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

HYSTERESIS_PCT = float(os.getenv("HYSTERESIS_PCT", "0.0"))
COOLDOWN_BARS = int(os.getenv("COOLDOWN_BARS", "0"))
STRATEGY = os.getenv("STRATEGY", "SMA")  # options: SMA, EMA_RSI
EMA_FAST = int(os.getenv("EMA_FAST", "12"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "26"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_LONG = int(os.getenv("RSI_LONG", "55"))
RSI_EXIT = int(os.getenv("RSI_EXIT", "45"))
