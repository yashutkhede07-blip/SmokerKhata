import pytest
from accounts.models import User
from shops.models import Shop, Role, ShopMember
from accounts.authentication import generate_tokens_for_user
from inventory.models import Item, StockLedgerEntry, StockMovementReason
from inventory.services import StockService

@pytest.fixture
def shop_setup(db):
    owner = User.objects.create(phone='9811100002')
    shop = Shop.objects.create(name='Sharmaji Cigarette & Cold Drinks', prefix='SCCD', owner=owner)
    tokens = generate_tokens_for_user(owner)
    headers = {'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'}
    return {'owner': owner, 'shop': shop, 'headers': headers}

@pytest.mark.django_db
def test_stock_ledger(shop_setup):
    shop = shop_setup['shop']
    owner = shop_setup['owner']
    item = Item.objects.create(
        shop=shop,
        name='Gold Flake Regular',
        selling_price_paise=18000,
        cost_price_paise=15000
    )

    # 1. Record stock purchase (+50)
    m1 = StockService.record_movement(
        shop=shop,
        item=item,
        delta=50,
        reason=StockMovementReason.PURCHASE,
        unit_cost_paise=15000,
        reference_id='BILL-1001',
        notes='Initial stock load',
        user=owner
    )
    assert m1.quantity_delta == 50
    assert StockService.get_current_stock(item.id) == 50

    # 2. Record sale (-5)
    m2 = StockService.record_movement(
        shop=shop,
        item=item,
        delta=-5,
        reason=StockMovementReason.SALE,
        reference_id='POS-001',
        user=owner
    )
    assert m2.quantity_delta == -5
    assert StockService.get_current_stock(item.id) == 45

    # 3. Test immutability: attempting to update should raise ValueError
    with pytest.raises(ValueError, match="immutable and cannot be updated"):
        m1.quantity_delta = 99
        m1.save()

    # 4. Test immutability: attempting to delete should raise ValueError
    with pytest.raises(ValueError, match="immutable and cannot be deleted"):
        m1.delete()

@pytest.mark.django_db
def test_stock_adjustment(client, shop_setup):
    headers = shop_setup['headers']
    shop = shop_setup['shop']
    item = Item.objects.create(
        shop=shop,
        name='Thums Up 250ml',
        selling_price_paise=2000
    )

    # Adjustment API (+30 bottles)
    adj_resp = client.post(
        '/api/inventory/stock/adjust/',
        {
            'item': str(item.id),
            'quantity_delta': 30,
            'reason': StockMovementReason.ADJUSTMENT_COUNT,
            'notes': 'Weekly audit adjustment'
        },
        format='json',
        **headers
    )
    assert adj_resp.status_code == 201
    assert adj_resp.json()['quantity_delta'] == 30
    assert StockService.get_current_stock(item.id) == 30

@pytest.mark.django_db
def test_current_stock_computation(client, shop_setup):
    headers = shop_setup['headers']
    shop = shop_setup['shop']
    owner = shop_setup['owner']
    item = Item.objects.create(
        shop=shop,
        name='Chips Salted',
        selling_price_paise=2000
    )

    # Direct movements
    StockService.record_movement(shop, item, 100, StockMovementReason.PURCHASE, user=owner)
    StockService.record_movement(shop, item, -15, StockMovementReason.SALE, user=owner)
    StockService.record_movement(shop, item, -2, StockMovementReason.DAMAGE, user=owner)

    # Check Item API returns aggregated current_stock = 83
    resp = client.get(f'/api/inventory/items/{item.id}/?shop_id={shop.id}', **headers)
    assert resp.status_code == 200
    assert resp.json()['current_stock'] == 83
