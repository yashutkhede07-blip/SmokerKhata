import pytest
from datetime import timedelta
from django.utils import timezone
from accounts.models import User
from shops.models import Shop
from accounts.authentication import generate_tokens_for_user
from inventory.models import Item, StockMovementReason, StockLedgerEntry
from inventory.services import StockService

@pytest.fixture
def shop_setup(db):
    owner = User.objects.create(phone='9811100003')
    shop = Shop.objects.create(name='Verma Tea & Cigarettes', prefix='VTC', owner=owner)
    tokens = generate_tokens_for_user(owner)
    headers = {'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'}
    return {'owner': owner, 'shop': shop, 'headers': headers}

@pytest.mark.django_db
def test_low_stock_alert(client, shop_setup):
    headers = shop_setup['headers']
    shop = shop_setup['shop']
    owner = shop_setup['owner']

    # Item with stock 2, threshold 5 -> Should trigger low stock
    item_low = Item.objects.create(
        shop=shop,
        name='Four Square Special',
        selling_price_paise=12000,
        low_stock_threshold=5
    )
    StockService.record_movement(shop, item_low, 2, StockMovementReason.INITIAL_STOCK, user=owner)

    # Item with stock 20, threshold 5 -> Should NOT trigger
    item_ok = Item.objects.create(
        shop=shop,
        name='Wills Navy Cut',
        selling_price_paise=15000,
        low_stock_threshold=5
    )
    StockService.record_movement(shop, item_ok, 20, StockMovementReason.INITIAL_STOCK, user=owner)

    resp = client.get(f'/api/inventory/alerts/low-stock/?shop_id={shop.id}', **headers)
    assert resp.status_code == 200
    alerts = resp.json()
    assert len(alerts) == 1
    assert alerts[0]['id'] == str(item_low.id)
    assert alerts[0]['current_stock'] == 2

@pytest.mark.django_db
def test_dead_stock_report(client, shop_setup):
    headers = shop_setup['headers']
    shop = shop_setup['shop']
    owner = shop_setup['owner']

    # Item with no movement ever
    dead_item = Item.objects.create(
        shop=shop,
        name='Old Cigar Box',
        selling_price_paise=50000
    )

    # Active item with recent movement
    active_item = Item.objects.create(
        shop=shop,
        name='Fresh Biscuits',
        selling_price_paise=1000
    )
    StockService.record_movement(shop, active_item, 50, StockMovementReason.INITIAL_STOCK, user=owner)

    resp = client.get(f'/api/inventory/reports/dead-stock/?shop_id={shop.id}&days=30', **headers)
    assert resp.status_code == 200
    dead_stock = resp.json()
    dead_ids = [d['id'] for d in dead_stock]
    assert str(dead_item.id) in dead_ids
    assert str(active_item.id) not in dead_ids
