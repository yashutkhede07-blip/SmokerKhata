# Plan 06-01 Summary: Immutable Audit Trail & Change Logging

- Created `backend/audit/` app and registered in `settings.INSTALLED_APPS` and `urls.py`.
- Defined `AuditLogEntry` model:
  - Captures `shop`, `user`, `model_name`, `record_id`, `action`, `old_values`, `new_values`, and `notes`.
  - Enforced strict append-only immutability in `save()` and `delete()` (`AUDT-03`).
- Created `AuditService.record_audit` helper for tracking modifications and conflict resolution losing versions (`AUDT-01`, `AUDT-04`).
- Implemented read-only endpoint `/api/audit/logs/` protected by `IsShopManagerOrOwner`.
- Applied initial migration `audit.0001_initial`.
