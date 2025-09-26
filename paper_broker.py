from __future__ import annotations


class PaperBroker:
    """Simple paper-trading broker with flat fee per trade."""

    def __init__(self, starting_usd: float = 1000.0, fee: float = 0.0005) -> None:
        self.usd = float(starting_usd)
        self.asset = 0.0
        self.fee = float(fee)
        self.trades = []  # list of dicts: ts, side, price, qty

    def buy_all(self, price: float, ts) -> None:
        if self.usd <= 0 or price <= 0:
            return
        qty = (self.usd * (1 - self.fee)) / price
        self.asset += qty
        self.trades.append({"ts": ts, "side": "BUY", "price": float(price), "qty": float(qty)})
        self.usd = 0.0

    def buy_fraction(self, price: float, ts, fraction: float) -> None:
        if self.usd <= 0 or price <= 0 or fraction <= 0:
            return
        frac = min(max(fraction, 0.0), 1.0)
        spend = self.usd * frac
        qty = (spend * (1 - self.fee)) / price
        self.asset += qty
        self.trades.append({"ts": ts, "side": "BUY", "price": float(price), "qty": float(qty)})
        self.usd -= spend

    def sell_all(self, price: float, ts) -> None:
        if self.asset <= 0 or price <= 0:
            return
        proceeds = self.asset * price * (1 - self.fee)
        self.trades.append({"ts": ts, "side": "SELL", "price": float(price), "qty": float(self.asset)})
        self.usd += proceeds
        self.asset = 0.0

    def equity(self, price: float) -> float:
        return float(self.usd + self.asset * price)
