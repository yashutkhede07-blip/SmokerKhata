import urllib.parse
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Q, Case, When, Value, IntegerField, F, Min
from rest_framework import serializers
from ledgers.models import (
    Customer, CustomerLedgerEntry, CustomerEntryType,
    Supplier, SupplierLedgerEntry, SupplierEntryType, PaymentMode
)

class CustomerLedgerEntrySerializer(serializers.ModelSerializer):
    created_by_phone = serializers.CharField(source='created_by.phone', read_only=True)

    class Meta:
        model = CustomerLedgerEntry
        fields = [
            'id', 'shop', 'customer', 'entry_type', 'amount_paise',
            'payment_mode', 'notes', 'reference_id', 'created_by',
            'created_by_phone', 'created_at'
        ]
        read_only_fields = ['id', 'shop', 'customer', 'created_by', 'created_at']


class CustomerSerializer(serializers.ModelSerializer):
    balance_paise = serializers.SerializerMethodField()
    oldest_unpaid_days = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'shop', 'name', 'phone', 'notes',
            'credit_limit_paise', 'balance_paise',
            'oldest_unpaid_days', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shop', 'created_at', 'updated_at']

    def get_balance_paise(self, obj):
        res = obj.ledger_entries.aggregate(
            credits=Sum('amount_paise', filter=Q(entry_type=CustomerEntryType.CREDIT_GIVEN)),
            payments=Sum('amount_paise', filter=Q(entry_type=CustomerEntryType.PAYMENT_RECEIVED))
        )
        credits = res['credits'] or 0
        payments = res['payments'] or 0
        return credits - payments

    def get_oldest_unpaid_days(self, obj):
        balance = self.get_balance_paise(obj)
        if balance <= 0:
            return 0
        oldest_entry = obj.ledger_entries.filter(entry_type=CustomerEntryType.CREDIT_GIVEN).order_by('created_at').first()
        if oldest_entry:
            return (timezone.now() - oldest_entry.created_at).days
        return 0


class SupplierLedgerEntrySerializer(serializers.ModelSerializer):
    created_by_phone = serializers.CharField(source='created_by.phone', read_only=True)

    class Meta:
        model = SupplierLedgerEntry
        fields = [
            'id', 'shop', 'supplier', 'entry_type', 'amount_paise',
            'bill_number', 'bill_date', 'payment_mode', 'notes',
            'created_by', 'created_by_phone', 'created_at'
        ]
        read_only_fields = ['id', 'shop', 'supplier', 'created_by', 'created_at']


class SupplierSerializer(serializers.ModelSerializer):
    balance_paise = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id', 'shop', 'name', 'phone', 'address',
            'gstin', 'balance_paise', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shop', 'created_at', 'updated_at']

    def get_balance_paise(self, obj):
        res = obj.ledger_entries.aggregate(
            bills=Sum('amount_paise', filter=Q(entry_type=SupplierEntryType.PURCHASE_BILL)),
            payments=Sum('amount_paise', filter=Q(entry_type=SupplierEntryType.PAYMENT_MADE))
        )
        bills = res['bills'] or 0
        payments = res['payments'] or 0
        return bills - payments
