import json
from django.shortcuts import get_object_or_404
from rest_framework import views, viewsets, permissions, status
from rest_framework.response import Response

from shops.models import Shop, ShopMember, Role
from subscriptions.models import Plan, Subscription, SubscriptionStatus
from subscriptions.serializers import PlanSerializer, SubscriptionSerializer
from subscriptions.services import SubscriptionService


class ShopContextMixin:
    def get_shop(self):
        shop_id = self.request.query_params.get('shop_id') or self.request.data.get('shop_id')
        if not shop_id:
            member = ShopMember.objects.filter(user=self.request.user).first()
            if member:
                return member.shop
            return Shop.objects.filter(owner=self.request.user).first()
        return get_object_or_404(Shop, id=shop_id)


class PlanListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        plans = Plan.objects.filter(is_active=True).prefetch_related('feature_flags')
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)


class CurrentSubscriptionView(ShopContextMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        sub = getattr(shop, 'subscription', None)
        if not sub:
            sub = SubscriptionService.create_trial_subscription(shop)
        serializer = SubscriptionSerializer(sub)
        return Response(serializer.data)


class ProrationPreviewView(ShopContextMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shop = self.get_shop()
        new_plan_id = request.data.get('plan_id')
        new_plan = get_object_or_404(Plan, id=new_plan_id)

        sub = getattr(shop, 'subscription', None)
        if not sub:
            sub = SubscriptionService.create_trial_subscription(shop)

        result = SubscriptionService.calculate_proration(sub, new_plan)
        return Response(result)


class RazorpayWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        signature = request.headers.get('X-Razorpay-Signature')
        if not signature:
            return Response({'error': 'Missing signature header'}, status=status.HTTP_400_BAD_REQUEST)

        payload_bytes = request.body
        is_valid = SubscriptionService.verify_razorpay_signature(payload_bytes, signature)
        if not is_valid:
            return Response({'error': 'Invalid webhook signature'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = json.loads(payload_bytes.decode('utf-8'))
        except Exception:
            return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        event_id = payload.get('event_id') or payload.get('id') or payload.get('payload', {}).get('subscription', {}).get('entity', {}).get('id')
        if not event_id:
            event_id = f"evt_{hash(payload_bytes)}"

        sub_event, processed = SubscriptionService.process_razorpay_event(event_id, payload)

        return Response({'status': 'received', 'processed': processed}, status=status.HTTP_200_OK)


class PlayBillingVerifyView(ShopContextMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shop = self.get_shop()
        purchase_token = request.data.get('purchase_token')
        product_id = request.data.get('product_id', 'monthly')

        if not purchase_token:
            return Response({'error': 'purchase_token is required'}, status=status.HTTP_400_BAD_REQUEST)

        sub = SubscriptionService.verify_play_billing(shop, purchase_token, product_id)
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_200_OK)
