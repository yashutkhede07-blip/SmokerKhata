# Walking Skeleton — SmokerKhata

**Phase:** 1 (Foundation & Auth)
**Generated:** 2026-11-04

## Capability Proven End-to-End

A retail shop owner can sign up with an Indian phone number, receive an OTP, authenticate to obtain a JWT token, create a shop, and invoke an authenticated API endpoint on the running Django backend, with database health confirmed via `/healthz`.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Python 3.12 + Django 5 + Django REST Framework | Mature ORM, built-in security features, admin interface, robust ecosystem. |
| Data Layer | PostgreSQL 16 (managed) + database cache table | Managed ACID transactions, JSONB support, ORM broker compatibility for background jobs. |
| Background Jobs | django-q2 with Postgres ORM broker | Eliminates Redis/Celery operational overhead; fits 512MB RAM constraint. |
| Auth & Tokens | Phone OTP (DB-backed) + JWT with DB blocklist | High-security session revocation without Redis; cashier-friendly 1-hr access / 30-day refresh. |
| Deployment | Gunicorn (2 workers) + Whitenoise + Render/VPS | Runs on minimal resources (<512MB RAM), single deployable unit. |
| Monorepo Layout | `/backend` (Django), `/frontend` (React PWA), `/deploy` | Co-located configuration with clean separation of concerns. |

## Stack Touched in Phase 1

- [ ] Project scaffold (`/backend` Django project, `smokerkhata/settings.py` with `django-environ`, whitenoise, gunicorn)
- [ ] Database — PostgreSQL connection, `common` abstract models (`UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`), database cache table
- [ ] Routing — `/healthz` DB health endpoint and `/api/auth/*` REST endpoints
- [ ] Auth & Storage — DB-backed phone OTP, JWT issuance and revocation blocklist
- [ ] Deployment — `render.yaml`, `Procfile`, `deploy/gunicorn.conf.py`, `deploy/nginx.conf`, systemd service unit

## Out of Scope (Deferred to Later Slices)

- POS billing counter and offline Dexie.js sync engine (Phase 4 & 5)
- Item master, barcode scanning, and inventory stock tracking (Phase 2)
- Customer udhaar and supplier purchase ledgers (Phase 3)
- Razorpay / Google Play subscription billing (Phase 7)
- React PWA frontend UI screens and Capacitor Android wrapper (Phase 8)

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- Phase 2: Item Master & Stock (inventory catalog, variants, stock movements)
- Phase 3: Customer & Supplier Ledgers (credit entries, running balance, WhatsApp links)
- Phase 4: POS Billing & Cash Book (counter checkout, multi-payment split, daily cash reconciliation)
- Phase 5: Offline Sync Engine (IndexedDB outbox, monotonic cursor pull, conflict resolution)
- Phase 6: Reports & Audit Log (sales summaries, Excel/PDF exports, immutable audit trail)
- Phase 7: Subscriptions & Admin Panel (Razorpay webhooks, Google Play verification, shop admin)
- Phase 8: PWA Frontend, Android & Go-Live (complete 10-screen UI in light/dark mode, signed AAB)
