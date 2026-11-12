# Summary: Plan 04-03 — Daily Cash Book, Closing Reconciliation & Discrepancy Tracking

## What Was Done
- Created `cashbook` Django app and registered it in `settings.INSTALLED_APPS`.
- Defined `CashBookDay` and `CashBookEntry` models tracking daily cash movements.
- Implemented `/api/cashbook/today/open/` allowing managers/owners to set starting cash.
- Implemented `/api/cashbook/today/entry/` allowing staff to record ad-hoc cash-in and cash-out operations.
- Implemented `/api/cashbook/today/` calculating expected closing cash: `opening + cash_sales + cash_in - cash_out`.
- Implemented `/api/cashbook/today/close/` where managers/owners record physical cash count; any discrepancy is recorded in `discrepancy_paise` and permanently flagged (never silently auto-corrected).

## Verification Evidence
- `pytest tests/test_cashbook.py`: 2 passed (models, full reconciliation flow with discrepancy and permissions).
