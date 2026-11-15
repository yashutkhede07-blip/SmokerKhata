# Plan 05-02 Summary: Batch Push API & Transactional Idempotent Processing

- Implemented `POST /api/sync/push/` handled by `SyncPushView` and `SyncEngineService.process_batch`.
- Supported operations:
  - `bill`: Creates bill atomically using `BillingService.create_bill_atomic` respecting offline sequences.
  - `customer_ledger`: Appends credit or payment entry.
  - `supplier_ledger`: Appends bill or payment entry.
  - `item`, `category`, `customer`, `supplier`: Creates, LWW updates (`SYNC-09`), or soft-deletes.
- Full idempotency deduplication (`SYNC-04`): replaying keys returns confirmed without re-executing.
- Append-only policy strictly enforced for bills and financial ledgers (`SYNC-08`).
