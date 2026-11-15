from django.urls import path
from subscriptions.views import (
    PlanListView, CurrentSubscriptionView, ProrationPreviewView,
    RazorpayWebhookView, PlayBillingVerifyView
)

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='subscription-plans'),
    path('current/', CurrentSubscriptionView.as_view(), name='subscription-current'),
    path('proration-preview/', ProrationPreviewView.as_view(), name='subscription-proration-preview'),
    path('webhook/razorpay/', RazorpayWebhookView.as_view(), name='subscription-webhook-razorpay'),
    path('play-billing/verify/', PlayBillingVerifyView.as_view(), name='subscription-play-verify'),
]
