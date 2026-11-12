# Summary: Plan 04-02 — Atomic Stock Decrement, Double-Sale Prevention & Offline Sync Replay

## What Was Done
- Implemented `BillingService.create_bill_atomic()` ensuring that bill creation, bill line persistence, and stock reductions happen in a single `transaction.atomic()` block.
- Implemented row-level locking via `Item.objects.select_for_update()` to prevent double sales during concurrent high-volume checkouts.
- Automated stock decrement through immutable `StockLedgerEntry` rows (`reason=StockMovementReason.SALE`, `quantity_delta=-quantity`).
- Implemented idempotent replay: replaying a bill submission with existing `(shop, bill_number)` returns the existing record without duplicate stock decrements or duplicate billing.

## Verification Evidence
- `pytest tests/test_billing.py -k "test_atomic_stock_decrement or test_idempotent_bill_submission"`: all passed.
