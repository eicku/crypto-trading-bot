import argparse, logging, pandas as pd
from data import fetch_ohlcv
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
    if getattr(cfg, "STRATEGY", "SMA").upper() == "EMA_RSI":
        from strategy import ema_rsi

        df = ema_rsi(
            df,
            fast=getattr(cfg, "EMA_FAST", 12),
            slow=getattr(cfg, "EMA_SLOW", 26),
            rsi_period=getattr(cfg, "RSI_PERIOD", 14),
            rsi_long=getattr(cfg, "RSI_LONG", 55),
            rsi_exit=getattr(cfg, "RSI_EXIT", 45),
        )
    else:
        from strategy import sma_crossover

        df = sma_crossover(
            df, fast, slow, hysteresis_pct=getattr(cfg, "HYSTERESIS_PCT", 0.0)
        )
    broker = PaperBroker(starting_usd=start_usd)
    try:
        if getattr(cfg, "BROKER", "paper").lower() == "binance_testnet":
            from live_broker_binance import BinanceTestnetBroker

            broker = BinanceTestnetBroker(
                api_key=getattr(cfg, "BINANCE_API_KEY", ""),
                api_secret=getattr(cfg, "BINANCE_API_SECRET", ""),
                symbol=symbol,
                fee=0.0005,
                testnet=True,
            )
            logging.info("Using BINANCE SPOT TESTNET broker")
    except Exception as e:
        logging.warning(f"Falling back to PaperBroker: {e}")

    prev = 0
    entry_price = None
    high_since_entry = None
    cooldown = int(getattr(cfg, "COOLDOWN_BARS", 0))

    wait = 0
    for _, row in df.iterrows():
        if pd.isna(row.get("sma_fast")) or pd.isna(row.get("sma_slow")):
            continue

        price = float(row["close"])
        sig = int(row["signal"])

        if broker.asset > 0:
            high_since_entry = max(high_since_entry or price, price)

        if wait > 0:
            wait -= 1
            continue

        # Trailing stop: exit if price falls X% from the highest price since entry
        ts_pct = float(getattr(cfg, "TRAILING_STOP_PCT", 0.0) or 0.0)
        if broker.asset > 0 and high_since_entry and ts_pct > 0:
            if price <= high_since_entry * (1 - ts_pct):
                broker.sell_all(price, row["ts"])
                logging.info(
                    f"TRAIL STOP at {price:.2f} (peak {high_since_entry:.2f}, drop {ts_pct*100:.2f}%)"
                )
                prev = -1
                entry_price = None
                high_since_entry = None
                wait = cooldown
                continue

        # optional SL/TP
        if broker.asset > 0 and entry_price:
            if cfg.STOP_LOSS_PCT > 0 and price <= entry_price * (1 - cfg.STOP_LOSS_PCT):
                broker.sell_all(price, row["ts"])
                logging.info(f"STOP LOSS at {price:.2f}")
                prev = -1
                entry_price = None
                high_since_entry = None
                wait = cooldown
                continue
            if cfg.TAKE_PROFIT_PCT > 0 and price >= entry_price * (1 + cfg.TAKE_PROFIT_PCT):
                broker.sell_all(price, row["ts"])
                logging.info(f"TAKE PROFIT at {price:.2f}")
                prev = -1
                entry_price = None
                high_since_entry = None
                wait = cooldown
                continue

        if sig == 1 and prev <= 0 and broker.usd > 0:
            broker.buy_all(price, row["ts"])
            entry_price = price
            high_since_entry = price
            logging.info(f"BUY at {price:.2f}")
            prev = 1
            wait = cooldown
        elif sig == -1 and prev >= 0 and broker.asset > 0:
            broker.sell_all(price, row["ts"])
            logging.info(f"SELL at {price:.2f}")
            entry_price = None
            high_since_entry = None
            prev = -1
            wait = cooldown

    last_price = float(df["close"].iloc[-1])
    # optionally close any open position at last bar
    last_ts = df["ts"].iloc[-1]
    if getattr(cfg, "CLOSE_AT_END", False) and broker.asset > 0:
        broker.sell_all(last_price, last_ts)
        logging.info(f"EOD CLOSE at {last_price:.2f}")

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
