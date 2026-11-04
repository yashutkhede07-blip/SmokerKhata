from rest_framework import permissions
from shops.models import Shop, ShopMember, Role

class IsShopOwner(permissions.BasePermission):
    """
    Allows access only to owners of the target shop.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        shop = getattr(obj, 'shop', obj)
        if not isinstance(shop, Shop):
            return False
        if shop.owner == request.user:
            return True
        return ShopMember.objects.filter(shop=shop, user=request.user, role=Role.OWNER).exists()

class IsShopManagerOrOwner(permissions.BasePermission):
    """
    Allows access to owners and managers of the target shop.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        shop = getattr(obj, 'shop', obj)
        if not isinstance(shop, Shop):
            return False
        if shop.owner == request.user:
            return True
        return ShopMember.objects.filter(
            shop=shop,
            user=request.user,
            role__in=[Role.OWNER, Role.MANAGER]
        ).exists()

class IsShopMember(permissions.BasePermission):
    """
    Allows access to any valid staff member of the shop.
    Cashiers are explicitly blocked from reports and editing past bills unless specific permission flags are granted.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        shop = getattr(obj, 'shop', obj)
        if not isinstance(shop, Shop):
            return False
        if shop.owner == request.user:
            return True

        member = ShopMember.objects.filter(shop=shop, user=request.user).first()
        if not member:
            return False

        # If accessing reports
        if getattr(view, 'is_reports_view', False):
            if member.role == Role.CASHIER and not member.can_view_reports:
                return False

        # If editing past bills
        if getattr(view, 'is_past_bill_edit', False):
            if member.role == Role.CASHIER and not member.can_edit_past_bills:
                return False

        return True
