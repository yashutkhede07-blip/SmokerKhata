import pytest
from datetime import timedelta
from django.utils import timezone
from accounts.models import User
from shops.models import Shop, Role, ShopMember
from accounts.authentication import generate_tokens_for_user
from ledgers.models import Customer, CustomerLedgerEntry, CustomerEntryType, PaymentMode

@pytest.fixture
def shop_setup(db):
    owner = User.objects.create(phone='9811100020')
    shop = Shop.objects.create(name='Bhole Chai & Paan', prefix='BCP', owner=owner)
    tokens = generate_tokens_for_user(owner)
    headers = {'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'}
    return {'owner': owner, 'shop': shop, 'headers': headers}

@pytest.mark.django_db
def test_customer_entries(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']

    # 1. Create customer
    c_resp = client.post(
        f'/api/ledgers/customers/?shop_id={shop.id}',
        {'name': 'Ramesh Kumar', 'phone': '9876543210', 'credit_limit_paise': 50000},
        format='json',
        **headers
    )
    assert c_resp.status_code == 201
    cust_id = c_resp.json()['id']

    # 2. Add credit entry (Udhaar given: ₹200.00 = 20000 paise)
    e1_resp = client.post(
        f'/api/ledgers/customers/{cust_id}/entries/',
        {
            'entry_type': CustomerEntryType.CREDIT_GIVEN,
            'amount_paise': 20000,
            'notes': '2 Gold Flake packs on credit'
        },
        format='json',
        **headers
    )
    assert e1_resp.status_code == 201

    # 3. Add payment entry (Payment received: ₹100.00 = 10000 paise via UPI)
    e2_resp = client.post(
        f'/api/ledgers/customers/{cust_id}/entries/',
        {
            'entry_type': CustomerEntryType.PAYMENT_RECEIVED,
            'amount_paise': 10000,
            'payment_mode': PaymentMode.UPI,
            'notes': 'Partial payment via PhonePe'
        },
        format='json',
        **headers
    )
    assert e2_resp.status_code == 201

    # 4. Check customer balance: should be 20000 - 10000 = 10000 paise
    cust_detail = client.get(f'/api/ledgers/customers/{cust_id}/?shop_id={shop.id}', **headers)
    assert cust_detail.status_code == 200
    assert cust_detail.json()['balance_paise'] == 10000

@pytest.mark.django_db
def test_customer_sorting(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']
    owner = shop_setup['owner']

    # Create 3 customers with different balances
    c1 = Customer.objects.create(shop=shop, name='Amit')
    c2 = Customer.objects.create(shop=shop, name='Bikas')
    c3 = Customer.objects.create(shop=shop, name='Chandan')

    CustomerLedgerEntry.objects.create(shop=shop, customer=c1, entry_type=CustomerEntryType.CREDIT_GIVEN, amount_paise=5000, created_by=owner)
    CustomerLedgerEntry.objects.create(shop=shop, customer=c2, entry_type=CustomerEntryType.CREDIT_GIVEN, amount_paise=25000, created_by=owner)
    CustomerLedgerEntry.objects.create(shop=shop, customer=c3, entry_type=CustomerEntryType.CREDIT_GIVEN, amount_paise=12000, created_by=owner)

    # Sort descending by balance
    resp = client.get(f'/api/ledgers/customers/?shop_id={shop.id}&ordering=-balance', **headers)
    assert resp.status_code == 200
    names = [c['name'] for c in resp.json()]
    assert names == ['Bikas', 'Chandan', 'Amit']

@pytest.mark.django_db
def test_whatsapp_link(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']
    owner = shop_setup['owner']

    c = Customer.objects.create(shop=shop, name='Vikram', phone='9876543210')
    CustomerLedgerEntry.objects.create(shop=shop, customer=c, entry_type=CustomerEntryType.CREDIT_GIVEN, amount_paise=15000, created_by=owner)

    resp = client.get(f'/api/ledgers/customers/{c.id}/whatsapp-link/', **headers)
    assert resp.status_code == 200
    data = resp.json()
    assert 'wa.me/919876543210' in data['whatsapp_url']
    assert '150.00' in data['message']

@pytest.mark.django_db
def test_aging_report(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']
    owner = shop_setup['owner']

    now = timezone.now()
    c_recent = Customer.objects.create(shop=shop, name='Recent Guy')
    CustomerLedgerEntry.objects.create(shop=shop, customer=c_recent, entry_type=CustomerEntryType.CREDIT_GIVEN, amount_paise=5000, created_by=owner)

    c_old = Customer.objects.create(shop=shop, name='Old Debt Guy')
    old_entry = CustomerLedgerEntry.objects.create(shop=shop, customer=c_old, entry_type=CustomerEntryType.CREDIT_GIVEN, amount_paise=8000, created_by=owner)
    # Manually update created_at via update() query (bypass immutability save check for test setup)
    CustomerLedgerEntry.objects.filter(id=old_entry.id).update(created_at=now - timedelta(days=45))

    resp = client.get(f'/api/ledgers/customers/reports/aging/?shop_id={shop.id}', **headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data['days_0_to_30']) == 1
    assert data['days_0_to_30'][0]['customer_name'] == 'Recent Guy'
    assert len(data['days_31_to_60']) == 1
    assert data['days_31_to_60'][0]['customer_name'] == 'Old Debt Guy'
    assert data['total_outstanding_paise'] == 13000
