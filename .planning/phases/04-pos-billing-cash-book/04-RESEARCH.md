# Phase 04: POS Billing & Cash Book — Technical Research

## Problem & Domain Analysis

Small retail shops in India (selling loose cigarettes, cold drinks, prepared snacks) require:
1. **High-Speed Counter POS Billing**:
   - Cashiers process transactions in seconds.
   - Quick-add items grid + barcode scanning + search.
   - Mixed bills across multiple categories (e.g. 1 Gold Flake + 1 Cold Drink + 1 Maggi).
   - Multi-mode payments:
     - `CASH`: increases cash in hand.
     - `UPI`: direct digital receipt.
     - `UDHAAR`: automatically writes a `CustomerLedgerEntry(CREDIT_GIVEN)` tied to customer.
     - `SPLIT`: combination of Cash, UPI, and Udhaar (sum must match total).

2. **Zero-Collision Offline Bill Numbering (`BILL-06`)**:
   - Bill numbers must be unique per shop and never collide, even when generated concurrently offline on multiple phones.
   - Format: `{shop_prefix}-{device_id}-{local_sequence}`.
   - Reconciled on sync. A sequence tracker table ensures sequence numbers are monotonic per device.

3. **Double-Sale Prevention & Atomic Stock Decrement (`BILL-09`)**:
   - Bill creation and stock decrements MUST execute inside a single `transaction.atomic()`.
   - Items are locked using `select_for_update()` before decrementing stock to prevent race conditions when two cashiers sell the same last piece of inventory.
   - Inserts immutable `StockLedgerEntry(reason=StockMovementReason.SALE, quantity_delta=-qty)`.

4. **Bill Sharing & Receipt Formatting (`BILL-07`)**:
   - Generates digital receipt details and WhatsApp shareable link (`wa.me`) with shop name, bill number, itemized lines, total amount in rupees, and payment mode.

5. **Daily Cash Book & Discrepancy Reconciliation (`CASH-01` through `CASH-05`)**:
   - `CashBookDailySession`:
     - `opening_cash_paise`: set at start of the day.
     - `cash_in_paise` & `cash_out_paise`: ad-hoc cash entries throughout the day with notes (e.g. cash paid for ice delivery, cash injected from owner's pocket).
     - `cash_sales_paise`: sum of all cash payments from POS bills for that day.
     - `expected_closing_paise` = `opening_cash_paise + cash_sales_paise + cash_in_paise - cash_out_paise`.
     - `actual_closing_paise`: physical cash count entered by owner/manager at close of day.
     - `discrepancy_paise` = `actual_closing_paise - expected_closing_paise`.
     - **Integrity Rule**: Any discrepancy is flagged and recorded with notes — NEVER auto-corrected or silently wiped.

## Data Models Architecture

### App: `backend/billing/` and `backend/cashbook/`
Two focused modular Django apps.

#### `backend/billing/models.py`
- `Bill` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`):
  - `shop`: FK(Shop)
  - `bill_number`: CharField(100, db_index=True) (e.g. `GPSC-DEV1-000142`)
  - `device_id`: CharField(50)
  - `local_sequence`: PositiveIntegerField()
  - `customer`: FK(Customer, null=True, blank=True, on_delete=models.SET_NULL)
  - `total_amount_paise`: BigIntegerField()
  - `discount_paise`: BigIntegerField(default=0)
  - `tax_paise`: BigIntegerField(default=0)
  - `final_amount_paise`: BigIntegerField()
  - `payment_mode`: CharField(choices: `CASH`, `UPI`, `UDHAAR`, `SPLIT`)
  - `cash_amount_paise`: BigIntegerField(default=0)
  - `upi_amount_paise`: BigIntegerField(default=0)
  - `udhaar_amount_paise`: BigIntegerField(default=0)
  - `status`: CharField(choices: `COMPLETED`, `CANCELLED`, default=`COMPLETED`)
  - `created_by`: FK(User, null=True, on_delete=models.SET_NULL)

- `BillItem` (`UUIDModel`, `TimeStampedModel`):
  - `bill`: FK(Bill, on_delete=models.CASCADE, related_name='items')
  - `item`: FK(Item, on_delete=models.PROTECT)
  - `variant`: FK(ItemVariant, null=True, blank=True, on_delete=models.SET_NULL)
  - `quantity`: PositiveIntegerField(default=1)
  - `unit_price_paise`: BigIntegerField()
  - `subtotal_paise`: BigIntegerField()
  - `item_name`: CharField(150) # snapshot in case item is later renamed

- `DeviceSequenceTracker` (`ShopScopedModel`, `UUIDModel`):
  - `shop`: FK(Shop)
  - `device_id`: CharField(50)
  - `last_sequence`: PositiveIntegerField(default=0)
  - Unique together: `('shop', 'device_id')`

#### `backend/cashbook/models.py`
- `CashBookDay` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`):
  - `shop`: FK(Shop)
  - `date`: DateField(db_index=True)
  - `opening_cash_paise`: BigIntegerField(default=0)
  - `expected_closing_paise`: BigIntegerField(default=0)
  - `actual_closing_paise`: BigIntegerField(null=True, blank=True)
  - `discrepancy_paise`: BigIntegerField(default=0)
  - `is_closed`: BooleanField(default=False)
  - `closed_at`: DateTimeField(null=True, blank=True)
  - `closed_by`: FK(User, null=True, on_delete=models.SET_NULL)
  - Unique together: `('shop', 'date')`

- `CashBookEntry` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`):
  - `shop`: FK(Shop)
  - `cashbook_day`: FK(CashBookDay, on_delete=models.CASCADE, related_name='entries')
  - `entry_type`: CharField(choices: `CASH_IN`, `CASH_OUT`)
  - `amount_paise`: BigIntegerField()
  - `reason`: CharField(max_length=200)
  - `created_by`: FK(User, null=True, on_delete=models.SET_NULL)

## Double Sale Prevention Logic
```python
with transaction.atomic():
    # Lock item rows
    item_ids = [line['item_id'] for line in items_data]
    locked_items = {item.id: item for item in Item.objects.select_for_update().filter(id__in=item_ids)}
    
    # Create bill and bill items
    bill = Bill.objects.create(...)
    for line in items_data:
        BillItem.objects.create(...)
        # Decrement stock via immutable ledger
        StockService.record_movement(
            shop=bill.shop,
            item=locked_items[line['item_id']],
            delta=-line['quantity'],
            reason=StockMovementReason.SALE,
            reference_id=bill.bill_number,
            user=user
        )
    # If Udhaar, record customer credit entry
    if bill.udhaar_amount_paise > 0 and bill.customer:
        CustomerLedgerEntry.objects.create(...)
```

## Verification Strategy
- Pytest suite:
  - Bill creation with single & split payment modes.
  - Stock auto-decrement check (ensuring StockLedgerEntry is created with delta = -qty).
  - Double sale prevention: `select_for_update` test.
  - Udhaar auto-booking into `CustomerLedgerEntry`.
  - Offline bill sequence generation (`{prefix}-{device}-{seq}`).
  - WhatsApp receipt URL generator.
  - Daily cashbook opening, cash-in/out, expected closing calculation, and discrepancy recording.
