# tests/test_handlers.py
"""
test_handlers.py – checks `needs_update`, `download_full/update` calls for `StockHandler`
"""
import pytest
from datetime import date
from frd_client.instruments.base import InstrumentHandler
from frd_client.instruments.stock import StockHandler

class DummyClient:
    def __init__(self): self.called = []
    def fetch_zip(self, endpoint, params, dest): self.called.append((endpoint, params))
    def _get(self, endpoint, params): return b'2025-05-22'

class DummyMeta:
    def __init__(self): self.store = {}
    def get(self, asset_type, period): return self.store.get((asset_type, period))
    def set_update(self, asset_type, period, d): self.store[(asset_type, period)] = d.isoformat()
    def set_full(self, asset_type, key, d): self.store[(asset_type, key)] = d.isoformat()

@pytest.fixture
def stock_handler():
    return StockHandler(DummyClient(), DummyMeta())

def test_needs_update_true_when_missing(stock_handler):
    assert stock_handler.needs_update('day')

def test_download_full_calls_fetch_and_meta(stock_handler):
    stock_handler.download_full('A', '1day', 'adj')
    assert stock_handler.client.called[0][0] == 'data_file'
    assert ('stock', 'full_A') in stock_handler.meta.store

def test_download_update_calls_fetch_and_meta(stock_handler):
    stock_handler.download_update('day', '1day', 'adj')
    assert stock_handler.client.called[0][0] == 'data_file'
    assert ('stock', 'day') in stock_handler.meta.store
