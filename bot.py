import argparse, logging, pandas as pd
from data import fetch_ohlcv
import config as cfg
from paper_broker import PaperBroker

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
        if getattr(cfg, "BROKER", "paper") in ("binance_testnet", "binance_live"):
            from live_broker_binance import BinanceBroker

            use_testnet = (cfg.BROKER == "binance_testnet")
            broker = BinanceBroker(
                api_key=getattr(cfg, "BINANCE_API_KEY", ""),
                api_secret=getattr(cfg, "BINANCE_API_SECRET", ""),
                symbol=symbol,
                fee=0.0005,
                testnet=use_testnet,
            )
            logging.info(f"Using Binance broker (testnet={use_testnet})")
    except Exception as e:
        logging.warning(f"Falling back to PaperBroker: {e}")

    def current_asset_qty() -> float:
        asset_val = getattr(broker, "asset", None)
        if asset_val is not None:
            try:
                return float(asset_val)
            except Exception:
                return 0.0
        free_fn = getattr(broker, "_free", None)
        base_code = getattr(broker, "base", None)
        if callable(free_fn) and base_code:
            try:
                return float(free_fn(base_code))
            except Exception:
                return 0.0
        return 0.0

    def available_cash() -> float:
        getter = getattr(broker, "quote_cash", None)
        try:
            if callable(getter):
                return float(getter())
        except Exception:
            return 0.0
        return float(getattr(broker, "usd", 0.0))

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

        asset_qty = current_asset_qty()

        if asset_qty > 0:
            high_since_entry = max(high_since_entry or price, price)

        if wait > 0:
            wait -= 1
            continue

        # Trailing stop: exit if price falls X% from the highest price since entry
        ts_pct = float(getattr(cfg, "TRAILING_STOP_PCT", 0.0) or 0.0)
        if asset_qty > 0 and high_since_entry and ts_pct > 0:
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
        if asset_qty > 0 and entry_price:
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

        cash = available_cash()
        if sig == 1 and prev <= 0 and cash > 0:
            frac_by_pct = max(0.0, min(1.0, float(getattr(cfg, "MAX_ALLOC_PCT", 0.25))))
            frac_by_usd = 1.0
            if cash > 0 and getattr(cfg, "MAX_TRADE_USD", 0.0) > 0:
                frac_by_usd = float(cfg.MAX_TRADE_USD) / cash
            alloc = max(0.0, min(frac_by_pct, frac_by_usd))
            if alloc > 0:
                broker.buy_fraction(price, row["ts"], alloc)
                entry_price = price
                high_since_entry = price
                logging.info(f"BUY {alloc*100:.1f}% at {price:.2f}")
                prev = 1
                wait = cooldown
        elif sig == -1 and prev >= 0 and asset_qty > 0:
            broker.sell_all(price, row["ts"])
            logging.info(f"SELL at {price:.2f}")
            entry_price = None
            high_since_entry = None
            prev = -1
            wait = cooldown

    last_price = float(df["close"].iloc[-1])
    # optionally close any open position at last bar
    last_ts = df["ts"].iloc[-1]
    if getattr(cfg, "CLOSE_AT_END", False) and current_asset_qty() > 0:
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
