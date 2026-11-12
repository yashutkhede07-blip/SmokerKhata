from datetime import date
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, Value, IntegerField
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response

from shops.models import Shop, ShopMember, Role
from billing.models import Bill, PaymentMode, BillStatus
from cashbook.models import CashBookDay, CashBookEntry, CashEntryType
from cashbook.serializers import CashBookDaySerializer, CashBookEntrySerializer

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


class TodayCashBookView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_or_create_today(self, shop):
        today = timezone.now().date()
        day, _ = CashBookDay.objects.get_or_create(
            shop=shop,
            date=today,
            defaults={'opening_cash_paise': 0}
        )
        return day

    def calculate_expected_closing(self, day):
        # 1. Opening cash
        opening = day.opening_cash_paise

        # 2. Cash sales from bills on this date
        cash_sales = Bill.objects.filter(
            shop=day.shop,
            created_at__date=day.date,
            status=BillStatus.COMPLETED
        ).aggregate(
            total=Coalesce(Sum('cash_amount_paise'), Value(0, output_field=IntegerField()))
        )['total']

        # 3. Cash in entries
        cash_in = day.entries.filter(
            entry_type=CashEntryType.CASH_IN
        ).aggregate(
            total=Coalesce(Sum('amount_paise'), Value(0, output_field=IntegerField()))
        )['total']

        # 4. Cash out entries
        cash_out = day.entries.filter(
            entry_type=CashEntryType.CASH_OUT
        ).aggregate(
            total=Coalesce(Sum('amount_paise'), Value(0, output_field=IntegerField()))
        )['total']

        return opening + cash_sales + cash_in - cash_out, cash_sales, cash_in, cash_out

    def get(self, request):
        shop = self.get_shop()
        day = self.get_or_create_today(shop)
        expected, cash_sales, cash_in, cash_out = self.calculate_expected_closing(day)

        if not day.is_closed:
            day.expected_closing_paise = expected
            day.save(update_fields=['expected_closing_paise'])

        data = CashBookDaySerializer(day).data
        data['cash_sales_paise'] = cash_sales
        data['total_cash_in_paise'] = cash_in
        data['total_cash_out_paise'] = cash_out
        return Response(data)


class OpenCashBookView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shop = self.get_shop()
        if not self.check_manager_or_owner(shop):
            raise exceptions.PermissionDenied("Only managers and owners can open the cash book.")

        today = timezone.now().date()
        day, _ = CashBookDay.objects.get_or_create(shop=shop, date=today)
        if day.is_closed:
            return Response({'error': 'Cash book for today is already closed.'}, status=status.HTTP_400_BAD_REQUEST)

        opening_cash = request.data.get('opening_cash_paise', 0)
        day.opening_cash_paise = int(opening_cash)
        day.save(update_fields=['opening_cash_paise'])
        return Response(CashBookDaySerializer(day).data)


class AddCashBookEntryView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shop = self.get_shop()
        today = timezone.now().date()
        day, _ = CashBookDay.objects.get_or_create(shop=shop, date=today)
        if day.is_closed:
            return Response({'error': 'Cannot add entries to a closed cash book.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CashBookEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = serializer.save(
            shop=shop,
            cashbook_day=day,
            created_by=request.user
        )
        return Response(CashBookEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


class CloseCashBookView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shop = self.get_shop()
        if not self.check_manager_or_owner(shop):
            raise exceptions.PermissionDenied("Only managers and owners can close the cash book.")

        today = timezone.now().date()
        day = get_object_or_404(CashBookDay, shop=shop, date=today)

        actual_closing = request.data.get('actual_closing_paise')
        if actual_closing is None:
            return Response({'error': 'actual_closing_paise is required.'}, status=status.HTTP_400_BAD_REQUEST)

        notes = request.data.get('notes', '')

        # Recalculate expected closing
        helper = TodayCashBookView()
        expected, _, _, _ = helper.calculate_expected_closing(day)

        day.expected_closing_paise = expected
        day.actual_closing_paise = int(actual_closing)
        day.discrepancy_paise = day.actual_closing_paise - day.expected_closing_paise
        day.is_closed = True
        day.closed_at = timezone.now()
        day.closed_by = request.user
        if notes:
            day.notes = notes
        day.save()

        return Response(CashBookDaySerializer(day).data)


class CashBookHistoryView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        days = CashBookDay.objects.filter(shop=shop).order_by('-date')[:30]
        return Response(CashBookDaySerializer(days, many=True).data)
