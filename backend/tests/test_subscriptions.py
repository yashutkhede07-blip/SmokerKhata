import json
import hmac
import hashlib
import pytest
from datetime import timedelta
from django.test import Client
from django.utils import timezone
from django.contrib.auth import get_user_model

from shops.models import Shop, ShopMember, Role
from subscriptions.models import (
    Plan, PlanInterval, Subscription, SubscriptionStatus,
    SubscriptionEvent, FeatureFlag
)
from subscriptions.services import SubscriptionService
from audit.models import AuditLogEntry

User = get_user_model()


@pytest.fixture
def sub_setup(db):
    user = User.objects.create_user(phone='9811003344', password='password123')
    shop = Shop.objects.create(name='Paan Palace Hub', prefix='PPH', owner=user)
    ShopMember.objects.create(shop=shop, user=user, role=Role.OWNER)

    # Create standard plans
    monthly = Plan.objects.create(
        name='Standard Monthly',
        interval=PlanInterval.MONTHLY,
        price_paise=49900,
        limits={'max_staff': 3, 'max_shops': 1}
    )
    FeatureFlag.objects.create(plan=monthly, name='EXCEL_EXPORT', is_enabled=True)
    FeatureFlag.objects.create(plan=monthly, name='WHATSAPP_ALERTS', is_enabled=True)

    yearly = Plan.objects.create(
        name='Standard Yearly',
        interval=PlanInterval.YEARLY,
        price_paise=499900,
        limits={'max_staff': 5, 'max_shops': 2}
    )

    return {
        'owner': user,
        'shop': shop,
        'monthly_plan': monthly,
        'yearly_plan': yearly
    }


@pytest.mark.django_db
def test_trial_auto_provision_and_expiry(sub_setup):
    """
    SUBS-01, SUBS-07, SUBS-08: 14-day trial auto-assignment and write access logic.
    """
    shop = sub_setup['shop']
    sub = SubscriptionService.create_trial_subscription(shop)

    assert sub.status == SubscriptionStatus.TRIAL
    assert (sub.trial_end - sub.trial_start).days == 14
    assert sub.is_write_allowed() is True

    # Simulate expired trial within 5-day grace period
    sub.trial_end = timezone.now() - timedelta(days=2)
    sub.grace_end = timezone.now() + timedelta(days=3)
    sub.status = SubscriptionStatus.GRACE
    assert sub.is_write_allowed() is True

    # Simulate expired past grace period (read-only mode)
    sub.trial_end = timezone.now() - timedelta(days=10)
    sub.grace_end = timezone.now() - timedelta(days=5)
    sub.status = SubscriptionStatus.EXPIRED
    assert sub.is_write_allowed() is False


@pytest.mark.django_db
def test_admin_trial_extension_audit_log(sub_setup):
    """
    ADMN-02: Admin manual trial extension records an audit log entry with reason.
    """
    shop = sub_setup['shop']
    admin_user = sub_setup['owner']
    sub = SubscriptionService.create_trial_subscription(shop)
    original_end = sub.trial_end

    SubscriptionService.extend_trial(
        subscription=sub,
        extra_days=7,
        admin_user=admin_user,
        reason='Customer requested trial extension'
    )
    sub.refresh_from_db()
    assert (sub.trial_end - original_end).days == 7

    audit = AuditLogEntry.objects.filter(shop=shop, model_name='Subscription').first()
    assert audit is not None
    assert 'Customer requested trial extension' in audit.notes
    assert audit.user == admin_user


@pytest.mark.django_db
def test_razorpay_webhook_idempotency(sub_setup):
    """
    SUBS-05: Razorpay webhook verification and idempotent deduplication.
    """
    shop = sub_setup['shop']
    sub = SubscriptionService.create_trial_subscription(shop)
    sub.razorpay_subscription_id = 'sub_Rzp123456'
    sub.save()

    payload = {
        'event': 'subscription.charged',
        'event_id': 'evt_998877',
        'payload': {
            'subscription': {
                'entity': {
                    'id': 'sub_Rzp123456'
                }
            }
        }
    }

    raw_body = json.dumps(payload)
    secret = 'test_secret'
    sig = hmac.new(secret.encode('utf-8'), raw_body.encode('utf-8'), hashlib.sha256).hexdigest()

    client = Client()

    # First call
    resp1 = client.post(
        '/api/subscriptions/webhook/razorpay/',
        data=raw_body,
        content_type='application/json',
        HTTP_X_RAZORPAY_SIGNATURE=sig
    )
    assert resp1.status_code == 200
    assert resp1.json()['processed'] is True

    sub.refresh_from_db()
    assert sub.status == SubscriptionStatus.ACTIVE

    # Second call (replay) with same payload & event ID
    resp2 = client.post(
        '/api/subscriptions/webhook/razorpay/',
        data=raw_body,
        content_type='application/json',
        HTTP_X_RAZORPAY_SIGNATURE=sig
    )
    assert resp2.status_code == 200
    assert resp2.json()['processed'] is False  # Acknowledged without duplicate processing


@pytest.mark.django_db
def test_play_billing_verification_and_proration(sub_setup):
    """
    SUBS-06, SUBS-10: Play Billing confirmation and plan proration calculation.
    """
    shop = sub_setup['shop']
    monthly = sub_setup['monthly_plan']
    yearly = sub_setup['yearly_plan']

    client = Client()
    client.force_login(sub_setup['owner'])

    resp = client.post(
        f'/api/subscriptions/play-billing/verify/?shop_id={shop.id}',
        data=json.dumps({
            'purchase_token': 'test_token_abc_123',
            'product_id': 'Standard Monthly'
        }),
        content_type='application/json'
    )
    assert resp.status_code == 200
    assert resp.json()['status'] == SubscriptionStatus.ACTIVE

    # Test proration upgrade preview to yearly
    sub = Subscription.objects.get(shop=shop)
    proration = SubscriptionService.calculate_proration(sub, yearly)
    assert proration['amount_due_paise'] < yearly.price_paise
    assert proration['credit_paise'] > 0
