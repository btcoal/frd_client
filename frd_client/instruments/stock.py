from datetime import datetime
from .base import InstrumentHandler

class StockHandler(InstrumentHandler):
    asset_type = "stock"

    def download_full(self, ticker_range: str, timeframe: str, adjustment: str):
        dest = self.client.work_dir / "stock" / "full" / ticker_range
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"stock","period":"full","ticker_range":ticker_range,
                    "timeframe":timeframe,"adjustment":adjustment},
            dest=dest
        )
        self.meta.set_full("stock", ticker_range, self.last_remote_update(full=True))

    def download_update(self, period: str, timeframe: str, adjustment: str):
        dest = self.client.work_dir / "stock" / period
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"stock","period":period,
                    "timeframe":timeframe,"adjustment":adjustment},
            dest=dest
        )
        self.meta.set_update("stock", period, self.last_remote_update(full=False))

    def last_remote_update(self, full=False):
        params={"type":"stock","is_full_update":str(full).lower()}
        raw = self.client._get("last_update", params)
        return datetime.strptime(raw.decode(), "%Y-%m-%d").date()