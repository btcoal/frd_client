# futures.py
from datetime import datetime
from .base import InstrumentHandler

class FuturesHandler(InstrumentHandler):
    asset_type = "futures"

    def download_full(self, contract_month: str, timeframe: str, adjustment: str=None):
        # full list of active contracts
        dest = self.client.work_dir / "futures" / "full" / contract_month
        # special endpoint for contract specs
        self.client.fetch_zip(
            endpoint="futures_contract",
            params={"type":"futures","period":"full","month":contract_month},
            dest=dest
        )
        # then fetch historical data
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"futures","period":"full","month":contract_month,
                    "timeframe":timeframe,"adjustment":adjustment},
            dest=dest
        )
        self.meta.set_full("futures", contract_month, self.last_remote_update(full=True))

    def download_update(self, period: str, timeframe: str, adjustment: str=None):
        dest = self.client.work_dir / "futures" / period
        self.client.fetch_zip(
            endpoint="data_file",
            params={"type":"futures","period":period,"timeframe":timeframe,
                    "adjustment":adjustment},
            dest=dest
        )
        self.meta.set_update("futures", period, self.last_remote_update(full=False))

    def last_remote_update(self, full=False):
        params={"type":"futures","is_full_update":str(full).lower()}
        raw=self.client._get("last_update", params)
        return datetime.strptime(raw.decode(), "%Y-%m-%d").date()