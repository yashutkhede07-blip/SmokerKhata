import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  MessageCircle, Plus, Search, ArrowDownLeft,
  ArrowUpRight, X, Users
} from 'lucide-react';

interface Customer {
  id: string;
  name: string;
  phone: string;
  due: number;
  lastEntry: string;
  notes?: string;
}

export const Customers: React.FC = () => {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'ALL' | 'DUE' | 'SETTLED'>('ALL');
  const [showAddModal, setShowAddModal] = useState(false);
  const [activeCustomer, setActiveCustomer] = useState<Customer | null>(null);
  const [txnType, setTxnType] = useState<'GAVE' | 'GOT'>('GAVE');
  const [txnAmount, setTxnAmount] = useState('');
  const [txnNote, setTxnNote] = useState('');

  // Add customer form state
  const [newName, setNewName] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [newOpeningBalance, setNewOpeningBalance] = useState('');

  const [customers, setCustomers] = useState<Customer[]>([
    { id: '1', name: 'Ramesh Sharma (Cloth Merchant)', phone: '9876543210', due: 1250.00, lastEntry: 'Today', notes: 'Pays weekly on Monday' },
    { id: '2', name: 'Amit Verma (Regular Milds)', phone: '9811223344', due: 840.00, lastEntry: 'Yesterday', notes: 'Classic Milds regular' },
    { id: '3', name: 'Sonu Bhai (Chai Counter)', phone: '9822334455', due: 450.00, lastEntry: '3 days ago', notes: 'Milk and tea supplies' },
    { id: '4', name: 'Vikram Singh (Driver)', phone: '9833445566', due: 320.00, lastEntry: '1 week ago', notes: 'Auto stand regular' },
    { id: '5', name: 'Gupta Medicals Staff', phone: '9844556677', due: 0.00, lastEntry: '5 days ago', notes: 'Account clear' },
    { id: '6', name: 'Deepak Electric Works', phone: '9855667788', due: 2100.00, lastEntry: '2 weeks ago', notes: 'Call in afternoon' },
  ]);

  const totalDue = customers.reduce((sum, c) => sum + Math.max(0, c.due), 0);

  const filteredCustomers = customers.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search);
    const matchesFilter =
      filter === 'ALL'
        ? true
        : filter === 'DUE'
        ? c.due > 0
        : c.due === 0;
    return matchesSearch && matchesFilter;
  });

  const handleAddCustomer = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || newPhone.length < 10) return;

    const newCust: Customer = {
      id: Date.now().toString(),
      name: newName.trim(),
      phone: newPhone.trim(),
      due: parseFloat(newOpeningBalance) || 0,
      lastEntry: 'Just now',
    };

    setCustomers([newCust, ...customers]);
    setNewName('');
    setNewPhone('');
    setNewOpeningBalance('');
    setShowAddModal(false);
  };

  const handleRecordTransaction = (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeCustomer || !txnAmount || parseFloat(txnAmount) <= 0) return;

    const amt = parseFloat(txnAmount);
    setCustomers((prev) =>
      prev.map((c) => {
        if (c.id === activeCustomer.id) {
          const updatedDue = txnType === 'GAVE' ? c.due + amt : c.due - amt;
          return { ...c, due: Math.max(0, updatedDue), lastEntry: 'Just now' };
        }
        return c;
      })
    );

    setActiveCustomer(null);
    setTxnAmount('');
    setTxnNote('');
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{t('customers')}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-300">
              Udhaar Ledger
            </span>
          </div>
          <p className="text-xs sm:text-sm text-muted mt-1">
            Customer Credit Ledger, WhatsApp Reminders & Payment Records
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="h-11 px-5 bg-foreground text-background font-bold rounded-xl flex items-center space-x-2 shadow-xs transition-all active:scale-95 cursor-pointer min-h-touch"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Customer</span>
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 border border-border bg-surface rounded-2xl space-y-1">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Total Market Udhaar Due</span>
          <div className="text-3xl font-extrabold text-amber-600 dark:text-amber-400 font-mono">
            ₹{totalDue.toFixed(2)}
          </div>
          <span className="text-xs text-muted block">Recoverable customer balance</span>
        </div>

        <div className="p-4 border border-border bg-surface rounded-2xl space-y-1">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Active Ledgers</span>
          <div className="text-3xl font-extrabold text-foreground font-mono">
            {customers.filter((c) => c.due > 0).length} / {customers.length}
          </div>
          <span className="text-xs text-muted block">Customers with pending credit</span>
        </div>

        <div className="p-4 border border-border bg-surface rounded-2xl space-y-1">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Collection Reminders</span>
          <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono">
            WhatsApp Ready
          </div>
          <span className="text-xs text-muted block">Direct 1-click payment request</span>
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
            placeholder="Search by customer name, mobile number or note..."
            className="w-full h-11 pl-10 pr-4 border border-border rounded-xl bg-surface text-foreground font-medium outline-none focus:ring-2 focus:ring-foreground/20"
          />
        </div>

        <div className="flex space-x-2 shrink-0">
          {(['ALL', 'DUE', 'SETTLED'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                filter === f
                  ? 'bg-foreground text-background border-foreground shadow-xs'
                  : 'bg-surface border-border text-muted hover:bg-surfaceHover'
              }`}
            >
              {f === 'ALL' ? 'All Customers' : f === 'DUE' ? 'Pending Due' : 'Settled (₹0)'}
            </button>
          ))}
        </div>
      </div>

      {/* Customers List */}
      <div className="border border-border bg-surface rounded-2xl overflow-hidden divide-y divide-border shadow-xs">
        {filteredCustomers.length === 0 ? (
          <div className="text-center py-12 text-muted text-sm">
            <Users className="w-8 h-8 mx-auto text-muted/60 mb-2" />
            <p>No customers match your search.</p>
          </div>
        ) : (
          filteredCustomers.map((c) => (
            <div
              key={c.id}
              className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-surfaceHover/50 transition-colors"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-base text-foreground">{c.name}</span>
                  {c.due > 0 ? (
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-300">
                      Pending Due
                    </span>
                  ) : (
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300">
                      Settled
                    </span>
                  )}
                </div>
                <div className="text-xs text-muted flex items-center space-x-2">
                  <span>📱 {c.phone}</span>
                  <span>•</span>
                  <span>Last active: {c.lastEntry}</span>
                  {c.notes && <span className="hidden sm:inline">• {c.notes}</span>}
                </div>
              </div>

              {/* Right Side: Balance & Quick Transaction CTAs */}
              <div className="flex items-center justify-between sm:justify-end space-x-4 border-t sm:border-t-0 pt-3 sm:pt-0 border-border/60">
                <div className="text-left sm:text-right">
                  <div className="text-[11px] text-muted font-semibold uppercase">{t('dueBalance')}</div>
                  <div className={`font-mono text-xl font-extrabold ${
                    c.due > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'
                  }`}>
                    ₹{c.due.toFixed(2)}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {/* Gave Udhaar */}
                  <button
                    onClick={() => {
                      setActiveCustomer(c);
                      setTxnType('GAVE');
                    }}
                    className="px-3 py-2 bg-rose-50 dark:bg-rose-950/30 hover:bg-rose-100 text-rose-700 dark:text-rose-300 font-bold text-xs rounded-xl border border-rose-200 dark:border-rose-900/50 flex items-center space-x-1 transition-colors cursor-pointer"
                    title="Give Credit / Udhaar"
                  >
                    <ArrowDownLeft className="w-3.5 h-3.5" />
                    <span>{t('gaveUdhaar')}</span>
                  </button>

                  {/* Got Payment */}
                  <button
                    onClick={() => {
                      setActiveCustomer(c);
                      setTxnType('GOT');
                    }}
                    className="px-3 py-2 bg-emerald-50 dark:bg-emerald-950/30 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-300 font-bold text-xs rounded-xl border border-emerald-200 dark:border-emerald-900/50 flex items-center space-x-1 transition-colors cursor-pointer"
                    title="Received Payment"
                  >
                    <ArrowUpRight className="w-3.5 h-3.5" />
                    <span>{t('gotPayment')}</span>
                  </button>

                  {/* WhatsApp Reminder */}
                  {c.due > 0 && (
                    <a
                      href={`https://wa.me/91${c.phone}?text=Namaste%20${encodeURIComponent(c.name)},%20Sharma%20Kirana%20se%20aapka%20baki%20Rs%20${c.due.toFixed(2)}%20hai.%20Kripya%20bhugtan%20karein.%20Dhanyawad!`}
                      target="_blank"
                      rel="noreferrer"
                      className="p-2.5 rounded-xl border border-border bg-background hover:bg-emerald-50 dark:hover:bg-emerald-950/40 text-emerald-600 transition-colors shadow-2xs cursor-pointer"
                      title="Send WhatsApp Reminder"
                    >
                      <MessageCircle className="w-4 h-4 text-emerald-600" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Record Transaction Modal (Gave Udhaar / Got Payment) */}
      {activeCustomer && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="w-full max-w-sm bg-surface border border-border rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-border pb-3">
              <div>
                <span className="font-extrabold text-base text-foreground">
                  {txnType === 'GAVE' ? '🔴 Give Udhaar (Credit)' : '🟢 Received Payment'}
                </span>
                <span className="text-xs text-muted block">{activeCustomer.name}</span>
              </div>
              <button
                onClick={() => setActiveCustomer(null)}
                className="p-1 rounded-lg hover:bg-surfaceHover text-muted cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRecordTransaction} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-muted block mb-1">Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  autoFocus
                  placeholder="Enter amount..."
                  value={txnAmount}
                  onChange={(e) => setTxnAmount(e.target.value)}
                  className="w-full h-12 px-3 border border-border rounded-xl font-mono text-xl font-extrabold bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">Notes / Items (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. 2 Gold Flake packs or GPay payment"
                  value={txnNote}
                  onChange={(e) => setTxnNote(e.target.value)}
                  className="w-full h-10 px-3 border border-border rounded-xl text-xs bg-background text-foreground outline-none"
                />
              </div>

              <div className="p-3 bg-background border border-border rounded-xl text-xs space-y-1">
                <div className="flex justify-between text-muted">
                  <span>Current Due:</span>
                  <span className="font-mono font-bold text-foreground">₹{activeCustomer.due.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-muted">
                  <span>New Due After Entry:</span>
                  <span className="font-mono font-bold text-foreground">
                    ₹{txnAmount && !isNaN(parseFloat(txnAmount))
                      ? (txnType === 'GAVE'
                          ? activeCustomer.due + parseFloat(txnAmount)
                          : Math.max(0, activeCustomer.due - parseFloat(txnAmount))
                        ).toFixed(2)
                      : activeCustomer.due.toFixed(2)}
                  </span>
                </div>
              </div>

              <button
                type="submit"
                className={`w-full h-12 text-white font-extrabold rounded-xl transition-all active:scale-[0.99] cursor-pointer ${
                  txnType === 'GAVE' ? 'bg-rose-600 hover:bg-rose-700' : 'bg-emerald-600 hover:bg-emerald-700'
                }`}
              >
                {txnType === 'GAVE' ? 'Confirm Udhaar (+)' : 'Confirm Payment Received (-)'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Add New Customer Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="w-full max-w-sm bg-surface border border-border rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-border pb-3">
              <span className="font-extrabold text-base text-foreground">Create Customer Khata</span>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1 rounded-lg hover:bg-surfaceHover text-muted cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddCustomer} className="space-y-3.5">
              <div>
                <label className="text-xs font-bold text-muted block mb-1">Customer Full Name</label>
                <input
                  type="text"
                  required
                  autoFocus
                  placeholder="e.g. Ramesh Sharma"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">Mobile Phone (for WhatsApp)</label>
                <input
                  type="tel"
                  required
                  placeholder="10-digit mobile number"
                  value={newPhone}
                  onChange={(e) => setNewPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20 font-mono"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-muted block mb-1">Opening Udhaar Balance (₹)</label>
                <input
                  type="number"
                  placeholder="0.00"
                  value={newOpeningBalance}
                  onChange={(e) => setNewOpeningBalance(e.target.value)}
                  className="w-full h-11 px-3 border border-border rounded-xl font-mono text-sm bg-background text-foreground outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={!newName.trim() || newPhone.length < 10}
                className="w-full h-12 bg-foreground text-background font-extrabold rounded-xl transition-all active:scale-[0.99] disabled:opacity-40 cursor-pointer mt-2"
              >
                Save Customer Ledger
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
