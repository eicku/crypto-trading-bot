class PaperBroker:
    """Minimal placeholder for a paper-trading broker."""

    def __init__(self, starting_usd: float = 1000.0, fee: float = 0.0005) -> None:
        self.usd = starting_usd
        self.asset = 0.0
        self.fee = fee
        self.trades = []

    def buy_all(self, price: float, ts) -> None:
        """Placeholder: implement later."""
        pass

    def sell_all(self, price: float, ts) -> None:
        """Placeholder: implement later."""
        pass

    def equity(self, price: float) -> float:
        """Placeholder: implement later – should return current equity in USD."""
        return float(self.usd)
