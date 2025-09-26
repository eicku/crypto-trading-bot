import pandas as pd

from data import fetch_ohlcv
from strategy import sma_crossover
from paper_broker import PaperBroker


def run(symbol="BTC/USDT", timeframe="5m", limit=500, fast=20, slow=50, start_usd=1000.0):
    df = fetch_ohlcv(symbol, timeframe, limit, "binance")
    df = sma_crossover(df, fast, slow)
    broker = PaperBroker(starting_usd=start_usd)

    prev = 0
    for _, row in df.iterrows():
        sig = int(row["signal"])
        if pd.isna(row["sma_fast"]) or pd.isna(row["sma_slow"]):
            continue
        if sig == 1 and prev <= 0:
            broker.buy_all(row["close"], row["ts"])
        elif sig == -1 and prev >= 0:
            broker.sell_all(row["close"], row["ts"])
        prev = sig

    # Close open position at last price
    last_price = float(df["close"].iloc[-1])
    equity = broker.equity(last_price)

    # Save trades
    trades = pd.DataFrame(broker.trades)
    if not trades.empty:
        trades.to_csv("trades.csv", index=False)

    print(f"Final equity: {equity:.2f} USD | Trades: {len(broker.trades)}")
    return equity, trades if not trades.empty else pd.DataFrame()


if __name__ == "__main__":
    run()
