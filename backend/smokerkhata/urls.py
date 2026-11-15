from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', include('health.urls')),
    path('healthz/', include('health.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/shops/', include('shops.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/ledgers/', include('ledgers.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/cashbook/', include('cashbook.urls')),
    path('api/sync/', include('sync.urls')),
    path('api/audit/', include('audit.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
]

# Serve PWA static assets and SPA index fallback (PWA-04)
static_pwa_dir = settings.BASE_DIR / 'static_pwa'
if static_pwa_dir.exists():
    urlpatterns += [
        re_path(r'^(?!api/|admin/|healthz).*$', serve, {
            'document_root': str(static_pwa_dir),
            'path': 'index.html',
        }),
    ]

