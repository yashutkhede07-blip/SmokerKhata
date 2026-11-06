# Summary: Plan 02-02 — Stock Ledger, Movements, and Balance Computation

## What Was Done
- Created immutable `StockLedgerEntry` model enforcing append-only architecture (no update, no delete).
- Implemented `StockService` with atomic `record_movement()` and `get_current_stock()` aggregations via SQL `Sum('quantity_delta')`.
- Implemented `POST /api/inventory/stock/adjust/` and `GET /api/inventory/stock/ledger/` endpoints.
- Integrated dynamic `current_stock` computation on item detail/list responses.

## Verification Evidence
- `pytest backend/tests/test_stock.py`: 3 passed (immutability enforcement, adjustment API, aggregated stock calculation).
