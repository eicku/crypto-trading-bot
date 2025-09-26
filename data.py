from typing import Literal, Optional

import ccxt
import pandas as pd


def fetch_ohlcv(
    symbol: str = "BTC/USDT",
    timeframe: Literal["1m", "5m", "15m", "1h", "4h", "1d"] = "5m",
    limit: Optional[int] = 200,
    exchange_name: str = "binance",
) -> pd.DataFrame:
    """Fetch OHLCV data for *symbol* from the requested exchange using ccxt."""

    exchange_id = exchange_name.lower()
    if not hasattr(ccxt, exchange_id):
        raise ValueError(f"Unknown exchange: {exchange_name}")

    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()

    try:
        fetch_kwargs = {"timeframe": timeframe}
        if limit is not None:
            fetch_kwargs["limit"] = limit

        candles = exchange.fetch_ohlcv(symbol, **fetch_kwargs)
    finally:
        # ensure we release any open connections/resources held by the exchange
        exchange.close()

    columns = ["ts", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(candles, columns=columns)
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    else:
        df = pd.DataFrame(columns=columns)
    return df
