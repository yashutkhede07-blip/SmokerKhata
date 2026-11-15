import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Plus, Tag } from 'lucide-react';

export const Items: React.FC = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('ALL');

  const categories = ['ALL', 'Cigarettes', 'Cold Drinks', 'Snacks', 'Prepared Food'];

  const items = [
    { id: '1', name: 'Gold Flake Kings', category: 'Cigarettes', price: 18.00, cost: 14.00, active: true },
    { id: '2', name: 'Classic Milds', category: 'Cigarettes', price: 20.00, cost: 15.00, active: true },
    { id: '3', name: 'Thums Up 250ml', category: 'Cold Drinks', price: 20.00, cost: 16.50, active: true },
    { id: '4', name: 'Maggi Masala (Cooked)', category: 'Prepared Food', price: 35.00, cost: 16.00, active: true },
    { id: '5', name: 'Chai Cup', category: 'Prepared Food', price: 10.00, cost: 4.50, active: true },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('items')}</h1>
          <p className="text-xs text-muted">Manage Catalogue, Categories & Selling Prices</p>
        </div>
        <button className="h-11 px-4 bg-primary text-primaryForeground font-semibold rounded-lg flex items-center space-x-2 min-h-touch">
          <Plus className="w-4 h-4" />
          <span>Add Item</span>
        </button>
      </div>

      {/* Category Tabs (ITEM-04) */}
      <div className="flex space-x-2 overflow-x-auto pb-1">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveTab(cat)}
            className={`px-3 py-2 rounded-lg text-xs font-semibold whitespace-nowrap border min-h-touch ${
              activeTab === cat
                ? 'bg-primary text-primaryForeground border-primary'
                : 'bg-surface border-border text-muted hover:bg-surfaceHover'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Items Table / Cards */}
      <div className="border border-border bg-surface rounded-xl overflow-hidden divide-y divide-border">
        {items
          .filter((i) => activeTab === 'ALL' || i.category === activeTab)
          .map((item) => (
            <div key={item.id} className="p-4 flex items-center justify-between">
              <div className="space-y-0.5">
                <div className="font-semibold text-sm">{item.name}</div>
                <div className="text-xs text-muted flex items-center space-x-1">
                  <Tag className="w-3 h-3" />
                  <span>{item.category}</span>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="text-sm font-bold">₹{item.price.toFixed(2)}</div>
                  <div className="text-[11px] text-muted">Cost: ₹{item.cost.toFixed(2)}</div>
                </div>
                <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 font-semibold">
                  Active
                </span>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
};
