---
status: testing
phase: 02-item-master-stock
source:
  - 02-01-SUMMARY.md
  - 02-02-SUMMARY.md
  - 02-03-SUMMARY.md
started: 2026-11-07T00:29:00Z
updated: 2026-11-07T00:29:00Z
---

## Current Test

number: 1
name: Item Master Creation, Category Filtering & Soft-Delete
expected: |
  POST /api/inventory/categories/ creates category. POST /api/inventory/items/ creates item with selling_price_paise, cost_price_paise, and pieces_per_pack. GET /api/inventory/items/?category={id} filters properly. DELETE /api/inventory/items/{id}/ soft-deletes the item (sets deleted_at and is_active=False).
awaiting: user response

## Tests

### 1. Item Master Creation, Category Filtering & Soft-Delete
expected: POST /api/inventory/categories/ creates category. POST /api/inventory/items/ creates item with selling_price_paise, cost_price_paise, and pieces_per_pack. GET /api/inventory/items/?category={id} filters properly. DELETE /api/inventory/items/{id}/ soft-deletes the item (sets deleted_at and is_active=False).
result: [pending]

### 2. Item Variants and Price Overrides
expected: POST /api/inventory/items/{id}/variants/ creates variant (e.g. single stick cigarette or special noodle flavor). Variant effective prices fall back to parent item price if null, or override with custom variant price.
result: [pending]

### 3. Append-Only Stock Ledger & Immutability Enforcement
expected: Stock changes can only be made via StockService or POST /api/inventory/stock/adjust/. Any attempt to directly update or delete a StockLedgerEntry row in Python or ORM raises ValueError.
result: [pending]

### 4. Dynamic Current Stock Calculation
expected: GET /api/inventory/items/{id}/ returns current_stock dynamically aggregated via SQL Sum('quantity_delta') from all historical ledger entries.
result: [pending]

### 5. Low-Stock Alerts and Dead-Stock Inactivity Report
expected: GET /api/inventory/alerts/low-stock/ returns active items with current stock <= low_stock_threshold. GET /api/inventory/reports/dead-stock/?days=30 lists items with zero movements in the last 30 days.
result: [pending]

### 6. Role Permissions on Catalog & Stock
expected: Cashier role can read categories and items, but attempting to create items, update items, or adjust stock returns HTTP 403 Forbidden.
result: [pending]

## Summary

total: 6
passed: 0
issues: 0
pending: 6
skipped: 0
blocked: 0

## Gaps

[none]
