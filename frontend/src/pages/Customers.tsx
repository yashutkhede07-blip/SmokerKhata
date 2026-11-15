import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { MessageCircle, Plus, Search } from 'lucide-react';

export const Customers: React.FC = () => {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');

  const customers = [
    { id: '1', name: 'Ramesh Sharma', phone: '9876543210', due: 1250.00, lastEntry: '2 days ago' },
    { id: '2', name: 'Amit Verma (Paan Regular)', phone: '9811223344', due: 840.00, lastEntry: 'Today' },
    { id: '3', name: 'Chai Wala Sonu', phone: '9822334455', due: 450.00, lastEntry: '5 days ago' },
    { id: '4', name: 'Vikram Singh', phone: '9833445566', due: 320.00, lastEntry: '1 week ago' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('customers')}</h1>
          <p className="text-xs text-muted">Udhaar Ledger & Payment Reminders</p>
        </div>
        <button className="h-11 px-4 bg-primary text-primaryForeground font-semibold rounded-lg flex items-center space-x-2 min-h-touch">
          <Plus className="w-4 h-4" />
          <span>Add Customer</span>
        </button>
      </div>

      <div className="relative">
        <Search className="w-4 h-4 absolute left-3 top-3.5 text-muted" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by customer name or phone..."
          className="w-full h-11 pl-9 pr-4 border border-border rounded-lg bg-surface text-foreground outline-none"
        />
      </div>

      {/* Customer List (CUST-05 sorted by highest outstanding balance) */}
      <div className="border border-border bg-surface rounded-xl divide-y divide-border overflow-hidden">
        {customers.map((c) => (
          <div key={c.id} className="p-4 flex items-center justify-between hover:bg-surfaceHover transition-colors">
            <div>
              <div className="font-semibold text-sm">{c.name}</div>
              <div className="text-xs text-muted">{c.phone} • Last: {c.lastEntry}</div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-xs text-muted">Due Balance</div>
                <div className="text-base font-bold text-red-600 dark:text-red-400">
                  ₹{c.due.toFixed(2)}
                </div>
              </div>
              <a
                href={`https://wa.me/91${c.phone}?text=Namaste%20${c.name},%20aapka%20baki%20Rs%20${c.due}%20hai.`}
                target="_blank"
                rel="noreferrer"
                className="w-10 h-10 rounded-lg border border-border bg-background flex items-center justify-center hover:bg-surfaceHover min-h-touch min-w-touch"
                title="Send WhatsApp Reminder"
              >
                <MessageCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
