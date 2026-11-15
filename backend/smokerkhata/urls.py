from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve
from django.conf import settings
from django.http import FileResponse, Http404
import os

def serve_spa(request, path=''):
    static_pwa_dir = settings.BASE_DIR / 'static_pwa'
    requested_file = static_pwa_dir / path
    if path and requested_file.exists() and requested_file.is_file():
        return serve(request, path, document_root=str(static_pwa_dir))
    index_file = static_pwa_dir / 'index.html'
    if index_file.exists():
        return FileResponse(open(index_file, 'rb'), content_type='text/html')
    raise Http404("PWA not built yet")

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
    re_path(r'^(?!api/|admin/|healthz)(?P<path>.*)$', serve_spa),
]


