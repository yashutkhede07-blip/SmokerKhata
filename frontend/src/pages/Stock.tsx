import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AlertCircle, ArrowDownUp, Search,
  CheckCircle, Share2, X
} from 'lucide-react';

interface StockItem {
  id: string;
  name: string;
  category: string;
  current: number;
  threshold: number;
  status: 'IN_STOCK' | 'LOW_STOCK';
  unit: string;
}

export const Stock: React.FC = () => {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'ALL' | 'LOW' | 'OK'>('ALL');
  const [selectedItem, setSelectedItem] = useState<StockItem | null>(null);
  const [adjustQty, setAdjustQty] = useState('');
  const [adjustReason, setAdjustReason] = useState<'DELIVERY' | 'DAMAGE'>('DELIVERY');

  const [stockItems, setStockItems] = useState<StockItem[]>([
    { id: '1', name: 'Gold Flake Kings', category: 'Cigarettes', current: 120, threshold: 30, status: 'IN_STOCK', unit: 'Sticks' },
    { id: '2', name: 'Classic Milds', category: 'Cigarettes', current: 6, threshold: 25, status: 'LOW_STOCK', unit: 'Sticks' },
    { id: '3', name: 'Thums Up 250ml', category: 'Cold Drinks', current: 4, threshold: 18, status: 'LOW_STOCK', unit: 'Bottles' },
    { id: '4', name: 'Marlboro Lights', category: 'Cigarettes', current: 8, threshold: 20, status: 'LOW_STOCK', unit: 'Sticks' },
    { id: '5', name: 'Maggi Packets', category: 'Chai & Food', current: 48, threshold: 12, status: 'IN_STOCK', unit: 'Packs' },
    { id: '6', name: 'Lays Magic Masala', category: 'Snacks', current: 36, threshold: 15, status: 'IN_STOCK', unit: 'Packs' },
    { id: '7', name: 'Sting Energy', category: 'Cold Drinks', current: 32, threshold: 12, status: 'IN_STOCK', unit: 'Bottles' },
  ]);

  const lowStockCount = stockItems.filter((i) => i.status === 'LOW_STOCK').length;

  const handleAdjustStock = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem || !adjustQty || parseInt(adjustQty) <= 0) return;

    const qty = parseInt(adjustQty);
    setStockItems((prev) =>
      prev.map((i) => {
        if (i.id === selectedItem.id) {
          const newStock = adjustReason === 'DELIVERY' ? i.current + qty : Math.max(0, i.current - qty);
          return {
            ...i,
            current: newStock,
            status: newStock <= i.threshold ? 'LOW_STOCK' : 'IN_STOCK',
          };
        }
        return i;
      })
    );

    setSelectedItem(null);
    setAdjustQty('');
  };

  const filteredStock = stockItems.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter =
      filter === 'ALL'
        ? true
        : filter === 'LOW'
        ? item.status === 'LOW_STOCK'
        : item.status === 'IN_STOCK';
    return matchesSearch && matchesFilter;
  });

  const lowItemsText = stockItems
    .filter((i) => i.status === 'LOW_STOCK')
    .map((i) => `• ${i.name}: ${i.current} ${i.unit} left`)
    .join('%0A');

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{t('stock')}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-purple-100 text-purple-900 dark:bg-purple-900/40 dark:text-purple-300">
              Inventory Tracking
            </span>
          </div>
          <p className="text-xs sm:text-sm text-muted mt-1">
            Real-time Retail Stock, Reorder Thresholds & Wholesale Deliveries
          </p>
        </div>

        {lowStockCount > 0 && (
          <a
            href={`https://wa.me/?text=Namaste%20Distributor!%20Need%20stock%20reorder%20for%20Sharma%20Kirana:%0A${lowItemsText}`}
            target="_blank"
            rel="noreferrer"
            className="h-11 px-5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl flex items-center space-x-2 shadow-xs transition-all active:scale-95 cursor-pointer min-h-touch"
          >
            <Share2 className="w-4 h-4" />
            <span>WhatsApp Distributor Order</span>
          </a>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 border border-border bg-surface rounded-2xl space-y-1">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Total SKUs Monitored</span>
          <div className="text-3xl font-extrabold font-mono text-foreground">{stockItems.length} Products</div>
          <span className="text-xs text-muted block">Active retail units</span>
        </div>

        <div className="p-4 border border-border bg-surface rounded-2xl space-y-1">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Low Stock Warnings</span>
          <div className="text-3xl font-extrabold font-mono text-rose-600 dark:text-rose-400">
            {lowStockCount} Products Low
          </div>
          <span className="text-xs text-muted block">Below threshold — immediate reorder recommended</span>
        </div>

        <div className="p-4 border border-border bg-surface rounded-2xl space-y-1">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Sufficient Stock</span>
          <div className="text-3xl font-extrabold font-mono text-emerald-600 dark:text-emerald-400">
            {stockItems.length - lowStockCount} Healthy
          </div>
          <span className="text-xs text-muted block">Ready for peak counter rush</span>
        </div>
      </div>

      {/* Search & Filter Controls */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search inventory by product name..."
            className="w-full h-11 pl-10 pr-4 border border-border rounded-xl bg-surface text-foreground font-medium outline-none focus:ring-2 focus:ring-foreground/20"
          />
        </div>

        <div className="flex space-x-2 shrink-0">
          {(['ALL', 'LOW', 'OK'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                filter === f
                  ? 'bg-foreground text-background border-foreground shadow-xs'
                  : 'bg-surface border-border text-muted hover:bg-surfaceHover'
              }`}
            >
              {f === 'ALL' ? 'All Stock' : f === 'LOW' ? `Low Stock (${lowStockCount})` : 'Sufficient'}
            </button>
          ))}
        </div>
      </div>

      {/* Stock Items Table */}
      <div className="border border-border bg-surface rounded-2xl overflow-hidden divide-y divide-border shadow-xs">
        {filteredStock.map((item) => (
          <div
            key={item.id}
            className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-surfaceHover/50 transition-colors"
          >
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base text-foreground">{item.name}</span>
                <span className="text-[10px] px-2 py-0.5 rounded font-semibold bg-background border border-border text-muted">
                  {item.category}
                </span>
              </div>
              <div className="text-xs text-muted">
                Warning threshold alert: {item.threshold} {item.unit}
              </div>
            </div>

            <div className="flex items-center justify-between sm:justify-end space-x-5 border-t sm:border-t-0 pt-3 sm:pt-0 border-border/60">
              <div className="text-left sm:text-right">
                <div className="font-mono text-xl font-extrabold text-foreground">
                  {item.current} <span className="text-xs font-normal text-muted">{item.unit}</span>
                </div>
                {item.status === 'LOW_STOCK' ? (
                  <span className="text-[11px] font-bold text-rose-600 dark:text-rose-400 flex items-center space-x-1 sm:justify-end">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>Low Stock Alert</span>
                  </span>
                ) : (
                  <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 flex items-center space-x-1 sm:justify-end">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>In Stock</span>
                  </span>
                )}
              </div>

              <button
                onClick={() => setSelectedItem(item)}
                className="px-3.5 py-2 bg-surface hover:bg-surfaceHover border border-border rounded-xl text-xs font-bold text-foreground flex items-center space-x-1.5 transition-colors cursor-pointer"
              >
                <ArrowDownUp className="w-3.5 h-3.5 text-muted" />
                <span>Adjust Stock</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Stock Adjustment Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="w-full max-w-sm bg-surface border border-border rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-border pb-3">
              <div>
                <span className="font-extrabold text-base text-foreground">Adjust Inventory Stock</span>
                <span className="text-xs text-muted block">{selectedItem.name}</span>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="p-1 rounded-lg hover:bg-surfaceHover text-muted cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAdjustStock} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-muted block mb-1">Adjustment Type</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setAdjustReason('DELIVERY')}
                    className={`py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                      adjustReason === 'DELIVERY'
                        ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                        : 'bg-background border-border text-muted hover:bg-surfaceHover'
                    }`}
                  >
                    + Wholesale Delivery
                  </button>
                  <button
                    type="button"
                    onClick={() => setAdjustReason('DAMAGE')}
                    className={`py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                      adjustReason === 'DAMAGE'
                        ? 'bg-rose-600 text-white border-rose-600 shadow-xs'
                        : 'bg-background border-border text-muted hover:bg-surfaceHover'
                    }`}
                  >
                    - Damage / Loss
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">
                  Quantity ({selectedItem.unit})
                </label>
                <input
                  type="number"
                  required
                  autoFocus
                  placeholder="e.g. 50"
                  value={adjustQty}
                  onChange={(e) => setAdjustQty(e.target.value)}
                  className="w-full h-12 px-3 border border-border rounded-xl font-mono text-xl font-extrabold bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20"
                />
              </div>

              <div className="p-3 bg-background border border-border rounded-xl text-xs space-y-1">
                <div className="flex justify-between text-muted">
                  <span>Current Stock:</span>
                  <span className="font-mono font-bold text-foreground">
                    {selectedItem.current} {selectedItem.unit}
                  </span>
                </div>
                <div className="flex justify-between text-muted">
                  <span>New Stock After Update:</span>
                  <span className="font-mono font-bold text-foreground">
                    {adjustQty && !isNaN(parseInt(adjustQty))
                      ? (adjustReason === 'DELIVERY'
                          ? selectedItem.current + parseInt(adjustQty)
                          : Math.max(0, selectedItem.current - parseInt(adjustQty))
                        )
                      : selectedItem.current}{' '}
                    {selectedItem.unit}
                  </span>
                </div>
              </div>

              <button
                type="submit"
                className="w-full h-12 bg-foreground text-background font-extrabold rounded-xl transition-all active:scale-[0.99] cursor-pointer"
              >
                Save Stock Adjustment
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
