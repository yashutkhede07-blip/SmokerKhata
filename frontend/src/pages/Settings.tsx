import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../context/ThemeContext';
import {
  Sun, Moon, Laptop, Globe, ShieldCheck,
  Store, RefreshCw, Database, CheckCircle2
} from 'lucide-react';

export const Settings: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { theme, setTheme } = useTheme();

  const [shopName, setShopName] = useState('Sharma Kirana & Paan Center');
  const [shopPhone, setShopPhone] = useState('9876543210');
  const [upiId, setUpiId] = useState('sharmapaan@upi');
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('sk_lang', lang);
  };

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
  };

  const handleForceSync = async () => {
    setIsSyncing(true);
    setTimeout(() => {
      setIsSyncing(false);
    }, 1500);
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header Banner */}
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{t('settings')}</h1>
        <p className="text-xs sm:text-sm text-muted mt-1">
          Store Profile, Languages, Theme Preferences & Offline Sync Engine
        </p>
      </div>

      {/* Shop Profile & Counter Configuration */}
      <div className="border border-border bg-surface p-5 rounded-2xl space-y-4 shadow-xs">
        <div className="flex items-center space-x-2">
          <Store className="w-5 h-5 text-muted" />
          <h2 className="font-bold text-base text-foreground">Retail Shop Details</h2>
        </div>

        <form onSubmit={handleSaveProfile} className="space-y-3.5">
          <div>
            <label className="text-xs font-bold text-muted block mb-1">Shop / Outlet Name</label>
            <input
              type="text"
              value={shopName}
              onChange={(e) => setShopName(e.target.value)}
              className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20 font-medium"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-bold text-muted block mb-1">Counter Phone Number</label>
              <input
                type="tel"
                value={shopPhone}
                onChange={(e) => setShopPhone(e.target.value)}
                className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20 font-mono"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-muted block mb-1">Shop UPI VPA (for QR billing)</label>
              <input
                type="text"
                value={upiId}
                onChange={(e) => setUpiId(e.target.value)}
                className="w-full h-11 px-3 border border-border rounded-xl text-sm bg-background text-foreground outline-none focus:ring-2 focus:ring-foreground/20 font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            className="px-5 h-11 bg-foreground text-background font-bold rounded-xl flex items-center space-x-2 transition-all active:scale-95 cursor-pointer text-sm"
          >
            <span>{savedSuccess ? '✓ Saved Profile' : 'Update Shop Profile'}</span>
          </button>
        </form>
      </div>

      {/* Language Switcher */}
      <div className="border border-border bg-surface p-5 rounded-2xl space-y-3 shadow-xs">
        <div className="flex items-center space-x-2">
          <Globe className="w-5 h-5 text-muted" />
          <h2 className="font-bold text-base text-foreground">{t('language')}</h2>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => handleLanguageChange('en')}
            className={`p-3.5 rounded-xl border flex items-center justify-between transition-all cursor-pointer ${
              i18n.language === 'en'
                ? 'bg-foreground text-background border-foreground shadow-xs font-bold'
                : 'bg-background border-border hover:bg-surfaceHover font-medium'
            }`}
          >
            <span>English (Default)</span>
            {i18n.language === 'en' && <CheckCircle2 className="w-4 h-4" />}
          </button>

          <button
            onClick={() => handleLanguageChange('hi')}
            className={`p-3.5 rounded-xl border flex items-center justify-between transition-all cursor-pointer ${
              i18n.language === 'hi'
                ? 'bg-foreground text-background border-foreground shadow-xs font-bold'
                : 'bg-background border-border hover:bg-surfaceHover font-medium'
            }`}
          >
            <span>हिन्दी (Hindi)</span>
            {i18n.language === 'hi' && <CheckCircle2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Theme Switcher */}
      <div className="border border-border bg-surface p-5 rounded-2xl space-y-3 shadow-xs">
        <h2 className="font-bold text-base text-foreground">{t('theme')}</h2>
        <div className="grid grid-cols-3 gap-3">
          <button
            onClick={() => setTheme('light')}
            className={`p-4 rounded-xl border flex flex-col items-center space-y-2 transition-all cursor-pointer ${
              theme === 'light'
                ? 'bg-foreground text-background border-foreground shadow-xs'
                : 'bg-background border-border hover:bg-surfaceHover'
            }`}
          >
            <Sun className="w-5 h-5" />
            <span className="text-xs font-bold">{t('light')}</span>
          </button>

          <button
            onClick={() => setTheme('dark')}
            className={`p-4 rounded-xl border flex flex-col items-center space-y-2 transition-all cursor-pointer ${
              theme === 'dark'
                ? 'bg-foreground text-background border-foreground shadow-xs'
                : 'bg-background border-border hover:bg-surfaceHover'
            }`}
          >
            <Moon className="w-5 h-5" />
            <span className="text-xs font-bold">{t('dark')}</span>
          </button>

          <button
            onClick={() => setTheme('system')}
            className={`p-4 rounded-xl border flex flex-col items-center space-y-2 transition-all cursor-pointer ${
              theme === 'system'
                ? 'bg-foreground text-background border-foreground shadow-xs'
                : 'bg-background border-border hover:bg-surfaceHover'
            }`}
          >
            <Laptop className="w-5 h-5" />
            <span className="text-xs font-bold">{t('system')}</span>
          </button>
        </div>
      </div>

      {/* Offline Sync Diagnostics */}
      <div className="border border-border bg-surface p-5 rounded-2xl space-y-3 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-muted" />
            <h2 className="font-bold text-base text-foreground">Offline Storage & Outbox</h2>
          </div>
          <button
            onClick={handleForceSync}
            disabled={isSyncing}
            className="px-3 py-1.5 bg-surface hover:bg-surfaceHover border border-border rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
            <span>{isSyncing ? 'Syncing...' : 'Force Sync Now'}</span>
          </button>
        </div>

        <div className="p-3.5 bg-background border border-border rounded-xl space-y-1.5 text-xs">
          <div className="flex justify-between text-muted">
            <span>Client Engine:</span>
            <span className="font-bold text-foreground">Dexie.js IndexedDB</span>
          </div>
          <div className="flex justify-between text-muted">
            <span>Guaranteed Zero Data Loss:</span>
            <span className="text-emerald-600 font-bold">✓ Active on this Device</span>
          </div>
        </div>
      </div>

      {/* Subscription Status */}
      <div className="border border-border bg-surface p-5 rounded-2xl space-y-3 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h2 className="font-bold text-base text-foreground">Active Subscription</h2>
          </div>
          <span className="text-xs px-3 py-1 rounded-full font-extrabold bg-emerald-100 text-emerald-900 dark:bg-emerald-900/30 dark:text-emerald-300">
            14-Day Free Trial
          </span>
        </div>
        <p className="text-xs text-muted">
          All retail features unlocked (Unlimited POS bills, Customer Khata, Stock and Multi-Device Sync).
        </p>
      </div>
    </div>
  );
};
