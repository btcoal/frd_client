# tests/test_metadata.py
"""
test_metadata.py – verifies empty/round-trip/upsert behavior
"""
import sqlite3
import pytest
from frd_client.metadata import MetadataStore
from datetime import date

def test_get_empty(tmp_path):
    db = tmp_path / "meta.db"
    store = MetadataStore(db)
    assert store.get("stock", "day") is None

@pytest.mark.parametrize("initial,update", [("2025-01-01","2025-02-01"), ("2024-12-31","2025-01-15")])
def test_set_and_get_update(tmp_path, initial, update):
    db = tmp_path / "meta.db"
    store = MetadataStore(db)
    d1 = date.fromisoformat(initial)
    d2 = date.fromisoformat(update)
    store.set_update("stock", "day", d1)
    assert store.get("stock", "day") == initial
    store.set_update("stock", "day", d2)
    assert store.get("stock", "day") == update