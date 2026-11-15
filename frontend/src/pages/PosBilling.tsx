import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Search, Plus, Minus, Trash2, CheckCircle2,
  Share2, Printer, RotateCcw, UserCheck, Sparkles
} from 'lucide-react';
import { db, type LocalBill } from '../db';

interface CartItem {
  id: string;
  name: string;
  price: number;
  qty: number;
  unit: string;
}

interface CatalogItem {
  id: string;
  name: string;
  category: string;
  price: number;
  packPrice?: number;
  stock: number;
  unit: string;
}

export const PosBilling: React.FC = () => {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [paymentMode, setPaymentMode] = useState<'CASH' | 'UPI' | 'UDHAAR' | 'SPLIT'>('CASH');
  const [tenderedCash, setTenderedCash] = useState<number | ''>('');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [completedBill, setCompletedBill] = useState<LocalBill | null>(null);

  const categories = ['ALL', 'Cigarettes', 'Cold Drinks', 'Snacks', 'Chai & Food', 'Paan Masala'];

  const catalog: CatalogItem[] = [
    { id: '1', name: 'Gold Flake Kings', category: 'Cigarettes', price: 18.00, packPrice: 180.00, stock: 84, unit: 'Stick' },
    { id: '2', name: 'Classic Milds', category: 'Cigarettes', price: 20.00, packPrice: 200.00, stock: 6, unit: 'Stick' },
    { id: '3', name: 'Marlboro Gold Lights', category: 'Cigarettes', price: 20.00, packPrice: 200.00, stock: 45, unit: 'Stick' },
    { id: '4', name: 'Wills Navy Cut', category: 'Cigarettes', price: 12.00, packPrice: 120.00, stock: 120, unit: 'Stick' },
    { id: '5', name: 'Thums Up 250ml (Cold)', category: 'Cold Drinks', price: 20.00, stock: 4, unit: 'Bottle' },
    { id: '6', name: 'Coca Cola 250ml Can', category: 'Cold Drinks', price: 40.00, stock: 24, unit: 'Can' },
    { id: '7', name: 'Red Bull 250ml', category: 'Cold Drinks', price: 125.00, stock: 16, unit: 'Can' },
    { id: '8', name: 'Sting Energy 250ml', category: 'Cold Drinks', price: 20.00, stock: 32, unit: 'Bottle' },
    { id: '9', name: 'Maggi Masala (Cooked)', category: 'Chai & Food', price: 35.00, stock: 999, unit: 'Plate' },
    { id: '10', name: 'Adrak Masala Chai', category: 'Chai & Food', price: 12.00, stock: 999, unit: 'Cup' },
    { id: '11', name: 'Lays Magic Masala (Blue)', category: 'Snacks', price: 10.00, stock: 36, unit: 'Pack' },
    { id: '12', name: 'Kurkure Masala Munch', category: 'Snacks', price: 20.00, stock: 28, unit: 'Pack' },
    { id: '13', name: 'Rajnigandha Silver Coated', category: 'Paan Masala', price: 40.00, stock: 50, unit: 'Pouch' },
    { id: '14', name: 'Vimal Pan Masala', category: 'Paan Masala', price: 10.00, stock: 85, unit: 'Pouch' },
  ];

  const [cart, setCart] = useState<CartItem[]>([
    { id: '1', name: 'Gold Flake Kings', price: 18.00, qty: 2, unit: 'Stick' },
    { id: '10', name: 'Adrak Masala Chai', price: 12.00, qty: 1, unit: 'Cup' },
  ]);

  const addToCart = (item: CatalogItem, isPack = false) => {
    const itemPrice = isPack && item.packPrice ? item.packPrice : item.price;
    const itemName = isPack ? `${item.name} (Pack)` : item.name;
    const itemUnit = isPack ? 'Pack' : item.unit;
    const itemId = isPack ? `${item.id}-pack` : item.id;

    setCart((prev) => {
      const existing = prev.find((i) => i.id === itemId);
      if (existing) {
        return prev.map((i) => (i.id === itemId ? { ...i, qty: i.qty + 1 } : i));
      }
      return [...prev, { id: itemId, name: itemName, price: itemPrice, qty: 1, unit: itemUnit }];
    });
  };

  const updateQty = (id: string, delta: number) => {
    setCart((prev) =>
      prev
        .map((i) => (i.id === id ? { ...i, qty: Math.max(0, i.qty + delta) } : i))
        .filter((i) => i.qty > 0)
    );
  };

  const removeItem = (id: string) => {
    setCart((prev) => prev.filter((i) => i.id !== id));
  };

  const clearCart = () => {
    setCart([]);
    setTenderedCash('');
    setCustomerName('');
    setCustomerPhone('');
  };

  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.qty, 0);

  // Auto exact tendered cash for non-cash modes
  useEffect(() => {
    if (paymentMode !== 'CASH') {
      setTenderedCash(totalAmount);
    }
  }, [paymentMode, totalAmount]);

  const changeDue =
    typeof tenderedCash === 'number' && tenderedCash >= totalAmount
      ? tenderedCash - totalAmount
      : 0;

  // Handle Complete Sale
  const handleCheckout = async () => {
    if (cart.length === 0) return;

    const billNumber = `SK-${Date.now().toString().slice(-6)}`;
    const bill: LocalBill = {
      id: `bill_${Date.now()}`,
      bill_number: billNumber,
      device_id: 'counter-pos-01',
      local_sequence: Math.floor(Math.random() * 1000),
      payment_mode: paymentMode,
      total_amount_paise: Math.round(totalAmount * 100),
      final_amount_paise: Math.round(totalAmount * 100),
      items: cart.map((i) => ({
        item_id: i.id,
        item_name: i.name,
        quantity: i.qty,
        unit_price_paise: Math.round(i.price * 100),
        subtotal_paise: Math.round(i.price * i.qty * 100),
      })),
      created_at: new Date().toISOString(),
      synced: false,
    };

    try {
      await db.bills.add(bill);
      await db.outbox.add({
        idempotency_key: `outbox_${bill.id}`,
        entity_type: 'BILL',
        entity_id: bill.id,
        action: 'CREATE',
        data: bill,
        created_at: new Date().toISOString(),
      });
    } catch (e) {
      console.warn('Local DB store fallback:', e);
    }

    setCompletedBill(bill);
  };

  const startNextBill = () => {
    setCompletedBill(null);
    clearCart();
  };

  // Keyboard shortcut listener (F2 for New Bill)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F2') {
        e.preventDefault();
        startNextBill();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const filteredCatalog = catalog.filter((item) => {
    const matchesCategory = selectedCategory === 'ALL' || item.category === selectedCategory;
    const matchesSearch = item.name.toLowerCase().includes(search.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-7rem)]">
      {/* Left Column: Catalog & Quick Add Grid */}
      <div className="lg:col-span-7 flex flex-col space-y-4 overflow-hidden">
        {/* Search Bar */}
        <div className="relative">
          <Search className="w-5 h-5 absolute left-3.5 top-3.5 text-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('searchItems')}
            className="w-full h-12 pl-11 pr-4 border border-border rounded-xl bg-surface text-foreground font-medium outline-none focus:ring-2 focus:ring-foreground/20 transition-all"
          />
        </div>

        {/* Category Filter Pills */}
        <div className="flex space-x-2 overflow-x-auto pb-1 shrink-0 no-scrollbar">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border cursor-pointer ${
                selectedCategory === cat
                  ? 'bg-foreground text-background border-foreground shadow-xs'
                  : 'bg-surface border-border text-muted hover:bg-surfaceHover hover:text-foreground'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Items Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 overflow-y-auto pr-1 flex-1">
          {filteredCatalog.map((item) => {
            const isLowStock = item.stock <= 10;
            return (
              <div
                key={item.id}
                className="p-3.5 border border-border rounded-xl bg-surface hover:border-foreground/40 transition-all flex flex-col justify-between shadow-2xs hover:shadow-xs group"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <span className="font-bold text-sm text-foreground line-clamp-1">{item.name}</span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-[11px] text-muted">{item.category}</span>
                    <span className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                      isLowStock ? 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300' : 'text-muted'
                    }`}>
                      {item.stock} in stock
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t border-border/60 mt-2 flex items-center justify-between">
                  <div>
                    <span className="font-mono text-base font-extrabold text-foreground">
                      ₹{item.price.toFixed(2)}
                    </span>
                    <span className="text-[10px] text-muted block">per {item.unit}</span>
                  </div>

                  <div className="flex items-center space-x-1.5">
                    {item.packPrice && (
                      <button
                        onClick={() => addToCart(item, true)}
                        className="px-2 py-1.5 bg-surfaceHover hover:bg-surface border border-border text-[11px] font-bold rounded-lg transition-colors cursor-pointer"
                        title="Add full pack"
                      >
                        Pack ₹{item.packPrice}
                      </button>
                    )}
                    <button
                      onClick={() => addToCart(item, false)}
                      className="p-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-2xs transition-all active:scale-95 cursor-pointer"
                      title="Add single stick/unit"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Active Bill & Rapid Checkout (BILL-04, BILL-05) */}
      <div className="lg:col-span-5 border border-border bg-surface rounded-2xl flex flex-col justify-between p-5 h-full shadow-xs">
        {/* Header with Clear & Hold actions */}
        <div>
          <div className="flex justify-between items-center border-b border-border pb-3">
            <div>
              <span className="font-extrabold text-base tracking-tight text-foreground">Active Counter Bill</span>
              <span className="text-xs text-muted block">Items: {cart.length}</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={clearCart}
                disabled={cart.length === 0}
                className="px-2.5 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition-colors disabled:opacity-40 cursor-pointer"
              >
                {t('clear')}
              </button>
            </div>
          </div>

          {/* Cart Items List */}
          <div className="space-y-2.5 overflow-y-auto max-h-[32vh] lg:max-h-[38vh] py-3 pr-1">
            {cart.length === 0 ? (
              <div className="text-center py-12 text-muted text-sm space-y-1">
                <Sparkles className="w-8 h-8 mx-auto text-muted/60 mb-2" />
                <p className="font-medium">{t('cartEmpty')}</p>
                <p className="text-xs text-muted">Tap any item from the left catalog to start billing</p>
              </div>
            ) : (
              cart.map((item) => (
                <div
                  key={item.id}
                  className="p-3 border border-border rounded-xl bg-background flex items-center justify-between shadow-2xs"
                >
                  <div className="flex-1 pr-2">
                    <div className="font-bold text-sm text-foreground">{item.name}</div>
                    <div className="text-xs text-muted font-mono">
                      ₹{item.price.toFixed(2)} × {item.qty} = <span className="font-bold text-foreground">₹{(item.price * item.qty).toFixed(2)}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1.5 shrink-0">
                    <button
                      onClick={() => updateQty(item.id, -1)}
                      className="w-8 h-8 rounded-lg border border-border bg-surface hover:bg-surfaceHover flex items-center justify-center transition-colors cursor-pointer"
                    >
                      <Minus className="w-3.5 h-3.5" />
                    </button>
                    <span className="w-7 text-center font-bold text-sm font-mono">{item.qty}</span>
                    <button
                      onClick={() => updateQty(item.id, 1)}
                      className="w-8 h-8 rounded-lg border border-border bg-surface hover:bg-surfaceHover flex items-center justify-center transition-colors cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="w-8 h-8 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30 flex items-center justify-center transition-colors ml-1 cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Checkout & Payment Area */}
        <div className="border-t border-border pt-4 space-y-3.5">
          {/* Payment Method Selector */}
          <div>
            <label className="text-xs font-bold text-muted uppercase tracking-wider block mb-1.5">
              {t('paymentMode')}
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[
                { key: 'CASH', label: t('cash'), color: 'emerald' },
                { key: 'UPI', label: t('upi'), color: 'blue' },
                { key: 'UDHAAR', label: t('udhaar'), color: 'amber' },
                { key: 'SPLIT', label: t('split'), color: 'purple' },
              ].map((mode) => (
                <button
                  key={mode.key}
                  onClick={() => setPaymentMode(mode.key as any)}
                  className={`py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                    paymentMode === mode.key
                      ? mode.key === 'CASH'
                        ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                        : mode.key === 'UPI'
                        ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                        : mode.key === 'UDHAAR'
                        ? 'bg-amber-600 text-white border-amber-600 shadow-xs'
                        : 'bg-purple-600 text-white border-purple-600 shadow-xs'
                      : 'bg-background border-border text-muted hover:bg-surfaceHover'
                  }`}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          </div>

          {/* Conditional Udhaar Customer Inputs */}
          {paymentMode === 'UDHAAR' && (
            <div className="p-3 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/40 rounded-xl space-y-2">
              <div className="flex items-center space-x-1.5 text-xs font-bold text-amber-800 dark:text-amber-300">
                <UserCheck className="w-4 h-4" />
                <span>Link Udhaar to Customer Ledger</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  placeholder="Customer Name (e.g. Ramesh)"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="h-10 px-3 border border-border rounded-lg bg-background text-xs font-medium outline-none"
                />
                <input
                  type="tel"
                  placeholder="10-digit Phone"
                  value={customerPhone}
                  onChange={(e) => setCustomerPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  className="h-10 px-3 border border-border rounded-lg bg-background text-xs font-medium outline-none"
                />
              </div>
            </div>
          )}

          {/* Tendered Cash & Change Calculation (Cash Mode) */}
          {paymentMode === 'CASH' && (
            <div className="p-3 bg-background border border-border rounded-xl space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted font-medium">Tendered Cash:</span>
                <div className="flex items-center space-x-1">
                  {[50, 100, 200, 500].map((denom) => (
                    <button
                      key={denom}
                      onClick={() => setTenderedCash(denom)}
                      className="px-2 py-0.5 rounded border border-border text-[10px] font-mono font-bold hover:bg-surfaceHover cursor-pointer"
                    >
                      ₹{denom}
                    </button>
                  ))}
                  <button
                    onClick={() => setTenderedCash(totalAmount)}
                    className="px-2 py-0.5 rounded border border-border text-[10px] font-bold bg-surface hover:bg-surfaceHover cursor-pointer"
                  >
                    Exact
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <input
                  type="number"
                  placeholder="Received ₹"
                  value={tenderedCash}
                  onChange={(e) => setTenderedCash(e.target.value === '' ? '' : parseFloat(e.target.value))}
                  className="h-9 w-28 px-2 border border-border rounded-lg font-mono font-bold text-sm bg-surface outline-none"
                />
                <div className="text-right">
                  <span className="text-[11px] text-muted block">Change to Return</span>
                  <span className="font-mono text-base font-extrabold text-emerald-600 dark:text-emerald-400">
                    ₹{changeDue.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Bill Total & Final CTA */}
          <div className="flex items-center justify-between pt-1">
            <span className="text-sm font-bold text-muted uppercase tracking-wider">{t('total')}:</span>
            <span className="text-3xl font-extrabold font-mono text-foreground">
              ₹{totalAmount.toFixed(2)}
            </span>
          </div>

          <button
            onClick={handleCheckout}
            disabled={cart.length === 0}
            className="w-full h-13 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold rounded-xl shadow-md transition-all active:scale-[0.99] flex items-center justify-center space-x-2 text-base disabled:opacity-40 cursor-pointer min-h-pos"
          >
            <CheckCircle2 className="w-5 h-5" />
            <span>Complete Sale & Print (Enter)</span>
          </button>
        </div>
      </div>

      {/* Bill Completed Success Modal */}
      {completedBill && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="w-full max-w-sm bg-surface border border-border rounded-2xl p-6 shadow-2xl space-y-5">
            <div className="text-center space-y-2">
              <div className="w-14 h-14 bg-emerald-500/20 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-extrabold text-foreground">{t('billSuccess')}</h3>
              <p className="font-mono text-xs text-muted font-bold">
                {completedBill.bill_number} • ₹{(completedBill.final_amount_paise / 100).toFixed(2)} ({completedBill.payment_mode})
              </p>
            </div>

            <div className="p-3 bg-background border border-border rounded-xl space-y-1.5 text-xs">
              <div className="flex justify-between text-muted">
                <span>Items Billed:</span>
                <span className="font-bold text-foreground">{completedBill.items.length} items</span>
              </div>
              <div className="flex justify-between text-muted">
                <span>Saved Offline (Dexie):</span>
                <span className="text-emerald-600 font-bold">✓ Synced to Outbox</span>
              </div>
            </div>

            <div className="space-y-2 pt-1">
              <a
                href={`https://wa.me/?text=Namaste!%20Your%20bill%20from%20Sharma%20Kirana%20is%20Rs%20${(completedBill.final_amount_paise / 100).toFixed(2)}.%20Bill%20No:%20${completedBill.bill_number}`}
                target="_blank"
                rel="noreferrer"
                className="w-full h-11 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl flex items-center justify-center space-x-2 text-sm transition-colors cursor-pointer"
              >
                <Share2 className="w-4 h-4" />
                <span>{t('shareWhatsApp')}</span>
              </a>

              <button
                onClick={() => window.print()}
                className="w-full h-11 bg-surface border border-border hover:bg-surfaceHover text-foreground font-semibold rounded-xl flex items-center justify-center space-x-2 text-sm transition-colors cursor-pointer"
              >
                <Printer className="w-4 h-4 text-muted" />
                <span>{t('printReceipt')}</span>
              </button>

              <button
                onClick={startNextBill}
                className="w-full h-11 bg-foreground text-background font-bold rounded-xl flex items-center justify-center space-x-2 text-sm transition-all active:scale-[0.99] cursor-pointer"
              >
                <RotateCcw className="w-4 h-4" />
                <span>{t('newBill')}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
