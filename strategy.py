import pandas as pd


def sma_crossover(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    out = df.copy()
    out["sma_fast"] = out["close"].rolling(fast).mean()
    out["sma_slow"] = out["close"].rolling(slow).mean()
    out["signal"] = 0
    out.loc[out["sma_fast"] > out["sma_slow"], "signal"] = 1
    out.loc[out["sma_fast"] < out["sma_slow"], "signal"] = -1
    return out
