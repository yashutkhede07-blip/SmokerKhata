---
status: testing
phase: 03-customer-supplier-ledgers
source:
  - 03-01-SUMMARY.md
  - 03-02-SUMMARY.md
  - 03-03-SUMMARY.md
started: 2026-11-12T11:44:00Z
updated: 2026-11-12T11:44:00Z
---

## Current Test

number: 1
name: Customer Credit & Payment Entries with Running Balance
expected: |
  POST /api/ledgers/customers/ creates customer. POST /api/ledgers/customers/{id}/entries/ records credit (CREDIT_GIVEN) and payments (PAYMENT_RECEIVED). GET /api/ledgers/customers/{id}/ returns balance_paise = (credits - payments).
awaiting: user response

## Tests

### 1. Customer Credit & Payment Entries with Running Balance
expected: POST /api/ledgers/customers/ creates customer. POST /api/ledgers/customers/{id}/entries/ records credit (CREDIT_GIVEN) and payments (PAYMENT_RECEIVED). GET /api/ledgers/customers/{id}/ returns balance_paise = (credits - payments).
result: [pending]

### 2. Customer List Sorting by Highest Outstanding Balance
expected: GET /api/ledgers/customers/?ordering=-balance returns customers sorted in descending order of outstanding udhaar balance.
result: [pending]

### 3. WhatsApp Debt Reminder Link Generator
expected: GET /api/ledgers/customers/{id}/whatsapp-link/ returns valid wa.me link with customer phone (with country code 91) and pre-filled Hindi payment reminder text with rupee balance.
result: [pending]

### 4. Customer Debt Aging Report
expected: GET /api/ledgers/customers/reports/aging/ categorizes outstanding debts across 0-30, 31-60, 61-90, and 90+ days based on the oldest unpaid credit entry.
result: [pending]

### 5. Supplier Master, Purchase Bills, and Payment Tracking
expected: POST /api/ledgers/suppliers/ creates supplier. POST /api/ledgers/suppliers/{id}/entries/ adds purchase bills and payments. GET /api/ledgers/suppliers/{id}/ledger/ returns append-only entries with running balance.
result: [pending]

### 6. Ledger Immutability & Role Permission Gating
expected: Direct modifications or deletions on CustomerLedgerEntry or SupplierLedgerEntry raise ValueError. Cashiers can record customer transactions but receive HTTP 403 when attempting to create, edit, or delete suppliers.
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
