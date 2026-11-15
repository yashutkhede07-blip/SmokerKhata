import Dexie, { type Table } from 'dexie';

export interface LocalItem {
  id: string;
  name: string;
  category_id?: string;
  category_name?: string;
  selling_price_paise: number;
  cost_price_paise: number;
  is_quick_add: boolean;
  quick_add_order: number;
  is_active: boolean;
}

export interface LocalCustomer {
  id: string;
  name: string;
  phone: string;
  balance_paise: number;
}

export interface LocalBill {
  id: string;
  bill_number: string;
  device_id: string;
  local_sequence: number;
  customer_id?: string;
  payment_mode: string;
  total_amount_paise: number;
  final_amount_paise: number;
  items: Array<{
    item_id: string;
    item_name: string;
    quantity: number;
    unit_price_paise: number;
    subtotal_paise: number;
  }>;
  created_at: string;
  synced: boolean;
}

export interface OutboxOperation {
  id?: number;
  idempotency_key: string;
  entity_type: string;
  entity_id: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  data: any;
  created_at: string;
}

export class SmokerKhataDB extends Dexie {
  items!: Table<LocalItem, string>;
  customers!: Table<LocalCustomer, string>;
  bills!: Table<LocalBill, string>;
  outbox!: Table<OutboxOperation, number>;

  constructor() {
    super('SmokerKhataDB');
    this.version(1).stores({
      items: 'id, name, category_name, is_quick_add, is_active',
      customers: 'id, name, phone, balance_paise',
      bills: 'id, bill_number, created_at, synced',
      outbox: '++id, idempotency_key, entity_type, action, created_at',
    });
  }
}

export const db = new SmokerKhataDB();
