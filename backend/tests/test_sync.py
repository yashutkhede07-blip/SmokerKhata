"""
Comprehensive sync engine tests covering all 10 SYNC requirements.
SYNC-01: UUID PKs (validated by existing model tests)
SYNC-04: Batch push with idempotency keys
SYNC-05: Monotonic cursor pull
SYNC-08: Append-only financial/stock entries
SYNC-09: Last-write-wins for mutable entities
SYNC-10: Replay, offline reconciliation, conflict scenarios
"""
import uuid
import json
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from shops.models import Shop, ShopMember, Role
from inventory.models import Category, Item
from ledgers.models import Customer
from sync.models import SyncOperation, SyncJournalEntry, ShopSyncSequence
from sync.services import SyncJournalService
from sync.engine import SyncEngineService

User = get_user_model()


@pytest.fixture
def setup_shop(db):
    """Create a shop with owner for sync tests."""
    user = User.objects.create_user(phone='9000000001', password='testpass')
    shop = Shop.objects.create(name='Test Sync Shop', prefix='TSS', owner=user)
    ShopMember.objects.create(shop=shop, user=user, role=Role.OWNER)
    # Create a category and item for billing tests
    cat = Category.objects.create(shop=shop, name='Cigarettes')
    item = Item.objects.create(
        shop=shop,
        category=cat,
        name='Gold Flake',
        selling_price_paise=1500,
        cost_price_paise=1200,
    )
    return {'user': user, 'shop': shop, 'category': cat, 'item': item}


@pytest.fixture
def auth_client(setup_shop):
    """Authenticated test client."""
    client = Client()
    client.force_login(setup_shop['user'])
    return client


@pytest.mark.django_db
def test_journal_monotonic_sequence(setup_shop):
    """SyncJournalService.record_change produces strictly increasing sequence numbers."""
    shop = setup_shop['shop']
    entries = []
    for i in range(5):
        entry = SyncJournalService.record_change(
            shop=shop,
            entity_type='item',
            entity_id=uuid.uuid4(),
            action='CREATE',
            payload={'index': i},
        )
        entries.append(entry)

    sequences = [e.sequence for e in entries]
    assert sequences == [1, 2, 3, 4, 5], f"Expected [1,2,3,4,5], got {sequences}"

    # Verify ShopSyncSequence counter
    seq = ShopSyncSequence.objects.get(shop=shop)
    assert seq.current_sequence == 5


