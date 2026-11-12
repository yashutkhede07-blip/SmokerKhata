from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', include('health.urls')),
    path('healthz/', include('health.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/shops/', include('shops.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/ledgers/', include('ledgers.urls')),
]
