from typing import Literal, Optional

import pandas as pd


def fetch_ohlcv(
    symbol: str = "BTC/USDT",
    timeframe: Literal["1m", "5m", "15m", "1h", "4h", "1d"] = "5m",
    limit: int = 200,
    exchange_name: str = "binance",
) -> pd.DataFrame:
    """Placeholder: returns an empty DataFrame for now.
    Later: use ccxt to fetch candles and return columns: ts, open, high, low, close, volume (ts as pandas datetime).
    """
    return pd.DataFrame(columns=["ts", "open", "high", "low", "close", "volume"])
