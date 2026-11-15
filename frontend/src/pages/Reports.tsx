import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FileSpreadsheet, FileText, Download
} from 'lucide-react';

export const Reports: React.FC = () => {
  const { t } = useTranslation();
  const [dateRange, setDateRange] = useState<'1D' | '7D' | '30D' | '90D'>('7D');
  const [isExporting, setIsExporting] = useState<'EXCEL' | 'PDF' | null>(null);

  const topItems = [
    { rank: 1, name: 'Gold Flake Kings', category: 'Cigarettes', qty: 384, revenue: 6912.00, margin: '28%' },
    { rank: 2, name: 'Classic Milds', category: 'Cigarettes', qty: 290, revenue: 5800.00, margin: '25%' },
    { rank: 3, name: 'Thums Up 250ml', category: 'Cold Drinks', qty: 142, revenue: 2840.00, margin: '21%' },
    { rank: 4, name: 'Adrak Masala Chai', category: 'Chai & Food', qty: 210, revenue: 2520.00, margin: '62%' },
    { rank: 5, name: 'Maggi Masala (Cooked)', category: 'Chai & Food', qty: 65, revenue: 2275.00, margin: '54%' },
  ];

  const handleExport = (type: 'EXCEL' | 'PDF') => {
    setIsExporting(type);
    setTimeout(() => {
      setIsExporting(null);
      // Trigger download
      window.open(`/api/reports/export/?format=${type.toLowerCase()}&range=${dateRange}`, '_blank');
    }, 1000);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{t('reports')}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-300">
              P&L & Analytics
            </span>
          </div>
          <p className="text-xs sm:text-sm text-muted mt-1">
            Revenue Analytics, Gross Margins, Fast-Moving Stock & Official Exports
          </p>
        </div>

        {/* Date Filter Pills */}
        <div className="flex space-x-2">
          {(['1D', '7D', '30D', '90D'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setDateRange(r)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                dateRange === r
                  ? 'bg-foreground text-background border-foreground shadow-xs'
                  : 'bg-surface border-border text-muted hover:bg-surfaceHover'
              }`}
            >
              {r === '1D' ? 'Today' : r === '7D' ? 'Last 7 Days' : r === '30D' ? 'This Month' : 'Quarter'}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Revenue & Profit Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 border border-border bg-surface rounded-2xl space-y-2 shadow-xs">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Total Sales Turnover</span>
          <div className="font-mono text-3xl font-extrabold text-foreground">
            ₹{dateRange === '1D' ? '6,480.00' : dateRange === '7D' ? '45,360.00' : '1,94,400.00'}
          </div>
          <span className="text-xs text-muted block">
            {dateRange === '1D' ? '28 bills' : dateRange === '7D' ? '194 bills' : '840 bills'}
          </span>
        </div>

        <div className="p-5 border border-border bg-surface rounded-2xl space-y-2 shadow-xs">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Cost of Goods Sold (COGS)</span>
          <div className="font-mono text-3xl font-extrabold text-foreground">
            ₹{dateRange === '1D' ? '4,795.00' : dateRange === '7D' ? '33,566.00' : '1,43,850.00'}
          </div>
          <span className="text-xs text-muted block">Stock replacement purchase cost</span>
        </div>

        <div className="p-5 border border-border bg-surface rounded-2xl space-y-2 shadow-xs">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Estimated Gross Profit</span>
          <div className="font-mono text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
            ₹{dateRange === '1D' ? '1,685.00' : dateRange === '7D' ? '11,794.00' : '50,550.00'}
          </div>
          <span className="text-xs text-emerald-600 dark:text-emerald-400 font-bold block">
            Average margin: 26.0%
          </span>
        </div>

        <div className="p-5 border border-border bg-surface rounded-2xl space-y-2 shadow-xs">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider">Average Bill Size</span>
          <div className="font-mono text-3xl font-extrabold text-foreground">₹233.80</div>
          <span className="text-xs text-muted block">3.2 items per transaction</span>
        </div>
      </div>

      {/* Top 5 Selling Products */}
      <div className="border border-border bg-surface p-5 rounded-2xl space-y-4 shadow-xs">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-base text-foreground">Top Fast-Moving Retail Items ({dateRange})</h2>
          <span className="text-xs text-muted">Sorted by sales volume</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs font-semibold text-muted uppercase">
                <th className="pb-3"># Rank</th>
                <th className="pb-3">Product Name</th>
                <th className="pb-3">Category</th>
                <th className="pb-3 text-right">Units Sold</th>
                <th className="pb-3 text-right">Gross Revenue</th>
                <th className="pb-3 text-right">Profit Margin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {topItems.map((item) => (
                <tr key={item.rank} className="hover:bg-surfaceHover/50 transition-colors">
                  <td className="py-3 font-bold text-muted">#{item.rank}</td>
                  <td className="py-3 font-bold text-foreground">{item.name}</td>
                  <td className="py-3 text-xs text-muted">{item.category}</td>
                  <td className="py-3 text-right font-mono font-bold">{item.qty}</td>
                  <td className="py-3 text-right font-mono font-bold text-foreground">₹{item.revenue.toFixed(2)}</td>
                  <td className="py-3 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">
                    {item.margin}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Export Actions (REPT-04, REPT-05) */}
      <div className="border border-border bg-surface p-5 rounded-2xl space-y-4 shadow-xs">
        <h2 className="font-bold text-base text-foreground">Export Official Documents</h2>
        <p className="text-xs text-muted">
          Generate branded spreadsheets for tax accounting or PDF statements for shop partners.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            onClick={() => handleExport('EXCEL')}
            disabled={isExporting !== null}
            className="p-4 border border-border rounded-xl bg-background hover:bg-surfaceHover flex items-center justify-between transition-all cursor-pointer group disabled:opacity-50"
          >
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 rounded-xl group-hover:scale-105 transition-transform">
                <FileSpreadsheet className="w-6 h-6" />
              </div>
              <div className="text-left">
                <span className="font-bold text-sm text-foreground block">
                  {isExporting === 'EXCEL' ? 'Generating Excel...' : 'Export to Excel (.xlsx)'}
                </span>
                <span className="text-xs text-muted">Detailed itemized transaction log</span>
              </div>
            </div>
            <Download className="w-5 h-5 text-muted group-hover:text-foreground transition-colors" />
          </button>

          <button
            onClick={() => handleExport('PDF')}
            disabled={isExporting !== null}
            className="p-4 border border-border rounded-xl bg-background hover:bg-surfaceHover flex items-center justify-between transition-all cursor-pointer group disabled:opacity-50"
          >
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-rose-500/10 dark:bg-rose-500/20 text-rose-600 rounded-xl group-hover:scale-105 transition-transform">
                <FileText className="w-6 h-6" />
              </div>
              <div className="text-left">
                <span className="font-bold text-sm text-foreground block">
                  {isExporting === 'PDF' ? 'Generating PDF...' : 'Export to PDF (.pdf)'}
                </span>
                <span className="text-xs text-muted">Printable summary statement</span>
              </div>
            </div>
            <Download className="w-5 h-5 text-muted group-hover:text-foreground transition-colors" />
          </button>
        </div>
      </div>
    </div>
  );
};
