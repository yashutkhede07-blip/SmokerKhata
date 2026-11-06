import pytest
from accounts.models import User
from shops.models import Shop, Role, ShopMember
from accounts.authentication import generate_tokens_for_user
from inventory.models import Item, StockMovementReason

@pytest.fixture
def permissions_setup(db):
    owner = User.objects.create(phone='9811100004')
    cashier = User.objects.create(phone='9811100005')
    shop = Shop.objects.create(name='Paan Palace', prefix='PP01', owner=owner)

    ShopMember.objects.create(
        shop=shop,
        user=cashier,
        role=Role.CASHIER,
        can_view_reports=False
    )

    owner_tokens = generate_tokens_for_user(owner)
    cashier_tokens = generate_tokens_for_user(cashier)

    return {
        'shop': shop,
        'owner_headers': {'HTTP_AUTHORIZATION': f'Bearer {owner_tokens["access"]}'},
        'cashier_headers': {'HTTP_AUTHORIZATION': f'Bearer {cashier_tokens["access"]}'}
    }

@pytest.mark.django_db
def test_cashier_restrictions_on_inventory(client, permissions_setup):
    shop = permissions_setup['shop']
    owner_headers = permissions_setup['owner_headers']
    cashier_headers = permissions_setup['cashier_headers']

    # 1. Owner creates an item
    create_resp = client.post(
        f'/api/inventory/items/?shop_id={shop.id}',
        {
            'name': 'Marlboro Gold',
            'selling_price_paise': 36000
        },
        format='json',
        **owner_headers
    )
    assert create_resp.status_code == 201
    item_id = create_resp.json()['id']

    # 2. Cashier can READ item list
    read_resp = client.get(f'/api/inventory/items/?shop_id={shop.id}', **cashier_headers)
    assert read_resp.status_code == 200

    # 3. Cashier CANNOT create new item -> 403 Forbidden
    bad_create = client.post(
        f'/api/inventory/items/?shop_id={shop.id}',
        {
            'name': 'Banned Attempt Item',
            'selling_price_paise': 1000
        },
        format='json',
        **cashier_headers
    )
    assert bad_create.status_code == 403

    # 4. Cashier CANNOT adjust stock directly -> 403 Forbidden
    bad_adjust = client.post(
        '/api/inventory/stock/adjust/',
        {
            'item': item_id,
            'quantity_delta': 10,
            'reason': StockMovementReason.ADJUSTMENT_COUNT
        },
        format='json',
        **cashier_headers
    )
    assert bad_adjust.status_code == 403

    # 5. Cashier CANNOT delete/soft-delete an item -> 403 Forbidden
    bad_del = client.delete(f'/api/inventory/items/{item_id}/?shop_id={shop.id}', **cashier_headers)
    assert bad_del.status_code == 403
