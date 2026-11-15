import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, Plus, Minus, Send } from 'lucide-react';

interface CartItem {
  id: string;
  name: string;
  price: number;
  qty: number;
}

export const PosBilling: React.FC = () => {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [paymentMode, setPaymentMode] = useState<'CASH' | 'UPI' | 'UDHAAR' | 'SPLIT'>('CASH');

  const [cart, setCart] = useState<CartItem[]>([
    { id: '1', name: 'Gold Flake Kings', price: 18.00, qty: 2 },
    { id: '2', name: 'Classic Milds', price: 20.00, qty: 1 },
    { id: '3', name: 'Thums Up 250ml', price: 20.00, qty: 1 },
  ]);

  const quickItems = [
    { id: '1', name: 'Gold Flake Kings', price: 18.00 },
    { id: '2', name: 'Classic Milds', price: 20.00 },
    { id: '3', name: 'Thums Up 250ml', price: 20.00 },
    { id: '4', name: 'Maggi Masala', price: 14.00 },
    { id: '5', name: 'Chai (Glass)', price: 10.00 },
    { id: '6', name: 'Lays Magic Masala', price: 10.00 },
  ];

  const addToCart = (item: { id: string; name: string; price: number }) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.id === item.id);
      if (existing) {
        return prev.map((i) => (i.id === item.id ? { ...i, qty: i.qty + 1 } : i));
      }
      return [...prev, { ...item, qty: 1 }];
    });
  };

  const updateQty = (id: string, delta: number) => {
    setCart((prev) =>
      prev
        .map((i) => (i.id === id ? { ...i, qty: Math.max(0, i.qty + delta) } : i))
        .filter((i) => i.qty > 0)
    );
  };

  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.qty, 0);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-6rem)]">
      {/* Left: Quick Add & Catalog */}
      <div className="lg:col-span-7 flex flex-col space-y-4 overflow-y-auto">
        <div className="relative">
          <Search className="w-5 h-5 absolute left-3 top-3.5 text-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('searchItems')}
            className="w-full h-12 pl-10 pr-4 border border-border rounded-xl bg-surface text-foreground outline-none focus:border-foreground"
          />
        </div>

        {/* Quick Add Grid (BILL-02) */}
        <div>
          <h2 className="text-xs font-bold text-muted uppercase tracking-wider mb-2">Quick Add (Counter Favorites)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {quickItems.map((item) => (
              <button
                key={item.id}
                onClick={() => addToCart(item)}
                className="p-3 border border-border rounded-xl bg-surface hover:bg-surfaceHover flex flex-col justify-between text-left min-h-[56px] transition-colors"
              >
                <span className="font-semibold text-sm line-clamp-1">{item.name}</span>
                <span className="font-mono text-xs font-bold mt-2">₹{item.price.toFixed(2)}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Right: Cart & Checkout (BILL-04, BILL-05, PWA-08) */}
      <div className="lg:col-span-5 border border-border bg-surface rounded-xl flex flex-col justify-between p-4 h-full">
        <div className="space-y-3 overflow-y-auto flex-1 pr-1">
          <div className="flex justify-between items-center border-b border-border pb-2">
            <span className="font-bold text-sm">Active Bill</span>
            <span className="text-xs text-muted">Items: {cart.length}</span>
          </div>

          {cart.length === 0 ? (
            <div className="text-center py-12 text-muted text-sm">Cart is empty. Tap items to add.</div>
          ) : (
            <div className="space-y-2">
              {cart.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-2 border border-border rounded-lg bg-background">
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{item.name}</div>
                    <div className="text-xs text-muted">₹{item.price.toFixed(2)} each</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => updateQty(item.id, -1)}
                      className="w-8 h-8 rounded border border-border flex items-center justify-center hover:bg-surfaceHover min-h-touch min-w-touch"
                    >
                      <Minus className="w-3.5 h-3.5" />
                    </button>
                    <span className="w-6 text-center font-bold text-sm">{item.qty}</span>
                    <button
                      onClick={() => updateQty(item.id, 1)}
                      className="w-8 h-8 rounded border border-border flex items-center justify-center hover:bg-surfaceHover min-h-touch min-w-touch"
                    >
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="w-16 text-right font-bold text-sm">
                    ₹{(item.price * item.qty).toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer Checkout Controls */}
        <div className="border-t border-border pt-4 space-y-4">
          <div className="grid grid-cols-4 gap-2">
            {(['CASH', 'UPI', 'UDHAAR', 'SPLIT'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setPaymentMode(mode)}
                className={`h-11 rounded-lg text-xs font-bold border transition-colors min-h-touch ${
                  paymentMode === mode
                    ? 'bg-primary text-primaryForeground border-primary'
                    : 'bg-background border-border text-foreground hover:bg-surfaceHover'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>

          <div className="flex justify-between items-center text-lg font-bold">
            <span>{t('total')}</span>
            <span className="text-2xl">₹{totalAmount.toFixed(2)}</span>
          </div>

          <div className="flex space-x-2">
            <button
              disabled={cart.length === 0}
              className="flex-1 h-14 bg-primary text-primaryForeground font-bold rounded-xl text-base hover:opacity-90 transition-opacity disabled:opacity-40 min-h-pos"
            >
              Complete Sale (Space)
            </button>
            <button
              title="Share on WhatsApp"
              className="w-14 h-14 border border-border bg-background rounded-xl flex items-center justify-center hover:bg-surfaceHover min-h-pos min-w-pos"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
