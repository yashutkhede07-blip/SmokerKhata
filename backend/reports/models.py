from django.db import models
from django.conf import settings
from common.models import ShopScopedModel


class ReportType(models.TextChoices):
    SALES_SUMMARY = 'SALES_SUMMARY', 'Sales & Profit Summary'
    TOP_ITEMS = 'TOP_ITEMS', 'Top Selling Items'
    ITEM_MARGINS = 'ITEM_MARGINS', 'Item Profit Margins'


class ReportFormat(models.TextChoices):
    XLSX = 'XLSX', 'Excel Spreadsheet'
    PDF = 'PDF', 'PDF Document'


class ReportStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'


class ReportRequest(ShopScopedModel):
    """
    Tracks requested reports, especially async exports (REPT-06).
    """
    report_type = models.CharField(max_length=30, choices=ReportType.choices)
    format = models.CharField(max_length=10, choices=ReportFormat.choices)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    file_path = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='report_requests'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_type} ({self.format}) - {self.status}"
