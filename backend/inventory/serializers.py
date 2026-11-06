from django.db.models import Sum
from rest_framework import serializers
from inventory.models import Category, Item, ItemVariant, StockLedgerEntry, StockMovementReason

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'shop', 'name', 'display_order', 'icon', 'created_at', 'updated_at']
        read_only_fields = ['id', 'shop', 'created_at', 'updated_at']


class ItemVariantSerializer(serializers.ModelSerializer):
    effective_selling_price_paise = serializers.IntegerField(read_only=True)
    effective_cost_price_paise = serializers.IntegerField(read_only=True)
    current_stock = serializers.SerializerMethodField()

    class Meta:
        model = ItemVariant
        fields = [
            'id', 'shop', 'item', 'name', 'selling_price_paise',
            'cost_price_paise', 'barcode', 'is_active',
            'effective_selling_price_paise', 'effective_cost_price_paise',
            'current_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shop', 'item', 'created_at', 'updated_at']

    def get_current_stock(self, obj):
        res = obj.stock_movements.aggregate(total=Sum('quantity_delta'))['total']
        return res or 0


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    variants = ItemVariantSerializer(many=True, read_only=True)
    current_stock = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'shop', 'category', 'category_name', 'name', 'barcode',
            'selling_price_paise', 'cost_price_paise', 'gst_rate',
            'is_active', 'is_quick_add', 'quick_add_order',
            'low_stock_threshold', 'unit', 'pieces_per_pack',
            'variants', 'current_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shop', 'created_at', 'updated_at']

    def get_current_stock(self, obj):
        res = obj.stock_movements.aggregate(total=Sum('quantity_delta'))['total']
        return res or 0


class StockLedgerEntrySerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    created_by_phone = serializers.CharField(source='created_by.phone', read_only=True)

    class Meta:
        model = StockLedgerEntry
        fields = [
            'id', 'shop', 'item', 'item_name', 'variant', 'variant_name',
            'quantity_delta', 'reason', 'unit_cost_paise', 'reference_id',
            'notes', 'created_by', 'created_by_phone', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']


class StockAdjustmentSerializer(serializers.Serializer):
    item = serializers.UUIDField()
    variant = serializers.UUIDField(required=False, allow_null=True)
    quantity_delta = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=StockMovementReason.choices)
    unit_cost_paise = serializers.IntegerField(default=0, min_value=0)
    reference_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
