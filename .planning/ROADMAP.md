# Roadmap: SmokerKhata

**Project:** SmokerKhata — Multi-tenant shop management for Indian retail
**Mode:** mvp (Vertical MVP slices)
**Granularity:** Standard (5-8 phases, 3-5 plans each)
**Total Phases:** 8
**Requirements Covered:** 83/83 ✓

---

## Phase Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|-----------------|
| 1 | Foundation & Auth | Secure multi-tenant skeleton with phone OTP auth, healthz, backups, and infra | AUTH-01–08, INFR-01–08, BACK-01–05 | 5 |
| 2 | Item Master & Stock | Shop owner can manage inventory, with stock ledger and low-stock alerts | ITEM-01–04, STCK-01–05 | 4 |
| 3 | Customer & Supplier Ledgers | Append-only udhaar and supplier ledgers with WhatsApp links and aging report | CUST-01–07, SUPP-01–04 | 4 |
| 4 | POS Billing & Cash Book | Full counter-screen billing with payment modes and daily cash reconciliation | BILL-01–09, CASH-01–05 | 5 |
| 5 | Offline Sync Engine | Idempotent push/pull with IndexedDB outbox, conflict resolution, and sync tests | SYNC-01–10 | 5 |
| 6 | Reports & Audit Log | Exportable sales/profit reports (Excel + PDF) and immutable audit trail | REPT-01–06, AUDT-01–04 | 4 |
| 7 | Subscriptions & Admin | Razorpay + Play Billing subscriptions, plan limits, grace period, Django admin | SUBS-01–10, ADMN-01–03 | 4 |
| 8 | PWA, Android & Go-Live | Complete PWA frontend (10 screens, light/dark, i18n), Capacitor AAB, go-live checklist | PWA-01–10, ANDR-01–03 | 5 |

---

## Phase Details

### Phase 1: Foundation & Auth
**Goal:** Stand up a secure, multi-tenant Django project skeleton with phone OTP auth, roles, /healthz, gunicorn config, Sentry, encrypted backups, and both PaaS and VPS deployment paths working end-to-end.
**Mode:** mvp
**Requirements:** AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, AUTH-07, AUTH-08, INFR-01, INFR-02, INFR-03, INFR-04, INFR-05, INFR-06, INFR-07, INFR-08, BACK-01, BACK-02, BACK-03, BACK-04, BACK-05
**Success Criteria:**
1. Owner can sign up with phone + OTP, receive a JWT, create a shop, and invite a cashier — all in a single API flow
2. `GET /healthz` returns 200 with DB connected and 503 with DB down, confirmed by integration test
3. `render.yaml` deploys the app to Render with migrations as a release step; gunicorn starts with 2 workers, logs to stdout
4. `deploy/backup.sh` runs `pg_dump`, encrypts with env key, uploads to B2; `deploy/restore.sh` restores to a staging DB
5. Sentry captures an intentional test exception with `shop_id` and `user_id` tags; no phone number appears in the payload

**Plans:**
- **1.1** Django project scaffold: monorepo layout, settings (dev/prod), django-environ, CONN_MAX_AGE, SECURE_* headers, whitenoise, database cache (createcachetable), django-q2 worker, Sentry integration
- **1.2** Accounts and auth: Shop, Owner, StaffMember models; phone OTP flow (console backend for dev, pluggable SMS interface for prod); JWT issuance; DRF permission classes (IsShopOwner, IsManager, IsCashier); rate limiting on OTP endpoint
- **1.3** Infrastructure: /healthz endpoint, gunicorn.conf.py, render.yaml + Procfile, systemd unit, nginx.conf, .env.example, GEMINI.md project instruction file
- **1.4** Backups: backup.sh (pg_dump + gpg encrypt + B2 upload), restore.sh (download + decrypt + psql restore), monthly restore drill checklist, django-q2 nightly scheduled task

---

### Phase 2: Item Master & Stock
**Goal:** Shop owner can fully manage the item catalogue with variants, and all stock movements are recorded as ledger entries with low-stock and dead-stock visibility.
**Mode:** mvp
**Requirements:** ITEM-01, ITEM-02, ITEM-03, ITEM-04, STCK-01, STCK-02, STCK-03, STCK-04, STCK-05
**Success Criteria:**
1. Owner creates a "Maggi" item with two variants (masala, chicken), different selling prices, barcode, and GST category — both appear on the item list with their categories
2. Marking an item inactive hides it from new bills but it still appears in historical bill line items
3. A purchase entry increases stock; selling an item (simulated) decrements stock in the same atomic transaction; direct stock column edits are not possible via API
4. Items below the low-stock threshold appear in a low-stock list with icon + label; a dead-stock query returns items with no sales in 30 days

