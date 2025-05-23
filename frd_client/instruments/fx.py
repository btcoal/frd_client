# fx.py
from datetime import datetime
from .base import InstrumentHandler

class FxHandler(InstrumentHandler):
    asset_type = "fx"

    def download_full(self, pair_list: str, timeframe: str):
        dest = self.client.work_dir / "fx" / "full" / pair_list
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"fx","period":"full","pairs":pair_list,
                    "timeframe":timeframe},
            dest=dest
        )
        self.meta.set_full("fx", pair_list, self.last_remote_update(full=True))

    def download_update(self, period: str, timeframe: str):
        dest = self.client.work_dir / "fx" / period
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"fx","period":period,"timeframe":timeframe},
            dest=dest
        )
        self.meta.set_update("fx", period, self.last_remote_update(full=False))

    def last_remote_update(self, full=False):
        params={"type":"fx","is_full_update":str(full).lower()}
        raw=self.client._get("last_update", params)
        return datetime.strptime(raw.decode(), "%Y-%m-%d").date()
