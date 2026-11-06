from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from shops.models import Shop, ShopMember, Role
from inventory.models import Category, Item, ItemVariant, StockLedgerEntry
from inventory.serializers import (
    CategorySerializer, ItemSerializer, ItemVariantSerializer,
    StockLedgerEntrySerializer, StockAdjustmentSerializer
)
from inventory.services import StockService
from inventory.reports import InventoryReportService
from inventory.permissions import IsInventoryManagerOrOwner

class ShopContextMixin:
    def get_shop(self):
        shop_id = self.request.query_params.get('shop_id') or self.request.data.get('shop')
        if not shop_id and hasattr(self, 'kwargs') and 'shop_id' in self.kwargs:
            shop_id = self.kwargs['shop_id']
        if not shop_id:
            # Fallback to first shop the user owns or belongs to
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


class CategoryViewSet(ShopContextMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsInventoryManagerOrOwner]

    def get_queryset(self):
        shop = self.get_shop()
        if not shop:
            return Category.objects.none()
        return Category.objects.filter(shop=shop)

    def perform_create(self, serializer):
        shop = self.get_shop()
        if not self.check_manager_or_owner(shop):
            raise exceptions.PermissionDenied("Only managers and owners can create categories.")
        serializer.save(shop=shop)

    def perform_update(self, serializer):
        shop = serializer.instance.shop
        if not self.check_manager_or_owner(shop):
            raise exceptions.PermissionDenied("Only managers and owners can update categories.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.check_manager_or_owner(instance.shop):
            raise exceptions.PermissionDenied("Only managers and owners can delete categories.")
        instance.delete()


class ItemViewSet(ShopContextMixin, viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsInventoryManagerOrOwner]

    def get_queryset(self):
        shop = self.get_shop()
        if not shop:
            return Item.objects.none()

        qs = Item.objects.filter(shop=shop)
        category_id = self.request.query_params.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        barcode = self.request.query_params.get('barcode')
        if barcode:
            qs = qs.filter(barcode=barcode)

        active = self.request.query_params.get('active')
        if active is not None:
            qs = qs.filter(is_active=(active.lower() in ['true', '1']))

        quick_add = self.request.query_params.get('quick_add')
        if quick_add is not None:
            qs = qs.filter(is_quick_add=(quick_add.lower() in ['true', '1'])).order_by('quick_add_order', 'name')

        return qs

    def perform_create(self, serializer):
        shop = self.get_shop()
        if not self.check_manager_or_owner(shop):
            raise exceptions.PermissionDenied("Only managers and owners can create items.")
        serializer.save(shop=shop)

    def perform_update(self, serializer):
        shop = serializer.instance.shop
        if not self.check_manager_or_owner(shop):
            raise exceptions.PermissionDenied("Only managers and owners can update items.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.check_manager_or_owner(instance.shop):
            raise exceptions.PermissionDenied("Only managers and owners can delete items.")
        instance.soft_delete()

    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        item = self.get_object()
        variant_id = request.query_params.get('variant_id')
        current_stock = StockService.get_current_stock(item.id, variant_id=variant_id)
        return Response({'item_id': item.id, 'current_stock': current_stock})


class ItemVariantViewSet(ShopContextMixin, viewsets.ModelViewSet):
    serializer_class = ItemVariantSerializer
    permission_classes = [permissions.IsAuthenticated, IsInventoryManagerOrOwner]

    def get_queryset(self):
        item_id = self.kwargs.get('item_pk')
        return ItemVariant.objects.filter(item_id=item_id)

    def perform_create(self, serializer):
        item = get_object_or_404(Item, id=self.kwargs.get('item_pk'))
        if not self.check_manager_or_owner(item.shop):
            raise exceptions.PermissionDenied("Only managers and owners can create variants.")
        serializer.save(item=item, shop=item.shop)

    def perform_update(self, serializer):
        if not self.check_manager_or_owner(serializer.instance.shop):
            raise exceptions.PermissionDenied("Only managers and owners can update variants.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.check_manager_or_owner(instance.shop):
            raise exceptions.PermissionDenied("Only managers and owners can delete variants.")
        instance.delete()


class StockAdjustmentView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        item = get_object_or_404(Item, id=data['item'])
        if not self.check_manager_or_owner(item.shop):
            return Response(
                {"detail": "Only managers and owners can adjust stock."},
                status=status.HTTP_403_FORBIDDEN
            )

        variant = None
        if data.get('variant'):
            variant = get_object_or_404(ItemVariant, id=data['variant'], item=item)

        movement = StockService.record_movement(
            shop=item.shop,
            item=item,
            delta=data['quantity_delta'],
            reason=data['reason'],
            variant=variant,
            unit_cost_paise=data.get('unit_cost_paise', 0),
            reference_id=data.get('reference_id', ''),
            notes=data.get('notes', ''),
            user=request.user
        )

        return Response(StockLedgerEntrySerializer(movement).data, status=status.HTTP_201_CREATED)


class StockLedgerView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        if not shop:
            return Response([])

        qs = StockLedgerEntry.objects.filter(shop=shop)
        item_id = request.query_params.get('item_id')
        if item_id:
            qs = qs.filter(item_id=item_id)

        variant_id = request.query_params.get('variant_id')
        if variant_id:
            qs = qs.filter(variant_id=variant_id)

        serializer = StockLedgerEntrySerializer(qs[:100], many=True)
        return Response(serializer.data)


class LowStockAlertView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        if not shop:
            return Response([])
        alerts = InventoryReportService.get_low_stock_items(shop.id)
        return Response(alerts)


class DeadStockReportView(ShopContextMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        if not shop:
            return Response([])
        days = int(request.query_params.get('days', 30))
        report = InventoryReportService.get_dead_stock_items(shop.id, days=days)
        return Response(report)
