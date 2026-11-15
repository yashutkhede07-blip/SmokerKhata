from django.db import transaction
from django.utils import timezone

from sync.models import SyncOperation, SyncOperationStatus, SyncActionType, ShopSyncSequence
from sync.services import SyncJournalService
from billing.services import BillingService
from ledgers.models import (
    Customer, CustomerLedgerEntry, CustomerEntryType,
    Supplier, SupplierLedgerEntry, SupplierEntryType,
)
from inventory.models import Item, Category


class SyncEngineService:
    """
    Processes a batch of client outbox operations inside a single
    atomic transaction. Deduplicates via SyncOperation idempotency keys.
    """

    # Entity types that are append-only / immutable (SYNC-08)
    APPEND_ONLY_ENTITIES = {
        'bill', 'customer_ledger', 'supplier_ledger', 'stock_ledger', 'cashbook_entry',
    }
    # Entity types that support last-write-wins updates (SYNC-09)
    MUTABLE_ENTITIES = {
        'item', 'category', 'customer', 'supplier',
    }

    @staticmethod
    @transaction.atomic
    def process_batch(shop, device_id, operations, user=None):
        """
        Process a batch of sync operations.

        Returns:
            dict with 'processed_keys' (list), 'skipped_keys' (list),
            'failed_keys' (list), and 'current_cursor' (int).
        """
        processed_keys = []
        skipped_keys = []
        failed_keys = []

        # Pre-fetch existing idempotency keys for this shop in one query
        incoming_keys = [op['idempotency_key'] for op in operations]
        existing_keys = set(
            SyncOperation.objects.filter(
                shop=shop,
                idempotency_key__in=incoming_keys,
            ).values_list('idempotency_key', flat=True)
        )

        for op in operations:
            idem_key = op['idempotency_key']

            # Already processed — skip (idempotent acknowledgement)
            if idem_key in existing_keys:
                skipped_keys.append(idem_key)
                continue

            entity_type = op['entity_type']
            action = op['action']
            entity_id = op['entity_id']
            data = op.get('data', {})

            try:
                SyncEngineService._dispatch_operation(
                    shop=shop,
                    device_id=device_id,
                    entity_type=entity_type,
                    action=action,
                    entity_id=entity_id,
                    data=data,
                    user=user,
                )

                # Record processed operation
                SyncOperation.objects.create(
                    shop=shop,
                    idempotency_key=idem_key,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                    status=SyncOperationStatus.PROCESSED,
                )

                # Record in journal
                SyncJournalService.record_change(
                    shop=shop,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                    payload=data,
                )

                processed_keys.append(idem_key)

            except Exception:
                # Record failure but don't break the batch
                SyncOperation.objects.create(
                    shop=shop,
                    idempotency_key=idem_key,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                    status=SyncOperationStatus.FAILED,
                )
                failed_keys.append(idem_key)

        # Get current cursor
        try:
            seq = ShopSyncSequence.objects.get(shop=shop)
            current_cursor = seq.current_sequence
        except ShopSyncSequence.DoesNotExist:
            current_cursor = 0

        return {
            'processed_keys': processed_keys,
            'skipped_keys': skipped_keys,
            'failed_keys': failed_keys,
            'current_cursor': current_cursor,
        }

    @staticmethod
    def _dispatch_operation(shop, device_id, entity_type, action, entity_id, data, user=None):
        """
        Route an operation to the appropriate domain handler.
        """
        if entity_type == 'bill' and action == 'CREATE':
            SyncEngineService._handle_bill_create(shop, device_id, data, user)
        elif entity_type == 'customer_ledger' and action == 'CREATE':
            SyncEngineService._handle_customer_ledger_create(shop, data, user)
        elif entity_type == 'supplier_ledger' and action == 'CREATE':
            SyncEngineService._handle_supplier_ledger_create(shop, data, user)
        elif entity_type in SyncEngineService.MUTABLE_ENTITIES:
            if action == 'CREATE':
                SyncEngineService._handle_mutable_create(shop, entity_type, entity_id, data, user)
            elif action == 'UPDATE':
                SyncEngineService._handle_mutable_update(shop, entity_type, entity_id, data)
        # DELETE on mutable entities → soft-delete
        elif action == 'DELETE' and entity_type in SyncEngineService.MUTABLE_ENTITIES:
            SyncEngineService._handle_mutable_delete(shop, entity_type, entity_id)

    @staticmethod
    def _handle_bill_create(shop, device_id, data, user):
        """Create bill through BillingService (handles its own idempotency by bill_number)."""
        bill_data = {
            'device_id': device_id,
            'bill_number': data.get('bill_number'),
            'local_sequence': data.get('local_sequence'),
            'payment_mode': data.get('payment_mode', 'CASH'),
            'items': data.get('items', []),
            'discount_paise': data.get('discount_paise', 0),
            'tax_paise': data.get('tax_paise', 0),
            'cash_amount_paise': data.get('cash_amount_paise', 0),
            'upi_amount_paise': data.get('upi_amount_paise', 0),
            'udhaar_amount_paise': data.get('udhaar_amount_paise', 0),
            'customer_id': data.get('customer_id'),
            'notes': data.get('notes', ''),
        }
        BillingService.create_bill_atomic(shop=shop, user=user, validated_data=bill_data)

    @staticmethod
    def _handle_customer_ledger_create(shop, data, user):
        """Append-only customer ledger entry."""
        CustomerLedgerEntry.objects.create(
            shop=shop,
            customer_id=data['customer_id'],
            entry_type=data.get('entry_type', CustomerEntryType.CREDIT_GIVEN),
            amount_paise=data['amount_paise'],
            notes=data.get('notes', ''),
            reference_id=data.get('reference_id', ''),
            created_by=user,
        )

    @staticmethod
    def _handle_supplier_ledger_create(shop, data, user):
        """Append-only supplier ledger entry."""
        SupplierLedgerEntry.objects.create(
            shop=shop,
            supplier_id=data['supplier_id'],
            entry_type=data.get('entry_type', SupplierEntryType.PURCHASE_BILL),
            amount_paise=data['amount_paise'],
            bill_number=data.get('bill_number', ''),
            notes=data.get('notes', ''),
            created_by=user,
        )

    @staticmethod
    def _handle_mutable_create(shop, entity_type, entity_id, data, user):
        """Create a new mutable entity."""
        if entity_type == 'item':
            Item.objects.create(
                id=entity_id,
                shop=shop,
                name=data['name'],
                selling_price_paise=data['selling_price_paise'],
                cost_price_paise=data.get('cost_price_paise', 0),
                category_id=data.get('category_id'),
                barcode=data.get('barcode', ''),
            )
        elif entity_type == 'category':
            Category.objects.create(
                id=entity_id,
                shop=shop,
                name=data['name'],
                display_order=data.get('display_order', 0),
            )
        elif entity_type == 'customer':
            Customer.objects.create(
                id=entity_id,
                shop=shop,
                name=data['name'],
                phone=data.get('phone', ''),
            )
        elif entity_type == 'supplier':
            Supplier.objects.create(
                id=entity_id,
                shop=shop,
                name=data['name'],
                phone=data.get('phone', ''),
                address=data.get('address', ''),
            )

    @staticmethod
    def _handle_mutable_update(shop, entity_type, entity_id, data):
        """Last-write-wins update on non-financial fields (SYNC-09)."""
        model_map = {
            'item': Item,
            'category': Category,
            'customer': Customer,
            'supplier': Supplier,
        }
        model = model_map.get(entity_type)
        if not model:
            return

        try:
            obj = model.objects.get(id=entity_id, shop=shop)
        except model.DoesNotExist:
            return

        # Apply updatable fields
        updatable = data.get('fields', data)
        for field, value in updatable.items():
            if field not in ('id', 'shop', 'shop_id', 'created_at', 'deleted_at'):
                if hasattr(obj, field):
                    setattr(obj, field, value)
        obj.save()

    @staticmethod
    def _handle_mutable_delete(shop, entity_type, entity_id):
        """Soft-delete a mutable entity."""
        model_map = {
            'item': Item,
            'category': Category,
            'customer': Customer,
            'supplier': Supplier,
        }
        model = model_map.get(entity_type)
        if not model:
            return

        try:
            obj = model.all_objects.get(id=entity_id, shop=shop)
            obj.delete()  # triggers soft-delete
        except model.DoesNotExist:
            pass
