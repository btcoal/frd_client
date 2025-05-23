# tests/test_scheduler.py
"""
test_scheduler.py – ensures only handlers needing update are invoked
"""
import pytest
from datetime import date
from frd_client.scheduler import UpdateScheduler

class DummyHandler:
    def __init__(self, asset_type, needs):
        self.asset_type = asset_type
        self._needs = needs
        self.downloaded = []
    def needs_update(self, p): return self._needs
    def download_update(self, period, **kw): self.downloaded.append(period)
    def last_remote_update(self, full=False): return date.today()

@pytest.fixture
def sched(monkeypatch):
    class DummyClient: pass
    meta = type('M',(),{'get':lambda self, a, p: None})()
    sched = UpdateScheduler(DummyClient(), meta)
    sched.handlers = {
        'foo': DummyHandler('foo', True),
        'bar': DummyHandler('bar', False),
    }
    return sched

def test_run_daily(sched):
    sched.run_daily()
    assert 'day' in sched.handlers['foo'].downloaded
    assert sched.handlers['bar'].downloaded == []