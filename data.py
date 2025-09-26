import ccxt
import pandas as pd


def fetch_ohlcv(symbol: str = "BTC/USDT", timeframe: str = "5m", limit: int = 500, exchange_name: str = "binance") -> pd.DataFrame:
    ex_class = getattr(ccxt, exchange_name)
    ex = ex_class({"enableRateLimit": True})
    ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["ts","open","high","low","close","volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    return df
