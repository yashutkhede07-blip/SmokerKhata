from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from shops.models import Shop, ShopMember, Role
from accounts.permissions import IsShopManagerOrOwner
from audit.models import AuditLogEntry
from audit.serializers import AuditLogEntrySerializer


class ShopContextMixin:
    def get_shop(self):
        shop_id = self.request.query_params.get('shop_id')
        if not shop_id:
            member = ShopMember.objects.filter(user=self.request.user).first()
            if member:
                return member.shop
            return Shop.objects.filter(owner=self.request.user).first()
        return get_object_or_404(Shop, id=shop_id)


class AuditLogViewSet(ShopContextMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only view for audit logs, restricted to owners and managers.
    """
    serializer_class = AuditLogEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsShopManagerOrOwner]

    def get_queryset(self):
        shop = self.get_shop()
        if not shop:
            return AuditLogEntry.objects.none()

        qs = AuditLogEntry.objects.filter(shop=shop)
        model_name = self.request.query_params.get('model')
        if model_name:
            qs = qs.filter(model_name=model_name)
        record_id = self.request.query_params.get('record_id')
        if record_id:
            qs = qs.filter(record_id=record_id)
        return qs
