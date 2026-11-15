from django.db import transaction
from django.utils import timezone

from sync.models import SyncJournalEntry, ShopSyncSequence


class SyncJournalService:
    """
    Records entity mutations into the monotonic sync journal.
    Uses select_for_update on ShopSyncSequence to guarantee strictly
    increasing, gap-free sequence numbers per shop.
    """

    @staticmethod
    @transaction.atomic
    def record_change(shop, entity_type, entity_id, action, payload=None):
        """
        Atomically allocate next sequence number and write a journal entry.

        Args:
            shop: Shop instance
            entity_type: string model name (e.g. 'item', 'bill')
            entity_id: UUID of the affected record
            action: 'CREATE', 'UPDATE', or 'DELETE'
            payload: dict of the current entity state (for pull clients)

        Returns:
            SyncJournalEntry instance
        """
        seq_tracker, _ = ShopSyncSequence.objects.select_for_update().get_or_create(
            shop=shop,
            defaults={'current_sequence': 0},
        )
        seq_tracker.current_sequence += 1
        seq_tracker.save(update_fields=['current_sequence'])

        entry = SyncJournalEntry.objects.create(
            shop=shop,
            sequence=seq_tracker.current_sequence,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            payload=payload or {},
        )
        return entry
