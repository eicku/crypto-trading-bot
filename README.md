# Crypto Trading Bot Scaffold

This repository provides a minimal scaffold for building a crypto paper-trading bot, giving you starting points for data fetching, strategy experimentation, and a paper broker loop.

## Getting started

1. `python -m venv .venv`
2. Windows: `.venv\Scripts\activate`
3. macOS/Linux: `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. Rename `.env.example` to `.env` and fill in your keys (you can keep them empty for now).

## Run
Create a Python venv, install deps, then run:
- Windows:
  - `python -m venv .venv` then `.venv\Scripts\activate`
- macOS/Linux:
  - `python -m venv .venv` then `source .venv/bin/activate`

Install:
`pip install -r requirements.txt`

Run:
`python bot.py`

Trades (if any) will be saved to `trades.csv`.

## CLI
Run with custom params:
`python bot.py --symbol ETH/USDT --timeframe 15m --fast 10 --slow 30 --start-usd 1500`

Backtest summary:
`python backtest.py`

## Multi-scan
Run a multi-symbol scan and generate `scan_results.csv` + `report.md`:
`python scan.py`

## Config via .env
Copy `.env.example` to `.env` and adjust values. CLI args override .env defaults.

## Noise filters
- `HYSTERESIS_PCT` (e.g., 0.001 = 0.1%) avoids rapid flip-flops.
- `COOLDOWN_BARS` waits N candles after each trade.

## Strategy switch
- `STRATEGY=SMA` (default) uses SMA crossover (+ optional hysteresis/cooldown).
- `STRATEGY=EMA_RSI` uses EMA(12/26) trend + RSI filter (enter when RSI ≥ RSI_LONG, exit when RSI ≤ RSI_EXIT or trend flips).

vbnet
Kopírovať kód
## Trailing stop
Set `TRAILING_STOP_PCT` (e.g., 0.02 = 2%). While in a position the bot tracks the highest price since entry and exits when price drops by that percentage from the peak.
