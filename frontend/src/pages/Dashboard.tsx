import React from 'react';
import { useTranslation } from 'react-i18next';
import { ShoppingCart, Users, AlertTriangle, IndianRupee } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const { t } = useTranslation();

  const metrics = [
    { label: t('todaySales'), value: '₹4,850.00', icon: IndianRupee, change: '+12% from yesterday' },
    { label: t('cashInDrawer'), value: '₹3,200.00', icon: IndianRupee, change: 'Reconciled today' },
    { label: t('totalUdhaar'), value: '₹14,500.00', icon: Users, change: '18 active accounts' },
    { label: t('lowStockCount'), value: '4 items', icon: AlertTriangle, change: 'Reorder suggested' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('dashboard')}</h1>
          <p className="text-xs text-muted">Daily Retail Performance & Live Stats</p>
        </div>
        <Link
          to="/pos"
          className="h-12 px-6 bg-primary text-primaryForeground font-semibold rounded-lg flex items-center space-x-2 min-h-pos"
        >
          <ShoppingCart className="w-5 h-5" />
          <span>New Bill (F2)</span>
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className="p-4 border border-border bg-surface rounded-xl space-y-2">
              <div className="flex items-center justify-between text-muted">
                <span className="text-xs font-medium">{m.label}</span>
                <Icon className="w-4 h-4" />
              </div>
              <div className="text-2xl font-bold">{m.value}</div>
              <div className="text-[11px] text-muted">{m.change}</div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions Grid */}
      <div className="border border-border bg-surface p-4 rounded-xl space-y-3">
        <h2 className="text-sm font-semibold">Quick Actions</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Link
            to="/pos"
            className="p-3 border border-border rounded-lg bg-background hover:bg-surfaceHover flex flex-col items-center justify-center min-h-[56px] text-center"
          >
            <span className="font-semibold text-sm">POS Billing</span>
            <span className="text-[10px] text-muted">Quick Sale</span>
          </Link>
          <Link
            to="/customers"
            className="p-3 border border-border rounded-lg bg-background hover:bg-surfaceHover flex flex-col items-center justify-center min-h-[56px] text-center"
          >
            <span className="font-semibold text-sm">Udhaar Ledger</span>
            <span className="text-[10px] text-muted">Customer Khata</span>
          </Link>
          <Link
            to="/cashbook"
            className="p-3 border border-border rounded-lg bg-background hover:bg-surfaceHover flex flex-col items-center justify-center min-h-[56px] text-center"
          >
            <span className="font-semibold text-sm">Cash Book</span>
            <span className="text-[10px] text-muted">Drawer Count</span>
          </Link>
          <Link
            to="/reports"
            className="p-3 border border-border rounded-lg bg-background hover:bg-surfaceHover flex flex-col items-center justify-center min-h-[56px] text-center"
          >
            <span className="font-semibold text-sm">Reports</span>
            <span className="text-[10px] text-muted">Excel / PDF</span>
          </Link>
        </div>
      </div>
    </div>
  );
};