**Plans:**
- **2.1** Item models: Category, Item, ItemVariant; UUIDv4 PKs; barcode field; GST category enum; active flag (soft-delete); DRF serializers and viewsets with shop-scoped filtering
- **2.2** Stock models: StockLedger (append-only entries), StockLevel (materialized current level); purchase entry endpoint; `select_for_update` on StockLevel for atomic decrement; low-stock threshold per item
- **2.3** Stock reports: dead-stock query (no sales in N days); low-stock alert list endpoint; item list with active/inactive filter and category filter

---

### Phase 3: Customer & Supplier Ledgers
**Goal:** Staff can record udhaar credits and payments for customers, and purchase bills and payments for suppliers, with running balances, WhatsApp links, and aging visibility.
**Mode:** mvp
**Requirements:** CUST-01, CUST-02, CUST-03, CUST-04, CUST-05, CUST-06, CUST-07, SUPP-01, SUPP-02, SUPP-03, SUPP-04
**Success Criteria:**
1. Adding a credit entry and then a partial payment shows the correct running balance in the customer ledger with IST timestamps in DD/MM/YYYY hh:mm format
2. Customer list sorted by highest outstanding balance; customer with ₹500 due appears above customer with ₹100 due
3. WhatsApp link opens wa.me URL pre-filled with the customer name and outstanding amount in ₹ with lakh formatting
4. Aging report returns the number of days since the oldest unpaid entry for each customer

**Plans:**
- **3.1** Customer models: Customer (UUID PK, shop FK, name, phone); CustomerLedgerEntry (append-only: type credit/payment, amount in paise, note, UTC timestamp); running balance computed field; DRF viewsets
- **3.2** Customer features: customer list sorted by outstanding balance; WhatsApp reminder link generation; aging report endpoint (days since oldest unpaid entry)
- **3.3** Supplier models: Supplier (UUID PK, shop FK, name, phone, address); SupplierPurchaseBill; SupplierPayment; balance due computed; DRF viewsets with shop-scoped permissions

---

### Phase 4: POS Billing & Cash Book
**Goal:** Cashier can complete a full sale — search/quick-add items, choose payment mode, receive a bill number — with stock decremented atomically; and owner can close the day's cash book flagging any mismatch.
**Mode:** mvp
**Requirements:** BILL-01, BILL-02, BILL-03, BILL-04, BILL-05, BILL-06, BILL-07, BILL-08, BILL-09, CASH-01, CASH-02, CASH-03, CASH-04, CASH-05
**Success Criteria:**
1. A bill is created with two items from different categories, payment mode "Split" (cash + UPI), and the stock levels of both items decrement by the correct quantities in one transaction; a concurrent second sale of the same item does not produce a negative stock level
2. Bill number follows the `{shop_prefix}-{device_id}-{local_sequence}` format and is unique even when two offline devices reconcile
3. An offline bill created in IndexedDB syncs to the server when connectivity returns; the idempotency key prevents a duplicate bill if the push is retried
4. Cash book closing: opening ₹1000 + cash sales ₹500 − cash-out ₹200 = expected ₹1300; entering ₹1250 as actual flags a ₹50 mismatch; entering ₹1300 shows "Balanced"
5. Bill can be shared as a WhatsApp link with itemized details and total

**Plans:**
- **4.1** Bill models: Bill (UUID PK, shop FK, bill_number, payment_mode, status, offline_device_id, offline_sequence); BillLineItem (item variant FK, qty, unit_price_paise); atomic bill creation + stock decrement endpoint with select_for_update; idempotency key on Bill
- **4.2** Cash book models: CashBookEntry (type: opening/cash_in/cash_out/closing_actual); DayClose model; expected closing calculation; mismatch flagging (never auto-correct); DRF viewsets
- **4.3** Bill utilities: bill number generation (shop_prefix + device_id + sequence); WhatsApp bill share link; bill print endpoint (returns formatted text/HTML for browser print); offline bill reconciliation notes

---

