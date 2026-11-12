import pytest
from datetime import date
from accounts.models import User
from shops.models import Shop, Role, ShopMember
from accounts.authentication import generate_tokens_for_user
from inventory.models import Item
from billing.models import Bill, PaymentMode
from billing.services import BillingService
from cashbook.models import CashBookDay, CashBookEntry, CashEntryType

@pytest.fixture
def shop_setup(db):
    owner = User.objects.create(phone='9811100040')
    manager = User.objects.create(phone='9811100041')
    cashier = User.objects.create(phone='9811100042')
    shop = Shop.objects.create(name='Kolkata Chai Point', prefix='KCP', owner=owner)

    ShopMember.objects.create(shop=shop, user=manager, role=Role.MANAGER)
    ShopMember.objects.create(shop=shop, user=cashier, role=Role.CASHIER)

    owner_tokens = generate_tokens_for_user(owner)
    manager_tokens = generate_tokens_for_user(manager)
    cashier_tokens = generate_tokens_for_user(cashier)

    # Initial bill setup
    item = Item.objects.create(shop=shop, name='Special Chai', selling_price_paise=1500)

    return {
        'owner': owner,
        'manager': manager,
        'cashier': cashier,
        'shop': shop,
        'item': item,
        'owner_headers': {'HTTP_AUTHORIZATION': f'Bearer {owner_tokens["access"]}'},
        'manager_headers': {'HTTP_AUTHORIZATION': f'Bearer {manager_tokens["access"]}'},
        'cashier_headers': {'HTTP_AUTHORIZATION': f'Bearer {cashier_tokens["access"]}'}
    }

@pytest.mark.django_db
def test_cashbook_models(shop_setup):
    shop = shop_setup['shop']
    owner = shop_setup['owner']

    today = date.today()
    day = CashBookDay.objects.create(
        shop=shop,
        date=today,
        opening_cash_paise=50000  # ₹500.00
    )
    assert day.opening_cash_paise == 50000
    assert day.is_closed is False

    entry = CashBookEntry.objects.create(
        shop=shop,
        cashbook_day=day,
        entry_type=CashEntryType.CASH_OUT,
        amount_paise=12000,  # ₹120.00
        reason='Bought 2 bags of ice',
        created_by=owner
    )
    assert entry.amount_paise == 12000
    assert str(entry).startswith('-₹120.00')

@pytest.mark.django_db
def test_cashbook_closing_flow(client, shop_setup):
    shop = shop_setup['shop']
    manager_headers = shop_setup['manager_headers']
    cashier_headers = shop_setup['cashier_headers']
    owner = shop_setup['owner']
    item = shop_setup['item']

    # 1. Manager opens cash book with ₹1000.00 (100000 paise)
    open_resp = client.post(
        f'/api/cashbook/today/open/?shop_id={shop.id}',
        {'opening_cash_paise': 100000},
        content_type='application/json',
        **manager_headers
    )
    assert open_resp.status_code == 200
    assert open_resp.json()['opening_cash_paise'] == 100000

    # 2. POS Bill with Cash Payment: 2 Chais = ₹30.00 (3000 paise)
    BillingService.create_bill_atomic(
        shop=shop,
        user=owner,
        validated_data={
            'items': [{'item_id': str(item.id), 'quantity': 2}],
            'payment_mode': PaymentMode.CASH
        }
    )

    # 3. Ad-hoc cash in: Owner injects ₹200.00 (20000 paise)
    in_resp = client.post(
        f'/api/cashbook/today/entry/?shop_id={shop.id}',
        {
            'entry_type': CashEntryType.CASH_IN,
            'amount_paise': 20000,
            'reason': 'Change for 500 note'
        },
        content_type='application/json',
        **cashier_headers
    )
    assert in_resp.status_code == 201

    # 4. Ad-hoc cash out: Milk purchase ₹50.00 (5000 paise)
    out_resp = client.post(
        f'/api/cashbook/today/entry/?shop_id={shop.id}',
        {
            'entry_type': CashEntryType.CASH_OUT,
            'amount_paise': 5000,
            'reason': 'Amul milk packet'
        },
        content_type='application/json',
        **cashier_headers
    )
    assert out_resp.status_code == 201

    # 5. Check expected closing:
    # opening (100000) + cash_sales (3000) + cash_in (20000) - cash_out (5000) = 118000 paise
    today_resp = client.get(f'/api/cashbook/today/?shop_id={shop.id}', **cashier_headers)
    assert today_resp.status_code == 200
    data = today_resp.json()
    assert data['expected_closing_paise'] == 118000
    assert data['cash_sales_paise'] == 3000
    assert data['total_cash_in_paise'] == 20000
    assert data['total_cash_out_paise'] == 5000

    # 6. Cashier tries to close cash book -> 403 Forbidden
    bad_close = client.post(
        f'/api/cashbook/today/close/?shop_id={shop.id}',
        {'actual_closing_paise': 118000},
        content_type='application/json',
        **cashier_headers
    )
    assert bad_close.status_code == 403

    # 7. Manager closes cash book with discrepancy:
    # Actual cash counted: ₹1175.00 (117500 paise) -> Shortage of ₹5.00 (-500 paise)
    close_resp = client.post(
        f'/api/cashbook/today/close/?shop_id={shop.id}',
        {
            'actual_closing_paise': 117500,
            'notes': '5 rupee coin missing from drawer'
        },
        content_type='application/json',
        **manager_headers
    )
    assert close_resp.status_code == 200
    closed_data = close_resp.json()
    assert closed_data['is_closed'] is True
    assert closed_data['expected_closing_paise'] == 118000
    assert closed_data['actual_closing_paise'] == 117500
    assert closed_data['discrepancy_paise'] == -500
    assert closed_data['notes'] == '5 rupee coin missing from drawer'
