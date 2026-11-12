# Summary: Plan 03-02 — Supplier Ledger, Purchase Bills, and Payment Tracking

## What Was Done
- Defined `Supplier` and immutable `SupplierLedgerEntry` models in `backend/ledgers/models.py`.
- Implemented `SupplierSerializer`, `SupplierLedgerEntrySerializer`, and `SupplierViewSet`.
- Implemented `POST /api/ledgers/suppliers/{id}/entries/` supporting wholesale purchase bills (`PURCHASE_BILL`) and supplier payments (`PAYMENT_MADE`).
- Implemented `GET /api/ledgers/suppliers/{id}/ledger/` calculating running debt balance across chronological purchase and payment entries.

## Verification Evidence
- `pytest tests/test_supplier_ledger.py`: 2 passed (models, ledger flow with running balance).
