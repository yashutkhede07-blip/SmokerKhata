import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Plus, Search, X, Percent } from 'lucide-react';

interface CatalogItem {
  id: string;
  name: string;
  category: string;
  price: number;
  cost: number;
  active: boolean;
  unit: string;
}

export const Items: React.FC = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('ALL');
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  // New item form state
  const [itemName, setItemName] = useState('');
  const [itemCategory, setItemCategory] = useState('Cigarettes');
  const [itemPrice, setItemPrice] = useState('');
  const [itemCost, setItemCost] = useState('');
  const [itemUnit, setItemUnit] = useState('Stick');

  const categories = ['ALL', 'Cigarettes', 'Cold Drinks', 'Snacks', 'Chai & Food', 'Paan Masala'];

  const [items, setItems] = useState<CatalogItem[]>([
    { id: '1', name: 'Gold Flake Kings', category: 'Cigarettes', price: 18.00, cost: 14.00, active: true, unit: 'Stick' },
    { id: '2', name: 'Classic Milds', category: 'Cigarettes', price: 20.00, cost: 15.50, active: true, unit: 'Stick' },
    { id: '3', name: 'Marlboro Lights', category: 'Cigarettes', price: 20.00, cost: 16.00, active: true, unit: 'Stick' },
    { id: '4', name: 'Thums Up 250ml', category: 'Cold Drinks', price: 20.00, cost: 16.50, active: true, unit: 'Bottle' },
    { id: '5', name: 'Coca Cola 250ml Can', category: 'Cold Drinks', price: 40.00, cost: 32.00, active: true, unit: 'Can' },
    { id: '6', name: 'Maggi Masala (Cooked)', category: 'Chai & Food', price: 35.00, cost: 16.00, active: true, unit: 'Plate' },
    { id: '7', name: 'Chai Cup', category: 'Chai & Food', price: 10.00, cost: 4.50, active: true, unit: 'Cup' },
    { id: '8', name: 'Lays Magic Masala', category: 'Snacks', price: 10.00, cost: 8.20, active: true, unit: 'Pack' },
    { id: '9', name: 'Rajnigandha Silver', category: 'Paan Masala', price: 40.00, cost: 32.00, active: true, unit: 'Pouch' },
  ]);

  const handleAddItem = (e: React.FormEvent) => {
    e.preventDefault();
    if (!itemName.trim() || !itemPrice) return;

    const newItem: CatalogItem = {
      id: Date.now().toString(),
      name: itemName.trim(),
      category: itemCategory,
      price: parseFloat(itemPrice),
      cost: parseFloat(itemCost) || parseFloat(itemPrice) * 0.8,
      active: true,
      unit: itemUnit,
    };

    setItems([newItem, ...items]);
    setItemName('');
    setItemPrice('');
    setItemCost('');
    setShowAddModal(false);
  };

  const toggleStatus = (id: string) => {
    setItems((prev) =>
      prev.map((i) => (i.id === id ? { ...i, active: !i.active } : i))
    );
  };

  const filteredItems = items.filter((item) => {
    const matchesCategory = activeTab === 'ALL' || item.category === activeTab;
    const matchesSearch = item.name.toLowerCase().includes(search.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{t('items')}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-blue-100 text-blue-900 dark:bg-blue-900/40 dark:text-blue-300">
              Master Catalog
            </span>
          </div>
          <p className="text-xs sm:text-sm text-muted mt-1">
            Price List, Product Categories, Margin Analysis & Quick Add Flags
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="h-11 px-5 bg-foreground text-background font-bold rounded-xl flex items-center space-x-2 shadow-xs transition-all active:scale-95 cursor-pointer min-h-touch"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Item</span>
        </button>
      </div>

      {/* Filter and Search Controls */}
      <div className="space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search items by product name or category..."
            className="w-full h-11 pl-10 pr-4 border border-border rounded-xl bg-surface text-foreground font-medium outline-none focus:ring-2 focus:ring-foreground/20"
          />
        </div>

        <div className="flex space-x-2 overflow-x-auto pb-1 no-scrollbar">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveTab(cat)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border cursor-pointer ${
                activeTab === cat
                  ? 'bg-foreground text-background border-foreground shadow-xs'
                  : 'bg-surface border-border text-muted hover:bg-surfaceHover'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Items Catalog List */}
      <div className="border border-border bg-surface rounded-2xl overflow-hidden divide-y divide-border shadow-xs">
        {filteredItems.map((item) => {
          const profit = item.price - item.cost;
          const margin = item.price > 0 ? (profit / item.price) * 100 : 0;
          return (
            <div
              key={item.id}
              className="p-4 sm:p-5 flex items-center justify-between hover:bg-surfaceHover/50 transition-colors"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-base text-foreground">{item.name}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded font-semibold bg-background border border-border text-muted">
                    {item.category}
                  </span>
                </div>
                <div className="text-xs text-muted">
                  Unit: {item.unit} • Purchase Cost: ₹{item.cost.toFixed(2)}
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="font-mono text-base font-extrabold text-foreground">
                    ₹{item.price.toFixed(2)}
                  </div>
                  <div className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 flex items-center justify-end space-x-1">
                    <Percent className="w-3 h-3" />
                    <span>{margin.toFixed(0)}% Margin (₹{profit.toFixed(1)})</span>
                  </div>
                </div>

                <button
                  onClick={() => toggleStatus(item.id)}
                  className={`px-2.5 py-1 text-xs font-bold rounded-lg cursor-pointer transition-colors ${
                    item.active
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300'
                      : 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300'
                  }`}
                >
                  {item.active ? 'Active' : 'Disabled'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add New Item Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="w-full max-w-sm bg-surface border border-border rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-border pb-3">
              <span className="font-extrabold text-base text-foreground">Add Catalog Item</span>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1 rounded-lg hover:bg-surfaceHover text-muted cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddItem} className="space-y-3.5">
              <div>
                <label className="text-xs font-bold text-muted block mb-1">Product Name</label>
                <input
                  type="text"
                  required
                  autoFocus
                  placeholder="e.g. Classic Milds (Stick)"
                  value={itemName}
                  onChange={(e) => setItemName(e.target.value)}
                  className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">Category</label>
                <select
                  value={itemCategory}
                  onChange={(e) => setItemCategory(e.target.value)}
                  className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none"
                >
                  {categories.filter((c) => c !== 'ALL').map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-muted block mb-1">Selling Price (₹)</label>
                  <input
                    type="number"
                    step="0.5"
                    required
                    placeholder="20.00"
                    value={itemPrice}
                    onChange={(e) => setItemPrice(e.target.value)}
                    className="w-full h-11 px-3 border border-border rounded-xl font-mono text-sm bg-background text-foreground outline-none"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-muted block mb-1">Purchase Cost (₹)</label>
                  <input
                    type="number"
                    step="0.5"
                    placeholder="15.00"
                    value={itemCost}
                    onChange={(e) => setItemCost(e.target.value)}
                    className="w-full h-11 px-3 border border-border rounded-xl font-mono text-sm bg-background text-foreground outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">Unit of Measurement</label>
                <select
                  value={itemUnit}
                  onChange={(e) => setItemUnit(e.target.value)}
                  className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none"
                >
                  <option value="Stick">Stick (Loose Cigarette)</option>
                  <option value="Pack">Pack / Packet</option>
                  <option value="Bottle">Bottle</option>
                  <option value="Can">Can</option>
                  <option value="Cup">Cup (Chai)</option>
                  <option value="Plate">Plate (Food)</option>
                  <option value="Pouch">Pouch (Paan Masala)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={!itemName.trim() || !itemPrice}
                className="w-full h-12 bg-foreground text-background font-extrabold rounded-xl transition-all active:scale-[0.99] disabled:opacity-40 cursor-pointer mt-2"
              >
                Save Product
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
