from datetime import date, datetime, time
from django.utils import timezone
from django.db.models import Sum, F, Count, Q
from billing.models import Bill, BillItem, BillStatus
from inventory.models import Item


def format_rupees(paise):
    """
    Format integer paise into Indian rupee string with lakh commas (e.g. ₹1,25,000.00).
    """
    rs = paise / 100.0
    is_neg = rs < 0
    rs = abs(rs)
    parts = f"{rs:.2f}".split('.')
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) > 3:
        last3 = integer_part[-3:]
        other = integer_part[:-3]
        res = ""
        while len(other) > 2:
            res = "," + other[-2:] + res
            other = other[:-2]
        formatted = other + res + "," + last3
    else:
        formatted = integer_part

    sign = "-" if is_neg else ""
    return f"{sign}₹{formatted}.{decimal_part}"


class ReportCalculationService:
    @staticmethod
    def get_sales_profit_summary(shop, date_from=None, date_to=None):
        bills_qs = Bill.objects.filter(shop=shop, status=BillStatus.COMPLETED)
        if date_from:
            bills_qs = bills_qs.filter(created_at__date__gte=date_from)
        if date_to:
            bills_qs = bills_qs.filter(created_at__date__lte=date_to)

        bill_ids = bills_qs.values_list('id', flat=True)

        items_qs = BillItem.objects.filter(bill_id__in=bill_ids)

        total_sales_paise = bills_qs.aggregate(total=Sum('final_amount_paise'))['total'] or 0
        total_bills = bills_qs.count()

        # Calculate cost of goods sold from bill items
        total_cost_paise = 0
        for b_item in items_qs.select_related('item', 'variant'):
            unit_cost = 0
            if b_item.variant and b_item.variant.effective_cost_price_paise:
                unit_cost = b_item.variant.effective_cost_price_paise
            elif b_item.item and b_item.item.cost_price_paise:
                unit_cost = b_item.item.cost_price_paise
            total_cost_paise += unit_cost * b_item.quantity

        gross_profit_paise = total_sales_paise - total_cost_paise
        margin_percentage = (gross_profit_paise / total_sales_paise * 100) if total_sales_paise > 0 else 0.0

        return {
            'date_from': str(date_from) if date_from else None,
            'date_to': str(date_to) if date_to else None,
            'total_bills': total_bills,
            'total_sales_paise': total_sales_paise,
            'total_cost_paise': total_cost_paise,
            'gross_profit_paise': gross_profit_paise,
            'margin_percentage': round(margin_percentage, 2),
            'formatted_sales': format_rupees(total_sales_paise),
            'formatted_cost': format_rupees(total_cost_paise),
            'formatted_gross_profit': format_rupees(gross_profit_paise),
        }

    @staticmethod
    def get_top_selling_items(shop, date_from=None, date_to=None, limit=10):
        bills_qs = Bill.objects.filter(shop=shop, status=BillStatus.COMPLETED)
        if date_from:
            bills_qs = bills_qs.filter(created_at__date__gte=date_from)
        if date_to:
            bills_qs = bills_qs.filter(created_at__date__lte=date_to)

        bill_ids = bills_qs.values_list('id', flat=True)

        items_agg = (
            BillItem.objects.filter(bill_id__in=bill_ids)
            .values('item_name')
            .annotate(
                total_qty=Sum('quantity'),
                total_revenue_paise=Sum('subtotal_paise')
            )
            .order_by('-total_qty')[:limit]
        )

        results = []
        for row in items_agg:
            results.append({
                'item_name': row['item_name'],
                'total_quantity': row['total_qty'],
                'total_revenue_paise': row['total_revenue_paise'],
                'formatted_revenue': format_rupees(row['total_revenue_paise']),
            })
        return results

    @staticmethod
    def get_item_margins(shop):
        items = Item.objects.filter(shop=shop, is_active=True).select_related('category')
        results = []
        for it in items:
            margin_paise = it.selling_price_paise - it.cost_price_paise
            margin_pct = (margin_paise / it.selling_price_paise * 100) if it.selling_price_paise > 0 else 0.0
            results.append({
                'item_id': str(it.id),
                'item_name': it.name,
                'category_name': it.category.name if it.category else 'Uncategorized',
                'selling_price_paise': it.selling_price_paise,
                'cost_price_paise': it.cost_price_paise,
                'margin_paise': margin_paise,
                'margin_percentage': round(margin_pct, 2),
                'formatted_selling_price': format_rupees(it.selling_price_paise),
                'formatted_cost_price': format_rupees(it.cost_price_paise),
                'formatted_margin': format_rupees(margin_paise),
            })
        return results
