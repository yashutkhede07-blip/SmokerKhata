import io
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from reports.services import ReportCalculationService, format_rupees


class ExcelReportGenerator:
    @staticmethod
    def generate_sales_summary_wb(shop, date_from=None, date_to=None):
        wb = Workbook()
        ws = wb.active
        ws.title = "Sales Summary"

        # Styling
        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=14, bold=True)
        bold_font = Font(name="Calibri", size=11, bold=True)

        ws['A1'] = f"{shop.name} - Sales & Gross Profit Summary"
        ws['A1'].font = title_font
        ws['A2'] = f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        if date_from or date_to:
            ws['A3'] = f"Period: {date_from or 'All'} to {date_to or 'All'}"

        data = ReportCalculationService.get_sales_profit_summary(shop, date_from, date_to)

        start_row = 5
        metrics = [
            ("Total Bills Completed", data['total_bills']),
            ("Total Sales (Revenue)", data['formatted_sales']),
            ("Cost of Goods Sold (COGS)", data['formatted_cost']),
            ("Gross Profit", data['formatted_gross_profit']),
            ("Gross Margin %", f"{data['margin_percentage']}%"),
        ]

        ws.cell(row=start_row, column=1, value="Metric").fill = header_fill
        ws.cell(row=start_row, column=1).font = header_font
        ws.cell(row=start_row, column=2, value="Value").fill = header_fill
        ws.cell(row=start_row, column=2).font = header_font

        for idx, (metric, val) in enumerate(metrics, start=start_row + 1):
            ws.cell(row=idx, column=1, value=metric)
            c2 = ws.cell(row=idx, column=2, value=val)
            if "Profit" in metric or "Sales" in metric:
                c2.font = bold_font

        # Top Items Sheet
        ws_top = wb.create_sheet(title="Top Selling Items")
        ws_top['A1'] = f"Top Selling Items - {shop.name}"
        ws_top['A1'].font = title_font

        top_headers = ["Item Name", "Quantity Sold", "Revenue"]
        for col_idx, h in enumerate(top_headers, start=1):
            cell = ws_top.cell(row=3, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font

        top_items = ReportCalculationService.get_top_selling_items(shop, date_from, date_to, limit=20)
        for r_idx, item in enumerate(top_items, start=4):
            ws_top.cell(row=r_idx, column=1, value=item['item_name'])
            ws_top.cell(row=r_idx, column=2, value=item['total_quantity'])
            ws_top.cell(row=r_idx, column=3, value=item['formatted_revenue'])

        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 20
        ws_top.column_dimensions['A'].width = 30
        ws_top.column_dimensions['B'].width = 18
        ws_top.column_dimensions['C'].width = 20

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf


class PdfReportGenerator:
    @staticmethod
    def generate_sales_summary_pdf(shop, date_from=None, date_to=None):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        elements = []

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#1F497D')
        )
        elements.append(Paragraph(f"<b>{shop.name}</b>", title_style))
        elements.append(Paragraph(f"Sales & Profit Summary Report", styles['Heading2']))
        period_str = f"Period: {date_from or 'Beginning'} to {date_to or 'Present'}"
        elements.append(Paragraph(f"{period_str} | Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 15))

        data = ReportCalculationService.get_sales_profit_summary(shop, date_from, date_to)

        table_data = [
            ["Metric", "Amount / Value"],
            ["Total Completed Bills", str(data['total_bills'])],
            ["Total Sales", data['formatted_sales']],
            ["Cost of Goods Sold", data['formatted_cost']],
            ["Gross Profit", data['formatted_gross_profit']],
            ["Gross Margin %", f"{data['margin_percentage']}%"],
        ]

        t = Table(table_data, colWidths=[240, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1F497D')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, -1), 6),
            ('TOPPADDING', (0, 0), (1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0, 4), (1, 4), colors.HexColor('#EBF1F5')),
            ('FONTNAME', (0, 4), (1, 4), 'Helvetica-Bold'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        # Top Items
        elements.append(Paragraph("<b>Top Selling Items</b>", styles['Heading3']))
        top_items = ReportCalculationService.get_top_selling_items(shop, date_from, date_to, limit=10)
        top_data = [["Item", "Qty Sold", "Revenue"]]
        for item in top_items:
            top_data.append([item['item_name'], str(item['total_quantity']), item['formatted_revenue']])

        top_table = Table(top_data, colWidths=[240, 100, 100])
        top_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#555555')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(top_table)

        doc.build(elements)
        buf.seek(0)
        return buf
