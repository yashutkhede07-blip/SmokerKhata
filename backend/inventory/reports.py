from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Max
from inventory.models import Item, StockLedgerEntry

class InventoryReportService:
    @staticmethod
    def get_low_stock_items(shop_id):
        """
        Returns active items where the current stock is <= low_stock_threshold.
        """
        items = Item.objects.filter(shop_id=shop_id, is_active=True).annotate(
            calculated_stock=Sum('stock_movements__quantity_delta')
        )
        low_stock = []
        for item in items:
            stock = item.calculated_stock or 0
            if stock <= item.low_stock_threshold:
                low_stock.append({
                    'id': str(item.id),
                    'name': item.name,
                    'current_stock': stock,
                    'low_stock_threshold': item.low_stock_threshold,
                    'unit': item.unit,
                    'selling_price_paise': item.selling_price_paise,
                    'is_active': item.is_active
                })
        return low_stock

    @staticmethod
    def get_dead_stock_items(shop_id, days=30):
        """
        Returns items with zero movement/sales in the last N days.
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        items = Item.objects.filter(shop_id=shop_id, is_active=True).annotate(
            last_activity=Max('stock_movements__created_at'),
            current_stock=Sum('stock_movements__quantity_delta')
        )
        dead_stock = []
        for item in items:
            last = item.last_activity
            if last is None or last < cutoff_date:
                dead_stock.append({
                    'id': str(item.id),
                    'name': item.name,
                    'current_stock': item.current_stock or 0,
                    'last_movement': last.isoformat() if last else None,
                    'days_inactive': (timezone.now() - last).days if last else None,
                    'unit': item.unit
                })
        return dead_stock
