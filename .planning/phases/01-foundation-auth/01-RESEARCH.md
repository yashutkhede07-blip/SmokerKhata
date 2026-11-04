# Phase 1: Foundation & Auth - Technical Research

**Researched:** 2026-11-04
**Domain:** Django 5, DRF, PostgreSQL 16, Whitenoise, django-q2 ORM broker, database cache rate limiting, Phone OTP & JWT, Sentry, GPG encrypted backups, Render/VPS deployment.

## Technical Architecture & Approach

### 1. Project Skeleton & Monorepo
- Monorepo structure:
  - `/backend`: Django project root (`manage.py`, `smokerkhata/` containing `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`)
  - `/frontend`: React 18 + Vite + TS + Tailwind PWA (will build static assets into `/backend/static_pwa/`)
  - `/android`: Capacitor wrapper
  - `/deploy`: `gunicorn.conf.py`, `nginx.conf`, systemd service unit, `backup.sh`, `restore.sh`, `render.yaml`, `Procfile`
- Apps defined per specification:
  - `common` (base models: `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`, `ShopScopedModel`)
  - `accounts` (User, Phone OTP, Staff invitations, Roles: Owner, Manager, Cashier, JWT token blocklist)
  - `shops` (Shop profile, multi-shop ownership)
  - `health` (`/healthz` endpoint verifying DB connectivity)
  - Remaining apps stubbed/created for app registry: `customers`, `suppliers`, `items`, `billing`, `stock`, `food`, `cashbook`, `reports`, `audit`, `sync`, `subscriptions`, `adminpanel`.

### 2. Authentication & Security
- **OTP Model**: 6-digit code, 5-minute expiry, max 3 attempts, phone normalization (10-digit Indian numbers `+91XXXXXXXXXX` or `XXXXXXXXXX`).
- **Pluggable SMS Backend**:
  - `BaseSMSBackend` abstract class with `send_otp(phone: str, code: str) -> bool`.
  - `ConsoleSMSBackend` (prints to stdout/console).
  - `FileSMSBackend` (writes to `logs/otp.log` for headless/CI inspection).
  - Configured via `SMS_BACKEND` env var.
- **JWT Authentication**:
  - `djangorestframework-simplejwt` or custom lightweight JWT utility with 1-hour access token, 30-day refresh token rotation.
  - Active session tracking and `OutstandingToken`/Blocklist check on authenticated requests.
  - Owner role can list and revoke staff tokens.
- **Rate Limiting**:
  - Django database cache (`django.core.cache.backends.db.DatabaseCache`) via `cache_table` created with `createcachetable`.
  - Rate limiting on OTP send/verify (max 5 requests per 10 minutes per phone/IP) using `django-ratelimit` or custom cache-based decorator.

### 3. Background Jobs & Cache
- `django-q2` with ORM broker (`Q_CLUSTER = {'name': 'smokerkhata', 'workers': 2, 'orm': 'default'}`).
- No Redis required.
- Scheduled task capability for nightly tasks (e.g. token blocklist pruning, backup trigger).

### 4. Observability & Health
- `/healthz` view checks default database connectivity via `connection.ensure_connection()`:
  - Returns `{"status": "ok", "database": "connected"}` (HTTP 200) when healthy.
  - Returns `{"status": "error", "database": "unreachable"}` (HTTP 503) when DB fails.
- Sentry SDK initialized in `smokerkhata/settings.py` when `SENTRY_DSN` is set:
  - Custom before-send / event processor strips 10-digit phone numbers and PII from request payloads and logs.
  - Tags events with `shop_id` and `user_id` when authenticated.

### 5. Backups & Deployment
- `deploy/backup.sh`: runs `pg_dump`, encrypts output with GPG symmetric cipher using `BACKUP_ENCRYPTION_KEY`, uploads to S3/B2 using AWS CLI or rclone, enforces 30-day retention.
- `deploy/restore.sh`: downloads archive, decrypts with GPG, restores to target/staging PostgreSQL DB.
- `render.yaml` & `Procfile`: WSGI server `gunicorn smokerkhata.wsgi:application --config deploy/gunicorn.conf.py`. Release command runs `python manage.py migrate --no-input && python manage.py createcachetable`.
- VPS config: `deploy/nginx.conf` reverse proxy to gunicorn unix socket, `deploy/smokerkhata.service` systemd unit with `Restart=always`.

## Validation Architecture

### Quick Verification
- `pytest backend/tests/ -k "healthz or auth"` (< 10 seconds)
### Full Test Suite
- `pytest backend/tests/` (< 30 seconds)
### Critical Test Cases
1. `GET /healthz` returns 200 when DB is up, 503 when DB connection is disrupted.
2. OTP flow: send OTP generates record, wrong code increments attempt, 3 failures locks OTP, correct code returns JWT pair.
3. Permission checks: Cashier cannot access owner-restricted endpoints.
4. Token revocation: revoked token in blocklist returns 401 Unauthorized.
5. Sentry PII filter: phone numbers in error context are redacted before transport.
