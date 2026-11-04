# Phase 1: Foundation & Auth - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-04
**Phase:** 1-Foundation & Auth
**Areas discussed:** OTP Provider Wiring, JWT Token Lifecycle, Django Project Layout

---

## OTP Provider Wiring

| Option | Description | Selected |
|--------|-------------|----------|
| Abstract base class with one method (send_otp) | Swap implementations via a single env var like SMS_BACKEND | ✓ |
| Provider registry | Register multiple providers by name, select at runtime; supports failover | |
| You decide | Pick simplest approach that works | |

| Option | Description | Selected |
|--------|-------------|----------|
| Console backend only | Prints OTP to stdout in dev | |
| Console + file backend | Also writes OTPs to a log file for easier testing in CI/headless environments | ✓ |
| You decide | | |

| Option | Description | Selected |
|--------|-------------|----------|
| 6-digit numeric, 5-minute expiry, max 3 attempts | Standard Indian banking/retail app security | ✓ |
| 4-digit numeric, 10-minute expiry, max 5 attempts | | |
| You decide | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Store in DB (OTP model) | Simple, queryable, works offline/audit | ✓ |
| Store in Django cache | Auto-expires, less DB clutter, but not queryable | |
| You decide | | |

---

## JWT Token Lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| 15 minutes | Standard security practice; requires frequent refresh | |
| 1 hour | Less friction for shop staff | |
| You decide | Balance security with the reality that cashiers use this all day | ✓ (Selected 1 hour access token) |

| Option | Description | Selected |
|--------|-------------|----------|
| Rotate on every use | Invalidate old refresh token on rotation | |
| Long-lived refresh token (30 days) | User stays logged in for a month | |
| You decide | | ✓ (Selected 30-day rotating refresh token) |

| Option | Description | Selected |
|--------|-------------|----------|
| Simple DB blocklist table | Add tokens on logout/password change; check on request; prune via django-q2 | ✓ |
| No blocklist | Rely on short access expiry | |
| You decide | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes | Owner can see and terminate active sessions from settings | ✓ |
| No | Just support logout | |
| You decide | | |

---

## Django Project Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Split settings (base/dev/prod) | Cleaner separation | |
| Single settings.py with django-environ | One file, all env-driven; simpler | |
| You decide | | ✓ (Selected single settings.py with django-environ) |

| Option | Description | Selected |
|--------|-------------|----------|
| All 16 apps from spec | accounts, shops, customers, suppliers, items, billing, stock, food, cashbook, reports, audit, sync, subscriptions, adminpanel, health + common | ✓ |
| Consolidated apps | Merge related apps | |
| You decide | | |

| Option | Description | Selected |
|--------|-------------|----------|
| config/ | Standard Django layout | |
| smokerkhata/ | Project package matches project name | ✓ |
| You decide | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes | Shared 'common' app for BaseModel, ShopScopedModel, etc. | |
| No | Define base models inline | |
| You decide | | ✓ (Selected shared 'common' app with UUID, timestamps, soft delete) |

---

## the agent's Discretion

- Access token lifetime set to 1 hour; refresh token lifetime 30 days with rotation.
- Settings structure consolidated in `smokerkhata/settings.py` using `django-environ`.
- Abstract base models placed in `common` app.

## Deferred Ideas

- None — discussion stayed within Phase 1 scope.
