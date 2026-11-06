# Phase 02: Item Master & Stock — Technical Research

## Problem & Domain Analysis

Small retail shops in India (paan shops, chai stalls, corner cigarette/cold-drink/chips stores) operate with unique operational constraints:
1. **Loose vs. Pack cigarette sales**: A customer can buy 1 loose stick or a full pack of 10/20. The system needs to support loose stick conversion or dual-unit pricing while tracking inventory accurately.
2. **Fast POS lookup**: The item master feeds directly into the billing grid. Items must support quick-tap priority/sort ordering, category grouping (Cigarettes, Cold Drinks, Chips/Snacks, Prepared Food, Tobacco/Paan), and optional barcodes.
3. **Immutable stock ledger (STCK-03)**: Direct column overwrites (e.g. `item.stock += 10`) are strictly prohibited by the architecture principles. Every change in stock must be an append-only transaction line in a `StockLedgerEntry` or `StockMovement` table with reasons: `PURCHASE`, `SALE`, `ADJUSTMENT_ADD`, `ADJUSTMENT_DAMAGE`, `ADJUSTMENT_THEFT`, `ADJUSTMENT_CORRECTION`.
4. **All money in integer paise**: `selling_price_paise` and `cost_price_paise` stored as `BigIntegerField` or `PositiveBigIntegerField`. No float math.
5. **Low-stock threshold & Dead-stock reporting**: Configurable `low_stock_threshold` on each item, with computed views/aggregates for low-stock warnings and items with zero movement in N days.

## Data Model Architecture

### App: `backend/inventory/` (or `backend/items/` + `backend/stock/`)
Prefer unified `backend/inventory/` to keep item definitions, categories, variants, and stock ledgers cleanly co-located and avoid circular imports.

### 1. `Category` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`)
- `shop`: FK(Shop)
- `name`: CharField(100) (e.g., "Cigarettes", "Cold Drinks", "Snacks", "Prepared Food")
- `display_order`: PositiveIntegerField(default=0)
- `icon`: CharField(50, blank=True)

### 2. `Item` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`)
- `shop`: FK(Shop)
- `category`: FK(Category, on_delete=SET_NULL, null=True, related_name='items')
- `name`: CharField(150)
- `barcode`: CharField(64, blank=True, db_index=True)
- `selling_price_paise`: BigIntegerField()
- `cost_price_paise`: BigIntegerField(default=0)
- `gst_rate`: DecimalField(max_digits=5, decimal_places=2, default=0.00) (GST slab: 0, 5, 12, 18, 28)
- `is_active`: BooleanField(default=True)
- `is_quick_add`: BooleanField(default=False)
- `quick_add_order`: PositiveIntegerField(default=0)
- `low_stock_threshold`: IntegerField(default=5)
- `unit`: CharField(20, default='PCS') (e.g. PCS, PACK, BOTTLE, CUP)
- `pieces_per_pack`: PositiveIntegerField(default=1) (for cigarettes/loose conversion: e.g. 10 or 20)

### 3. `ItemVariant` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`)
- `item`: FK(Item, on_delete=CASCADE, related_name='variants')
- `name`: CharField(100) (e.g., "Classic Regular", "Classic Mild", "Maggi Masala", "Maggi Atta")
- `selling_price_paise`: BigIntegerField(null=True, blank=True) (overrides item base price if present)
- `cost_price_paise`: BigIntegerField(null=True, blank=True)
- `barcode`: CharField(64, blank=True)
- `is_active`: BooleanField(default=True)

### 4. `StockLedgerEntry` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`)
- Immutable ledger table. Never updated or deleted.
- `shop`: FK(Shop)
- `item`: FK(Item, on_delete=CASCADE, related_name='stock_movements')
- `variant`: FK(ItemVariant, null=True, blank=True, on_delete=SET_NULL)
- `quantity_delta`: IntegerField() (+ve for purchase/inflow, -ve for sale/loss)
- `reason`: CharField(choices: `PURCHASE`, `SALE`, `ADJUSTMENT_COUNT`, `DAMAGE`, `RETURN`, `INITIAL_STOCK`)
- `unit_cost_paise`: BigIntegerField(default=0)
- `reference_id`: CharField(100, blank=True) (e.g. PurchaseBill UUID, POS Bill UUID, or Adjustment note)
- `notes`: TextField(blank=True)
- `created_by`: FK(User, null=True, on_delete=SET_NULL)

### Current Stock Computation
Stock level is calculated via SQL aggregation `Sum('quantity_delta')` on the `StockLedgerEntry` table, with optional denormalized caching if needed, ensuring zero drift between ledger and current balance.

## Verification & Nyquist Strategy
- Unit tests with `pytest-django`:
  - Item CRUD with soft-delete verification (item marked inactive still fetchable for historical records)
  - Variants creation and pricing inheritance
  - Stock ledger entry creation & balance aggregation
  - Low stock filter query tests
  - Dead stock report query tests (calculating days since last movement)
- DRF permission tests:
  - Cashier cannot perform manual stock adjustments or edit item prices unless owner/manager.
