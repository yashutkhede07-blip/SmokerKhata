---
status: testing
phase: 04-pos-billing-cash-book
source:
  - 04-01-SUMMARY.md
  - 04-02-SUMMARY.md
  - 04-03-SUMMARY.md
started: 2026-11-12T12:12:00Z
updated: 2026-11-12T12:12:00Z
---

## Current Test

number: 1
name: POS Bill Creation & Sequence Numbering
expected: |
  GET /api/billing/next-sequence/ generates unique {shop_prefix}-{device_id}-{local_sequence}. POST /api/billing/bills/ creates multi-item bill with integer paise amounts.
awaiting: user response

## Tests

### 1. POS Bill Creation & Sequence Numbering
expected: GET /api/billing/next-sequence/ generates unique {shop_prefix}-{device_id}-{local_sequence}. POST /api/billing/bills/ creates multi-item bill with integer paise amounts.
result: [pending]

### 2. Payment Modes (Cash, UPI, Udhaar, Split)
expected: Split payments validate that sum of Cash, UPI, and Udhaar matches final amount. Udhaar portions automatically create a credit entry in CustomerLedgerEntry.
result: [pending]

### 3. WhatsApp Bill Receipt Link Generator
expected: GET /api/billing/bills/{id}/whatsapp-link/ generates a valid wa.me link with itemized lines, total in rupees, and payment mode.
result: [pending]

### 4. Atomic Stock Decrement & Double-Sale Prevention
expected: Creating a bill atomically creates negative StockLedgerEntry rows for sold items with select_for_update locking.
result: [pending]

### 5. Idempotent Bill Submission
expected: Replaying an offline bill with identical (shop, bill_number) returns the existing bill and prevents duplicate stock deductions.
result: [pending]

### 6. Daily Cash Book Opening, Entries, Reconciliation & Discrepancy
expected: Expected closing cash equals opening + cash_sales + cash_in - cash_out. Closing records discrepancy and flags mismatch without auto-correcting.
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
