# Phase 03: Customer & Supplier Ledgers — Technical Research

## Problem & Domain Analysis

Small retail shops in India run heavily on credit (**Udhaar**):
1. **Customer Udhaar Ledger**:
   - Customers buy cigarettes, chai, chips, and snacks on daily credit and settle weekly/monthly.
   - Every transaction is either **Credit Given** (store extends goods on credit, increasing debt) or **Payment Received** (customer settles in full or part, reducing debt).
   - Zero-loss and tamper-proof ledger entries: All entries are strictly append-only.
   - Customers must be sorted by highest outstanding balance (`CUST-05`).
   - WhatsApp payment reminder links (`wa.me/91...?text=...`) constructed dynamically with the shop name, outstanding balance formatted in rupees, and payment request text (`CUST-06`).
   - Aging report: Days since oldest unsettled credit entry (`CUST-07`).

2. **Supplier Ledger**:
   - Retailers receive wholesale inventory deliveries (ITC cigarettes, Pepsi/Coke crates, Haldiram snacks).
   - Staff record **Purchase Bills** (supplier, items, invoice number, amount, date) and **Supplier Payments** (cash, UPI, bank transfer).
   - Ledger tracks purchase bills, payments, and net balance owed to the supplier (`SUPP-04`).

3. **Core Architectural Constraints**:
   - Money stored as **integer paise** (`BigIntegerField`).
   - Strict soft-deletes (`deleted_at`).
   - Tenant isolation via `ShopScopedModel`.
   - Immutable financial transaction lines.

## Data Models Architecture

### App: `backend/ledgers/`
Co-locates customer and supplier ledger logic to maintain consistency.

### 1. `Customer` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`)
- `shop`: FK(Shop)
- `name`: CharField(150)
- `phone`: CharField(15, blank=True)
- `notes`: TextField(blank=True)
- `credit_limit_paise`: BigIntegerField(default=0) (0 = unlimited)

### 2. `CustomerLedgerEntry` (`UUIDModel`, `TimeStampedModel`)
- Immutable financial ledger table.
- `shop`: FK(Shop)
- `customer`: FK(Customer, on_delete=CASCADE, related_name='ledger_entries')
- `entry_type`: CharField(choices: `CREDIT_GIVEN`, `PAYMENT_RECEIVED`)
- `amount_paise`: BigIntegerField() (always positive; sign is determined by entry_type)
- `payment_mode`: CharField(choices: `CASH`, `UPI`, `BANK_TRANSFER`, `OTHER`, blank=True)
- `notes`: TextField(blank=True)
- `reference_id`: CharField(100, blank=True) (e.g. POS Bill ID or receipt number)
- `created_by`: FK(User, null=True, on_delete=SET_NULL)

### Current Customer Balance Calculation
`balance_paise` = `Sum(CREDIT_GIVEN) - Sum(PAYMENT_RECEIVED)`.
A positive balance means customer owes money to the shop.

### 3. `Supplier` (`ShopScopedModel`, `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`)
- `shop`: FK(Shop)
- `name`: CharField(150)
- `phone`: CharField(15, blank=True)
- `address`: TextField(blank=True)
- `gstin`: CharField(20, blank=True)

### 4. `SupplierLedgerEntry` (`UUIDModel`, `TimeStampedModel`)
- Immutable supplier transaction line.
- `shop`: FK(Shop)
- `supplier`: FK(Supplier, on_delete=CASCADE, related_name='ledger_entries')
- `entry_type`: CharField(choices: `PURCHASE_BILL`, `PAYMENT_MADE`)
- `amount_paise`: BigIntegerField()
- `bill_number`: CharField(100, blank=True)
- `bill_date`: DateField(default=timezone.now)
- `payment_mode`: CharField(choices: `CASH`, `UPI`, `BANK_TRANSFER`, `CHEQUE`, blank=True)
- `notes`: TextField(blank=True)
- `created_by`: FK(User, null=True, on_delete=SET_NULL)

### Current Supplier Balance Calculation
`balance_paise` = `Sum(PURCHASE_BILL) - Sum(PAYMENT_MADE)`.
A positive balance means shop owes money to the supplier.

## WhatsApp Reminder Formatting
URL pattern:
`https://wa.me/91{customer.phone}?text={encoded_message}`
Message format:
"Namaste {customer.name}, aapka {shop.name} par kul baki ₹{balance_in_rupees} hai. Kripya bhugtan karein. Dhanyawad!"

## Verification Strategy
- Pytest suite:
  - Customer CRUD, Credit entries, Payment entries, balance calculations.
  - Sorting customers by highest outstanding balance (`balance_paise`).
  - WhatsApp link generation with valid Indian phone numbers and amounts.
  - Aging debt report (grouping / calculation of days since oldest unpaid credit).
  - Supplier CRUD, Purchase bill entries, Payment entries, balance calculations.
  - Immutability check on `CustomerLedgerEntry` and `SupplierLedgerEntry` (updates/deletions raise ValueError).
