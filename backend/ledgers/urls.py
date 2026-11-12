from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ledgers.views import (
    CustomerViewSet, SupplierViewSet, CustomerAgingReportView
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'suppliers', SupplierViewSet, basename='supplier')

urlpatterns = [
    path('customers/reports/aging/', CustomerAgingReportView.as_view(), name='customer-aging-report'),
    path('', include(router.urls)),
]
