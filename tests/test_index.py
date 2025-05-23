# tests/test_index.py
import pytest
import pandas as pd
from pathlib import Path
from frd_client.index import load_dataframe
from frd_client.client import FrdClient
from frd_client.metadata import MetadataStore
from frd_client.scheduler import UpdateScheduler

@pytest.fixture
def setup_data(tmp_path, monkeypatch):
    # prepare dummy files
    base = tmp_path / 'crypto' / 'day'
    base.mkdir(parents=True)
    df = pd.DataFrame({'x':[1,2]})
    df.to_csv(base / 'a.csv', index=False)
    # stub scheduler and handler
    monkeypatch.setattr(UpdateScheduler, '__init__', lambda s,c,m: None)
    monkeypatch.setattr(UpdateScheduler, 'handlers', {'crypto': type('H',(),{ 'needs_update':lambda s,p: False})()})
    client = FrdClient('id', tmp_path)
    meta = MetadataStore(tmp_path / 'meta.db')
    return client, meta

def test_load_dataframe(setup_data):
    client, meta = setup_data
    df = load_dataframe(client, meta, 'crypto', 'day', '1day')
    assert isinstance(df, pd.DataFrame)
    assert df['x'].tolist() == [1,2]
