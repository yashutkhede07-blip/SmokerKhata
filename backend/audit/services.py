from audit.models import AuditLogEntry, AuditAction


class AuditService:
    @staticmethod
    def record_audit(shop, user, model_name, record_id, action, old_values=None, new_values=None, notes=''):
        """
        Record an immutable audit log entry.
        """
        return AuditLogEntry.objects.create(
            shop=shop,
            user=user if (user and user.is_authenticated) else None,
            model_name=model_name,
            record_id=str(record_id),
            action=action,
            old_values=old_values or {},
            new_values=new_values or {},
            notes=notes
        )
