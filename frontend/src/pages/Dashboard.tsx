import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  ShoppingCart, Users, AlertTriangle, IndianRupee,
  ArrowUpRight, Clock, Smartphone, Banknote, ShieldAlert
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const { t } = useTranslation();

  const metrics = [
    {
      label: t('todaySales'),
      value: '₹6,480.00',
      icon: IndianRupee,
      trend: '+14% vs yesterday',
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-500/10 dark:bg-emerald-500/20'
    },
    {
      label: t('cashInDrawer'),
      value: '₹4,120.00',
      icon: Banknote,
      trend: 'Balanced with register',
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-500/10 dark:bg-blue-500/20'
    },
    {
      label: t('totalUdhaar'),
      value: '₹12,850.00',
      icon: Users,
      trend: '16 active customer ledgers',
      color: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-500/10 dark:bg-amber-500/20'
    },
    {
      label: t('lowStockCount'),
      value: '3 items',
      icon: AlertTriangle,
      trend: 'Classic Milds & Thums Up low',
      color: 'text-rose-600 dark:text-rose-400',
      bg: 'bg-rose-500/10 dark:bg-rose-500/20'
    },
  ];

  const recentBills = [
    { id: 'BILL-1042', time: '2 mins ago', items: 'Gold Flake Kings (2), Chai (1)', total: 46.00, mode: 'CASH', customer: 'Walk-in' },
    { id: 'BILL-1041', time: '14 mins ago', items: 'Classic Milds (1), Thums Up (1)', total: 40.00, mode: 'UPI', customer: 'Sonu Bhai' },
    { id: 'BILL-1040', time: '28 mins ago', items: 'Maggi Masala (2), Gold Flake (1)', total: 88.00, mode: 'UDHAAR', customer: 'Ramesh Sharma' },
    { id: 'BILL-1039', time: '45 mins ago', items: 'Lays Chips (2), Sting Drink (1)', total: 40.00, mode: 'CASH', customer: 'Walk-in' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{t('dashboard')}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
              Live Register
            </span>
          </div>
          <p className="text-xs sm:text-sm text-muted mt-1">
            Sharma Kirana & Cigarette Counter • Shift 1 (Morning to Night)
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            to="/pos"
            className="h-12 px-6 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl flex items-center space-x-2 shadow-sm transition-all active:scale-[0.98] min-h-pos"
          >
            <ShoppingCart className="w-5 h-5" />
            <span>New Sale (F2)</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div
              key={idx}
              className="p-5 border border-border bg-surface rounded-2xl shadow-xs hover:border-foreground/30 transition-all flex flex-col justify-between space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-muted uppercase tracking-wider">{m.label}</span>
                <div className={`p-2 rounded-xl ${m.bg}`}>
                  <Icon className={`w-4 h-4 ${m.color}`} />
                </div>
              </div>
              <div>
                <div className="text-3xl font-extrabold tracking-tight font-mono">{m.value}</div>
                <div className="text-xs text-muted font-medium mt-1 flex items-center space-x-1">
                  <span>{m.trend}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Action Shortcuts */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Link
          to="/pos"
          className="p-4 border border-border rounded-xl bg-surface hover:bg-surfaceHover flex flex-col items-center justify-center text-center transition-all group"
        >
          <div className="w-10 h-10 rounded-full bg-emerald-500/10 dark:bg-emerald-500/20 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
            <ShoppingCart className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </div>
          <span className="font-bold text-sm">POS Billing</span>
          <span className="text-[11px] text-muted">Counter Sale</span>
        </Link>

        <Link
          to="/customers"
          className="p-4 border border-border rounded-xl bg-surface hover:bg-surfaceHover flex flex-col items-center justify-center text-center transition-all group"
        >
          <div className="w-10 h-10 rounded-full bg-amber-500/10 dark:bg-amber-500/20 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
            <Users className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          </div>
          <span className="font-bold text-sm">Customer Khata</span>
          <span className="text-[11px] text-muted">Udhaar & WhatsApp</span>
        </Link>

        <Link
          to="/cashbook"
          className="p-4 border border-border rounded-xl bg-surface hover:bg-surfaceHover flex flex-col items-center justify-center text-center transition-all group"
        >
          <div className="w-10 h-10 rounded-full bg-blue-500/10 dark:bg-blue-500/20 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
            <Banknote className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <span className="font-bold text-sm">Drawer Cash</span>
          <span className="text-[11px] text-muted">Day Reconciliation</span>
        </Link>

        <Link
          to="/stock"
          className="p-4 border border-border rounded-xl bg-surface hover:bg-surfaceHover flex flex-col items-center justify-center text-center transition-all group"
        >
          <div className="w-10 h-10 rounded-full bg-purple-500/10 dark:bg-purple-500/20 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
            <AlertTriangle className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <span className="font-bold text-sm">Stock Inventory</span>
          <span className="text-[11px] text-muted">3 Items Low</span>
        </Link>
      </div>

      {/* Payment Split & Recent Sales Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Payment Method Split */}
        <div className="lg:col-span-5 border border-border bg-surface p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold">Today's Payment Mix</h2>
            <span className="text-xs text-muted">₹6,480 total</span>
          </div>

          {/* Progress bar */}
          <div className="h-4 w-full bg-background rounded-full overflow-hidden flex border border-border">
            <div style={{ width: '64%' }} className="bg-emerald-500" title="Cash 64%"></div>
            <div style={{ width: '22%' }} className="bg-blue-500" title="UPI 22%"></div>
            <div style={{ width: '14%' }} className="bg-amber-500" title="Udhaar 14%"></div>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                <span className="font-medium">Cash in Drawer</span>
              </div>
              <div className="font-mono font-bold">₹4,147.20 (64%)</div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                <span className="font-medium">UPI / QR Scan</span>
              </div>
              <div className="font-mono font-bold">₹1,425.60 (22%)</div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                <span className="font-medium">Customer Udhaar</span>
              </div>
              <div className="font-mono font-bold">₹907.20 (14%)</div>
            </div>
          </div>

          <div className="p-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/40 rounded-xl flex items-start space-x-2.5 text-xs text-amber-900 dark:text-amber-200">
            <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5 text-amber-600" />
            <span>Reminder: Always take mobile number before recording Udhaar billing for automated SMS/WhatsApp alerts.</span>
          </div>
        </div>

        {/* Right: Recent Bills List */}
        <div className="lg:col-span-7 border border-border bg-surface p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold">Recent Counter Transactions</h2>
            <Link to="/reports" className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center space-x-1">
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-border overflow-hidden">
            {recentBills.map((bill) => (
              <div key={bill.id} className="py-3 flex items-center justify-between hover:bg-surfaceHover/50 transition-colors">
                <div className="space-y-0.5">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-foreground">{bill.id}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                      bill.mode === 'CASH'
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300'
                        : bill.mode === 'UPI'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                        : 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300'
                    }`}>
                      {bill.mode}
                    </span>
                    <span className="text-xs font-medium text-muted">• {bill.customer}</span>
                  </div>
                  <div className="text-xs text-muted line-clamp-1">{bill.items}</div>
                </div>

                <div className="text-right">
                  <div className="font-mono font-bold text-sm text-foreground">₹{bill.total.toFixed(2)}</div>
                  <div className="text-[11px] text-muted flex items-center justify-end space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{bill.time}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
