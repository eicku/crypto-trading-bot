class PaperBroker:
    """Minimal placeholder for a paper-trading broker."""

    def __init__(self, starting_usd: float = 1000.0, fee: float = 0.0005) -> None:
        self.usd = starting_usd
        self.asset = 0.0
        self.fee = fee
        self.trades = []

    def buy_all(self, price: float, ts) -> None:
        """Use all USD balance to purchase the asset at *price*, accounting for fees."""

        if price <= 0 or self.usd <= 0:
            return

        usd_spent = self.usd
        gross_asset = usd_spent / price
        fee_asset = gross_asset * self.fee
        asset_bought = gross_asset - fee_asset

        self.asset += asset_bought
        self.usd = 0.0
        self.trades.append(
            {
                "type": "buy",
                "ts": ts,
                "price": price,
                "usd_spent": usd_spent,
                "asset_acquired": asset_bought,
                "fee": fee_asset,
            }
        )

    def sell_all(self, price: float, ts) -> None:
        """Sell the entire asset balance for USD at *price*, accounting for fees."""

        if price <= 0 or self.asset <= 0:
            return

        asset_sold = self.asset
        gross_usd = asset_sold * price
        fee_usd = gross_usd * self.fee
        usd_received = gross_usd - fee_usd

        self.asset = 0.0
        self.usd += usd_received
        self.trades.append(
            {
                "type": "sell",
                "ts": ts,
                "price": price,
                "asset_sold": asset_sold,
                "usd_received": usd_received,
                "fee": fee_usd,
            }
        )

    def equity(self, price: float) -> float:
        """Return the total equity in USD using the provided *price* for the asset."""

        return float(self.usd + self.asset * price)
