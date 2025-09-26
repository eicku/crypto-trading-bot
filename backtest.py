import numpy as np
import pandas as pd

from bot import run


def max_drawdown(equity_curve: pd.Series) -> float:
    peak = equity_curve.cummax()
    dd = (equity_curve - peak) / peak
    return float(dd.min())


def sharpe(returns: pd.Series, rf: float = 0.0) -> float:
    if returns.std(ddof=0) == 0:
        return 0.0
    return float((returns.mean() - rf) / returns.std(ddof=0) * np.sqrt(252 * 24 * 12))  # rough scale for 5m


def main():
    equity, trades = run()
    print("=== Backtest summary ===")
    if trades is not None and not trades.empty:
        # Build a rough equity curve from trades assuming last price marks-to-market
        cash = []
        bal = 1000.0
        for _ in trades.itertuples(index=False):
            # Not precise; for quick sanity only
            pass
        # Minimal outputs for now:
        print(f"Trades: {len(trades)}")
    else:
        print("No trades executed.")
    print("Done.")


if __name__ == "__main__":
    main()
