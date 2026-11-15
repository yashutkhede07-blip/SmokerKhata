from rest_framework import permissions
from shops.models import Shop, ShopMember


class EnforceSubscriptionStatus(permissions.BasePermission):
    """
    SUBS-07, SUBS-08, SUBS-09:
    Allows SAFE methods (GET, HEAD, OPTIONS) always (90-day read-only data retention).
    Blocks mutating methods (POST, PUT, PATCH, DELETE) if the subscription has expired
    and exceeded the 5-day grace period.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Resolve shop
        shop = getattr(request, 'shop', None)
        if not shop and hasattr(view, 'get_shop'):
            try:
                shop = view.get_shop()
            except Exception:
                shop = None

        if not shop:
            return True

        sub = getattr(shop, 'subscription', None)
        if not sub:
            return True

        if not sub.is_write_allowed():
            self.message = "Subscription expired past grace period. Account is in read-only mode."
            return False

        return True
