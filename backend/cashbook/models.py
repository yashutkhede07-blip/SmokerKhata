from django.db import models
from django.conf import settings
from common.models import ShopScopedModel, UUIDModel, TimeStampedModel

class CashBookDay(ShopScopedModel):
    date = models.DateField(db_index=True)
    opening_cash_paise = models.BigIntegerField(default=0)
    expected_closing_paise = models.BigIntegerField(default=0)
    actual_closing_paise = models.BigIntegerField(null=True, blank=True)
    discrepancy_paise = models.BigIntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cashbook_days_closed'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('shop', 'date')

    def __str__(self):
        status = "Closed" if self.is_closed else "Open"
        return f"{self.shop.name} - {self.date} ({status})"


class CashEntryType(models.TextChoices):
    CASH_IN = 'CASH_IN', 'Cash In (Deposit)'
    CASH_OUT = 'CASH_OUT', 'Cash Out (Expense/Withdrawal)'


class CashBookEntry(ShopScopedModel):
    cashbook_day = models.ForeignKey(
        CashBookDay,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    entry_type = models.CharField(max_length=20, choices=CashEntryType.choices)
    amount_paise = models.BigIntegerField()
    reason = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cashbook_entries_created'
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sign = "+" if self.entry_type == CashEntryType.CASH_IN else "-"
        return f"{sign}₹{self.amount_paise / 100:.2f} ({self.reason})"
