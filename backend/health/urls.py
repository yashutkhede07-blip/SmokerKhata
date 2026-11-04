from django.urls import path
from health.views import healthz

urlpatterns = [
    path('', healthz, name='healthz'),
]
