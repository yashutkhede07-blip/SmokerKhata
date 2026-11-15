import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Lock, Plus, Calculator, CheckCircle2,
  AlertTriangle, Banknote
} from 'lucide-react';

interface CashTxn {
  id: string;
  time: string;
  type: 'IN' | 'OUT';
  amount: number;
  category: string;
  notes: string;
}

export const CashBook: React.FC = () => {
  const { t } = useTranslation();
  const [openingCash] = useState(1500.00);
  const [cashSales] = useState(3840.00);
  const [showAddTxn, setShowAddTxn] = useState(false);
  const [txnType, setTxnType] = useState<'IN' | 'OUT'>('OUT');
  const [txnAmount, setTxnAmount] = useState('');
  const [txnCategory, setTxnCategory] = useState('Supplier Delivery');
  const [txnNotes, setTxnNotes] = useState('');
  const [dayClosed, setDayClosed] = useState(false);

  // Denominations count state
  const [notes500, setNotes500] = useState('');
  const [notes200, setNotes200] = useState('');
  const [notes100, setNotes100] = useState('');
  const [notes50, setNotes50] = useState('');
  const [notes20, setNotes20] = useState('');
  const [notes10, setNotes10] = useState('');
  const [coins, setCoins] = useState('');

  const [cashTransactions, setCashTransactions] = useState<CashTxn[]>([
    { id: '1', time: '09:30 AM', type: 'IN', amount: 500.00, category: 'Udhaar Recovered', notes: 'Ramesh Sharma payment' },
    { id: '2', time: '11:15 AM', type: 'OUT', amount: 350.00, category: 'Milk & Bread Delivery', notes: 'Morning bakery supplier' },
    { id: '3', time: '03:45 PM', type: 'OUT', amount: 120.00, category: 'Tea & Snacks', notes: 'Counter expense' },
  ]);

  const totalCashIn = cashTransactions
    .filter((t) => t.type === 'IN')
    .reduce((sum, t) => sum + t.amount, 0);

  const totalCashOut = cashTransactions
    .filter((t) => t.type === 'OUT')
    .reduce((sum, t) => sum + t.amount, 0);

  const expectedCash = openingCash + cashSales + totalCashIn - totalCashOut;

  // Calculate counted physical cash from denominations
  const totalCountedCash =
    (parseInt(notes500) || 0) * 500 +
    (parseInt(notes200) || 0) * 200 +
    (parseInt(notes100) || 0) * 100 +
    (parseInt(notes50) || 0) * 50 +
    (parseInt(notes20) || 0) * 20 +
    (parseInt(notes10) || 0) * 10 +
    (parseFloat(coins) || 0);

  const hasEnteredDenominations =
    notes500 !== '' || notes200 !== '' || notes100 !== '' ||
    notes50 !== '' || notes20 !== '' || notes10 !== '' || coins !== '';

  const mismatch = hasEnteredDenominations ? totalCountedCash - expectedCash : null;

  const handleAddTransaction = (e: React.FormEvent) => {
    e.preventDefault();
    if (!txnAmount || parseFloat(txnAmount) <= 0) return;

    const newTxn: CashTxn = {
      id: Date.now().toString(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      type: txnType,
      amount: parseFloat(txnAmount),
      category: txnCategory,
      notes: txnNotes.trim() || txnCategory,
    };

    setCashTransactions([newTxn, ...cashTransactions]);
    setTxnAmount('');
    setTxnNotes('');
    setShowAddTxn(false);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{t('cashbook')}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-300">
              Cash Drawer Ledger
            </span>
          </div>
          <p className="text-xs sm:text-sm text-muted mt-1">
            Opening Balance, Cash In/Out, Physical Denominations & Day Closing Reconciliation
          </p>
        </div>

        <button
          onClick={() => setShowAddTxn(true)}
          className="h-11 px-5 bg-foreground text-background font-bold rounded-xl flex items-center space-x-2 shadow-xs transition-all active:scale-95 cursor-pointer min-h-touch"
        >
          <Plus className="w-4 h-4" />
          <span>Record Cash In / Out</span>
        </button>
      </div>

      {/* Ledger Formula Summary Grid */}
      <div className="border border-border bg-surface p-5 rounded-2xl space-y-4 shadow-xs">
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-muted uppercase tracking-wider">
            Today's Drawer Cash Math (Ledger vs Register)
          </span>
          <span className="text-xs text-muted">Auto-computed</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          <div className="p-3.5 border border-border rounded-xl bg-background space-y-1">
            <span className="text-xs text-muted font-medium">Opening Cash</span>
            <div className="font-mono text-xl font-extrabold text-foreground">₹{openingCash.toFixed(2)}</div>
            <span className="text-[10px] text-muted block">Morning float</span>
          </div>

          <div className="p-3.5 border border-border rounded-xl bg-background space-y-1">
            <span className="text-xs text-muted font-medium">Cash Sales (+)</span>
            <div className="font-mono text-xl font-extrabold text-emerald-600 dark:text-emerald-400">
              +₹{cashSales.toFixed(2)}
            </div>
            <span className="text-[10px] text-muted block">From POS bills</span>
          </div>

          <div className="p-3.5 border border-border rounded-xl bg-background space-y-1">
            <span className="text-xs text-muted font-medium">Cash In (+)</span>
            <div className="font-mono text-xl font-extrabold text-emerald-600 dark:text-emerald-400">
              +₹{totalCashIn.toFixed(2)}
            </div>
            <span className="text-[10px] text-muted block">Debt recoveries</span>
          </div>

          <div className="p-3.5 border border-border rounded-xl bg-background space-y-1">
            <span className="text-xs text-muted font-medium">Cash Out (-)</span>
            <div className="font-mono text-xl font-extrabold text-rose-600 dark:text-rose-400">
              -₹{totalCashOut.toFixed(2)}
            </div>
            <span className="text-[10px] text-muted block">Supplier & expenses</span>
          </div>
        </div>

        <div className="p-4 bg-background border border-border rounded-xl flex flex-col sm:flex-row justify-between sm:items-center gap-2">
          <div className="flex items-center space-x-2">
            <Banknote className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <span className="font-bold text-sm sm:text-base text-foreground">
              Expected Physical Cash in Drawer:
            </span>
          </div>
          <span className="font-mono text-2xl sm:text-3xl font-extrabold text-foreground">
            ₹{expectedCash.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Denominations Counter & Reconciliation */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Denominations Calculator */}
        <div className="lg:col-span-7 border border-border bg-surface p-5 rounded-2xl space-y-4 shadow-xs">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center space-x-2">
              <Calculator className="w-4 h-4 text-muted" />
              <h2 className="font-bold text-base text-foreground">Evening Cash Count (Denominations)</h2>
            </div>
            <span className="text-xs text-muted">Count physical notes</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[
              { label: '₹500', value: notes500, setter: setNotes500, mult: 500 },
              { label: '₹200', value: notes200, setter: setNotes200, mult: 200 },
              { label: '₹100', value: notes100, setter: setNotes100, mult: 100 },
              { label: '₹50', value: notes50, setter: setNotes50, mult: 50 },
              { label: '₹20', value: notes20, setter: setNotes20, mult: 20 },
              { label: '₹10', value: notes10, setter: setNotes10, mult: 10 },
            ].map((denom) => (
              <div key={denom.label} className="p-3 border border-border rounded-xl bg-background space-y-1">
                <span className="text-xs font-bold text-foreground block">{denom.label} Notes</span>
                <input
                  type="number"
                  min="0"
                  placeholder="0"
                  value={denom.value}
                  onChange={(e) => denom.setter(e.target.value)}
                  className="w-full h-9 px-2 border border-border rounded-lg font-mono font-bold text-sm bg-surface outline-none"
                />
                <span className="text-[10px] text-muted block text-right font-mono">
                  = ₹{((parseInt(denom.value) || 0) * denom.mult).toLocaleString('en-IN')}
                </span>
              </div>
            ))}
          </div>

          {/* Coins input */}
          <div className="p-3 border border-border rounded-xl bg-background flex items-center justify-between">
            <span className="text-xs font-bold text-foreground">Loose Coins Total (₹)</span>
            <input
              type="number"
              placeholder="0.00"
              value={coins}
              onChange={(e) => setCoins(e.target.value)}
              className="h-9 w-28 px-2 border border-border rounded-lg font-mono font-bold text-sm bg-surface outline-none"
            />
          </div>

          {/* Reconciliation Verdict */}
          <div className="p-4 bg-background border border-border rounded-xl space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted font-medium">Physical Cash Counted:</span>
              <span className="font-mono text-xl font-extrabold text-foreground">
                ₹{totalCountedCash.toFixed(2)}
              </span>
            </div>

            {mismatch !== null && (
              <div
                className={`p-3 rounded-xl flex items-center justify-between text-xs font-bold ${
                  mismatch === 0
                    ? 'bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-200'
                    : mismatch > 0
                    ? 'bg-blue-100 text-blue-900 dark:bg-blue-900/40 dark:text-blue-200'
                    : 'bg-rose-100 text-rose-900 dark:bg-rose-900/40 dark:text-rose-200'
                }`}
              >
                <div className="flex items-center space-x-1.5">
                  {mismatch === 0 ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4" />
                  )}
                  <span>
                    {mismatch === 0
                      ? '✓ Cash Register Perfectly Balanced'
                      : mismatch > 0
                      ? '⚠️ Cash Excess in Drawer'
                      : '⚠️ Cash Shortage in Drawer'}
                  </span>
                </div>
                <span className="font-mono text-sm">
                  {mismatch > 0 ? `+₹${mismatch.toFixed(2)}` : mismatch < 0 ? `-₹${Math.abs(mismatch).toFixed(2)}` : '₹0.00'}
                </span>
              </div>
            )}
          </div>

          <button
            onClick={() => setDayClosed(true)}
            disabled={dayClosed}
            className="w-full h-12 bg-foreground text-background font-extrabold rounded-xl flex items-center justify-center space-x-2 shadow-xs transition-all active:scale-[0.99] cursor-pointer disabled:opacity-50"
          >
            <Lock className="w-4 h-4" />
            <span>{dayClosed ? '✓ Day Closing Finalized' : 'Finalize & Close Register for Today'}</span>
          </button>
        </div>

        {/* Right: Cash In/Out Activity Log */}
        <div className="lg:col-span-5 border border-border bg-surface p-5 rounded-2xl space-y-4 shadow-xs">
          <h2 className="font-bold text-base text-foreground">Cash Drawer Log (Today)</h2>

          <div className="divide-y divide-border overflow-hidden">
            {cashTransactions.map((t) => (
              <div key={t.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                      t.type === 'IN'
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300'
                        : 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300'
                    }`}>
                      {t.type === 'IN' ? 'CASH IN' : 'CASH OUT'}
                    </span>
                    <span className="font-bold text-sm text-foreground">{t.category}</span>
                  </div>
                  <span className="text-xs text-muted block mt-0.5">{t.notes} • {t.time}</span>
                </div>

                <div className={`font-mono font-extrabold text-sm ${
                  t.type === 'IN' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
                }`}>
                  {t.type === 'IN' ? `+₹${t.amount.toFixed(2)}` : `-₹${t.amount.toFixed(2)}`}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Record Cash In/Out Modal */}
      {showAddTxn && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="w-full max-w-sm bg-surface border border-border rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-border pb-3">
              <span className="font-extrabold text-base text-foreground">Record Drawer Cash</span>
              <button
                onClick={() => setShowAddTxn(false)}
                className="p-1 rounded-lg hover:bg-surfaceHover text-muted cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAddTransaction} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-muted block mb-1">Entry Type</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setTxnType('IN')}
                    className={`py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                      txnType === 'IN'
                        ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                        : 'bg-background border-border text-muted hover:bg-surfaceHover'
                    }`}
                  >
                    + Cash In (Deposit)
                  </button>
                  <button
                    type="button"
                    onClick={() => setTxnType('OUT')}
                    className={`py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                      txnType === 'OUT'
                        ? 'bg-rose-600 text-white border-rose-600 shadow-xs'
                        : 'bg-background border-border text-muted hover:bg-surfaceHover'
                    }`}
                  >
                    - Cash Out (Expense)
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  autoFocus
                  placeholder="0.00"
                  value={txnAmount}
                  onChange={(e) => setTxnAmount(e.target.value)}
                  className="w-full h-12 px-3 border border-border rounded-xl font-mono text-xl font-extrabold bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">Category / Reason</label>
                <select
                  value={txnCategory}
                  onChange={(e) => setTxnCategory(e.target.value)}
                  className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none"
                >
                  <option value="Supplier Delivery">Supplier Delivery / Wholesale</option>
                  <option value="Milk & Bread">Milk, Bread, Eggs, Ice</option>
                  <option value="Tea & Snacks">Tea & Staff Snacks</option>
                  <option value="Udhaar Recovered">Udhaar Cash Recovery</option>
                  <option value="Owner Injected">Owner Float Injection</option>
                  <option value="Personal Withdrawal">Owner Personal Withdrawal</option>
                  <option value="Electricity / Rent">Utility / Shop Rent</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">Optional Notes</label>
                <input
                  type="text"
                  placeholder="e.g. Paid to Ramu milk delivery"
                  value={txnNotes}
                  onChange={(e) => setTxnNotes(e.target.value)}
                  className="w-full h-10 px-3 border border-border rounded-xl text-xs bg-background text-foreground outline-none"
                />
              </div>

              <button
                type="submit"
                className="w-full h-12 bg-foreground text-background font-extrabold rounded-xl transition-all active:scale-[0.99] cursor-pointer"
              >
                Save Drawer Entry
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
