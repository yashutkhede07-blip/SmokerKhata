import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FileSpreadsheet, FileText } from 'lucide-react';

export const Reports: React.FC = () => {
  const { t } = useTranslation();
  const [dateRange, setDateRange] = useState('7D');

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('reports')}</h1>
          <p className="text-xs text-muted">Sales Summary, Gross Margins & Document Exports</p>
        </div>
        <div className="flex space-x-2">
          {(['1D', '7D', '30D', '90D'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setDateRange(r)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold border min-h-touch ${
                dateRange === r
                  ? 'bg-primary text-primaryForeground border-primary'
                  : 'bg-surface border-border text-muted hover:bg-surfaceHover'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Summary KPI Cards (REPT-01) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 border border-border bg-surface rounded-xl space-y-1">
          <div className="text-xs text-muted font-medium">Total Sales Revenue</div>
          <div className="text-2xl font-bold">₹38,400.00</div>
          <div className="text-[11px] text-muted">184 completed bills</div>
        </div>
        <div className="p-4 border border-border bg-surface rounded-xl space-y-1">
          <div className="text-xs text-muted font-medium">Cost of Goods Sold (COGS)</div>
          <div className="text-2xl font-bold">₹28,600.00</div>
          <div className="text-[11px] text-muted">Total inventory purchase cost</div>
        </div>
        <div className="p-4 border border-border bg-surface rounded-xl space-y-1">
          <div className="text-xs text-muted font-medium">Gross Profit</div>
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">₹9,800.00</div>
          <div className="text-[11px] text-muted font-medium">Margin: 25.52%</div>
        </div>
      </div>

      {/* Export Options (REPT-04, REPT-05, REPT-06) */}
      <div className="border border-border bg-surface p-4 rounded-xl space-y-3">
        <h2 className="text-sm font-semibold">Download Business Reports</h2>
        <div className="flex flex-col sm:flex-row gap-3">
          <a
            href="/api/reports/export/"
            className="flex-1 p-3 border border-border rounded-lg bg-background hover:bg-surfaceHover flex items-center justify-center space-x-2 min-h-touch text-sm font-semibold"
          >
            <FileSpreadsheet className="w-5 h-5 text-green-600 dark:text-green-400" />
            <span>Export to Excel (.xlsx)</span>
          </a>
          <a
            href="/api/reports/export/"
            className="flex-1 p-3 border border-border rounded-lg bg-background hover:bg-surfaceHover flex items-center justify-center space-x-2 min-h-touch text-sm font-semibold"
          >
            <FileText className="w-5 h-5 text-red-600 dark:text-red-400" />
            <span>Export to PDF (.pdf)</span>
          </a>
        </div>
      </div>
    </div>
  );
};
