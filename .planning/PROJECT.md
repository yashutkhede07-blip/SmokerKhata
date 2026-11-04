# SmokerKhata

## What This Is

SmokerKhata is a production-ready, multi-tenant shop management system designed for small retail shops in India that sell cigarettes, cold drinks, chips, and prepared food (maggi, french fries, nuggets, chai). It is a mobile-first Progressive Web App with offline-first sync, a Python/Django backend, and a signed Android AAB, targeting shop owners and their staff who need reliable POS billing, udhaar (credit) ledger management, stock tracking, and cash book reconciliation — with zero data loss as the top non-negotiable.

## Core Value

**Zero data loss and uptime above all features** — every rupee transacted must be recorded and recoverable, even on a low-end Android phone with intermittent connectivity.

## Business Context

- **Customer**: Small retail shop owners and managers in India (cigarettes, cold drinks, chips, prepared food)
- **Revenue model**: SaaS subscriptions — Monthly / Quarterly / Yearly plans via Razorpay (web) and Google Play Billing (Android)
- **Success metric**: Monthly Recurring Revenue (MRR); churn tracked per shop in Django admin
- **Strategy notes**: Free 14-day trial (no card required); data never deleted after expiry; 90-day export window post-expiry

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Phone OTP auth with multi-shop owner accounts and role-based access (owner, manager, cashier)
- [ ] Customer udhaar ledger — append-only credit/payment entries, running balance, WhatsApp reminder, aging report
- [ ] Supplier ledger — purchase bills, payments made, balance due
- [ ] Item master — categories, variants, prices, barcodes, GST, active flag
- [ ] POS billing — fast counter screen, mixed categories, cash/UPI/udhaar/split payments, offline bill IDs, print/WhatsApp
- [ ] Stock management — purchase entries, auto-decrement on sale, low-stock alerts, dead-stock report, ledger-only edits
- [ ] Prepared food models (recipe, wastage, expiry, oil log) — data layer now, UI phase 2
- [ ] Cash book — opening, in, out, expected/actual closing, mismatch flagged never auto-corrected
- [ ] Reports — daily/weekly/monthly sales & profit, top sellers, margin; Excel (openpyxl) & PDF (ReportLab) export
- [ ] Audit log — every CUD operation with user, UTC timestamp, old/new value; soft-delete only
- [ ] Offline-first sync engine — IndexedDB/Dexie.js outbox, exponential backoff, idempotent push/pull with monotonic cursor
- [ ] Subscriptions — Razorpay webhooks + Google Play Billing, 14-day trial, plan limits in DB, grace period, read-only after expiry
- [ ] PWA — service worker, offline shell, manifest, installable
- [ ] Light / Dark / System theme with strict grayscale design system (WCAG AA)
- [ ] Signed Android AAB via Capacitor
- [ ] Deployment — Render/Railway PaaS + VPS fallback (gunicorn + Nginx + systemd)
- [ ] Encrypted daily pg_dump backups to S3-compatible storage, 30-day retention, restore drill documented
- [ ] /healthz endpoint, Sentry error tracking, UptimeRobot monitoring

### Out of Scope

- Redis or Celery — explicitly replaced by django-q2 with Postgres ORM broker
- WeasyPrint — heavy system deps; replaced by ReportLab for PDF
- Docker — not in scope per spec; deploy via gunicorn/systemd or PaaS
- Real-time features (WebSocket push) — offline-first polling sync is sufficient for MVP
- Age-restricted product compliance features — will stop and ask before adding any such category
- Hard deletes from API or UI — soft-delete everywhere
- Float money storage — all amounts in integer paise (BigIntegerField)

## Context

- Target users run low-end Android phones (under 2 GB RAM); page load target < 3s on 3G
- Indian locale: ₹ with lakh comma formatting, DD/MM/YYYY dates, IST display, UTC storage
- Monorepo layout: `/backend` (Django), `/frontend` (React PWA → builds to `/backend/static_pwa`), `/android` (Capacitor), `/deploy`
- Phone numbers validated as 10 digits on client and server; no PII (full phone numbers) in Sentry logs
- Hindi and English UI: Django i18n for API messages, i18next on frontend
- Bill IDs are unique per shop even offline: `{shop_prefix}-{device_id}-{local_sequence}`, reconciled on sync
- All UUIDs v4 for business records; never auto-increment IDs in the API surface
- Double-sale prevention: stock decrement + bill creation in one `atomic` transaction with `select_for_update`
- Conflict policy: ledger/bill/stock entries are append-only; non-financial fields use last-write-wins by server timestamp; losing version kept in audit log

## Constraints

- **Tech stack**: Python 3.12, Django 5, DRF, PostgreSQL 16, gunicorn, whitenoise, django-environ — no Redis, no Docker, no Celery
- **Background jobs**: django-q2 with Postgres ORM broker only; nightly backups from scheduled task, not web process
- **Cache**: Django database cache (`createcachetable`); django-ratelimit uses this cache
- **Auth**: Phone OTP → JWT for API clients; session auth for Django admin
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS; PWA with Dexie.js offline store; built to static and served by whitenoise
- **Android**: Capacitor wrapper, signed AAB for Google Play
- **Payments**: Razorpay Subscriptions (web), Google Play Billing (Android) verified via Google Play Developer API
- **Reports**: openpyxl (Excel), ReportLab (PDF)
- **Hosting**: Render or Railway (primary); single Ubuntu VPS gunicorn + Nginx + systemd (fallback); same codebase, same env vars
- **Monitoring**: Sentry free tier; `/healthz` endpoint; UptimeRobot
- **Tests**: pytest + pytest-django + factory_boy (backend); Vitest (frontend); 80% coverage target on sync, billing, ledger
- **Memory budget**: app must run within 512 MB at 2 gunicorn workers
- **Security**: HTTPS only, rate limiting on OTP/login, role checks on every route, CORS locked to known origins, encrypted backups, no secrets in client bundle

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| All money stored as integer paise (BigIntegerField) | Eliminates float rounding errors in financial records | — Pending |
| django-q2 with Postgres ORM broker instead of Redis/Celery | Removes Redis operational dependency; Postgres already required | — Pending |
| Offline-first with IndexedDB (Dexie.js) outbox + idempotent sync | Zero data loss on network drop; retries on reconnect | — Pending |
| Soft-delete everywhere (deleted_at) | Audit compliance; no accidental permanent data loss | — Pending |
| UUIDv4 for all business records in API | Enables client-side ID generation for offline bills | — Pending |
| Monotonic sequence cursor for sync pull (not timestamp) | Avoids clock-skew conflicts and missed changes | — Pending |
| Subscription plan limits live in DB (Plan model) | Allows admin to change limits without code deploy | — Pending |
| Razorpay webhook payload saved to DB first, then processed by django-q2 | Idempotent; survives process restart mid-processing | — Pending |
| WhatsApp reminder via wa.me link (not API) | No WhatsApp Business API cost or approval required for MVP | — Pending |
| ReportLab for PDF instead of WeasyPrint | Avoids heavy system dependencies that cause deploy failures | — Pending |
| Build frontend to static_pwa, served by Django whitenoise | Single deployable unit; no separate static hosting needed | — Pending |
| Bill ID: shop_prefix + device_id + local_sequence | Unique across shops and devices without server round-trip | — Pending |
| Capacitor for Android AAB | Reuses PWA codebase; no native Android development required | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-11-04 after initialization*
