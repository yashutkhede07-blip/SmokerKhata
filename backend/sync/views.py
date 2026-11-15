from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from shops.models import Shop, ShopMember
from sync.models import SyncJournalEntry
from sync.serializers import SyncPushSerializer, SyncJournalEntrySerializer
from sync.engine import SyncEngineService


class ShopContextMixin:
    def get_shop(self):
        shop_id = self.request.query_params.get('shop_id') or self.request.data.get('shop_id')
        if not shop_id:
            member = ShopMember.objects.filter(user=self.request.user).first()
            if member:
                return member.shop
            return Shop.objects.filter(owner=self.request.user).first()
        return get_object_or_404(Shop, id=shop_id)


class SyncPushView(ShopContextMixin, APIView):
    """
    POST /api/sync/push/
    Accepts a batch of offline operations, processes them transactionally
    with idempotency key deduplication, and returns confirmed keys.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shop = self.get_shop()
        if not shop:
            return Response(
                {'error': 'No shop found for this user.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SyncPushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_id = serializer.validated_data['device_id']
        operations = serializer.validated_data['operations']

        result = SyncEngineService.process_batch(
            shop=shop,
            device_id=device_id,
            operations=operations,
            user=request.user,
        )

        return Response({
            'success': True,
            'processed_keys': result['processed_keys'],
            'skipped_keys': result['skipped_keys'],
            'failed_keys': result['failed_keys'],
            'current_cursor': result['current_cursor'],
        }, status=status.HTTP_200_OK)


class SyncPullView(ShopContextMixin, APIView):
    """
    GET /api/sync/pull/?cursor=0&limit=100
    Returns journal entries since the given cursor (monotonic sequence),
    with pagination metadata.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        if not shop:
            return Response(
                {'error': 'No shop found for this user.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cursor = int(request.query_params.get('cursor', 0))
        except (ValueError, TypeError):
            cursor = 0

        try:
            limit = min(int(request.query_params.get('limit', 100)), 500)
        except (ValueError, TypeError):
            limit = 100

        entries = SyncJournalEntry.objects.filter(
            shop=shop,
            sequence__gt=cursor,
        ).order_by('sequence')[:limit + 1]

        entries_list = list(entries)
        has_more = len(entries_list) > limit
        if has_more:
            entries_list = entries_list[:limit]

        if entries_list:
            next_cursor = entries_list[-1].sequence
        else:
            next_cursor = cursor

        serializer = SyncJournalEntrySerializer(entries_list, many=True)

        return Response({
            'changes': serializer.data,
            'next_cursor': next_cursor,
            'has_more': has_more,
        })
