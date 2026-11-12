# Summary: Plan 03-03 — Ledger Immutability, Tamper Protection & Role Restrictions

## What Was Done
- Enforced strict immutability checks on `CustomerLedgerEntry` and `SupplierLedgerEntry` models: any attempt to modify (`save()` on existing) or delete (`delete()`) raises `ValueError`.
- Defined role-based permissions in `ledgers/permissions.py`:
  - `IsLedgerStaffOrManager`: all shop staff (Cashier, Manager, Owner) can view and add customer udhaar and payments.
  - `IsSupplierManagerOrOwner`: cashiers can view suppliers, but cannot create, modify, or delete suppliers (HTTP 403 Forbidden).

## Verification Evidence
- `pytest tests/test_ledger_immutability.py`: 3 passed (customer ledger immutability, supplier ledger immutability, cashier role permissions).
