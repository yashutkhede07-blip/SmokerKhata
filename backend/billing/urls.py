from django.urls import path, include
from rest_framework.routers import DefaultRouter
from billing.views import BillViewSet, NextBillSequenceView

router = DefaultRouter()
router.register(r'bills', BillViewSet, basename='bill')

urlpatterns = [
    path('next-sequence/', NextBillSequenceView.as_view(), name='next-bill-sequence'),
    path('', include(router.urls)),
]
