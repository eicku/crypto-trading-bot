import pandas as pd

from bot import run


SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]
TIMEFRAMES = ["5m", "15m"]


def main():
    rows = []
    for sym in SYMBOLS:
        for tf in TIMEFRAMES:
            final_eq, trades, _ = run(symbol=sym, timeframe=tf)
            rows.append(
                {
                    "symbol": sym,
                    "timeframe": tf,
                    "final_equity": final_eq,
                    "trades": 0 if trades is None else len(trades),
                }
            )
    df = pd.DataFrame(rows)
    df.sort_values(["final_equity"], ascending=False, inplace=True)
    df.to_csv("scan_results.csv", index=False)

    with open("report.md", "w", encoding="utf-8") as f:
        f.write("# Scan report\n\n")
        f.write(df.to_markdown(index=False))


if __name__ == "__main__":
    main()
