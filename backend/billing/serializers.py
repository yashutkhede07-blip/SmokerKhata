from rest_framework import serializers
from billing.models import Bill, BillItem, PaymentMode, BillStatus
from inventory.models import Item, ItemVariant

class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = [
            'id', 'item', 'variant', 'item_name', 'quantity',
            'unit_price_paise', 'subtotal_paise'
        ]
        read_only_fields = ['id', 'subtotal_paise']


class BillItemInputSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    unit_price_paise = serializers.IntegerField(required=False, min_value=0)


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_phone = serializers.CharField(source='created_by.phone', read_only=True)

    class Meta:
        model = Bill
        fields = [
            'id', 'shop', 'bill_number', 'device_id', 'local_sequence',
            'customer', 'customer_name', 'total_amount_paise', 'discount_paise',
            'tax_paise', 'final_amount_paise', 'payment_mode',
            'cash_amount_paise', 'upi_amount_paise', 'udhaar_amount_paise',
            'status', 'notes', 'created_by', 'created_by_phone',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shop', 'created_by', 'created_at', 'updated_at']


class CreateBillInputSerializer(serializers.Serializer):
    bill_number = serializers.CharField(max_length=100, required=False)
    device_id = serializers.CharField(max_length=50, default='COUNTER1')
    local_sequence = serializers.IntegerField(required=False)
    customer_id = serializers.UUIDField(required=False, allow_null=True)
    items = BillItemInputSerializer(many=True)
    discount_paise = serializers.IntegerField(default=0, min_value=0)
    tax_paise = serializers.IntegerField(default=0, min_value=0)
    payment_mode = serializers.ChoiceField(choices=PaymentMode.choices)
    cash_amount_paise = serializers.IntegerField(default=0, min_value=0)
    upi_amount_paise = serializers.IntegerField(default=0, min_value=0)
    udhaar_amount_paise = serializers.IntegerField(default=0, min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError("At least one item is required in the bill.")

        payment_mode = data.get('payment_mode')
        customer_id = data.get('customer_id')

        if payment_mode == PaymentMode.UDHAAR and not customer_id:
            raise serializers.ValidationError("Customer is mandatory for Udhaar payment.")

        if payment_mode == PaymentMode.SPLIT:
            udhaar = data.get('udhaar_amount_paise', 0)
            if udhaar > 0 and not customer_id:
                raise serializers.ValidationError("Customer is mandatory when Udhaar is included in Split payment.")

        return data