### Phase 5: Offline Sync Engine
**Goal:** The sync engine provides bulletproof offline-first guarantees: writes never lost, idempotent push, monotonic cursor pull, correct conflict resolution, and comprehensive test coverage.
**Mode:** mvp
**Requirements:** SYNC-01, SYNC-02, SYNC-03, SYNC-04, SYNC-05, SYNC-06, SYNC-07, SYNC-08, SYNC-09, SYNC-10
**Success Criteria:**
1. Pushing the same batch twice (same idempotency keys) produces exactly one record each — verified by test
2. `GET /api/sync/pull?cursor=0` returns all changes; a second call with the returned cursor returns only newer changes — no duplicates
3. Offline bill created on device A and offline bill on device B with the same local sequence but different device IDs reconcile without conflict
4. A server restart mid-batch does not lose the partial batch; the client retries and the server deduplicates by idempotency key
5. All 10 SYNC requirements have passing pytest tests; sync test suite runs in under 30 seconds

**Plans:**
- **5.1** Sync models: SyncOperation (idempotency_key, model_name, record_uuid, operation type, payload, processed_at); SyncCursor (monotonic integer sequence, per-shop); server-side idempotency enforcement
- **5.2** Sync API: `POST /api/sync/push` — batch receive, transaction wrap, idempotency check, apply operations in order, return confirmed keys; `GET /api/sync/pull?cursor=N` — return paginated changes since cursor, return new cursor
- **5.3** Conflict resolution: append-only policy for ledger/bill/stock (no overwrite); last-write-wins for non-financial fields by server timestamp; losing version written to audit log
- **5.4** Sync tests: pytest suite covering replay (idempotency), offline-to-online (re-push on reconnect), conflicting edits (two devices edit same item name), server restart mid-batch (simulate crash and retry)

---

### Phase 6: Reports & Audit Log
**Goal:** Owner can generate daily/weekly/monthly sales and profit reports with Excel and PDF export, and every data change is captured in an immutable audit log.
**Mode:** mvp
**Requirements:** REPT-01, REPT-02, REPT-03, REPT-04, REPT-05, REPT-06, AUDT-01, AUDT-02, AUDT-03, AUDT-04
**Success Criteria:**
1. Daily report for a shop shows correct total sales, total cost, and gross profit (all in paise, displayed in ₹ with lakh formatting)
2. Excel export of a 90-day report is generated by a django-q2 background job; the UI shows "Generating…" and then "Download ready" when done
3. PDF export of the same report uses ReportLab only (no WeasyPrint dependency)
4. After editing an item's selling price, the audit log shows the old price, new price, user, and UTC timestamp; the entry is immutable

**Plans:**
- **6.1** Audit log: AuditLog model (UUID PK, shop FK, user FK, model_name, record_uuid, operation, old_value JSON, new_value JSON, created_at UTC); Django signal hook on all business models; immutability enforced (no update/delete endpoint)
- **6.2** Reports core: ReportRequest model (shop FK, type, date_range, status, result_file); synchronous computation for small ranges (<7 days); django-q2 task for large ranges; daily/weekly/monthly aggregation queries from BillLineItem
- **6.3** Export: openpyxl Excel generation (formatted: ₹ with lakh comma, DD/MM/YYYY); ReportLab PDF generation; presigned download URL or inline download endpoint

---

### Phase 7: Subscriptions & Admin Panel
**Goal:** Owners can subscribe via Razorpay (web) or Play Billing (Android), plan limits are enforced server-side, and the Django admin gives full subscription and shop management visibility.
**Mode:** mvp
**Requirements:** SUBS-01, SUBS-02, SUBS-03, SUBS-04, SUBS-05, SUBS-06, SUBS-07, SUBS-08, SUBS-09, SUBS-10, ADMN-01, ADMN-02, ADMN-03
**Success Criteria:**
1. A new account gets a 14-day trial automatically; the trial status is visible in the API and in Django admin
2. After trial expiry + 5-day grace period, all write endpoints return 403 "read-only" until a subscription is active; read and export endpoints remain accessible for 90 days
3. Razorpay webhook: a `subscription.charged` event with a valid signature saves the raw payload, enqueues a django-q2 job, and replaying the same webhook event does not create a duplicate subscription period
4. Django admin shows each shop's MRR, subscription status, and allows an admin to extend a trial with a mandatory reason note that appears in the audit log

