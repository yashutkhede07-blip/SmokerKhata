# Summary: Plan 02-03 — Low-Stock Alerts, Dead-Stock Reports, and Role Restrictions

## What Was Done
- Implemented `GET /api/inventory/alerts/low-stock/` querying active items where aggregate stock <= `low_stock_threshold`.
- Implemented `GET /api/inventory/reports/dead-stock/?days=30` detecting items with no ledger movement in N days.
- Enforced strict role-based permission checks: cashiers can read catalog and view items, but receive HTTP 403 Forbidden when attempting to create/modify items, categories, or adjust stock.

## Verification Evidence
- `pytest backend/tests/test_stock_reports.py`: 2 passed (low stock threshold, dead stock detection).
- `pytest backend/tests/test_inventory_permissions.py`: 1 passed (cashier restricted from modifications and adjustments).
