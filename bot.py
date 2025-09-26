import argparse
import logging
import pandas as pd
from data import fetch_ohlcv
from strategy import sma_crossover
from paper_broker import PaperBroker
import config as cfg

logging.basicConfig(level=getattr(logging, cfg.LOG_LEVEL.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(message)s")

def run(symbol=None, timeframe=None, limit=None, fast=None, slow=None, start_usd=None, exchange=None):
    symbol = symbol or cfg.SYMBOL
    timeframe = timeframe or cfg.TIMEFRAME
    limit = limit or cfg.LIMIT
    fast = fast or cfg.FAST
    slow = slow or cfg.SLOW
    start_usd = start_usd or cfg.START_USD
    exchange = exchange or cfg.EXCHANGE_NAME

    logging.info(f"Start run: {symbol} {timeframe} fast={fast} slow={slow} start_usd={start_usd}")
    df = fetch_ohlcv(symbol, timeframe, limit, exchange)
    df = sma_crossover(df, fast, slow)
    broker = PaperBroker(starting_usd=start_usd)

    prev = 0
    entry_price = None
    for _, row in df.iterrows():
        sig = int(row["signal"])
        price = float(row["close"])
        if pd.isna(row.get("sma_fast")) or pd.isna(row.get("sma_slow")):
            continue

        if broker.asset > 0 and entry_price:
            if cfg.STOP_LOSS_PCT > 0 and price <= entry_price * (1 - cfg.STOP_LOSS_PCT):
                broker.sell_all(price, row["ts"])
                logging.info(f"STOP LOSS at {price:.2f}")
                prev = -1
                entry_price = None
                continue
            if cfg.TAKE_PROFIT_PCT > 0 and price >= entry_price * (1 + cfg.TAKE_PROFIT_PCT):
                broker.sell_all(price, row["ts"])
                logging.info(f"TAKE PROFIT at {price:.2f}")
                prev = -1
                entry_price = None
                continue

        if sig == 1 and prev <= 0 and broker.usd > 0:
            alloc = 0.5  # use 50% of available cash per entry
            broker.buy_fraction(price, row["ts"], alloc)
            entry_price = price
            logging.info(f"BUY {alloc*100:.0f}% at {price:.2f}")
        elif sig == -1 and prev >= 0 and broker.asset > 0:
            broker.sell_all(price, row["ts"])
            logging.info(f"SELL at {price:.2f}")
            entry_price = None
        prev = sig

    last_price = float(df["close"].iloc[-1])
    final_equity = broker.equity(last_price)
    trades = pd.DataFrame(broker.trades)
    if not trades.empty:
        trades.to_csv("trades.csv", index=False)
    logging.info(f"Final equity: {final_equity:.2f} USD | Trades: {len(broker.trades)}")
    return final_equity, trades, None

def parse_args():
    p = argparse.ArgumentParser(description="Paper-trading SMA bot with .env defaults")
    p.add_argument("--symbol")
    p.add_argument("--timeframe")
    p.add_argument("--limit", type=int)
    p.add_argument("--fast", type=int)
    p.add_argument("--slow", type=int)
    p.add_argument("--start-usd", type=float)
    p.add_argument("--exchange")
    return p.parse_args()

if __name__ == "__main__":
    a = parse_args()
    run(a.symbol, a.timeframe, a.limit, a.fast, a.slow, a.start_usd, a.exchange)
