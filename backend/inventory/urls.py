from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory.views import (
    CategoryViewSet, ItemViewSet, ItemVariantViewSet,
    StockAdjustmentView, StockLedgerView, LowStockAlertView, DeadStockReportView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', ItemViewSet, basename='item')

urlpatterns = [
    path('', include(router.urls)),
    path('items/<uuid:item_pk>/variants/', ItemVariantViewSet.as_view({'get': 'list', 'post': 'create'}), name='item-variants-list'),
    path('items/<uuid:item_pk>/variants/<uuid:pk>/', ItemVariantViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='item-variant-detail'),
    path('stock/adjust/', StockAdjustmentView.as_view(), name='stock-adjust'),
    path('stock/ledger/', StockLedgerView.as_view(), name='stock-ledger'),
    path('alerts/low-stock/', LowStockAlertView.as_view(), name='low-stock-alerts'),
    path('reports/dead-stock/', DeadStockReportView.as_view(), name='dead-stock-report'),
]
