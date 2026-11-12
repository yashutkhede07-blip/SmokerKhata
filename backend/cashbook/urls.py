from django.urls import path
from cashbook.views import (
    TodayCashBookView, OpenCashBookView, AddCashBookEntryView,
    CloseCashBookView, CashBookHistoryView
)

urlpatterns = [
    path('today/', TodayCashBookView.as_view(), name='cashbook-today'),
    path('today/open/', OpenCashBookView.as_view(), name='cashbook-today-open'),
    path('today/entry/', AddCashBookEntryView.as_view(), name='cashbook-today-entry'),
    path('today/close/', CloseCashBookView.as_view(), name='cashbook-today-close'),
    path('history/', CashBookHistoryView.as_view(), name='cashbook-history'),
]
