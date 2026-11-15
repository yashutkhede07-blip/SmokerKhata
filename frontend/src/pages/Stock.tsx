import React from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle, ArrowDownUp } from 'lucide-react';

export const Stock: React.FC = () => {
  const { t } = useTranslation();

  const stockItems = [
    { id: '1', name: 'Gold Flake Kings', current: 120, threshold: 20, status: 'IN_STOCK' },
    { id: '2', name: 'Classic Milds', current: 8, threshold: 15, status: 'LOW_STOCK' },
    { id: '3', name: 'Thums Up 250ml', current: 4, threshold: 12, status: 'LOW_STOCK' },
    { id: '4', name: 'Maggi Packets', current: 48, threshold: 10, status: 'IN_STOCK' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('stock')}</h1>
          <p className="text-xs text-muted">Real-time Stock Levels & Low Stock Alerts</p>
        </div>
        <button className="h-11 px-4 bg-primary text-primaryForeground font-semibold rounded-lg flex items-center space-x-2 min-h-touch">
          <ArrowDownUp className="w-4 h-4" />
          <span>Adjust Stock</span>
        </button>
      </div>

      <div className="border border-border bg-surface rounded-xl overflow-hidden divide-y divide-border">
        {stockItems.map((item) => (
          <div key={item.id} className="p-4 flex items-center justify-between">
            <div>
              <div className="font-semibold text-sm">{item.name}</div>
              <div className="text-xs text-muted">Threshold: {item.threshold} units</div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-base font-bold">{item.current} units</div>
              </div>
              {item.status === 'LOW_STOCK' ? (
                <div className="flex items-center space-x-1 px-2.5 py-1 rounded bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200 text-xs font-semibold">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>Low Stock</span>
                </div>
              ) : (
                <span className="text-xs px-2.5 py-1 rounded bg-surface text-muted border border-border font-semibold">
                  Sufficient
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
