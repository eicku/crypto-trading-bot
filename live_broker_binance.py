import ccxt


class BinanceTestnetBroker:
    """Market-order broker for Binance Spot TESTNET. For safety, testnet only."""

    def __init__(self, api_key: str, api_secret: str, symbol: str, fee: float = 0.0005, testnet: bool = True):
        self.symbol = symbol
        self.fee = float(fee)
        self.trades = []
        self.testnet = bool(testnet)

        self.exchange = ccxt.binance({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        })
        # try sandbox mode, then hard-override URLs as fallback
        if self.testnet:
            try:
                self.exchange.set_sandbox_mode(True)
            except Exception:
                pass
        try:
            self.exchange.urls["api"]["public"] = "https://testnet.binance.vision/api"
            self.exchange.urls["api"]["private"] = "https://testnet.binance.vision/api"
        except Exception:
            pass

        self.exchange.load_markets()
        self.market = self.exchange.market(self.symbol)
        self.base = self.market["base"]  # e.g. ETH for ETH/USDT
        self.quote = self.market["quote"]  # e.g. USDT

    def _free(self, code: str) -> float:
        bal = self.exchange.fetch_balance()
        info = bal.get(code) or {}
        return float(info.get("free", 0.0))

    def _amt_from_usd(self, usd: float, price: float) -> float:
        raw = (usd * (1 - self.fee)) / float(price)
        return float(self.exchange.amount_to_precision(self.symbol, raw))

    @property
    def usd(self) -> float:
        return self._free(self.quote)

    @property
    def asset(self) -> float:
        return self._free(self.base)

    def buy_all(self, price: float, ts) -> None:
        usdt = self._free(self.quote)
        if usdt <= 0:
            return
        amt = self._amt_from_usd(usdt, price)
        if amt <= 0:
            return
        order = self.exchange.create_market_buy_order(self.symbol, amt)
        self.trades.append({"ts": ts, "side": "BUY", "price": float(price), "qty": float(amt), "orderId": order.get("id")})

    def buy_fraction(self, price: float, ts, fraction: float) -> None:
        usdt = self._free(self.quote)
        if usdt <= 0:
            return
        spend = usdt * max(0.0, min(1.0, float(fraction)))
        amt = self._amt_from_usd(spend, price)
        if amt <= 0:
            return
        order = self.exchange.create_market_buy_order(self.symbol, amt)
        self.trades.append({"ts": ts, "side": "BUY", "price": float(price), "qty": float(amt), "orderId": order.get("id")})

    def sell_all(self, price: float, ts) -> None:
        qty = float(self._free(self.base))
        qty = float(self.exchange.amount_to_precision(self.symbol, qty))
        if qty <= 0:
            return
        order = self.exchange.create_market_sell_order(self.symbol, qty)
        self.trades.append({"ts": ts, "side": "SELL", "price": float(price), "qty": float(qty), "orderId": order.get("id")})

    def equity(self, price: float) -> float:
        bal = self.exchange.fetch_balance()
        usd = float((bal.get(self.quote) or {}).get("free", 0.0))
        asset = float((bal.get(self.base) or {}).get("free", 0.0))
        return usd + asset * float(price)
