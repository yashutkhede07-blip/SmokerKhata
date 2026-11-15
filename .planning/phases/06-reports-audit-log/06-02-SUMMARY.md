# Plan 06-02 Summary: Reports Computation Core & Aggregations

- Created `backend/reports/` app and registered in `settings.INSTALLED_APPS` and `urls.py`.
- Implemented `ReportCalculationService`:
  - `get_sales_profit_summary`: Computes total sales, cost of goods sold, gross profit, and margin percentage with Indian lakh comma currency formatting (`REPT-01`).
  - `get_top_selling_items`: Aggregates items by sold quantity and revenue (`REPT-02`).
  - `get_item_margins`: Calculates per-item margin in paise and percentage (`REPT-03`).
- Added endpoints:
  - `GET /api/reports/sales-summary/`
  - `GET /api/reports/top-items/`
  - `GET /api/reports/margins/`
- Enforced role checks blocking cashiers without `can_view_reports` flag (`AUTH-05`).
