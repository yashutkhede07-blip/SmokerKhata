import pytest
from accounts.models import User
from shops.models import Shop, Role, ShopMember
from accounts.authentication import generate_tokens_for_user
from inventory.models import Category, Item, ItemVariant

@pytest.fixture
def shop_setup(db):
    owner = User.objects.create(phone='9811100001')
    shop = Shop.objects.create(name='Gupta Paan & Smoke Corner', prefix='GPSC', owner=owner)
    tokens = generate_tokens_for_user(owner)
    headers = {'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'}
    return {'owner': owner, 'shop': shop, 'headers': headers}

@pytest.mark.django_db
def test_item_models(shop_setup):
    shop = shop_setup['shop']
    cat = Category.objects.create(shop=shop, name='Cigarettes', display_order=1)
    item = Item.objects.create(
        shop=shop,
        category=cat,
        name='Classic Regular 10s',
        barcode='8901234567890',
        selling_price_paise=17000,
        cost_price_paise=15000,
        pieces_per_pack=10
    )
    variant = ItemVariant.objects.create(
        shop=shop,
        item=item,
        name='Single Stick',
        selling_price_paise=1800,
        cost_price_paise=1500
    )
    assert item.selling_price_paise == 17000
    assert variant.effective_selling_price_paise == 1800
    assert str(item).startswith('Classic Regular 10s')

@pytest.mark.django_db
def test_item_crud(client, shop_setup):
    headers = shop_setup['headers']
    shop = shop_setup['shop']

    # 1. Create Category
    cat_resp = client.post(
        f'/api/inventory/categories/?shop_id={shop.id}',
        {'name': 'Cold Drinks', 'display_order': 2},
        format='json',
        **headers
    )
    assert cat_resp.status_code == 201
    cat_id = cat_resp.json()['id']

    # 2. Create Item
    item_resp = client.post(
        f'/api/inventory/items/?shop_id={shop.id}',
        {
            'category': cat_id,
            'name': 'Coca Cola 750ml',
            'selling_price_paise': 4500,
            'cost_price_paise': 3800,
            'low_stock_threshold': 10
        },
        format='json',
        **headers
    )
    assert item_resp.status_code == 201
    item_id = item_resp.json()['id']

    # 3. Read Items list with filter
    list_resp = client.get(f'/api/inventory/items/?shop_id={shop.id}&category={cat_id}', **headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]['name'] == 'Coca Cola 750ml'

@pytest.mark.django_db
def test_variants(client, shop_setup):
    headers = shop_setup['headers']
    shop = shop_setup['shop']
    item = Item.objects.create(
        shop=shop,
        name='Maggi Noodles',
        selling_price_paise=1500,
        cost_price_paise=1200
    )

    resp = client.post(
        f'/api/inventory/items/{item.id}/variants/',
        {'name': 'Atta Noodles', 'selling_price_paise': 2000},
        format='json',
        **headers
    )
    assert resp.status_code == 201
    assert resp.json()['effective_selling_price_paise'] == 2000

@pytest.mark.django_db
def test_soft_delete(client, shop_setup):
    headers = shop_setup['headers']
    shop = shop_setup['shop']
    item = Item.objects.create(
        shop=shop,
        name='Gold Flake Lights',
        selling_price_paise=18000
    )

    del_resp = client.delete(f'/api/inventory/items/{item.id}/?shop_id={shop.id}', **headers)
    assert del_resp.status_code == 204

    # Item still exists in DB but soft-deleted
    refreshed = Item.all_objects.get(id=item.id)
    assert refreshed.deleted_at is not None
    assert refreshed.is_active is False
    # Not returned in regular active query
    assert Item.objects.filter(id=item.id).count() == 0
