# crypto.py
from datetime import datetime
from .base import InstrumentHandler

class CryptoHandler(InstrumentHandler):
    asset_type = "crypto"

    def download_full(self, symbol_list: str, timeframe: str):
        dest = self.client.work_dir / "crypto" / "full" / symbol_list
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"crypto","period":"full","symbols":symbol_list,
                    "timeframe":timeframe},
            dest=dest
        )
        self.meta.set_full("crypto", symbol_list, self.last_remote_update(full=True))

    def download_update(self, period: str, timeframe: str):
        dest = self.client.work_dir / "crypto" / period
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"crypto","period":period,"timeframe":timeframe},
            dest=dest
        )
        self.meta.set_update("crypto", period, self.last_remote_update(full=False))

    def last_remote_update(self, full=False):
        params={"type":"crypto","is_full_update":str(full).lower()}
        raw=self.client._get("last_update", params)
        return datetime.strptime(raw.decode(), "%Y-%m-%d").date()