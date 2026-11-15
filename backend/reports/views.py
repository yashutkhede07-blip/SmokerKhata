import os
from datetime import datetime, date
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from rest_framework import views, viewsets, permissions, status
from rest_framework.response import Response

from shops.models import Shop, ShopMember, Role
from reports.models import ReportRequest, ReportStatus, ReportFormat, ReportType
from reports.services import ReportCalculationService
from reports.generators import ExcelReportGenerator, PdfReportGenerator
from reports.tasks import generate_report_file


class ReportsPermission(permissions.BasePermission):
    """
    Cashiers cannot view reports unless explicitly granted can_view_reports (AUTH-05).
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        shop = getattr(obj, 'shop', obj)
        if not isinstance(shop, Shop):
            return False
        if shop.owner == request.user:
            return True
        member = ShopMember.objects.filter(shop=shop, user=request.user).first()
        if not member:
            return False
        if member.role in [Role.OWNER, Role.MANAGER]:
            return True
        return member.can_view_reports


class ShopContextMixin:
    is_reports_view = True

    def get_shop(self):
        shop_id = self.request.query_params.get('shop_id') or self.request.data.get('shop_id')
        if not shop_id:
            member = ShopMember.objects.filter(user=self.request.user).first()
            if member:
                shop = member.shop
            else:
                shop = Shop.objects.filter(owner=self.request.user).first()
        else:
            shop = get_object_or_404(Shop, id=shop_id)

        if shop:
            # Check permissions
            member = ShopMember.objects.filter(shop=shop, user=self.request.user).first()
            if shop.owner != self.request.user and member and member.role == Role.CASHIER and not member.can_view_reports:
                from rest_framework import exceptions
                raise exceptions.PermissionDenied("Cashier does not have permission to view reports.")
        return shop


class SalesSummaryReportView(ShopContextMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        df = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None
        dt = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None

        data = ReportCalculationService.get_sales_profit_summary(shop, df, dt)
        return Response(data)


class TopItemsReportView(ShopContextMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        limit = int(request.query_params.get('limit', 10))

        df = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None
        dt = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None

        data = ReportCalculationService.get_top_selling_items(shop, df, dt, limit)
        return Response(data)


class ItemMarginsReportView(ShopContextMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop = self.get_shop()
        data = ReportCalculationService.get_item_margins(shop)
        return Response(data)


class ExportReportView(ShopContextMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shop = self.get_shop()
        report_type = request.data.get('report_type', ReportType.SALES_SUMMARY)
        fmt = request.data.get('format', ReportFormat.XLSX).upper()
        date_from_str = request.data.get('date_from')
        date_to_str = request.data.get('date_to')

        df = datetime.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else None
        dt = datetime.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else None

        days_count = 0
        if df and dt:
            days_count = (dt - df).days

        # Create ReportRequest
        req = ReportRequest.objects.create(
            shop=shop,
            report_type=report_type,
            format=fmt,
            date_from=df,
            date_to=dt,
            created_by=request.user
        )

        # REPT-06: Large date range (> 7 days) can run via django-q or background task
        # For simplicity and determinism in tests, generate or queue:
        if days_count > 7:
            try:
                from django_q.tasks import async_task
                async_task(generate_report_file, req.id)
                return Response({
                    'request_id': str(req.id),
                    'status': req.status,
                    'message': 'Generating report in background...'
                }, status=status.HTTP_202_ACCEPTED)
            except Exception:
                # Fallback to sync if q cluster not active
                generate_report_file(req.id)
                req.refresh_from_db()
                return Response({
                    'request_id': str(req.id),
                    'status': req.status,
                    'message': 'Report generated successfully.'
                }, status=status.HTTP_200_OK)
        else:
            generate_report_file(req.id)
            req.refresh_from_db()
            return Response({
                'request_id': str(req.id),
                'status': req.status,
                'message': 'Report generated successfully.'
            }, status=status.HTTP_200_OK)


class ReportDownloadView(ShopContextMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        shop = self.get_shop()
        req = get_object_or_404(ReportRequest, id=pk, shop=shop)
        if req.status != ReportStatus.COMPLETED or not req.file_path or not os.path.exists(req.file_path):
            raise Http404("Report not ready or file missing.")

        filename = os.path.basename(req.file_path)
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if req.format == ReportFormat.XLSX else 'application/pdf'
        return FileResponse(open(req.file_path, 'rb'), as_attachment=True, filename=filename, content_type=content_type)
