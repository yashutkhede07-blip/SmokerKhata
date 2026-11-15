import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard, ShoppingCart, Users, Package, Layers,
  BookOpen, BarChart3, Settings, Wifi, WifiOff, RefreshCw
} from 'lucide-react';
import { db } from '../db';

export const Layout: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
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

  const navItems = [
    { path: '/', label: t('dashboard'), icon: LayoutDashboard },
    { path: '/pos', label: t('pos'), icon: ShoppingCart },
    { path: '/customers', label: t('customers'), icon: Users },
    { path: '/items', label: t('items'), icon: Package },
    { path: '/stock', label: t('stock'), icon: Layers },
    { path: '/cashbook', label: t('cashbook'), icon: BookOpen },
    { path: '/reports', label: t('reports'), icon: BarChart3 },
    { path: '/settings', label: t('settings'), icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col pb-16 md:pb-0 md:pl-64">
      {/* Header with Sync Bar */}
      <header className="h-14 border-b border-border bg-surface px-4 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-lg tracking-tight">🚬 {t('appName')}</span>
        </div>

        {/* Sync Status Badge (SYNC-07, PWA-10) */}
        <div className="flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-full border border-border bg-background">
          {!isOnline ? (
            <>
              <WifiOff className="w-3.5 h-3.5 text-muted" />
              <span className="text-muted">{t('offline')}</span>
            </>
          ) : pendingCount > 0 ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>{t('pendingSync', { count: pendingCount })}</span>
            </>
          ) : (
            <>
              <Wifi className="w-3.5 h-3.5" />
              <span>{t('synced')}</span>
            </>
          )}
        </div>
      </header>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 border-r border-border bg-surface fixed top-0 bottom-0 left-0 pt-14 z-20">
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? 'bg-primary text-primaryForeground'
                    : 'text-muted hover:bg-surfaceHover hover:text-foreground'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Screen Outlet */}
      <main className="flex-1 p-4 md:p-6 max-w-7xl w-full mx-auto">
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-surface border-t border-border flex items-center justify-around z-30 px-2">
        {navItems.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const active = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center min-h-[44px] min-w-[44px] p-1 rounded-md ${
                active ? 'text-foreground font-bold' : 'text-muted'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] mt-0.5">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
};
