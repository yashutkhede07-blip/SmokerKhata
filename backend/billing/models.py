from django.db import models
from django.conf import settings
from common.models import ShopScopedModel, UUIDModel, TimeStampedModel, SoftDeleteModel
from inventory.models import Item, ItemVariant
from ledgers.models import Customer

class PaymentMode(models.TextChoices):
    CASH = 'CASH', 'Cash'
    UPI = 'UPI', 'UPI'
    UDHAAR = 'UDHAAR', 'Udhaar'
    SPLIT = 'SPLIT', 'Split'


class BillStatus(models.TextChoices):
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Bill(ShopScopedModel):
    bill_number = models.CharField(max_length=100, db_index=True)
    device_id = models.CharField(max_length=50)
    local_sequence = models.PositiveIntegerField()
    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bills'
    )
    total_amount_paise = models.BigIntegerField()
    discount_paise = models.BigIntegerField(default=0)
    tax_paise = models.BigIntegerField(default=0)
    final_amount_paise = models.BigIntegerField()
    payment_mode = models.CharField(max_length=20, choices=PaymentMode.choices)
    cash_amount_paise = models.BigIntegerField(default=0)
    upi_amount_paise = models.BigIntegerField(default=0)
    udhaar_amount_paise = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=BillStatus.choices, default=BillStatus.COMPLETED)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bills_created'
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ('shop', 'bill_number')

    def __str__(self):
        return f"{self.bill_number} - ₹{self.final_amount_paise / 100:.2f} ({self.payment_mode})"


class BillItem(UUIDModel, TimeStampedModel):
    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='bill_items'
    )
    variant = models.ForeignKey(
        ItemVariant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bill_items'
    )
    item_name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_paise = models.BigIntegerField()
    subtotal_paise = models.BigIntegerField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.item_name} x {self.quantity} = ₹{self.subtotal_paise / 100:.2f}"


class DeviceSequenceTracker(ShopScopedModel):
    device_id = models.CharField(max_length=50)
    last_sequence = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('shop', 'device_id')

    def __str__(self):
        return f"{self.shop.prefix} - {self.device_id}: {self.last_sequence}"
