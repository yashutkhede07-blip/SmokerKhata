import pytest
from datetime import date
from accounts.models import User
from shops.models import Shop
from accounts.authentication import generate_tokens_for_user
from ledgers.models import Supplier, SupplierLedgerEntry, SupplierEntryType, PaymentMode

@pytest.fixture
def shop_setup(db):
    owner = User.objects.create(phone='9811100021')
    shop = Shop.objects.create(name='Paan Palace Wholesale', prefix='PPW', owner=owner)
    tokens = generate_tokens_for_user(owner)
    headers = {'HTTP_AUTHORIZATION': f'Bearer {tokens["access"]}'}
    return {'owner': owner, 'shop': shop, 'headers': headers}

@pytest.mark.django_db
def test_supplier_models(shop_setup):
    shop = shop_setup['shop']
    owner = shop_setup['owner']

    supplier = Supplier.objects.create(
        shop=shop,
        name='ITC Cigarettes Distributor',
        phone='9812345678',
        address='Transport Nagar, Kanpur',
        gstin='09AAACI1234A1Z5'
    )
    assert supplier.name == 'ITC Cigarettes Distributor'

    entry = SupplierLedgerEntry.objects.create(
        shop=shop,
        supplier=supplier,
        entry_type=SupplierEntryType.PURCHASE_BILL,
        amount_paise=1500000,
        bill_number='ITC-2026-99',
        bill_date=date.today(),
        created_by=owner
    )
    assert entry.amount_paise == 1500000
    assert str(entry).startswith('ITC Cigarettes Distributor +₹15000.00')

@pytest.mark.django_db
def test_supplier_ledger_flow(client, shop_setup):
    shop = shop_setup['shop']
    headers = shop_setup['headers']

    # 1. Create Supplier
    s_resp = client.post(
        f'/api/ledgers/suppliers/?shop_id={shop.id}',
        {
            'name': 'Hindustan Beverages Agency',
            'phone': '9988776655',
            'address': 'Warehouse Road'
        },
        format='json',
        **headers
    )
    assert s_resp.status_code == 201
    supp_id = s_resp.json()['id']

    # 2. Add purchase bill: ₹5000.00 (500000 paise)
    b_resp = client.post(
        f'/api/ledgers/suppliers/{supp_id}/entries/',
        {
            'entry_type': SupplierEntryType.PURCHASE_BILL,
            'amount_paise': 500000,
            'bill_number': 'INV-402',
            'bill_date': str(date.today()),
            'notes': '5 crates Thums Up, 3 crates Coke'
        },
        format='json',
        **headers
    )
    assert b_resp.status_code == 201

    # 3. Add payment made: ₹3000.00 (300000 paise) via Bank Transfer
    p_resp = client.post(
        f'/api/ledgers/suppliers/{supp_id}/entries/',
        {
            'entry_type': SupplierEntryType.PAYMENT_MADE,
            'amount_paise': 300000,
            'payment_mode': PaymentMode.BANK_TRANSFER,
            'notes': 'NEFT advance'
        },
        format='json',
        **headers
    )
    assert p_resp.status_code == 201

    # 4. Check supplier balance: 500000 - 300000 = 200000 paise
    s_detail = client.get(f'/api/ledgers/suppliers/{supp_id}/?shop_id={shop.id}', **headers)
    assert s_detail.status_code == 200
    assert s_detail.json()['balance_paise'] == 200000

    # 5. Check ledger endpoint running balance
    ledger_resp = client.get(f'/api/ledgers/suppliers/{supp_id}/ledger/', **headers)
    assert ledger_resp.status_code == 200
    entries = ledger_resp.json()
    assert len(entries) == 2
    assert entries[0]['running_balance_paise'] == 500000
    assert entries[1]['running_balance_paise'] == 200000
