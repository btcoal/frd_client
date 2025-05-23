import sqlite3

class MetadataStore:
    """
    Added the `needs_update` helper in the base class to centralize and DRY-up the “should I pull again?” logic. Here's why:

    * **Single source of truth**
    Instead of each handler re-implementing the compare-remote-vs-local date logic, `needs_update` lives once in `InstrumentHandler`. All subclasses inherit it, so you never risk subtle inconsistencies (e.g. one handler accidentally comparing the wrong period key).

    * **Cleaner subclass code**
    With `needs_update`, your scheduler can simply do

    ```python
    if handler.needs_update("day"):
        handler.download_update(...)
    ```

    —no need to fetch & parse dates in two places.

    * **Easier testing**
    You can unit-test `needs_update` in isolation against mocked metadata, ensuring your update-decision logic is rock-solid. Subclasses then only need tests for “does my download call the right endpoint”.

    * **Future extensibility**
    If you later want to add an “only update on weekdays” or “throttle if no network” rule, you can hook that into `needs_update` (or override it) without touching every handler.

    In short, it keeps your handlers focused purely on *how* to download their data, while the base class uniformly handles *when* that download is needed.

    """
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
          CREATE TABLE IF NOT EXISTS updates (
            asset_type TEXT,
            period TEXT,
            last_date  TEXT,
            PRIMARY KEY (asset_type, period)
          )
        """)

    def get(self, asset_type, period):
        cur = self.conn.execute(
          "SELECT last_date FROM updates WHERE asset_type=? AND period=?",
          (asset_type, period)
        )
        row = cur.fetchone()
        return row[0] if row else None

    """
    1. **`set_update(...)`**
    * Records or refreshes the “last\_date” for an incremental pull (day/week/month).
    * Keyed by `(asset_type, period)` where `period` is one of `"day"`, `"week"`, or `"month"`.
    * Used by your scheduler (via `needs_update`) to decide if, say, the daily feed has advanced past what you’ve already downloaded.

    2. **`set_full(...)`**
    * Records the timestamp for when you last did a *full* harvest of everything.
    * You’ve chosen to key it as `(asset_type, "full_<ticker_range>")`, so you can track full downloads separately for different ranges, e.g. `"full_A–E"` vs `"full_F–J"`.
    * That way you could trigger a fresh full pull if, for example, you want to re-bootstrap or backfill a new range of tickers.

    If you only ever do one monolithic “full” download (no split by ticker‐range), you could simplify by folding `set_full` into `set_update` (e.g. use `period="full"`). But if you want to track multiple full‐harvests—say per batch of tickers—it’s handy to have a distinct helper.

    Bottom line: keep both if you need to distinguish incremental vs. full-range downloads; if not, you can collapse them into a single `set()` that you call with `period="full"` or `period="day"`.

    """

    def set_update(self, asset_type, period, date):
        self.conn.execute("""
          INSERT INTO updates(asset_type,period,last_date)
            VALUES(?,?,?)
          ON CONFLICT(asset_type,period) DO UPDATE SET last_date=excluded.last_date
        """, (asset_type, period, date.isoformat()))
        self.conn.commit()

    def set_full(self, asset_type, ticker_range, date):
        key = f"full_{ticker_range}"
        self.set_update(asset_type, key, date)