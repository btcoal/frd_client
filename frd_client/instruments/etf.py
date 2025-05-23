# etf.py
from datetime import datetime
from .base import InstrumentHandler

class EtfHandler(InstrumentHandler):
    asset_type = "etf"

    def download_full(self, ticker_list: str, timeframe: str, adjustment: str):
        dest = self.client.work_dir / "etf" / "full" / ticker_list
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"etf","period":"full","ticker":ticker_list,
                    "timeframe":timeframe,"adjustment":adjustment},
            dest=dest
        )
        meta_dest = dest / "meta"
        self.client.fetch_zip(
            endpoint="meta_file",
            params={"type":"etf","period":"full","ticker":ticker_list},
            dest=meta_dest
        )
        self.meta.set_full("etf", ticker_list, self.last_remote_update(full=True))

    def download_update(self, period: str, timeframe: str, adjustment: str):
        dest = self.client.work_dir / "etf" / period
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"etf","period":period,
                    "timeframe":timeframe,"adjustment":adjustment},
            dest=dest
        )
        meta_dest = dest / "meta"
        self.client.fetch_zip(
            endpoint="meta_file",
            params={"type":"etf","period":period},
            dest=meta_dest
        )
        self.meta.set_update("etf", period, self.last_remote_update(full=False))

    def last_remote_update(self, full=False):
        params={"type":"etf","is_full_update":str(full).lower()}
        raw = self.client._get("last_update", params)
        return datetime.strptime(raw.decode(), "%Y-%m-%d").date()