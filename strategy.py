import pandas as pd


def sma_crossover(df: pd.DataFrame, fast: int = 20, slow: int = 50, hysteresis_pct: float = 0.0) -> pd.DataFrame:
    out = df.copy()
    out["sma_fast"] = out["close"].rolling(fast).mean()
    out["sma_slow"] = out["close"].rolling(slow).mean()
    out["signal"] = 0
    if hysteresis_pct and hysteresis_pct > 0:
        up = out["sma_fast"] > out["sma_slow"] * (1 + hysteresis_pct)
        dn = out["sma_fast"] < out["sma_slow"] * (1 - hysteresis_pct)
    else:
        up = out["sma_fast"] > out["sma_slow"]
        dn = out["sma_fast"] < out["sma_slow"]
    out.loc[up, "signal"] = 1
    out.loc[dn, "signal"] = -1
    return out
