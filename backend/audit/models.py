from django.db import models
from django.conf import settings
from common.models import UUIDModel, TimeStampedModel


class AuditAction(models.TextChoices):
    CREATE = 'CREATE', 'Create'
    UPDATE = 'UPDATE', 'Update'
    SOFT_DELETE = 'SOFT_DELETE', 'Soft Delete'
    CONFLICT_LOST = 'CONFLICT_LOST', 'Conflict Lost (Overwritten)'


class AuditLogEntry(UUIDModel, TimeStampedModel):
    """
    Immutable audit trail recording every change on critical business entities.
    AUDT-01, AUDT-02, AUDT-03, AUDT-04.
    """
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='audit_logs',
        db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_entries'
    )
    model_name = models.CharField(max_length=100, db_index=True)
    record_id = models.CharField(max_length=100, db_index=True)
    action = models.CharField(max_length=20, choices=AuditAction.choices)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shop', 'model_name']),
            models.Index(fields=['shop', 'created_at']),
        ]

    def __str__(self):
        user_str = self.user.phone if self.user else "System"
        return f"[{self.action}] {self.model_name}:{self.record_id} by {user_str}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("AuditLogEntry is immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("AuditLogEntry is immutable and cannot be deleted.")
