---
gsd_state_version: "1.0"
status: unknown
stopped_at: Phase 01 complete, ready to plan Phase 2
last_updated: "2026-11-06T18:25:20.447Z"
state_head: 5b51bd98a05a0e6cdaf10f6dbe6739ba0025186d
progress:
  total_phases: 8
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
  percent: 13
current_phase: 2
current_phase_name: Item Master & Stock
---

# Project State: SmokerKhata

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-04)

**Core value:** Zero data loss and uptime above all features — every rupee transacted must be recorded and recoverable, even on a low-end Android phone with intermittent connectivity.
**Current focus:** Phase 1 — Foundation & Auth

## Current State

- **Phase:** 0 (Initialized — not started)
- **Active phase:** None
- **Last action:** Project initialized with 8-phase roadmap
- **Next action:** `/gsd-plan-phase 1` or `/gsd-discuss-phase 1`

## Phase Status

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation & Auth | ⬜ Not started |
| 2 | Item Master & Stock | ⬜ Not started |
| 3 | Customer & Supplier Ledgers | ⬜ Not started |
| 4 | POS Billing & Cash Book | ⬜ Not started |
| 5 | Offline Sync Engine | ⬜ Not started |
| 6 | Reports & Audit Log | ⬜ Not started |
| 7 | Subscriptions & Admin Panel | ⬜ Not started |
| 8 | PWA Frontend, Android & Go-Live | ⬜ Not started |

## Key Context

- **Monorepo:** /backend (Django), /frontend (React PWA → /backend/static_pwa), /android (Capacitor), /deploy
- **No Redis, no Docker, no Celery** — django-q2 with Postgres ORM broker only
- **All money in integer paise** (BigIntegerField) — no floats anywhere
- **UUIDv4 for all business records** in the API surface
- **Offline-first:** IndexedDB (Dexie.js) outbox → idempotent sync push/pull
- **Soft-delete everywhere** (deleted_at) — no hard deletes from API or UI
- **Indian locale:** ₹ lakh formatting, DD/MM/YYYY, IST display, UTC storage

## Decisions Log

- 2026-11-04: Initialized project — 8 phases, 83 v1 requirements, MVP mode (vertical slices)

## Session

**Last session:** 2026-11-04T18:23:56.650Z
**Stopped at:** Phase 01 complete, ready to plan Phase 2
**Resume file:** .planning/phases/01-foundation-auth/01-03-SUMMARY.md
