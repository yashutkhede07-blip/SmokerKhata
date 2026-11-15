import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard, ShoppingCart, Users, Package, Layers,
  BookOpen, BarChart3, Settings, WifiOff, RefreshCw,
  Sun, Moon, Globe
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { db } from '../db';

export const Layout: React.FC = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const { theme, setTheme } = useTheme();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const checkOutbox = async () => {
      try {
        const count = await db.outbox.count();
        setPendingCount(count);
      } catch (e) {
        // DB not ready or Dexie error
      }
    };
    checkOutbox();
    const interval = setInterval(checkOutbox, 3000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  const toggleLanguage = () => {
    const next = i18n.language === 'en' ? 'hi' : 'en';
    i18n.changeLanguage(next);
    localStorage.setItem('sk_lang', next);
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const navItems = [
    { path: '/', label: t('dashboard'), icon: LayoutDashboard },
    { path: '/pos', label: t('pos'), icon: ShoppingCart, badge: 'F2' },
    { path: '/customers', label: t('customers'), icon: Users },
    { path: '/items', label: t('items'), icon: Package },
    { path: '/stock', label: t('stock'), icon: Layers },
    { path: '/cashbook', label: t('cashbook'), icon: BookOpen },
    { path: '/reports', label: t('reports'), icon: BarChart3 },
    { path: '/settings', label: t('settings'), icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col pb-20 md:pb-0 md:pl-64 transition-colors duration-150">
      {/* Top Header */}
      <header className="h-16 border-b border-border bg-surface/90 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-xs">
        <div className="flex items-center space-x-3">
          <Link to="/" className="flex items-center space-x-2.5 group">
            <span className="text-2xl transform group-hover:scale-110 transition-transform">🚬</span>
            <div className="leading-tight">
              <span className="font-extrabold text-base tracking-tight block text-foreground">
                {t('appName')}
              </span>
              <span className="text-[10px] text-muted hidden sm:block font-medium">
                Sharma Kirana & Paan Center
              </span>
            </div>
          </Link>
        </div>

        {/* Header Right Actions */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Quick Lang Switch */}
          <button
            onClick={toggleLanguage}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg border border-border bg-surface hover:bg-surfaceHover text-xs font-semibold text-foreground transition-colors cursor-pointer"
            title="Switch Language / भाषा बदलें"
          >
            <Globe className="w-3.5 h-3.5 text-muted" />
            <span>{i18n.language === 'en' ? 'हिन्दी' : 'EN'}</span>
          </button>

          {/* Theme Quick Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg border border-border bg-surface hover:bg-surfaceHover text-muted hover:text-foreground transition-colors cursor-pointer"
            title="Toggle Light/Dark Theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
          </button>

          {/* Sync Status Badge */}
          <div className="flex items-center space-x-2 text-xs font-semibold px-3 py-1.5 rounded-full border border-border bg-surface shadow-xs">
            {!isOnline ? (
              <>
                <WifiOff className="w-3.5 h-3.5 text-amber-500 animate-pulse" />
                <span className="text-amber-600 dark:text-amber-400 font-bold">{t('offline')}</span>
              </>
            ) : pendingCount > 0 ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 text-blue-500 animate-spin" />
                <span className="text-blue-600 dark:text-blue-400">{t('pendingSync', { count: pendingCount })}</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-emerald-500/20"></span>
                <span className="text-emerald-700 dark:text-emerald-400">{t('synced')}</span>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 border-r border-border bg-surface fixed top-0 bottom-0 left-0 pt-16 z-20">
        <div className="p-3">
          <Link
            to="/pos"
            className="w-full h-11 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl flex items-center justify-center space-x-2 shadow-sm transition-all active:scale-[0.98]"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>{t('newBill')}</span>
          </Link>
        </div>

        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  active
                    ? 'bg-foreground text-background shadow-xs'
                    : 'text-muted hover:bg-surfaceHover hover:text-foreground'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-bold ${active ? 'bg-background/20 text-background' : 'bg-surface border border-border text-muted'}`}>
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-border">
          <div className="p-3 rounded-xl bg-background border border-border space-y-1">
            <div className="flex items-center justify-between text-[11px] font-bold text-foreground">
              <span>Offline-First PWA</span>
              <span className="text-emerald-600 font-bold">100% Active</span>
            </div>
            <p className="text-[10px] text-muted leading-tight">
              Zero Data Loss: Every transaction saved to local Dexie before network sync.
            </p>
          </div>
        </div>
      </aside>

      {/* Main Content Viewport */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation Bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-surface/95 backdrop-blur-lg border-t border-border flex items-center justify-around px-2 z-30 shadow-lg">
        {navItems.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const active = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center flex-1 py-1 rounded-lg transition-colors min-h-[44px] ${
                active ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-muted'
              }`}
            >
              <Icon className={`w-5 h-5 ${active ? 'stroke-[2.5]' : 'stroke-[1.75]'}`} />
              <span className="text-[10px] tracking-tight mt-0.5 line-clamp-1">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
};
