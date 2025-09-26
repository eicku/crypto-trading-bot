import pandas as pd
from data import fetch_ohlcv
from strategy import sma_crossover
from paper_broker import PaperBroker


def main():
    df = fetch_ohlcv("BTC/USDT", "5m", 200, "binance")
    df = sma_crossover(df, fast=20, slow=50)
    broker = PaperBroker(1000.0)
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
    last_price = df["close"].iloc[-1]
    print(f"Final equity: {broker.equity(last_price):.2f} USD")


if __name__ == "__main__":
    main()
