import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Lock } from 'lucide-react';

export const CashBook: React.FC = () => {
  const { t } = useTranslation();
  const [openingCash] = useState(1500.00);
  const [cashSales] = useState(2450.00);
  const [cashIn] = useState(500.00);
  const [cashOut] = useState(200.00);
  const [actualCount, setActualCount] = useState<number | ''>('');

  const expectedCash = openingCash + cashSales + cashIn - cashOut;
  const mismatch = actualCount !== '' ? (actualCount as number) - expectedCash : null;

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t('cashbook')}</h1>
        <p className="text-xs text-muted">Daily Drawer Cash Balance & Day Closing Reconciliation</p>
      </div>

      {/* Cash Calculation Summary (CASH-03, CASH-05) */}
      <div className="border border-border bg-surface p-4 rounded-xl space-y-4">
        <h2 className="text-sm font-semibold">Today's Cash Ledger Calculation</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          <div className="p-3 border border-border rounded-lg bg-background">
            <div className="text-xs text-muted">Opening Cash</div>
            <div className="text-lg font-bold">₹{openingCash.toFixed(2)}</div>
          </div>
          <div className="p-3 border border-border rounded-lg bg-background">
            <div className="text-xs text-muted">Cash Sales</div>
            <div className="text-lg font-bold text-green-600 dark:text-green-400">+₹{cashSales.toFixed(2)}</div>
          </div>
          <div className="p-3 border border-border rounded-lg bg-background">
            <div className="text-xs text-muted">Cash In</div>
            <div className="text-lg font-bold text-green-600 dark:text-green-400">+₹{cashIn.toFixed(2)}</div>
          </div>
          <div className="p-3 border border-border rounded-lg bg-background">
            <div className="text-xs text-muted">Cash Out</div>
            <div className="text-lg font-bold text-red-600 dark:text-red-400">-₹{cashOut.toFixed(2)}</div>
          </div>
        </div>

        <div className="p-4 border border-border rounded-lg bg-background flex justify-between items-center">
          <span className="font-semibold text-base">Expected Drawer Closing Balance:</span>
          <span className="text-2xl font-bold font-mono">₹{expectedCash.toFixed(2)}</span>
        </div>
      </div>

      {/* Physical Cash Count Reconciliation (CASH-04, CASH-05) */}
      <div className="border border-border bg-surface p-4 rounded-xl space-y-4">
        <h2 className="text-sm font-semibold">Evening Day Closing & Physical Count</h2>
        <div className="space-y-2">
          <label className="text-xs font-semibold block">Actual Physical Cash Counted in Drawer (₹)</label>
          <input
            type="number"
            value={actualCount}
            onChange={(e) => setActualCount(e.target.value === '' ? '' : parseFloat(e.target.value))}
            placeholder="Enter counted rupees..."
            className="w-full h-12 px-4 border border-border rounded-lg bg-background text-foreground font-mono text-lg font-bold outline-none"
          />
        </div>

        {mismatch !== null && (
          <div
            className={`p-3 rounded-lg text-sm font-semibold flex justify-between items-center ${
              mismatch === 0
                ? 'bg-green-100 text-green-900 dark:bg-green-900/30 dark:text-green-300'
                : 'bg-red-100 text-red-900 dark:bg-red-900/30 dark:text-red-300'
            }`}
          >
            <span>{mismatch === 0 ? '✓ Balanced: No Discrepancy' : '⚠️ Cash Mismatch Flagged:'}</span>
            <span className="font-mono text-base font-bold">
              {mismatch > 0 ? `+₹${mismatch.toFixed(2)} (Excess)` : mismatch < 0 ? `-₹${Math.abs(mismatch).toFixed(2)} (Short)` : '₹0.00'}
            </span>
          </div>
        )}

        <button className="w-full h-12 bg-primary text-primaryForeground font-semibold rounded-lg flex items-center justify-center space-x-2 min-h-touch">
          <Lock className="w-4 h-4" />
          <span>Finalize & Close Day</span>
        </button>
      </div>
    </div>
  );
};
