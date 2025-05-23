# frd_client

A Python client library for the FirstRate Data API, providing unified download, incremental updates, and handlers for multiple asset types.

## Overview

`frd_client` is architected as a **layered**, **modular**, and **easily extensible** toolkit for programmatic access and continuous ingestion of financial time-series data from the FirstRate Data API. Below is a deep dive into its core components and the decisions behind them:

### 1. FrdClient: HTTP & I/O Layer

- **Responsibilities**: Authentication, request orchestration, retry logic, ZIP extraction, and filesystem management.
- **Design**: A single class (`FrdClient`) encapsulates all low-level concerns:
  - `_get()`: Centralizes header/parameter injection (`userid`), status checking, and byte-stream retrieval.
  - `fetch_zip()`: Transparently downloads ZIP archives, unpacks CSV members, and ensures directory creation.
- **Rationale**: By isolating HTTP and file I/O here, tests can stub or mock this boundary. Higher layers remain agnostic of networking or compression details.

### 2. MetadataStore: Persistence Layer for Update State

- **Responsibilities**: Track and persist the last-successful download date for each `(asset_type, period)` tuple.
- **Design**: Implements a lightweight SQLite-backed store:
  - Schema: Single table `updates(asset_type, period, last_date)` with a composite primary key.
  - Methods:
    - `get(asset_type, period)`: Retrieves ISO date string or `None`.
    - `set_update(...)` & `set_full(...)`: Upsert patterns to record incremental vs full-harvest timestamps.
- **Rationale**: A local database offers ACID guarantees, simple file-based distribution, and fast lookups.  Future enhancements (e.g., per-ticker-range history, deletion of stale entries) fit naturally in SQL.

### 3. Instruments Package: Asset-Specific Handlers

- **Structure**: One subclass of `InstrumentHandler` per asset type under `instruments/` (e.g. `StockHandler`, `EtfHandler`, `FxHandler`, etc.).
- **Responsibilities**:
  - **`download_full()`**: Harvest the entire available history or contract set.
  - **`download_update()`**: Pull only new data for daily/weekly/monthly cadence.
  - **`last_remote_update()`**: Query API for the last-available timestamp.
- **Base Class (`InstrumentHandler`)**:
  - Declares the `asset_type` attribute and the three abstract methods.
  - Provides `needs_update(period)` to compare API vs local state.
- **Rationale**: Each handler encapsulates API quirks (endpoint names, parameter vocabulary, multi-step splits & dividends, contract roll logic, etc.). Adding new asset types is as simple as creating a new file and registering it—no edits to core logic.

### 4. UpdateScheduler: Orchestration Layer

- **Responsibilities**: Decide *when* to invoke each `download_update()`, based on `"day"`, `"week"`, or `"month"` runs.
- **Design**:
  - Maintains a dictionary of `{asset_type: handler_instance}`.
  - For each cadence method (`run_daily()`, etc.), iterates handlers and calls `handler.needs_update('day')`.
  - Invokes `download_update()` only when local state is stale.
- **Integration Points**: Easily wired into Cron, Airflow, or other schedulers.
- **Rationale**: Centralizes cadence logic so you don’t accidentally schedule multiple downloads or miss a type. Handlers remain focused purely on how to download.

### 5. High-Level API (index.py)

- **Functions**:
  - `initialize()`: Bootstrap all core objects in one call.
  - `load_dataframe()`: Combines `needs_update` checking, `download_update`, and CSV concatenation into a single DataFrame return.
- **Rationale**: Data scientists and analytics code rarely care about download mechanics. These helpers allow a one-line data load that is guaranteed up-to-date.

### Cross-Cutting Principles

- **DRY & Single Responsibility**: No layer does more than one thing; shared logic (e.g. date comparisons) lives in one place.
- **Mock-Friendly**: Clear boundaries (HTTP vs persistence vs business logic) make unit testing trivial with `monkeypatch` or `responses`.
- **Extensibility**: New endpoints, asset types, or business rules slot in with minimal friction.
- **Documentation & Discoverability**: `README.md`, comprehensive docstrings, and the usage guide ensure developers can onboard quickly.

### Project Layout
```
frd_client/
├── frd_client/            # Main package
│   ├── __init__.py
│   ├── client.py
│   ├── metadata.py
│   ├── scheduler.py
│   ├── index.py            # High-level convenience functions
│   └── instruments/
│       ├── __init__.py
│       ├── base.py
│       ├── stock.py
│       ├── etf.py
│       ├── index.py        # IndexHandler
│       ├── crypto.py       # CryptoHandler
│       ├── fx.py           # FxHandler
│       └── futures.py      # FuturesHandler
├── tests/
│   └── test_client.py
├── LICENSE
├── MANIFEST.in
├── README.md
├── setup.py
└── pyproject.toml
├── requirements.txt      # pinned dependencies
```


## Installation

From source:

```bash
git clone https://github.com/btcoal/frd_client.git
cd frd_client
pip install -r requirements.txt
pip install .
```

## Usage

### 1. Initialize
```python
from pathlib import Path
from frd_client.client import FrdClient
from frd_client.metadata import MetadataStore
from frd_client.scheduler import UpdateScheduler

client = FrdClient(userid="YOUR_USER_ID", work_dir=Path("data"))
meta   = MetadataStore(db_path="data/metadata.db")
sched  = UpdateScheduler(client, meta)

# Perform daily pulls:
sched.run_daily()
```

### 2. Pull Updates

You can run any or all of these:

```python
# Incremental daily pulls
scheduler.run_daily()

# Weekly and monthly pulls
scheduler.run_weekly()
scheduler.run_monthly()
```

### 3. Loading Data into a DataFrame

```python
from frd_client.index import load_dataframe

# Example: load daily crypto data
df_crypto = load_dataframe(
    client, meta,
    asset_type="crypto",
    period="day",
    timeframe="1day"
)

# Example: load full ETF data for tickers AAPL and SPY
df_etf = load_dataframe(
    client, meta,
    asset_type="etf",
    period="full",
    timeframe="1day",
    ticker_list="AAPL,SPY",
    adjustment="adj_splitdiv"
)
```

### Handler-Specific Parameters

| Asset Type  | Required Kwargs                                            |
| ----------- | ---------------------------------------------------------- |
| **stock**   | `ticker_range` (e.g. `"A–E"`), `timeframe`, `adjustment`   |
| **etf**     | `ticker_list` (comma-separated), `timeframe`, `adjustment` |
| **index**   | `ticker_list`, `timeframe`, *optional* `adjustment`        |
| **crypto**  | `symbol_list`, `timeframe`                                 |
| **fx**      | `pair_list`, `timeframe`                                   |
| **futures** | `contract_month`, `timeframe`, *optional* `adjustment`     |

Pass these into `load_dataframe(...)` to target exactly the slice of data you need.

## Handlers
Implement asset-specific logic under `frd_client.instruments` (e.g., StockHandler, EtfHandler).