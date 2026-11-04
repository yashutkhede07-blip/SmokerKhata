from django.db import models
from django.conf import settings
from common.models import UUIDModel, TimeStampedModel, SoftDeleteModel

class Role(models.TextChoices):
    OWNER = 'OWNER', 'Owner'
    MANAGER = 'MANAGER', 'Manager'
    CASHIER = 'CASHIER', 'Cashier'

class Shop(UUIDModel, TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    prefix = models.CharField(max_length=10, db_index=True)
    address = models.TextField(blank=True)
    currency = models.CharField(max_length=10, default='INR')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_shops')

    def __str__(self):
        return f"{self.name} ({self.prefix})"

class ShopMember(UUIDModel, TimeStampedModel, SoftDeleteModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop_memberships')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CASHIER)
    can_edit_past_bills = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)

    class Meta:
        unique_together = ('shop', 'user')

    def __str__(self):
        return f"{self.user.phone} - {self.role} at {self.shop.name}"