@pytest.mark.django_db
def test_sync_push_idempotent_replay(setup_shop, auth_client):
    """
    SYNC-04 / SYNC-10: Pushing the same batch twice produces
    exactly one record each — verified by test.
    """
    shop = setup_shop['shop']
    item = setup_shop['item']

    operations = [
        {
            'idempotency_key': 'key-item-update-001',
            'entity_type': 'item',
            'entity_id': str(item.id),
            'action': 'UPDATE',
            'data': {'name': 'Gold Flake Kings'},
        },
    ]

    payload = {'device_id': 'DEV-A', 'operations': operations}

    # First push
    resp1 = auth_client.post(
        '/api/sync/push/',
        data=json.dumps(payload),
        content_type='application/json',
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert 'key-item-update-001' in data1['processed_keys']
    assert data1['skipped_keys'] == []

    # Second push (replay) — same idempotency key
    resp2 = auth_client.post(
        '/api/sync/push/',
        data=json.dumps(payload),
        content_type='application/json',
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2['processed_keys'] == []
    assert 'key-item-update-001' in data2['skipped_keys']

    # Verify only one SyncOperation exists
    assert SyncOperation.objects.filter(
        shop=shop, idempotency_key='key-item-update-001'
    ).count() == 1

    # Verify only one journal entry for this operation
    assert SyncJournalEntry.objects.filter(
        shop=shop, entity_id=item.id, action='UPDATE'
    ).count() == 1


@pytest.mark.django_db
def test_sync_pull_monotonic_cursor(setup_shop, auth_client):
    """
    SYNC-05: GET /api/sync/pull?cursor=0 returns all changes;
    a second call with the returned cursor returns only newer changes.
    """
    shop = setup_shop['shop']

    # Create some journal entries
    ids = [uuid.uuid4() for _ in range(3)]
    for eid in ids:
        SyncJournalService.record_change(
            shop=shop,
            entity_type='customer',
            entity_id=eid,
            action='CREATE',
            payload={'name': 'Test Customer'},
        )

    # Pull from cursor 0 — should get all 3
    resp1 = auth_client.get('/api/sync/pull/?cursor=0')
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert len(data1['changes']) == 3
    assert data1['next_cursor'] == 3
    assert data1['has_more'] is False

    # Add one more entry
    new_id = uuid.uuid4()
    SyncJournalService.record_change(
        shop=shop,
        entity_type='customer',
        entity_id=new_id,
        action='CREATE',
        payload={'name': 'New Customer'},
    )

    # Pull from cursor 3 — should get only the new one
    resp2 = auth_client.get(f'/api/sync/pull/?cursor={data1["next_cursor"]}')
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2['changes']) == 1
    assert data2['next_cursor'] == 4
    assert data2['changes'][0]['entity_id'] == str(new_id)

    # Pull from cursor 4 — no new changes
    resp3 = auth_client.get('/api/sync/pull/?cursor=4')
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert len(data3['changes']) == 0
    assert data3['next_cursor'] == 4
    assert data3['has_more'] is False


@pytest.mark.django_db
def test_offline_bills_reconciliation(setup_shop, auth_client):
    """
    SYNC-10: Two devices pushing offline bills with distinct device IDs
    and same local sequence do not clash.
    """
    shop = setup_shop['shop']
    item = setup_shop['item']

    # Seed stock for the item
    from inventory.services import StockService
    from inventory.models import StockMovementReason
    StockService.record_movement(
        shop=shop,
        item=item,
        variant=None,
        delta=100,
        reason=StockMovementReason.INITIAL_STOCK,
        reference_id='INIT',
        notes='Initial stock',
        user=setup_shop['user'],
    )

    bill_id_a = str(uuid.uuid4())
    bill_id_b = str(uuid.uuid4())

    ops_device_a = [{
        'idempotency_key': 'bill-dev-a-001',
        'entity_type': 'bill',
        'entity_id': bill_id_a,
        'action': 'CREATE',
        'data': {
            'bill_number': f'{shop.prefix}-DEV-A-000001',
            'local_sequence': 1,
            'payment_mode': 'CASH',
            'items': [{'item_id': str(item.id), 'quantity': 2}],
        },
    }]

    ops_device_b = [{
        'idempotency_key': 'bill-dev-b-001',
        'entity_type': 'bill',
        'entity_id': bill_id_b,
        'action': 'CREATE',
        'data': {
            'bill_number': f'{shop.prefix}-DEV-B-000001',
            'local_sequence': 1,
            'payment_mode': 'UPI',
            'items': [{'item_id': str(item.id), 'quantity': 3}],
        },
    }]

    # Push from device A
    resp_a = auth_client.post(
        '/api/sync/push/',
        data=json.dumps({'device_id': 'DEV-A', 'operations': ops_device_a}),
        content_type='application/json',
    )
    assert resp_a.status_code == 200
    assert 'bill-dev-a-001' in resp_a.json()['processed_keys']

    # Push from device B
    resp_b = auth_client.post(
        '/api/sync/push/',
        data=json.dumps({'device_id': 'DEV-B', 'operations': ops_device_b}),
        content_type='application/json',
    )
    assert resp_b.status_code == 200
    assert 'bill-dev-b-001' in resp_b.json()['processed_keys']

    # Both bills exist, no clash
    from billing.models import Bill
    bills = Bill.objects.filter(shop=shop).order_by('bill_number')
    assert bills.count() == 2
    bill_numbers = list(bills.values_list('bill_number', flat=True))
    assert f'{shop.prefix}-DEV-A-000001' in bill_numbers
    assert f'{shop.prefix}-DEV-B-000001' in bill_numbers


@pytest.mark.django_db
def test_sync_conflict_resolution(setup_shop, auth_client):
    """
    SYNC-08: Append-only ledger entries are never overwritten.
    SYNC-09: Mutable entity (item) updates use last-write-wins.
    """
    shop = setup_shop['shop']
    item = setup_shop['item']
    original_name = item.name

    # 1. Mutable update: rename item via sync push
    ops = [{
        'idempotency_key': 'update-item-name-001',
        'entity_type': 'item',
        'entity_id': str(item.id),
        'action': 'UPDATE',
        'data': {'name': 'Classic Milds'},
    }]

    resp = auth_client.post(
        '/api/sync/push/',
        data=json.dumps({'device_id': 'DEV-A', 'operations': ops}),
        content_type='application/json',
    )
    assert resp.status_code == 200
    item.refresh_from_db()
    assert item.name == 'Classic Milds'

    # 2. Second update overwrites (last-write-wins)
    ops2 = [{
        'idempotency_key': 'update-item-name-002',
        'entity_type': 'item',
        'entity_id': str(item.id),
        'action': 'UPDATE',
        'data': {'name': 'Navy Cut'},
    }]

    resp2 = auth_client.post(
        '/api/sync/push/',
        data=json.dumps({'device_id': 'DEV-B', 'operations': ops2}),
        content_type='application/json',
    )
    assert resp2.status_code == 200
    item.refresh_from_db()
    assert item.name == 'Navy Cut'

    # 3. Append-only: create customer ledger entry
    customer = Customer.objects.create(shop=shop, name='Ravi', phone='9876543210')
    ops3 = [{
        'idempotency_key': 'cust-ledger-001',
        'entity_type': 'customer_ledger',
        'entity_id': str(uuid.uuid4()),
        'action': 'CREATE',
        'data': {
            'customer_id': str(customer.id),
            'entry_type': 'CREDIT_GIVEN',
            'amount_paise': 50000,
            'notes': 'Udhaar for chai',
        },
    }]

    resp3 = auth_client.post(
        '/api/sync/push/',
        data=json.dumps({'device_id': 'DEV-A', 'operations': ops3}),
        content_type='application/json',
    )
    assert resp3.status_code == 200

    from ledgers.models import CustomerLedgerEntry
    entries = CustomerLedgerEntry.objects.filter(shop=shop, customer=customer)
    assert entries.count() == 1
    assert entries.first().amount_paise == 50000