**Plans:**
- **7.1** Subscription models: Plan (name, price_paise, interval, limits JSON); Subscription (shop FK, plan FK, status, trial_end, current_period_end, grace_end); SubscriptionEvent (raw webhook payload, processed_at); prorated upgrade/downgrade logic
- **7.2** Razorpay integration: webhook endpoint (signature verification, payload save, django-q2 enqueue); subscription creation flow; plan display with savings vs monthly (Quarterly, Yearly)
- **7.3** Google Play Billing: purchase token verification via Google Play Developer API; server-side confirmation endpoint called by Android app after purchase; idempotent handler
- **7.4** Django admin customization: ShopAdmin (subscription status, MRR column, churn flag); trial extension action with mandatory reason note → audit log; FeatureFlag model per plan; plan limits editor

---

### Phase 8: PWA Frontend, Android & Go-Live
**Goal:** Complete the PWA frontend (all 10 screens, light/dark/system theme, Hindi/English i18n, offline-first), publish the signed Android AAB, and execute the full go-live checklist.
**Mode:** mvp
**Requirements:** PWA-01, PWA-02, PWA-03, PWA-04, PWA-05, PWA-06, PWA-07, PWA-08, PWA-09, PWA-10, ANDR-01, ANDR-02, ANDR-03
**Success Criteria:**
1. App installs as a PWA from the browser and opens with no network (service worker cache); sync status shows "Offline" in the header
2. All 10 screens render correctly in Light and Dark mode (system theme follows OS preference); theme switches instantly with no reload; all text/background pairs pass WCAG AA contrast check
3. POS screen loads under 3 seconds on a 3G throttled connection in Chrome DevTools; touch targets are at least 44px; POS buttons are at least 56px
4. Signed Android AAB builds successfully from Capacitor; Google Play Billing integration works end-to-end in a test track
5. Go-live checklist complete: staging deploy verified, Sentry receiving errors, UptimeRobot monitoring /healthz, backup run and restore verified, DEBUG=False, HTTPS confirmed

**Plans:**
- **8.1** Design system and routing: Tailwind CSS tokens (CSS variables on :root and [data-theme="dark"]), theme provider (Light/Dark/System), i18next setup (English + Hindi), React Router, Dexie.js store schema, service worker (Workbox), manifest.json
- **8.2** Core screens: Login (phone + OTP), Home dashboard (today's sales, cash in hand, udhaar outstanding, low-stock count), Settings (shop profile, employees, theme toggle, subscription status)
- **8.3** Transaction screens: POS/Billing (search, quick-add grid, bill list, payment buttons, keyboard shortcuts on desktop), Customer ledger (list by highest due, detail with running balance, WhatsApp button), Cash book (opening, in, out, expected, actual, mismatch row)
- **8.4** Management screens: Item master (table on desktop, cards on mobile, category tabs, active/inactive toggle), Stock (table, low-stock rows with icon + label), Reports (date range, summary numbers, table, Excel/PDF export buttons), Sync status header indicator
- **8.5** Android and go-live: Capacitor init, Android project config, keystore setup, AAB build, Play Console checklist (privacy policy, data safety form, subscription product IDs); go-live checklist execution (staging, Sentry, UptimeRobot, backup/restore drill, DEBUG=False, HTTPS)

---

## Requirement Coverage

**AUTH:** 8 requirements → Phase 1 ✓
**INFR:** 8 requirements → Phase 1 ✓
**BACK:** 5 requirements → Phase 1 ✓
**ITEM:** 4 requirements → Phase 2 ✓
**STCK:** 5 requirements → Phase 2 ✓
**CUST:** 7 requirements → Phase 3 ✓
**SUPP:** 4 requirements → Phase 3 ✓
**BILL:** 9 requirements → Phase 4 ✓
**CASH:** 5 requirements → Phase 4 ✓
**SYNC:** 10 requirements → Phase 5 ✓
**REPT:** 6 requirements → Phase 6 ✓
**AUDT:** 4 requirements → Phase 6 ✓
**SUBS:** 10 requirements → Phase 7 ✓
**ADMN:** 3 requirements → Phase 7 ✓
**PWA:** 10 requirements → Phase 8 ✓
**ANDR:** 3 requirements → Phase 8 ✓

**Total:** 83/83 ✓

---
*Roadmap created: 2026-11-04*
*Last updated: 2026-11-04 after initialization*
