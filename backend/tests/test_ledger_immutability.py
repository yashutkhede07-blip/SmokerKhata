import pytest
from datetime import date
from accounts.models import User
from shops.models import Shop, Role, ShopMember
from accounts.authentication import generate_tokens_for_user
from ledgers.models import (
    Customer, CustomerLedgerEntry, CustomerEntryType,
    Supplier, SupplierLedgerEntry, SupplierEntryType
)

@pytest.fixture
def permissions_setup(db):
    owner = User.objects.create(phone='9811100022')
    cashier = User.objects.create(phone='9811100023')
    shop = Shop.objects.create(name='Paan Khata', prefix='PK01', owner=owner)

    ShopMember.objects.create(
        shop=shop,
        user=cashier,
        role=Role.CASHIER
    )

    owner_tokens = generate_tokens_for_user(owner)
    cashier_tokens = generate_tokens_for_user(cashier)

    return {
        'shop': shop,
        'owner': owner,
        'cashier': cashier,
        'owner_headers': {'HTTP_AUTHORIZATION': f'Bearer {owner_tokens["access"]}'},
        'cashier_headers': {'HTTP_AUTHORIZATION': f'Bearer {cashier_tokens["access"]}'}
    }

@pytest.mark.django_db
def test_customer_ledger_immutability(permissions_setup):
    shop = permissions_setup['shop']
    owner = permissions_setup['owner']
    customer = Customer.objects.create(shop=shop, name='Suresh')

    entry = CustomerLedgerEntry.objects.create(
        shop=shop,
        customer=customer,
        entry_type=CustomerEntryType.CREDIT_GIVEN,
        amount_paise=1000,
        created_by=owner
    )

    # 1. Update must raise ValueError
    with pytest.raises(ValueError, match="immutable and cannot be updated"):
        entry.amount_paise = 2000
        entry.save()

    # 2. Delete must raise ValueError
    with pytest.raises(ValueError, match="immutable and cannot be deleted"):
        entry.delete()

@pytest.mark.django_db
def test_supplier_ledger_immutability(permissions_setup):
    shop = permissions_setup['shop']
    owner = permissions_setup['owner']
    supplier = Supplier.objects.create(shop=shop, name='Biscuit Traders')

    entry = SupplierLedgerEntry.objects.create(
        shop=shop,
        supplier=supplier,
        entry_type=SupplierEntryType.PURCHASE_BILL,
        amount_paise=50000,
        created_by=owner
    )

    # 1. Update must raise ValueError
    with pytest.raises(ValueError, match="immutable and cannot be updated"):
        entry.amount_paise = 60000
        entry.save()

    # 2. Delete must raise ValueError
    with pytest.raises(ValueError, match="immutable and cannot be deleted"):
        entry.delete()

@pytest.mark.django_db
def test_cashier_role_permissions(client, permissions_setup):
    shop = permissions_setup['shop']
    owner_headers = permissions_setup['owner_headers']
    cashier_headers = permissions_setup['cashier_headers']

    # 1. Cashier CAN create customer and record credit/payments
    cust_resp = client.post(
        f'/api/ledgers/customers/?shop_id={shop.id}',
        {'name': 'Daily Customer'},
        format='json',
        **cashier_headers
    )
    assert cust_resp.status_code == 201
    cust_id = cust_resp.json()['id']

    entry_resp = client.post(
        f'/api/ledgers/customers/{cust_id}/entries/',
        {
            'entry_type': CustomerEntryType.CREDIT_GIVEN,
            'amount_paise': 500
        },
        format='json',
        **cashier_headers
    )
    assert entry_resp.status_code == 201

    # 2. Cashier CAN read suppliers
    supp = Supplier.objects.create(shop=shop, name='Cold Drink Wholesaler')
    s_read = client.get(f'/api/ledgers/suppliers/?shop_id={shop.id}', **cashier_headers)
    assert s_read.status_code == 200

    # 3. Cashier CANNOT create supplier -> 403 Forbidden
    bad_supp = client.post(
        f'/api/ledgers/suppliers/?shop_id={shop.id}',
        {'name': 'Unauthorized Supplier'},
        format='json',
        **cashier_headers
    )
    assert bad_supp.status_code == 403

    # 4. Cashier CANNOT edit or delete supplier -> 403 Forbidden
    bad_del = client.delete(f'/api/ledgers/suppliers/{supp.id}/?shop_id={shop.id}', **cashier_headers)
    assert bad_del.status_code == 403
