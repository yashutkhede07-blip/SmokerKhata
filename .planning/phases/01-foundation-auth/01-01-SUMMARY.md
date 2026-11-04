# Summary: Plan 01-01 — Project Scaffold, Common Models & Health Check

## What Was Done
- Created Django 5 project monorepo structure with `/backend` and `/deploy`.
- Configured 12-factor settings in `backend/smokerkhata/settings.py` via `django-environ` reading `DATABASE_URL`, `CONN_MAX_AGE`, `DJANGO_DEBUG`, `DJANGO_SECRET_KEY`, and security headers.
- Implemented core abstract base models in `backend/common/models.py` (`UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`, `ShopScopedModel`).
- Created `/healthz` view in `backend/health/views.py` testing database connectivity via `connection.ensure_connection()`, returning 200 (healthy) and 503 (database down) without sensitive data leakage.
- Configured `backend/pytest.ini` test runner and verified with passing unit and integration tests.

## Verification Evidence
- `pytest backend/tests/test_healthz.py`: 2 passed (healthy 200, db down 503).
- `pytest backend/tests/test_settings.py`: 2 passed (security configuration & abstract models).
