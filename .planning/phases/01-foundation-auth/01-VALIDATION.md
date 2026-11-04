---
phase: "01"
slug: "foundation-auth"
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-11-04"
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-django |
| **Config file** | `backend/pytest.ini` |
| **Quick run command** | `pytest backend/tests/ -k "healthz or auth"` |
| **Full suite command** | `pytest backend/tests/` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest backend/tests/ -k "test_unit"`
- **After every plan wave:** Run `pytest backend/tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | INFR-01, INFR-08 | T-01-01 | /healthz handles DB failures safely without leaking credentials | integration | `pytest backend/tests/test_healthz.py` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | INFR-02, INFR-07 | T-01-SC | Security headers & env parsing configured without defaults in prod | unit | `pytest backend/tests/test_settings.py` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 2 | AUTH-01, AUTH-07 | T-01-02 | Phone OTP generation, rate limiting (5 req/10m), expiration | integration | `pytest backend/tests/test_otp.py` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 2 | AUTH-02, AUTH-08 | T-01-03 | JWT issuance, 1-hour access, 30-day refresh, DB blocklist revocation | integration | `pytest backend/tests/test_jwt_auth.py` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 2 | AUTH-03..06 | T-01-04 | Multi-shop access control; Cashier denied from reports/past bills | integration | `pytest backend/tests/test_permissions.py` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 3 | BACK-01..05 | T-01-05 | Backup script produces encrypted archive; restore recovers data | e2e / script | `bash deploy/test_backup_restore.sh` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 3 | INFR-03..06 | T-01-06 | Sentry PII filter redacts phone numbers from error reports | unit | `pytest backend/tests/test_observability.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/pytest.ini` — pytest configuration with Django settings module
- [ ] `backend/tests/conftest.py` — base test client, DB fixtures, shop & user factories
- [ ] `requirements.txt` / dev dependencies — `pytest`, `pytest-django`, `factory-boy`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Render PaaS deployment check | INFR-03 | Requires active cloud infrastructure | Deploy repo to Render staging service and verify build & release phases complete |
| Sentry live event receipt | INFR-06 | Requires Sentry cloud service | Trigger test exception in staging and confirm issue appears in Sentry dashboard without phone PII |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all test setup references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-11-04
