from __future__ import annotations

import argparse
import importlib

import pandas as pd

import config as cfg

# less logs
cfg.LOG_LEVEL = "ERROR"

# we will mutate cfg.* before each run()
bot_mod = importlib.import_module("bot")


def run_one(
    symbol: str,
    timeframe: str,
    limit: int,
    start_usd: float,
    ema_fast: int,
    ema_slow: int,
    rsi_long: int,
    rsi_exit: int,
) -> tuple[float, int]:
    cfg.STRATEGY = "EMA_RSI"
    cfg.EMA_FAST = int(ema_fast)
    cfg.EMA_SLOW = int(ema_slow)
    cfg.RSI_LONG = int(rsi_long)
    cfg.RSI_EXIT = int(rsi_exit)
    final, trades, _ = bot_mod.run(
        symbol=symbol, timeframe=timeframe, limit=limit, start_usd=start_usd
    )
    return float(final), 0 if trades is None else int(len(trades))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="ETH/USDT")
    parser.add_argument("--timeframe", default="5m")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--start-usd", type=float, default=1000)
    parser.add_argument("--fast", nargs="+", type=int, default=[10, 12, 15, 20])
    parser.add_argument("--slow", nargs="+", type=int, default=[26, 30, 35, 50])
    parser.add_argument("--rsi-long", nargs="+", type=int, default=[55, 60, 65])
    parser.add_argument("--rsi-exit", nargs="+", type=int, default=[40, 45, 50])
    args = parser.parse_args()

    rows = []
    for f in args.fast:
        for s in args.slow:
            if f >= s:
                continue
            for rl in args.rsi_long:
                for rx in args.rsi_exit:
                    final, trade_count = run_one(
                        args.symbol,
                        args.timeframe,
                        args.limit,
                        args.start_usd,
                        f,
                        s,
                        rl,
                        rx,
                    )
                    rows.append(
                        {
                            "ema_fast": f,
                            "ema_slow": s,
                            "rsi_long": rl,
                            "rsi_exit": rx,
                            "final_equity": final,
                            "trades": trade_count,
                        }
                    )

    df = pd.DataFrame(rows).sort_values("final_equity", ascending=False)
    df.to_csv("tune_results.csv", index=False)
    with open("tune_best.md", "w", encoding="utf-8") as fh:
        fh.write("# Best params\n\n")
        fh.write(df.head(10).to_markdown(index=False))
    print(df.head(10))


if __name__ == "__main__":
    main()
