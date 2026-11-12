import urllib.parse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from shops.models import Shop, ShopMember, Role
from billing.models import Bill, PaymentMode
from billing.serializers import BillSerializer, CreateBillInputSerializer
from billing.services import BillingService

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


class BillViewSet(ShopContextMixin, viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        shop = self.get_shop()
        if not shop:
            return Bill.objects.none()
        qs = Bill.objects.filter(shop=shop)

        payment_mode = self.request.query_params.get('payment_mode')
        if payment_mode:
            qs = qs.filter(payment_mode=payment_mode)

        customer_id = self.request.query_params.get('customer')
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        return qs

    def create(self, request, *args, **kwargs):
        shop = self.get_shop()
        serializer = CreateBillInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bill, created = BillingService.create_bill_atomic(
            shop=shop,
            user=request.user,
            validated_data=serializer.validated_data
        )

        resp_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(BillSerializer(bill).data, status=resp_status)

    @action(detail=True, methods=['get'], url_path='whatsapp-link')
    def whatsapp_link(self, request, pk=None):
        bill = self.get_object()
        phone = ""
        if bill.customer and bill.customer.phone:
            phone = bill.customer.phone.strip().replace('+', '').replace('-', '')
            if len(phone) == 10:
                phone = f"91{phone}"

        lines = [f"{item.item_name} x {item.quantity} = Rs {item.subtotal_paise/100:.2f}" for item in bill.items.all()]
        items_text = "\n".join(lines)
        amount_rs = f"{bill.final_amount_paise / 100:.2f}"

        msg = (
            f"*{bill.shop.name}*\n"
            f"Bill No: {bill.bill_number}\n"
            f"------------------\n"
            f"{items_text}\n"
            f"------------------\n"
            f"Total: Rs {amount_rs}\n"
            f"Mode: {bill.payment_mode}\n"
            f"Dhanyawad! Phir aaiye!"
        )
        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/{phone}?text={encoded_msg}" if phone else f"https://wa.me/?text={encoded_msg}"

        return Response({
            'bill_number': bill.bill_number,
            'phone': phone,
            'message': msg,
            'whatsapp_url': wa_url
        })


class NextBillSequenceView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        device_id = request.query_params.get('device_id', 'COUNTER1')
        bill_number, seq = BillingService.get_next_bill_number(shop, device_id)
        return Response({
            'bill_number': bill_number,
            'device_id': device_id,
            'sequence': seq
        })
