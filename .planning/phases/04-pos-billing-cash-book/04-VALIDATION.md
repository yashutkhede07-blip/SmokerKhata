---
phase: "04"
slug: "pos-billing-cash-book"
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-11-12"
---

# Phase 04 — Validation Strategy (POS Billing & Cash Book)

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-django |
| **Config file** | `backend/pytest.ini` |
| **Quick run command** | `pytest backend/tests/test_billing.py backend/tests/test_cashbook.py` |
| **Full suite command** | `pytest backend/tests/` |
| **Estimated runtime** | ~4.5 seconds |

## Sampling Rate
- Run quick test command after every task commit.
- Run full suite before phase completion.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Secure Behavior | Automated Command | Status |
|---------|------|------|-------------|-----------------|-------------------|--------|
| 04-01-01 | 01 | 1 | BILL-01, BILL-02, BILL-03, BILL-04, BILL-06 | POS Bill model, items, and offline-safe bill numbering | `pytest backend/tests/test_billing.py -k test_bill_creation` | ⬜ pending |
| 04-01-02 | 01 | 1 | BILL-05, BILL-07 | Cash, UPI, Udhaar, Split payments & WhatsApp receipt link | `pytest backend/tests/test_billing.py -k "test_payment_modes or test_bill_whatsapp"` | ⬜ pending |
| 04-02-01 | 02 | 2 | BILL-09, STCK-02 | Atomic stock decrement on sale with `select_for_update` (double-sale prevention) | `pytest backend/tests/test_billing.py -k test_atomic_stock_decrement` | ⬜ pending |
| 04-02-02 | 02 | 2 | BILL-08, BILL-06 | Idempotent bill submission / offline sync handling | `pytest backend/tests/test_billing.py -k test_idempotent_bill_submission` | ⬜ pending |
| 04-03-01 | 03 | 3 | CASH-01, CASH-02, CASH-03, CASH-04, CASH-05 | Cash book opening, cash-in/out, expected closing, and discrepancy recording | `pytest backend/tests/test_cashbook.py` | 04-03-01 | ⬜ pending |

## Validation Sign-Off
- [x] All tasks have automated verify commands
- [x] Full suite verifies zero regressions across all prior phases
- [x] `nyquist_compliant: true`
