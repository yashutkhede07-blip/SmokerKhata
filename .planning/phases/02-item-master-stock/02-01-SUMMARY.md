# Summary: Plan 02-01 — Item Master, Categories, and Variants Models & APIs

## What Was Done
- Created `inventory` app and registered it in `settings.INSTALLED_APPS`.
- Implemented `Category`, `Item`, and `ItemVariant` models with integer paise pricing (`selling_price_paise`, `cost_price_paise`), pieces per pack, barcode, GST rate, quick-add toggles, and soft-delete capabilities.
- Implemented DRF serializers and ViewSets with category filtering, search, and active/inactive status.
- Connected inventory endpoints to `backend/smokerkhata/urls.py` under `/api/inventory/`.

## Verification Evidence
- `pytest backend/tests/test_items.py`: 4 passed (models, CRUD, variants, soft-delete).
