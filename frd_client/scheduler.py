from datetime import date
from .instruments.stock import StockHandler
from .instruments.etf import EtfHandler
from .instruments.futures import FuturesHandler
from .instruments.index import IndexHandler
from .instruments.fx import FxHandler
from .instruments.crypto import CryptoHandler

class UpdateScheduler:
    def __init__(self, client, meta):
        self.client = client
        self.meta   = meta
        self.handlers = {
          "stock": StockHandler(client, meta),
          "etf": EtfHandler(client, meta),
          "futures": FuturesHandler(client, meta),
          "index": IndexHandler(client, meta),
          "fx": FxHandler(client, meta),
          "crypto": CryptoHandler(client, meta),
        }

    def run_daily(self):
        for t, h in self.handlers.items():
            if h.needs_update("day"):
                h.download_update(period="day", timeframe="1day", adjustment="adj_splitdiv")

    def run_weekly(self):
        for t, h in self.handlers.items():
            remote = h.last_remote_update(full=False)
            local  = self.meta.get(t, "week")
            if local is None or remote > date.fromisoformat(local):
                h.download_update(period="week", timeframe="1day", adjustment="adj_splitdiv")

    def run_monthly(self):
        for t, h in self.handlers.items():
            remote = h.last_remote_update(full=False)
            local  = self.meta.get(t, "month")
            if local is None or remote > date.fromisoformat(local):
                h.download_update(period="month", timeframe="1day", adjustment="adj_splitdiv")