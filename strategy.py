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


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1/period, adjust=False).mean()
    roll_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = roll_up / (roll_down.replace(0, 1e-12))
    return 100 - (100 / (1 + rs))


def ema_rsi(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    rsi_period: int = 14,
    rsi_long: int = 55,
    rsi_exit: int = 45,
) -> pd.DataFrame:
    out = df.copy()
    out["ema_fast"] = out["close"].ewm(span=fast, adjust=False).mean()
    out["ema_slow"] = out["close"].ewm(span=slow, adjust=False).mean()
    out["rsi"] = rsi(out["close"], rsi_period)
    out["signal"] = 0
    long_cond = (out["ema_fast"] > out["ema_slow"]) & (out["rsi"] >= rsi_long)
    exit_cond = (out["ema_fast"] < out["ema_slow"]) | (out["rsi"] <= rsi_exit)
    out.loc[long_cond, "signal"] = 1
    out.loc[exit_cond, "signal"] = -1
    return out
