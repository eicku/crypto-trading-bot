import argparse
import pandas as pd
from data import fetch_ohlcv
from strategy import sma_crossover
from paper_broker import PaperBroker

def run(symbol="BTC/USDT", timeframe="5m", limit=500, fast=20, slow=50, start_usd=1000.0, exchange="binance"):
    df = fetch_ohlcv(symbol, timeframe, limit, exchange)
    df = sma_crossover(df, fast, slow)
    broker = PaperBroker(starting_usd=start_usd)

    prev = 0
    equity_points = []
    for _, row in df.iterrows():
        sig = int(row["signal"])
        if pd.isna(row.get("sma_fast")) or pd.isna(row.get("sma_slow")):
            equity_points.append((row["ts"], broker.equity(row["close"])))
            continue
        if sig == 1 and prev <= 0:
            broker.buy_all(row["close"], row["ts"])
        elif sig == -1 and prev >= 0:
            broker.sell_all(row["close"], row["ts"])
        prev = sig
        equity_points.append((row["ts"], broker.equity(row["close"])))

    last_price = float(df["close"].iloc[-1])
    final_equity = broker.equity(last_price)

    trades = pd.DataFrame(broker.trades)
    if not trades.empty:
        trades.to_csv("trades.csv", index=False)

    equity_curve = pd.Series(
        [v for _, v in equity_points],
        index=[t for t, _ in equity_points],
        name="equity"
    )

    print(f"[{symbol} {timeframe}] Final equity: {final_equity:.2f} USD | Trades: {len(broker.trades)}")
    return final_equity, trades if not trades.empty else pd.DataFrame(), equity_curve

def parse_args():
    p = argparse.ArgumentParser(description="Paper-trading SMA bot")
    p.add_argument("--symbol", default="BTC/USDT")
    p.add_argument("--timeframe", default="5m")
    p.add_argument("--limit", type=int, default=500)
    p.add_argument("--fast", type=int, default=20)
    p.add_argument("--slow", type=int, default=50)
    p.add_argument("--start-usd", type=float, default=1000.0)
    p.add_argument("--exchange", default="binance")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run(
        symbol=args.symbol,
        timeframe=args.timeframe,
        limit=args.limit,
        fast=args.fast,
        slow=args.slow,
        start_usd=args.start_usd,
        exchange=args.exchange,
    )
