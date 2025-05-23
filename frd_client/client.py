import requests, zipfile, io
from pathlib import Path

class FrdClient:
    BASE = "https://firstratedata.com/api"
    def __init__(self, userid: str, work_dir: Path):
        self.userid = userid
        self.work_dir = work_dir
        work_dir.mkdir(parents=True, exist_ok=True)

    def _get(self, endpoint: str, params: dict) -> bytes:
        params["userid"] = self.userid
        r = requests.get(f"{self.BASE}/{endpoint}", params=params, timeout=60)
        r.raise_for_status()
        return r.content

    def fetch_zip(self, endpoint: str, params: dict, dest: Path):
        raw = self._get(endpoint, params)
        z = zipfile.ZipFile(io.BytesIO(raw))
        dest.mkdir(parents=True, exist_ok=True)
        for member in z.namelist():
            z.extract(member, path=dest)