import numpy as np
import pandas as pd
from bot import run

def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min())

def sharpe(equity: pd.Series, rf: float = 0.0) -> float:
    rets = equity.pct_change().dropna()
    if rets.empty or rets.std(ddof=0) == 0:
        return 0.0
    # scale roughly for 5m candles (~12 per hour * 24 * 252 trading days)
    scale = np.sqrt(12*24*252)
    return float(((rets.mean() - rf) / rets.std(ddof=0)) * scale)

def main():
    final_eq, trades, equity_curve = run()
    print("=== Backtest summary ===")
    print(f"Final equity: {final_eq:.2f} USD")
    print(f"Trades: {0 if trades is None else len(trades)}")
    if equity_curve is not None and not equity_curve.empty:
        print(f"Max drawdown: {max_drawdown(equity_curve):.2%}")
        print(f"Sharpe (rough): {sharpe(equity_curve):.2f}")
    else:
        print("No equity curve available.")
    print("Done.")

if __name__ == "__main__":
    main()
