import urllib.parse
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, F, Value, IntegerField, Case, When
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from shops.models import Shop, ShopMember, Role
from ledgers.models import (
    Customer, CustomerLedgerEntry, CustomerEntryType,
    Supplier, SupplierLedgerEntry, SupplierEntryType
)
from ledgers.serializers import (
    CustomerSerializer, CustomerLedgerEntrySerializer,
    SupplierSerializer, SupplierLedgerEntrySerializer
)
from ledgers.permissions import IsLedgerStaffOrManager, IsSupplierManagerOrOwner

class ShopContextMixin:
    def get_shop(self):
        shop_id = self.request.query_params.get('shop_id') or self.request.data.get('shop')
        if not shop_id and hasattr(self, 'kwargs') and 'shop_id' in self.kwargs:
            shop_id = self.kwargs['shop_id']
        if not shop_id:
            member = ShopMember.objects.filter(user=self.request.user).first()
            if member:
                return member.shop
            return Shop.objects.filter(owner=self.request.user).first()
        return get_object_or_404(Shop, id=shop_id)

    def check_manager_or_owner(self, shop):
        if shop.owner == self.request.user:
            return True
        return ShopMember.objects.filter(
            shop=shop,
            user=self.request.user,
            role__in=[Role.OWNER, Role.MANAGER]
        ).exists()


class CustomerViewSet(ShopContextMixin, viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsLedgerStaffOrManager]

    def get_queryset(self):
        shop = self.get_shop()
        if not shop:
            return Customer.objects.none()

        qs = Customer.objects.filter(shop=shop)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search))

        ordering = self.request.query_params.get('ordering')
        if ordering in ['balance', '-balance']:
            # Annotate balance
            qs = qs.annotate(
                total_credit=Coalesce(Sum('ledger_entries__amount_paise', filter=Q(ledger_entries__entry_type=CustomerEntryType.CREDIT_GIVEN)), Value(0, output_field=IntegerField())),
                total_paid=Coalesce(Sum('ledger_entries__amount_paise', filter=Q(ledger_entries__entry_type=CustomerEntryType.PAYMENT_RECEIVED)), Value(0, output_field=IntegerField()))
            ).annotate(
                calculated_balance=F('total_credit') - F('total_paid')
            )
            if ordering == '-balance':
                qs = qs.order_by('-calculated_balance', 'name')
            else:
                qs = qs.order_by('calculated_balance', 'name')

        return qs

    def perform_create(self, serializer):
        shop = self.get_shop()
        serializer.save(shop=shop)

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=['get', 'post'], url_path='entries')
    def entries(self, request, pk=None):
        customer = self.get_object()
        if request.method == 'GET':
            qs = customer.ledger_entries.all().order_by('created_at')
            serializer = CustomerLedgerEntrySerializer(qs, many=True)
            return Response(serializer.data)

        # POST new ledger entry
        serializer = CustomerLedgerEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = serializer.save(
            shop=customer.shop,
            customer=customer,
            created_by=request.user
        )
        return Response(CustomerLedgerEntrySerializer(entry).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='whatsapp-link')
    def whatsapp_link(self, request, pk=None):
        customer = self.get_object()
        serializer = self.get_serializer(customer)
        balance = serializer.data['balance_paise']
        if not customer.phone:
            return Response({'error': 'Customer has no phone number on record.'}, status=status.HTTP_400_BAD_REQUEST)

        phone = customer.phone.strip().replace('+', '').replace('-', '')
        if len(phone) == 10:
            phone = f"91{phone}"

        amount_rs = f"{balance / 100:.2f}"
        msg = f"Namaste {customer.name}, aapka {customer.shop.name} par kul baki Rs {amount_rs} hai. Kripya bhugtan karein. Dhanyawad!"
        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/{phone}?text={encoded_msg}"

        return Response({
            'phone': phone,
            'balance_paise': balance,
            'message': msg,
            'whatsapp_url': wa_url
        })


class CustomerAgingReportView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, IsLedgerStaffOrManager]

    def get(self, request):
        shop = self.get_shop()
        if not shop:
            return Response([])

        customers = Customer.objects.filter(shop=shop)
        now = timezone.now()
        report = {
            'days_0_to_30': [],
            'days_31_to_60': [],
            'days_61_to_90': [],
            'days_90_plus': [],
            'total_outstanding_paise': 0
        }

        for cust in customers:
            serializer = CustomerSerializer(cust)
            balance = serializer.data['balance_paise']
            if balance > 0:
                report['total_outstanding_paise'] += balance
                oldest_days = serializer.data['oldest_unpaid_days']
                item = {
                    'customer_id': str(cust.id),
                    'customer_name': cust.name,
                    'phone': cust.phone,
                    'balance_paise': balance,
                    'oldest_unpaid_days': oldest_days
                }
                if oldest_days <= 30:
                    report['days_0_to_30'].append(item)
                elif oldest_days <= 60:
                    report['days_31_to_60'].append(item)
                elif oldest_days <= 90:
                    report['days_61_to_90'].append(item)
                else:
                    report['days_90_plus'].append(item)

        return Response(report)


class SupplierViewSet(ShopContextMixin, viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated, IsSupplierManagerOrOwner]

    def get_queryset(self):
        shop = self.get_shop()
        if not shop:
            return Supplier.objects.none()

        qs = Supplier.objects.filter(shop=shop)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search))
        return qs

    def perform_create(self, serializer):
        shop = self.get_shop()
        if not self.check_manager_or_owner(shop):
            raise exceptions.PermissionDenied("Only managers and owners can create suppliers.")
        serializer.save(shop=shop)

    def perform_update(self, serializer):
        shop = serializer.instance.shop
        if not self.check_manager_or_owner(shop):
            raise exceptions.PermissionDenied("Only managers and owners can update suppliers.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.check_manager_or_owner(instance.shop):
            raise exceptions.PermissionDenied("Only managers and owners can delete suppliers.")
        instance.delete()

    @action(detail=True, methods=['get', 'post'], url_path='entries')
    def entries(self, request, pk=None):
        supplier = self.get_object()
        if request.method == 'GET':
            qs = supplier.ledger_entries.all().order_by('bill_date', 'created_at')
            serializer = SupplierLedgerEntrySerializer(qs, many=True)
            return Response(serializer.data)

        # POST entry (bill or payment)
        serializer = SupplierLedgerEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = serializer.save(
            shop=supplier.shop,
            supplier=supplier,
            created_by=request.user
        )
        return Response(SupplierLedgerEntrySerializer(entry).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='ledger')
    def ledger(self, request, pk=None):
        supplier = self.get_object()
        entries = supplier.ledger_entries.all().order_by('bill_date', 'created_at')
        running_balance = 0
        ledger_data = []

        for entry in entries:
            if entry.entry_type == SupplierEntryType.PURCHASE_BILL:
                running_balance += entry.amount_paise
            else:
                running_balance -= entry.amount_paise

            serialized = SupplierLedgerEntrySerializer(entry).data
            serialized['running_balance_paise'] = running_balance
            ledger_data.append(serialized)

        return Response(ledger_data)
