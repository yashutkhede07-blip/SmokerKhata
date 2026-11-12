from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import exceptions

from billing.models import Bill, BillItem, DeviceSequenceTracker, PaymentMode, BillStatus
from inventory.models import Item, ItemVariant, StockMovementReason
from inventory.services import StockService
from ledgers.models import Customer, CustomerLedgerEntry, CustomerEntryType, PaymentMode as LedgerPaymentMode

class BillingService:
    @staticmethod
    def get_next_bill_number(shop, device_id='COUNTER1'):
        with transaction.atomic():
            tracker, _ = DeviceSequenceTracker.objects.select_for_update().get_or_create(
                shop=shop,
                device_id=device_id,
                defaults={'last_sequence': 0}
            )
            tracker.last_sequence += 1
            tracker.save()
            bill_number = f"{shop.prefix}-{device_id}-{tracker.last_sequence:06d}"
            return bill_number, tracker.last_sequence

    @staticmethod
    @transaction.atomic
    def create_bill_atomic(shop, user, validated_data):
        device_id = validated_data.get('device_id', 'COUNTER1')
        bill_number = validated_data.get('bill_number')
        local_sequence = validated_data.get('local_sequence')

        # Idempotency check: if bill_number provided and already exists for this shop, return it
        if bill_number:
            existing = Bill.objects.filter(shop=shop, bill_number=bill_number).first()
            if existing:
                return existing, False  # (bill, created=False)

        # Generate sequence if not provided
        if not bill_number or not local_sequence:
            generated_number, seq = BillingService.get_next_bill_number(shop, device_id)
            if not bill_number:
                bill_number = generated_number
            if not local_sequence:
                local_sequence = seq

        items_input = validated_data['items']
        item_ids = [item_data['item_id'] for item_data in items_input]

        # Double-sale prevention: row-level lock on items
        locked_items = {
            str(item.id): item
            for item in Item.objects.select_for_update().filter(id__in=item_ids, shop=shop)
        }

        # Calculate totals
        total_amount_paise = 0
        bill_items_to_create = []

        for item_data in items_input:
            item_id = str(item_data['item_id'])
            if item_id not in locked_items:
                raise exceptions.ValidationError(f"Item {item_id} not found in this shop.")

            item = locked_items[item_id]
            variant_id = item_data.get('variant_id')
            variant = None
            if variant_id:
                variant = get_object_or_404(ItemVariant, id=variant_id, item=item)
                unit_price = variant.effective_selling_price_paise
                item_name = f"{item.name} - {variant.name}"
            else:
                unit_price = item_data.get('unit_price_paise') or item.selling_price_paise
                item_name = item.name

            quantity = item_data['quantity']
            subtotal = unit_price * quantity
            total_amount_paise += subtotal

            bill_items_to_create.append({
                'item': item,
                'variant': variant,
                'item_name': item_name,
                'quantity': quantity,
                'unit_price_paise': unit_price,
                'subtotal_paise': subtotal
            })

        discount_paise = validated_data.get('discount_paise', 0)
        tax_paise = validated_data.get('tax_paise', 0)
        final_amount_paise = max(0, total_amount_paise - discount_paise + tax_paise)

        payment_mode = validated_data['payment_mode']
        cash_amount = validated_data.get('cash_amount_paise', 0)
        upi_amount = validated_data.get('upi_amount_paise', 0)
        udhaar_amount = validated_data.get('udhaar_amount_paise', 0)

        if payment_mode == PaymentMode.CASH:
            cash_amount = final_amount_paise
            upi_amount = 0
            udhaar_amount = 0
        elif payment_mode == PaymentMode.UPI:
            upi_amount = final_amount_paise
            cash_amount = 0
            udhaar_amount = 0
        elif payment_mode == PaymentMode.UDHAAR:
            udhaar_amount = final_amount_paise
            cash_amount = 0
            upi_amount = 0
        elif payment_mode == PaymentMode.SPLIT:
            split_total = cash_amount + upi_amount + udhaar_amount
            if split_total != final_amount_paise:
                raise exceptions.ValidationError(
                    f"Split payments sum (₹{split_total/100:.2f}) does not match final bill amount (₹{final_amount_paise/100:.2f})."
                )

        customer = None
        customer_id = validated_data.get('customer_id')
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id, shop=shop)

        # Create Bill record
        bill = Bill.objects.create(
            shop=shop,
            bill_number=bill_number,
            device_id=device_id,
            local_sequence=local_sequence,
            customer=customer,
            total_amount_paise=total_amount_paise,
            discount_paise=discount_paise,
            tax_paise=tax_paise,
            final_amount_paise=final_amount_paise,
            payment_mode=payment_mode,
            cash_amount_paise=cash_amount,
            upi_amount_paise=upi_amount,
            udhaar_amount_paise=udhaar_amount,
            status=BillStatus.COMPLETED,
            notes=validated_data.get('notes', ''),
            created_by=user
        )

        # Create BillItems and Decrement Stock atomically
        for line in bill_items_to_create:
            BillItem.objects.create(
                bill=bill,
                item=line['item'],
                variant=line['variant'],
                item_name=line['item_name'],
                quantity=line['quantity'],
                unit_price_paise=line['unit_price_paise'],
                subtotal_paise=line['subtotal_paise']
            )

            # Auto-decrement stock via immutable ledger
            StockService.record_movement(
                shop=shop,
                item=line['item'],
                variant=line['variant'],
                delta=-line['quantity'],
                reason=StockMovementReason.SALE,
                reference_id=bill.bill_number,
                notes=f"Sold on Bill {bill.bill_number}",
                user=user
            )

        # If Udhaar is part of the bill, record in Customer ledger
        if udhaar_amount > 0 and customer:
            CustomerLedgerEntry.objects.create(
                shop=shop,
                customer=customer,
                entry_type=CustomerEntryType.CREDIT_GIVEN,
                amount_paise=udhaar_amount,
                notes=f"Bill {bill.bill_number} (Udhaar)",
                reference_id=bill.bill_number,
                created_by=user
            )

        return bill, True
