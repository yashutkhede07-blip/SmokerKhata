import os
from django.utils import timezone
from django.conf import settings
from reports.models import ReportRequest, ReportStatus, ReportFormat
from reports.generators import ExcelReportGenerator, PdfReportGenerator


def generate_report_file(report_request_id):
    """
    Task executed synchronously or via django-q2 worker.
    """
    try:
        req = ReportRequest.objects.get(id=report_request_id)
        req.status = ReportStatus.PROCESSING
        req.save(update_fields=['status'])

        shop = req.shop
        media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
        reports_dir = os.path.join(media_root, 'reports', str(shop.id))
        os.makedirs(reports_dir, exist_ok=True)

        if req.format == ReportFormat.XLSX:
            filename = f"report_{req.report_type}_{req.id}.xlsx"
            buf = ExcelReportGenerator.generate_sales_summary_wb(shop, req.date_from, req.date_to)
        else:
            filename = f"report_{req.report_type}_{req.id}.pdf"
            buf = PdfReportGenerator.generate_sales_summary_pdf(shop, req.date_from, req.date_to)

        full_path = os.path.join(reports_dir, filename)
        with open(full_path, 'wb') as f:
            f.write(buf.getvalue())

        req.file_path = full_path
        req.status = ReportStatus.COMPLETED
        req.completed_at = timezone.now()
        req.save(update_fields=['file_path', 'status', 'completed_at'])
        return True

    except Exception as e:
        if 'req' in locals():
            req.status = ReportStatus.FAILED
            req.error_message = str(e)
            req.save(update_fields=['status', 'error_message'])
        raise
