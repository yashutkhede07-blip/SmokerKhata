from rest_framework import permissions
from shops.models import Shop, ShopMember, Role

class IsInventoryManagerOrOwner(permissions.BasePermission):
    """
    Read allowed for all shop staff (Cashier, Manager, Owner).
    Write/Edit/Delete allowed only for Manager and Owner.
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

        if request.method in permissions.SAFE_METHODS:
            return True

        return member.role in [Role.OWNER, Role.MANAGER]
