<!-- GSD:project-start source:PROJECT.md -->

## Project

**SmokerKhata**

SmokerKhata is a production-ready, multi-tenant shop management system designed for small retail shops in India that sell cigarettes, cold drinks, chips, and prepared food (maggi, french fries, nuggets, chai). It is a mobile-first Progressive Web App with offline-first sync, a Python/Django backend, and a signed Android AAB, targeting shop owners and their staff who need reliable POS billing, udhaar (credit) ledger management, stock tracking, and cash book reconciliation — with zero data loss as the top non-negotiable.

**Core Value:** **Zero data loss and uptime above all features** — every rupee transacted must be recorded and recoverable, even on a low-end Android phone with intermittent connectivity.

### Constraints

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

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-fast` for a trivial task inline, with no subagents and no PLAN.md
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
