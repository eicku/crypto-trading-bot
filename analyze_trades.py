import pandas as pd


def analyze(path: str = "trades.csv"):
    try:
        df = pd.read_csv(path, parse_dates=["ts"])
    except FileNotFoundError:
        print("trades.csv not found")
        return
    if df.empty:
        print("No trades")
        return

    # pair BUY -> SELL in order
    open_stack = []
    rows = []
    for r in df.itertuples(index=False):
        if r.side.upper() == "BUY":
            open_stack.append(r)
        elif r.side.upper() == "SELL" and open_stack:
            b = open_stack.pop(0)
            pnl = (float(r.price) - float(b.price)) * float(b.qty)
            rows.append(
                {
                    "entry_ts": b.ts,
                    "exit_ts": r.ts,
                    "qty": float(b.qty),
                    "entry_price": float(b.price),
                    "exit_price": float(r.price),
                    "pnl_usd": float(pnl),
                }
            )

    rep = pd.DataFrame(rows)
    if rep.empty:
        print("No closed trades")
        return

    rep.to_csv("trades_report.csv", index=False)
    rep.to_csv("trades_report_semicolon.csv", index=False, sep=";")

    wins = int((rep["pnl_usd"] > 0).sum())
    total = len(rep)
    print(rep.tail(5))
    print(
        f"Trades: {total} | Wins: {wins} ({wins/total:.0%}) | "
        f"Total PnL: {rep['pnl_usd'].sum():.2f} USD | Avg: {rep['pnl_usd'].mean():.2f} USD"
    )


if __name__ == "__main__":
    analyze()
