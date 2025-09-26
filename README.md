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
