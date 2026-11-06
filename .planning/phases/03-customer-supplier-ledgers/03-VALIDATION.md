---
phase: "03"
slug: "customer-supplier-ledgers"
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-11-07"
---

# Phase 03 — Validation Strategy (Customer & Supplier Ledgers)

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-django |
| **Config file** | `backend/pytest.ini` |
| **Quick run command** | `pytest backend/tests/test_customer_ledger.py backend/tests/test_supplier_ledger.py` |
| **Full suite command** | `pytest backend/tests/` |
| **Estimated runtime** | ~3.5 seconds |

## Sampling Rate
- Run quick test command after every task commit.
- Run full suite before phase completion.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Secure Behavior | Automated Command | Status |
|---------|------|------|-------------|-----------------|-------------------|--------|
| 03-01-01 | 01 | 1 | CUST-01, CUST-02, CUST-03, CUST-04 | Append-only customer credit & payment ledger | `pytest backend/tests/test_customer_ledger.py -k test_customer_entries` | ⬜ pending |
| 03-01-02 | 01 | 1 | CUST-05 | Customer list sorted by highest outstanding balance | `pytest backend/tests/test_customer_ledger.py -k test_customer_sorting` | ⬜ pending |
| 03-01-03 | 01 | 1 | CUST-06, CUST-07 | WhatsApp reminder link generation & debt aging report | `pytest backend/tests/test_customer_ledger.py -k "test_whatsapp_link or test_aging_report"` | ⬜ pending |
| 03-02-01 | 02 | 2 | SUPP-01, SUPP-02, SUPP-03, SUPP-04 | Supplier creation, purchase bills, and payments ledger | `pytest backend/tests/test_supplier_ledger.py` | ⬜ pending |
| 03-03-01 | 03 | 3 | CUST-04, SUPP-04 | Ledger immutability & role permissions | `pytest backend/tests/test_ledger_immutability.py` | ⬜ pending |

## Validation Sign-Off
- [x] All tasks have automated verify commands
- [x] Full suite verifies zero regressions across Phases 1, 2, and 3
- [x] `nyquist_compliant: true`
