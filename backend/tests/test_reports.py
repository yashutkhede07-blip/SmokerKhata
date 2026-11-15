import io
import json
import pytest
from datetime import date, timedelta
from django.test import Client
from django.contrib.auth import get_user_model
from openpyxl import load_workbook

from shops.models import Shop, ShopMember, Role
from inventory.models import Category, Item
from billing.models import Bill, BillItem, PaymentMode, BillStatus
from audit.models import AuditLogEntry, AuditAction
from audit.services import AuditService
from reports.models import ReportRequest, ReportStatus, ReportFormat
from reports.services import ReportCalculationService

User = get_user_model()


@pytest.fixture
def shop_setup(db):
    user = User.objects.create_user(phone='9811002233', password='password123')
    shop = Shop.objects.create(name='Paan Shop Express', prefix='PSE', owner=user)
    ShopMember.objects.create(shop=shop, user=user, role=Role.OWNER)

    # Cashier with no reports view permission
    cashier = User.objects.create_user(phone='9811002244', password='password123')
    ShopMember.objects.create(shop=shop, user=cashier, role=Role.CASHIER, can_view_reports=False)

    # Create category & items
    cat = Category.objects.create(shop=shop, name='Tobacco')
    item1 = Item.objects.create(
        shop=shop, category=cat, name='Gold Flake Lights',
        selling_price_paise=1800, cost_price_paise=1400
    )
    item2 = Item.objects.create(
        shop=shop, category=cat, name='Classic Milds',
        selling_price_paise=2000, cost_price_paise=1500
    )

    # Create bills
    bill1 = Bill.objects.create(
        shop=shop, bill_number='PSE-C1-000001', device_id='C1', local_sequence=1,
        total_amount_paise=3800, final_amount_paise=3800,
        payment_mode=PaymentMode.CASH, cash_amount_paise=3800,
        status=BillStatus.COMPLETED, created_by=user
    )
    BillItem.objects.create(
        bill=bill1, item=item1, item_name=item1.name, quantity=1,
        unit_price_paise=1800, subtotal_paise=1800
    )
    BillItem.objects.create(
        bill=bill1, item=item2, item_name=item2.name, quantity=1,
        unit_price_paise=2000, subtotal_paise=2000
    )

    return {
        'owner': user,
        'cashier': cashier,
        'shop': shop,
        'item1': item1,
        'item2': item2,
        'bill1': bill1
    }


@pytest.mark.django_db
def test_audit_log_immutability(shop_setup):
    """
    AUDT-01, AUDT-03: Verify audit log entry creation and immutability.
    """
    shop = shop_setup['shop']
    user = shop_setup['owner']
    item = shop_setup['item1']

    entry = AuditService.record_audit(
        shop=shop,
        user=user,
        model_name='Item',
        record_id=item.id,
        action=AuditAction.UPDATE,
        old_values={'selling_price_paise': 1800},
        new_values={'selling_price_paise': 2000},
        notes='Price revision'
    )
    assert entry.id is not None
    assert entry.old_values['selling_price_paise'] == 1800
    assert entry.new_values['selling_price_paise'] == 2000

    # Immutability check: update and delete must fail
    with pytest.raises(ValueError, match="AuditLogEntry is immutable"):
        entry.notes = 'Changed note'
        entry.save()

    with pytest.raises(ValueError, match="AuditLogEntry is immutable"):
        entry.delete()


@pytest.mark.django_db
def test_reports_calculation_service(shop_setup):
    """
    REPT-01, REPT-02, REPT-03: Profit calculation, top items, item margins.
    """
    shop = shop_setup['shop']
    summary = ReportCalculationService.get_sales_profit_summary(shop)

    # Total Sales = 3800 paise (₹38.00)
    # Total Cost = 1400 + 1500 = 2900 paise (₹29.00)
    # Gross Profit = 3800 - 2900 = 900 paise (₹9.00)
    assert summary['total_sales_paise'] == 3800
    assert summary['total_cost_paise'] == 2900
    assert summary['gross_profit_paise'] == 900
    assert summary['formatted_sales'] == '₹38.00'
    assert summary['formatted_gross_profit'] == '₹9.00'

    top_items = ReportCalculationService.get_top_selling_items(shop)
    assert len(top_items) == 2
    assert top_items[0]['total_quantity'] == 1

    margins = ReportCalculationService.get_item_margins(shop)
    assert len(margins) == 2
    item1_margin = next(m for m in margins if m['item_name'] == 'Gold Flake Lights')
    assert item1_margin['margin_paise'] == 400


@pytest.mark.django_db
def test_reports_api_permissions(shop_setup):
    """
    AUTH-05: Cashier without report permission gets 403 Forbidden.
    Owner gets 200 OK.
    """
    shop = shop_setup['shop']
    cashier = shop_setup['cashier']
    owner = shop_setup['owner']

    client = Client()

    # Cashier attempt
    client.force_login(cashier)
    resp_cashier = client.get(f'/api/reports/sales-summary/?shop_id={shop.id}')
    assert resp_cashier.status_code == 403

    # Owner attempt
    client.force_login(owner)
    resp_owner = client.get(f'/api/reports/sales-summary/?shop_id={shop.id}')
    assert resp_owner.status_code == 200
    assert resp_owner.json()['total_sales_paise'] == 3800


@pytest.mark.django_db
def test_report_export_excel_and_pdf(shop_setup):
    """
    REPT-04, REPT-05, REPT-06: Export to Excel and PDF formats and download.
    """
    shop = shop_setup['shop']
    owner = shop_setup['owner']
    client = Client()
    client.force_login(owner)

    # Export Excel
    resp_xlsx = client.post(
        '/api/reports/export/',
        data=json.dumps({
            'shop_id': str(shop.id),
            'report_type': 'SALES_SUMMARY',
            'format': 'XLSX'
        }),
        content_type='application/json'
    )
    assert resp_xlsx.status_code == 200
    req_id_xlsx = resp_xlsx.json()['request_id']

    # Download Excel
    dl_xlsx = client.get(f'/api/reports/requests/{req_id_xlsx}/download/?shop_id={shop.id}')
    assert dl_xlsx.status_code == 200
    assert dl_xlsx['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    wb = load_workbook(io.BytesIO(b"".join(dl_xlsx.streaming_content)))
    assert "Sales Summary" in wb.sheetnames
    assert "Top Selling Items" in wb.sheetnames

    # Export PDF
    resp_pdf = client.post(
        '/api/reports/export/',
        data=json.dumps({
            'shop_id': str(shop.id),
            'report_type': 'SALES_SUMMARY',
            'format': 'PDF'
        }),
        content_type='application/json'
    )
    assert resp_pdf.status_code == 200
    req_id_pdf = resp_pdf.json()['request_id']

    # Download PDF
    dl_pdf = client.get(f'/api/reports/requests/{req_id_pdf}/download/?shop_id={shop.id}')
    assert dl_pdf.status_code == 200
    assert dl_pdf['Content-Type'] == 'application/pdf'
    pdf_bytes = b"".join(dl_pdf.streaming_content)
    assert pdf_bytes.startswith(b"%PDF")
