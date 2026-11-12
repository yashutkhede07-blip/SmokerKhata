from django.db import models
from django.conf import settings
from django.utils import timezone
from common.models import ShopScopedModel, UUIDModel, TimeStampedModel, SoftDeleteModel

class Customer(ShopScopedModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    notes = models.TextField(blank=True)
    credit_limit_paise = models.BigIntegerField(default=0)  # 0 = unlimited

    class Meta:
        ordering = ['name']
        unique_together = ('shop', 'name')

    def __str__(self):
        return f"{self.name} ({self.phone or 'No phone'})"


class CustomerEntryType(models.TextChoices):
    CREDIT_GIVEN = 'CREDIT_GIVEN', 'Credit Given (Udhaar)'
    PAYMENT_RECEIVED = 'PAYMENT_RECEIVED', 'Payment Received (Jama)'


class PaymentMode(models.TextChoices):
    CASH = 'CASH', 'Cash'
    UPI = 'UPI', 'UPI'
    BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
    CHEQUE = 'CHEQUE', 'Cheque'
    OTHER = 'OTHER', 'Other'


class CustomerLedgerEntry(UUIDModel, TimeStampedModel):
    """
    Immutable financial ledger entry for customer credit and payments.
    Direct updates or deletions are strictly prohibited.
    """
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='customer_ledger_entries',
        db_index=True
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='ledger_entries'
    )
    entry_type = models.CharField(max_length=20, choices=CustomerEntryType.choices)
    amount_paise = models.BigIntegerField()
    payment_mode = models.CharField(
        max_length=20,
        choices=PaymentMode.choices,
        blank=True
    )
    notes = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_ledger_entries_recorded'
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sign = "+" if self.entry_type == CustomerEntryType.CREDIT_GIVEN else "-"
        return f"{self.customer.name} {sign}₹{self.amount_paise / 100:.2f} ({self.entry_type})"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("CustomerLedgerEntry is immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("CustomerLedgerEntry is immutable and cannot be deleted.")


class Supplier(ShopScopedModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']
        unique_together = ('shop', 'name')

    def __str__(self):
        return f"{self.name} ({self.phone or 'No phone'})"


class SupplierEntryType(models.TextChoices):
    PURCHASE_BILL = 'PURCHASE_BILL', 'Purchase Bill Received'
    PAYMENT_MADE = 'PAYMENT_MADE', 'Payment Made to Supplier'


def get_today():
    return timezone.now().date()


class SupplierLedgerEntry(UUIDModel, TimeStampedModel):
    """
    Immutable financial ledger entry for supplier bills and payments.
    Direct updates or deletions are strictly prohibited.
    """
    shop = models.ForeignKey(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='supplier_ledger_entries',
        db_index=True
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='ledger_entries'
    )
    entry_type = models.CharField(max_length=20, choices=SupplierEntryType.choices)
    amount_paise = models.BigIntegerField()
    bill_number = models.CharField(max_length=100, blank=True)
    bill_date = models.DateField(default=get_today)
    payment_mode = models.CharField(
        max_length=20,
        choices=PaymentMode.choices,
        blank=True
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='supplier_ledger_entries_recorded'
    )

    class Meta:
        ordering = ['bill_date', 'created_at']

    def __str__(self):
        sign = "+" if self.entry_type == SupplierEntryType.PURCHASE_BILL else "-"
        return f"{self.supplier.name} {sign}₹{self.amount_paise / 100:.2f} ({self.entry_type})"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("SupplierLedgerEntry is immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("SupplierLedgerEntry is immutable and cannot be deleted.")
