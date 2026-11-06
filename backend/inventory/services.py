from django.db import transaction
from django.db.models import Sum
from inventory.models import Item, ItemVariant, StockLedgerEntry

class StockService:
    @staticmethod
    def get_current_stock(item_id, variant_id=None):
        qs = StockLedgerEntry.objects.filter(item_id=item_id)
        if variant_id:
            qs = qs.filter(variant_id=variant_id)
        res = qs.aggregate(total=Sum('quantity_delta'))['total']
        return res or 0

    @staticmethod
    @transaction.atomic
    def record_movement(shop, item, delta, reason, variant=None, unit_cost_paise=0, reference_id="", notes="", user=None):
        """
        Creates an immutable stock movement record.
        """
        return StockLedgerEntry.objects.create(
            shop=shop,
            item=item,
            variant=variant,
            quantity_delta=delta,
            reason=reason,
            unit_cost_paise=unit_cost_paise,
            reference_id=reference_id,
            notes=notes,
            created_by=user
        )
