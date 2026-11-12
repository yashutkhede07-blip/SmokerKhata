# Phase 5 Research: Offline Sync Engine

## Domain & Architecture Analysis

### Core Problem & Guarantees
- India retail environments (tea stalls, cigarette kiosks, snacks shops) experience intermittent 2G/4G connectivity, phone restarts, and battery drops.
- **Top non-negotiable:** Zero data loss. No customer bill, stock deduction, udhaar credit, or cash entry can be lost or double-counted upon reconnect.
- Offline clients generate UUIDv4 IDs locally so records can reference each other offline without server round-trips (`SYNC-01`).
- Server must provide two fundamental sync endpoints:
  1. `POST /api/sync/push`: Batch push of client outbox items wrapped in atomic transaction, guarded by idempotency keys (`SYNC-04`).
  2. `GET /api/sync/pull?cursor=...`: Monotonic integer cursor pull returning changes per shop since the requested sequence (`SYNC-05`).

### Data Model Design

#### 1. Monotonic Server Sequence (`SyncLog` / `SyncRecord`)
- Avoid timestamp-based synchronization (clock skew across devices/server causes missing records or re-read loops).
- Maintain a monotonic sequence counter per `Shop`:
  - `ShopSyncSequence` (or shop integer sequence field with `select_for_update`) generating integer `1, 2, 3...`.
  - Alternatively, a global/shop-scoped auto-increment `BigIntegerField` sequence on a `SyncJournalEntry` table.
- Every mutating event (create/update/delete) on syncable entities (`Item`, `Category`, `Customer`, `Supplier`, `Bill`, `CustomerLedgerEntry`, `SupplierLedgerEntry`, `StockLedgerEntry`, `CashBookDay`, `CashBookEntry`) writes an entry to `SyncJournalEntry`:
  - `id`: Auto-incrementing primary key or monotonic `sequence` (BigInteger)
  - `shop`: FK to Shop
  - `entity_type`: Model name (e.g. `'item'`, `'bill'`, `'customer_ledger'`)
  - `entity_id`: UUID of the affected record
  - `action`: `'CREATE'`, `'UPDATE'`, `'DELETE'`
  - `payload`: JSON representation of current state (for pull)
  - `created_at`: UTC timestamp

#### 2. Idempotency & Operation Outbox (`SyncOperation`)
- `SyncOperation` model:
  - `id`: UUID PK
  - `shop`: FK to Shop
  - `idempotency_key`: string (UUID or unique client identifier per operation)
  - `entity_type`: string
  - `entity_id`: UUID
  - `action`: string
  - `status`: `'PROCESSED'`, `'FAILED'`, `'REJECTED'`
  - `created_at`: UTC timestamp
  - `processed_at`: UTC timestamp
  - Unique constraint: `(shop, idempotency_key)`

### Conflict Resolution Strategy (`SYNC-08`, `SYNC-09`)
1. **Append-Only Immutable Ledgers:**
   - Financial & stock ledger entries (`Bill`, `BillItem`, `CustomerLedgerEntry`, `SupplierLedgerEntry`, `StockLedgerEntry`, `CashBookEntry`) are strictly append-only.
   - If a client pushes an entry that already exists (matched by UUID or idempotency key), it's treated as idempotent success (no-op, acknowledged).
   - Never overwritten.
2. **Entity Mutables (Items, Categories, Customers, Suppliers):**
   - For non-financial fields (e.g. item name, category name, customer phone): Last-write-wins (LWW) based on server processing timestamp or client timestamp with fallback.
   - Losing version is captured in `AuditLog` (or logged for Phase 6 audit log integration).
3. **Soft-Deletes:**
   - Deletions are represented by `is_active=False` or `deleted_at=timestamp`.

### Batch Push Semantics (`SYNC-03`, `SYNC-04`, `SYNC-06`)
- `POST /api/sync/push`:
  - Payload: `{ "device_id": "...", "operations": [ { "idempotency_key": "...", "entity_type": "...", "action": "...", "data": {...} } ] }`
  - Transaction boundary: The batch of operations is processed within `transaction.atomic()`.
  - For each operation:
    - Check if `idempotency_key` exists in `SyncOperation`.
    - If exists: skip execution, mark as confirmed in response.
    - If new: route to entity handler (e.g. create bill via `BillingService.create_bill_atomic`, create ledger entry, update item), log to `SyncOperation` and write to `SyncJournalEntry`.
  - Return: `{ "success": true, "processed_keys": [...], "current_cursor": <latest_shop_sequence> }`.

### Monotonic Pull Semantics (`SYNC-05`)
- `GET /api/sync/pull?cursor=0&limit=100`:
  - Filters `SyncJournalEntry.objects.filter(shop=request.shop, sequence__gt=cursor).order_by('sequence')[:limit]`.
  - Return: `{ "changes": [ ... ], "next_cursor": <last_sequence_in_batch_or_current>, "has_more": bool }`.
  - If no new changes, returns `next_cursor=cursor` and `has_more=false`.

### Verification Strategy
- Pytest suite:
  - Idempotency test (pushing exact batch twice produces identical state).
  - Monotonic pull test (cursor 0 pulls changes, next cursor returns only delta).
  - Multi-device sequence interleaving test.
  - Conflict resolution test (immutable entries preserved, mutable fields updated with audit trace).
