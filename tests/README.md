# frd_client/tests/README.md

Key areas to cover with tests (using Pytest + unittest.mock or a library like responses):

1. **`FrdClient` core**

   * *HTTP error handling*: mock out `requests.get` to raise HTTP errors or return bad status codes, assert that `_get` raises.
   * *ZIP unpacking*: feed a small in-memory ZIP blob (e.g. created via `io.BytesIO` and `zipfile`) into `fetch_zip` and verify that expected files appear under a temporary `tmp_path` directory.

2. **`MetadataStore`**

   * *Empty DB*: calling `get(...)` on a fresh store returns `None`.
   * *Round-trip*: after `set_update("stock","day", some_date)`, `get("stock","day")` returns the same ISO string.
   * *Upsert behavior*: calling `set_update` twice with two dates ensures the later date overwrites the first.

3. **`InstrumentHandler.needs_update`**

   * Create a dummy handler subclass where `last_remote_update` is stubbed to return a fixed date.
   * Simulate metadata having an older date vs. newer date vs. missing entry, and assert `needs_update` returns `True`/`False` appropriately.

4. **Concrete handlers (`StockHandler`, `EtfHandler`, etc.)**

   * *Parameter passing*: monkey-patch the `FrdClient.fetch_zip` and `FrdClient._get` methods, call `download_full(...)` / `download_update(...)` and assert that they invoked `.fetch_zip` with the correct `endpoint` and `params` dict.
   * *Meta writes*: similarly, mock the `MetadataStore` so you can check that `.set_full` or `.set_update` is called with the right `(asset_type, period_or_key, date)` arguments.

5. **`UpdateScheduler`**

   * *Happy path*: set up one handler whose `needs_update` returns `True` and verify that `download_update` is called exactly once for each period method.
   * *Skip path*: if `needs_update` is `False`, assert no download method is invoked.

6. **`load_dataframe` (in `index.py`)**

   * Use a temporary work dir and create a handful of small CSV files under `<work_dir>/stock/day/…`.
   * Mock `needs_update` to `False` so no downloads happen, then call `load_dataframe` and assert the returned DataFrame has the expected rows/columns.
   * Also test the “no files” path raises a `FileNotFoundError`.

---

**Structure & tooling tips**

* Put these in `tests/test_client.py`, `tests/test_metadata.py`, `tests/test_handlers.py`, etc.
* Use `tmp_path` fixtures for filesystem isolation.
* Use `monkeypatch` or `responses` to stub out HTTP calls.
* Parametrize similar tests across handlers via Pytest parametrization (e.g. iterate over `[StockHandler, EtfHandler, …]` with their expected endpoints/params).