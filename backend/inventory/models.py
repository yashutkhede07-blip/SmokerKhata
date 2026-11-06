from django.db import models
from django.conf import settings
from common.models import ShopScopedModel, UUIDModel, TimeStampedModel, SoftDeleteModel

class Category(ShopScopedModel):
    name = models.CharField(max_length=100)
    display_order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
        unique_together = ('shop', 'name')

    def __str__(self):
        return f"{self.name} ({self.shop.name})"


class Item(ShopScopedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    name = models.CharField(max_length=150)
    barcode = models.CharField(max_length=64, blank=True, db_index=True)
    selling_price_paise = models.BigIntegerField()
    cost_price_paise = models.BigIntegerField(default=0)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    is_quick_add = models.BooleanField(default=False)
    quick_add_order = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    unit = models.CharField(max_length=20, default='PCS')
    pieces_per_pack = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['name']
        unique_together = ('shop', 'name')

    def __str__(self):
        return f"{self.name} - ₹{self.selling_price_paise / 100:.2f}"

    def soft_delete(self):
        from django.utils import timezone
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])


class ItemVariant(ShopScopedModel):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    name = models.CharField(max_length=100)
    selling_price_paise = models.BigIntegerField(null=True, blank=True)
    cost_price_paise = models.BigIntegerField(null=True, blank=True)
    barcode = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ('item', 'name')

    def __str__(self):
        return f"{self.item.name} - {self.name}"

    @property
    def effective_selling_price_paise(self):
        if self.selling_price_paise is not None:
            return self.selling_price_paise
        return self.item.selling_price_paise

    @property
    def effective_cost_price_paise(self):
        if self.cost_price_paise is not None:
            return self.cost_price_paise
        return self.item.cost_price_paise


class StockMovementReason(models.TextChoices):
    PURCHASE = 'PURCHASE', 'Purchase Received'
    SALE = 'SALE', 'Sale'
    ADJUSTMENT_COUNT = 'ADJUSTMENT_COUNT', 'Inventory Count Adjustment'
    DAMAGE = 'DAMAGE', 'Damaged or Expired'
    THEFT = 'THEFT', 'Missing or Theft'
    RETURN = 'RETURN', 'Customer Return'
    INITIAL_STOCK = 'INITIAL_STOCK', 'Initial Stock Setup'


class StockLedgerEntry(UUIDModel, TimeStampedModel):
    """
    Immutable ledger of all stock quantity changes.
    Direct updates or deletions are strictly prohibited (STCK-03).
    """
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='stock_ledger_entries',
        db_index=True
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='stock_movements'
    )
    variant = models.ForeignKey(
        ItemVariant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='stock_movements'
    )
    quantity_delta = models.IntegerField()
    reason = models.CharField(max_length=30, choices=StockMovementReason.choices)
    unit_cost_paise = models.BigIntegerField(default=0)
    reference_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='stock_movements_recorded'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = "+" if self.quantity_delta > 0 else ""
        return f"{self.item.name} {sign}{self.quantity_delta} ({self.reason})"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("StockLedgerEntry is immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("StockLedgerEntry is immutable and cannot be deleted.")
