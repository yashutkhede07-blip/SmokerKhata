from django.db import models
from django.conf import settings
from common.models import UUIDModel, TimeStampedModel


class SyncActionType(models.TextChoices):
    CREATE = 'CREATE', 'Create'
    UPDATE = 'UPDATE', 'Update'
    DELETE = 'DELETE', 'Delete'


class SyncOperationStatus(models.TextChoices):
    PROCESSED = 'PROCESSED', 'Processed'
    FAILED = 'FAILED', 'Failed'
    REJECTED = 'REJECTED', 'Rejected'


class SyncOperation(UUIDModel, TimeStampedModel):
    """
    Tracks each client outbox operation by (shop, idempotency_key).
    Ensures replaying the same key never creates duplicate records.
    """
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='sync_operations',
        db_index=True,
    )
    idempotency_key = models.CharField(max_length=255, db_index=True)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    action = models.CharField(max_length=10, choices=SyncActionType.choices)
    status = models.CharField(
        max_length=10,
        choices=SyncOperationStatus.choices,
        default=SyncOperationStatus.PROCESSED,
    )
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shop', 'idempotency_key')
        ordering = ['-created_at']

    def __str__(self):
        return f"SyncOp({self.idempotency_key}) {self.entity_type}:{self.action} [{self.status}]"


class SyncJournalEntry(models.Model):
    """
    Monotonic shop-scoped change feed. Every mutation on a syncable entity
    records an entry here with a strictly increasing sequence number.
    Clients pull changes via cursor = last-seen sequence.
    """
    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='sync_journal_entries',
        db_index=True,
    )
    sequence = models.BigIntegerField(db_index=True)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    action = models.CharField(max_length=10, choices=SyncActionType.choices)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shop', 'sequence')
        ordering = ['sequence']
        indexes = [
            models.Index(fields=['shop', 'sequence']),
        ]

    def __str__(self):
        return f"Journal(#{self.sequence}) {self.entity_type}:{self.entity_id} [{self.action}]"


class ShopSyncSequence(models.Model):
    """
    Thread-safe monotonic sequence allocator per shop.
    Always access via select_for_update() to prevent races.
    """
    shop = models.OneToOneField(
        'shops.Shop',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='sync_sequence',
    )
    current_sequence = models.BigIntegerField(default=0)

    def __str__(self):
        return f"SyncSeq({self.shop.name}): {self.current_sequence}"
