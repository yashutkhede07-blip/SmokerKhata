from rest_framework import serializers
from cashbook.models import CashBookDay, CashBookEntry, CashEntryType

class CashBookEntrySerializer(serializers.ModelSerializer):
    created_by_phone = serializers.CharField(source='created_by.phone', read_only=True)

    class Meta:
        model = CashBookEntry
        fields = [
            'id', 'shop', 'cashbook_day', 'entry_type',
            'amount_paise', 'reason', 'created_by', 'created_by_phone',
            'created_at'
        ]
        read_only_fields = ['id', 'shop', 'cashbook_day', 'created_by', 'created_at']


class CashBookDaySerializer(serializers.ModelSerializer):
    entries = CashBookEntrySerializer(many=True, read_only=True)
    closed_by_phone = serializers.CharField(source='closed_by.phone', read_only=True)

    class Meta:
        model = CashBookDay
        fields = [
            'id', 'shop', 'date', 'opening_cash_paise',
            'expected_closing_paise', 'actual_closing_paise',
            'discrepancy_paise', 'is_closed', 'closed_at',
            'closed_by', 'closed_by_phone', 'notes', 'entries',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shop', 'created_at', 'updated_at']
