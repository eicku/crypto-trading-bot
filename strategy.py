import pandas as pd


def sma_crossover(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    """Placeholder: later compute SMA fast/slow and produce a `signal` column in {-1,0,1}."""
    out = df.copy()
    out["signal"] = 0
    return out
