# Phase 1: Foundation & Auth - Context

**Gathered:** 2026-11-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the secure multi-tenant Django skeleton, phone OTP auth, role-based permissions (owner, manager, cashier), /healthz endpoint, deployment configuration (Render/Railway and VPS Nginx/systemd), encrypted nightly backup scripts, and project logging/monitoring (Sentry, no PII).
</domain>

<decisions>
## Implementation Decisions

### OTP Provider Wiring
- **D-01:** Abstract base class with `send_otp(phone, otp)` interface; swapped via `SMS_BACKEND` env var. — **Reversibility:** costly — affects SMS provider implementations and settings.
- **D-02:** Include both Console and File backends for dev/CI environments.
- **D-03:** 6-digit numeric OTP, 5-minute expiry, max 3 verification attempts per OTP.
- **D-04:** Pending OTPs stored in database (`OTP` model with phone, code, created_at, attempts, verified) to support offline/queryable audit.

### JWT Token Lifecycle
- **D-05:** Database token blocklist table for immediate revocation on logout or staff change; expired entries pruned via django-q2. — **Reversibility:** costly — DB table and middleware check.
- **D-06:** Multi-device session visibility in backend: shop owners can inspect active sessions and revoke cashier/manager tokens.
- **D-07:** Expiry balance (Agent discretion): 1-hour access token, 30-day rotating refresh token to prevent cashier friction while keeping revocation responsive.

### Django Project Layout
- **D-08:** Django project root package named `smokerkhata/` (wsgi, asgi, settings, urls).
- **D-09:** All 16 modular apps from specification: `accounts`, `shops`, `customers`, `suppliers`, `items`, `billing`, `stock`, `food`, `cashbook`, `reports`, `audit`, `sync`, `subscriptions`, `adminpanel`, `health`, plus `common` for base abstract models. — **Reversibility:** one-way — app structure and migration dependency graph.
- **D-10:** Single settings module (`smokerkhata/settings.py`) driven strictly by `django-environ`, avoiding split settings drift.
- **D-11:** Base model in `common` app: `UUIDModel` (UUIDv4 primary keys), `TimeStampedModel`, and `SoftDeleteModel` (`deleted_at`).

### the agent's Discretion
- JWT access/refresh duration: 1-hour access token with 30-day refresh token rotation.
- Settings structure: single `settings.py` powered by `django-environ`.
- Base models: `common/models.py` defining `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`, `ShopScopedModel`.
- Backup encryption: GPG symmetric encryption with env passphrase for simplicity and portable restoration.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- `.planning/PROJECT.md` — Core architectural rules (integer paise, no Redis/Docker, django-q2 Postgres broker)
- `.planning/REQUIREMENTS.md` — Requirements AUTH-01 to AUTH-08, INFR-01 to INFR-08, BACK-01 to BACK-05
- `.planning/ROADMAP.md` § Phase 1 — Phase 1 scope and success criteria

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Greenfield project. No existing code assets.

### Established Patterns
- All money stored in integer paise (`BigIntegerField`).
- Soft delete everywhere (`deleted_at`).
- Monorepo structure: `/backend`, `/frontend`, `/android`, `/deploy`.

### Integration Points
- `/healthz` external probe for host and UptimeRobot.
- Pluggable SMS provider interface loaded dynamically via `SMS_BACKEND`.
- Sentry integration configured in `settings.py` capturing `shop_id` and `user_id` tags.

</code_context>

<specifics>
## Specific Ideas

- Ensure phone OTP rate-limiting is backed by Django database cache table (`createcachetable`).
- Ensure no phone numbers or PII leak into Sentry exception payloads.
</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed strictly within Phase 1 boundary.
</deferred>

---

*Phase: 1-Foundation & Auth*
*Context gathered: 2026-11-04*
