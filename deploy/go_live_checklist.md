# SmokerKhata Go-Live Checklist & Sign-Off

**Target Environment:** Single Deployable Production Unit (Render / Ubuntu VPS)
**Non-Negotiable:** Zero data loss, integer paise precision, strictly authenticated multi-tenancy.

---

### 1. Infrastructure & Security Readiness
- [x] **Single Deployable Unit:** React 18 PWA builds to `backend/static_pwa/` and is served via Whitenoise.
- [x] **Environment Security:** `DEBUG=False` in production; `SECRET_KEY` sourced from env.
- [x] **Rate Limiting:** OTP endpoints rate-limited to 5 requests per 10 minutes per phone via database cache table.
- [x] **HTTPS & Headers:** `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`.
- [x] **CORS:** Locked strictly to configured domains in `CORS_ALLOWED_ORIGINS`.

### 2. Database & Data Integrity
- [x] **Integer Paise Precision:** All money amounts stored as `BigIntegerField` paise across billing, cashbook, ledgers, and subscriptions.
- [x] **Row-Level Concurrency:** `select_for_update` locks applied on stock decrements (`BillingService.create_bill_atomic`) to prevent double sales.
- [x] **Append-Only Ledgers:** `CustomerLedgerEntry`, `SupplierLedgerEntry`, `StockLedgerEntry`, `SyncJournalEntry`, and `AuditLogEntry` prevent in-place modifications and deletions.
- [x] **Soft-Deletes:** `deleted_at` timestamp used for all shop catalog entities.

### 3. Offline Sync & Resilience
- [x] **Monotonic Pull:** `GET /api/sync/pull?cursor=N` uses shop-scoped monotonic sequence tracking (never system timestamps).
- [x] **Idempotent Batch Push:** `POST /api/sync/push` deduplicates via `(shop, idempotency_key)` to prevent double billing or phantom ledger rows.
- [x] **IndexedDB Outbox:** Client writes to Dexie.js outbox and displays sync header indicator.

### 4. Backups & Disaster Recovery
- [x] **Automated Backups:** `deploy/backup.sh` runs `pg_dump`, encrypts with symmetric key, and uploads to object storage.
- [x] **Restore Verification:** `deploy/restore.sh` verified with restore drill documentation.
- [x] **Audit Log:** Back-office administrative actions (e.g. trial extensions) require mandatory reason note logged to audit trail.

### 5. Health & Monitoring
- [x] **Health Check:** `GET /healthz` verifies active DB query and returns 200/503.
- [x] **Sentry Error Tracking:** PII scrubbing configured for Indian phone numbers and customer details.
- [x] **Memory Budget:** Configured for 2 gunicorn workers operating within 512 MB RAM footprint.
