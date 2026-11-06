---
phase: "02"
slug: "item-master-stock"
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-11-06"
---

# Phase 02 — Validation Strategy (Item Master & Stock)

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-django |
| **Config file** | `backend/pytest.ini` |
| **Quick run command** | `pytest backend/tests/test_items.py backend/tests/test_stock.py` |
| **Full suite command** | `pytest backend/tests/` |
| **Estimated runtime** | ~3.5 seconds |

## Sampling Rate
- Run quick test command after every task commit.
- Run full suite before phase completion.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Secure Behavior | Automated Command | Status |
|---------|------|------|-------------|-----------------|-------------------|--------|
| 02-01-01 | 01 | 1 | ITEM-01, ITEM-04 | Shop-scoped item creation, paise pricing, soft-delete | `pytest backend/tests/test_items.py -k test_item_crud` | ⬜ pending |
| 02-01-02 | 01 | 1 | ITEM-02 | Item variants creation & pricing override | `pytest backend/tests/test_items.py -k test_variants` | ⬜ pending |
| 02-01-03 | 01 | 1 | ITEM-03 | Soft-delete retains item in DB with deleted_at | `pytest backend/tests/test_items.py -k test_soft_delete` | ⬜ pending |
| 02-02-01 | 02 | 2 | STCK-01, STCK-03 | Stock changes are append-only ledger entries | `pytest backend/tests/test_stock.py -k test_stock_ledger` | ⬜ pending |
| 02-02-02 | 02 | 2 | STCK-04 | Low-stock query returns items below threshold | `pytest backend/tests/test_stock.py -k test_low_stock_alert` | ⬜ pending |
| 02-02-03 | 02 | 2 | STCK-05 | Dead-stock query flags items without sales in N days | `pytest backend/tests/test_stock.py -k test_dead_stock_report` | ⬜ pending |
| 02-03-01 | 03 | 3 | ITEM-01, STCK-03 | DRF permission checks (cashier cannot edit items/adjust stock) | `pytest backend/tests/test_inventory_permissions.py` | ⬜ pending |

## Validation Sign-Off
- [x] All tasks have automated verify commands
- [x] Full suite verifies zero regressions across Phase 1
- [x] `nyquist_compliant: true`
