from django.db import models
from django.conf import settings
from common.models import UUIDModel, TimeStampedModel


class PlanInterval(models.TextChoices):
    MONTHLY = 'MONTHLY', 'Monthly'
    QUARTERLY = 'QUARTERLY', 'Quarterly'
    YEARLY = 'YEARLY', 'Yearly'


class SubscriptionStatus(models.TextChoices):
    TRIAL = 'TRIAL', 'Trial'
    ACTIVE = 'ACTIVE', 'Active'
    GRACE = 'GRACE', 'Grace Period'
    EXPIRED = 'EXPIRED', 'Expired (Read Only)'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Plan(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    interval = models.CharField(max_length=20, choices=PlanInterval.choices, default=PlanInterval.MONTHLY)
    price_paise = models.BigIntegerField()
    limits = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['price_paise']

    def __str__(self):
        return f"{self.name} ({self.interval}) - ₹{self.price_paise / 100:.2f}"


class FeatureFlag(UUIDModel, TimeStampedModel):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='feature_flags')
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('plan', 'name')

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"{self.name} for {self.plan.name}: {status}"


class Subscription(UUIDModel, TimeStampedModel):
    shop = models.OneToOneField(
        'shops.Shop',
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        Plan,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subscriptions'
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIAL
    )
    trial_start = models.DateTimeField()
    trial_end = models.DateTimeField()
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    grace_end = models.DateTimeField(null=True, blank=True)
    razorpay_subscription_id = models.CharField(max_length=100, blank=True)
    play_billing_purchase_token = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shop.name} - {self.status} ({self.plan.name if self.plan else 'Trial'})"

    def is_write_allowed(self):
        """
        SUBS-07, SUBS-08: Write is allowed during Trial, Active, and Grace periods.
        Blocked once in EXPIRED read-only status.
        """
        from django.utils import timezone
        now = timezone.now()

        if self.status == SubscriptionStatus.ACTIVE:
            if self.current_period_end and now > self.current_period_end:
                if self.grace_end and now <= self.grace_end:
                    return True  # Within grace period
                return False
            return True

        if self.status == SubscriptionStatus.TRIAL:
            if now <= self.trial_end:
                return True
            if self.grace_end and now <= self.grace_end:
                return True
            return False

        if self.status == SubscriptionStatus.GRACE:
            if self.grace_end and now <= self.grace_end:
                return True
            return False

        return False


class SubscriptionEvent(UUIDModel, TimeStampedModel):
    """
    Raw webhook / billing event log for idempotency (SUBS-05).
    """
    event_id = models.CharField(max_length=150, unique=True, db_index=True)
    provider = models.CharField(max_length=50, default='RAZORPAY')
    raw_payload = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "Processed" if self.processed else "Pending"
        return f"{self.provider} Event {self.event_id} - {status}"
