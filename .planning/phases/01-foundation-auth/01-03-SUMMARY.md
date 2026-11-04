# Summary: Plan 01-03 — Deployment Configs, Sentry PII Scrubbing & Encrypted Backups

## What Was Done
- Created `deploy/gunicorn.conf.py` (2 workers from WEB_CONCURRENCY, memory budget <512MB RAM, max requests recycling).
- Created `deploy/render.yaml` and `deploy/Procfile` with automated release migrations and cache table generation.
- Created `deploy/nginx.conf` and `deploy/smokerkhata.service` systemd unit for single VPS deployment fallback.
- Implemented Sentry `before_send` PII scrubber in `backend/smokerkhata/observability.py` redacting 10-digit Indian phone numbers from error traces, logs, and breadcrumbs.
- Created `deploy/backup.sh` (Postgres pg_dump + GPG symmetric encryption + 30-day retention) and `deploy/restore.sh`.
- Created `deploy/test_backup_restore.sh` for monthly disaster recovery drills.
- Created comprehensive `.env.example` documenting all configuration keys.

## Verification Evidence
- `pytest backend/tests/test_observability.py`: 2 passed (phone regex matching & PII redaction from error payloads).
- Shell syntax checks on deploy scripts passed.
