import pytest
from accounts.models import User
from shops.models import Shop
from accounts.authentication import generate_tokens_for_user
from inventory.models import Item, StockMovementReason
from inventory.services import StockService
from ledgers.models import Customer
from billing.models import Bill, BillItem, PaymentMode

@pytest.fixture
def shop_setup(db):
    owner = User.objects.create(phone='9811100030')
    shop = Shop.objects.create(name='Gupta Corner POS', prefix='GCP', owner=owner)
    tokens = generate_tokens_for_user(owner)
    headers = {'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'}

    # Add items and initial stock
    item1 = Item.objects.create(shop=shop, name='Classic Milds', selling_price_paise=18000)
    item2 = Item.objects.create(shop=shop, name='Pepsi 500ml', selling_price_paise=4000)
    StockService.record_movement(shop, item1, 50, StockMovementReason.INITIAL_STOCK, user=owner)
    StockService.record_movement(shop, item2, 30, StockMovementReason.INITIAL_STOCK, user=owner)

    return {
        'owner': owner,
        'shop': shop,
        'headers': headers,
        'item1': item1,
        'item2': item2
    }

@pytest.mark.django_db
def test_bill_creation(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']
    item1 = shop_setup['item1']
    item2 = shop_setup['item2']

    # 1. Test next-sequence endpoint
    seq_resp = client.get(f'/api/billing/next-sequence/?shop_id={shop.id}', **headers)
    assert seq_resp.status_code == 200
    assert seq_resp.json()['bill_number'] == 'GCP-COUNTER1-000001'

    # 2. Create bill with multi-category items
    payload = {
        'items': [
            {'item_id': str(item1.id), 'quantity': 2},  # 2 * 18000 = 36000
            {'item_id': str(item2.id), 'quantity': 1}   # 1 * 4000 = 4000
        ],
        'discount_paise': 1000,
        'payment_mode': PaymentMode.CASH
    }
    # final = 40000 - 1000 = 39000 paise
    resp = client.post(f'/api/billing/bills/?shop_id={shop.id}', payload, content_type='application/json', **headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data['total_amount_paise'] == 40000
    assert data['discount_paise'] == 1000
    assert data['final_amount_paise'] == 39000
    assert data['cash_amount_paise'] == 39000
    assert len(data['items']) == 2

@pytest.mark.django_db
def test_payment_modes(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']
    item1 = shop_setup['item1']

    customer = Customer.objects.create(shop=shop, name='Raju Bhaiya', phone='9876500001')

    # SPLIT Payment: Total 36000 paise -> Cash: 20000, UPI: 10000, Udhaar: 6000
    payload = {
        'customer_id': str(customer.id),
        'items': [{'item_id': str(item1.id), 'quantity': 2}],
        'payment_mode': PaymentMode.SPLIT,
        'cash_amount_paise': 20000,
        'upi_amount_paise': 10000,
        'udhaar_amount_paise': 6000
    }
    resp = client.post(f'/api/billing/bills/?shop_id={shop.id}', payload, content_type='application/json', **headers)
    assert resp.status_code == 201
    assert resp.json()['payment_mode'] == 'SPLIT'

    # Check Udhaar automatically added to Customer's ledger balance
    c_resp = client.get(f'/api/ledgers/customers/{customer.id}/?shop_id={shop.id}', **headers)
    assert c_resp.status_code == 200
    assert c_resp.json()['balance_paise'] == 6000

@pytest.mark.django_db
def test_bill_whatsapp(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']
    item1 = shop_setup['item1']

    customer = Customer.objects.create(shop=shop, name='Sunil', phone='9988776655')
    payload = {
        'customer_id': str(customer.id),
        'items': [{'item_id': str(item1.id), 'quantity': 1}],
        'payment_mode': PaymentMode.UPI
    }
    create_resp = client.post(f'/api/billing/bills/?shop_id={shop.id}', payload, content_type='application/json', **headers)
    bill_id = create_resp.json()['id']

    wa_resp = client.get(f'/api/billing/bills/{bill_id}/whatsapp-link/', **headers)
    assert wa_resp.status_code == 200
    data = wa_resp.json()
    assert 'wa.me/919988776655' in data['whatsapp_url']
    assert 'Classic Milds' in data['message']

@pytest.mark.django_db
def test_atomic_stock_decrement(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']
    item1 = shop_setup['item1']

    # Initial stock was 50
    assert StockService.get_current_stock(item1.id) == 50

    # Sell 5
    payload = {
        'items': [{'item_id': str(item1.id), 'quantity': 5}],
        'payment_mode': PaymentMode.CASH
    }
    resp = client.post(f'/api/billing/bills/?shop_id={shop.id}', payload, content_type='application/json', **headers)
    assert resp.status_code == 201

    # Stock immediately decremented to 45
    assert StockService.get_current_stock(item1.id) == 45

@pytest.mark.django_db
def test_idempotent_bill_submission(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']
    item1 = shop_setup['item1']

    custom_bill_number = 'GCP-OFFLINE-999001'
    payload = {
        'bill_number': custom_bill_number,
        'local_sequence': 1,
        'items': [{'item_id': str(item1.id), 'quantity': 3}],
        'payment_mode': PaymentMode.CASH
    }

    # First submission
    stock_before = StockService.get_current_stock(item1.id)
    r1 = client.post(f'/api/billing/bills/?shop_id={shop.id}', payload, content_type='application/json', **headers)
    assert r1.status_code == 201
    assert StockService.get_current_stock(item1.id) == stock_before - 3

    # Replay same submission (e.g. offline queue retry)
    r2 = client.post(f'/api/billing/bills/?shop_id={shop.id}', payload, content_type='application/json', **headers)
    assert r2.status_code == 200
    assert r2.json()['bill_number'] == custom_bill_number
    # Stock must NOT be decremented twice!
    assert StockService.get_current_stock(item1.id) == stock_before - 3
    assert Bill.objects.filter(shop=shop, bill_number=custom_bill_number).count() == 1
