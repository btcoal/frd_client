# tests/test_client.py
"""
test_client.py – mocks HTTP to test ZIP fetch/unpack
"""
import io, zipfile
import pytest
from pathlib import Path
from frd_client.client import FrdClient

class DummyResponse:
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP error")

@pytest.fixture(autouse=True)
def patch_requests(monkeypatch):
    def fake_get(url, params, timeout):
        # Return a zip with one file
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            z.writestr('test.csv', 'a,b\n1,2')
        return DummyResponse(buf.getvalue())
    monkeypatch.setattr('frd_client.client.requests.get', fake_get)

def test_fetch_zip(tmp_path):
    client = FrdClient('id', tmp_path)
    dest = tmp_path / 'out'
    client.fetch_zip('endpoint', {'foo':'bar'}, dest)
    files = list(dest.rglob('test.csv'))
    assert len(files) == 1