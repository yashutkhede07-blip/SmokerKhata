from django.urls import path
from reports.views import (
    SalesSummaryReportView, TopItemsReportView,
    ItemMarginsReportView, ExportReportView, ReportDownloadView
)

urlpatterns = [
    path('sales-summary/', SalesSummaryReportView.as_view(), name='report-sales-summary'),
    path('top-items/', TopItemsReportView.as_view(), name='report-top-items'),
    path('margins/', ItemMarginsReportView.as_view(), name='report-margins'),
    path('export/', ExportReportView.as_view(), name='report-export'),
    path('requests/<uuid:pk>/download/', ReportDownloadView.as_view(), name='report-download'),
]
