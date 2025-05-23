from datetime import datetime
from .base import InstrumentHandler

class IndexHandler(InstrumentHandler):
    asset_type = "index"

    def download_full(self, ticker_list: str, timeframe: str, adjustment: str = None):
        """
        Download full index data for given tickers.
        """
        dest = self.client.work_dir / "index" / "full" / ticker_list
        params = {
            "type": "index",
            "period": "full",
            "ticker": ticker_list,
            "timeframe": timeframe,
        }
        if adjustment:
            params["adjustment"] = adjustment
        self.client.fetch_zip(
            endpoint="data_file",
            params=params,
            dest=dest
        )
        self.meta.set_full("index", ticker_list, self.last_remote_update(full=True))

    def download_update(self, period: str, timeframe: str, adjustment: str = None):
        """
        Download incremental index updates for 'day', 'week', or 'month'.
        """
        dest = self.client.work_dir / "index" / period
        params = {
            "type": "index",
            "period": period,
            "timeframe": timeframe,
        }
        if adjustment:
            params["adjustment"] = adjustment
        self.client.fetch_zip(
            endpoint="data_file",
            params=params,
            dest=dest
        )
        self.meta.set_update("index", period, self.last_remote_update(full=False))

    def last_remote_update(self, full=False):
        """
        Query API for last update date for index data.
        """
        params = {"type": "index", "is_full_update": str(full).lower()}
        raw = self.client._get("last_update", params)
        return datetime.strptime(raw.decode(), "%Y-%m-%d").date()