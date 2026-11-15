import React from 'react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, Laptop, Globe, ShieldCheck } from 'lucide-react';

export const Settings: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { theme, setTheme } = useTheme();

  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('sk_lang', lang);
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t('settings')}</h1>
        <p className="text-xs text-muted">Shop Configuration, Themes & Subscriptions</p>
      </div>

      {/* Language Switcher (PWA-07) */}
      <div className="border border-border bg-surface p-4 rounded-xl space-y-3">
        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-muted" />
          <h2 className="text-sm font-semibold">{t('language')}</h2>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => handleLanguageChange('en')}
            className={`p-3 rounded-lg border text-sm font-semibold min-h-touch ${
              i18n.language === 'en'
                ? 'bg-primary text-primaryForeground border-primary'
                : 'bg-background border-border hover:bg-surfaceHover'
            }`}
          >
            English
          </button>
          <button
            onClick={() => handleLanguageChange('hi')}
            className={`p-3 rounded-lg border text-sm font-semibold min-h-touch ${
              i18n.language === 'hi'
                ? 'bg-primary text-primaryForeground border-primary'
                : 'bg-background border-border hover:bg-surfaceHover'
            }`}
          >
            हिन्दी (Hindi)
          </button>
        </div>
      </div>

      {/* Theme Switcher (PWA-05, PWA-06) */}
      <div className="border border-border bg-surface p-4 rounded-xl space-y-3">
        <h2 className="text-sm font-semibold">{t('theme')}</h2>
        <div className="grid grid-cols-3 gap-3">
          <button
            onClick={() => setTheme('light')}
            className={`p-3 rounded-lg border flex flex-col items-center space-y-1 min-h-touch ${
              theme === 'light'
                ? 'bg-primary text-primaryForeground border-primary'
                : 'bg-background border-border hover:bg-surfaceHover'
            }`}
          >
            <Sun className="w-5 h-5" />
            <span className="text-xs font-semibold">{t('light')}</span>
          </button>
          <button
            onClick={() => setTheme('dark')}
            className={`p-3 rounded-lg border flex flex-col items-center space-y-1 min-h-touch ${
              theme === 'dark'
                ? 'bg-primary text-primaryForeground border-primary'
                : 'bg-background border-border hover:bg-surfaceHover'
            }`}
          >
            <Moon className="w-5 h-5" />
            <span className="text-xs font-semibold">{t('dark')}</span>
          </button>
          <button
            onClick={() => setTheme('system')}
            className={`p-3 rounded-lg border flex flex-col items-center space-y-1 min-h-touch ${
              theme === 'system'
                ? 'bg-primary text-primaryForeground border-primary'
                : 'bg-background border-border hover:bg-surfaceHover'
            }`}
          >
            <Laptop className="w-5 h-5" />
            <span className="text-xs font-semibold">{t('system')}</span>
          </button>
        </div>
      </div>

      {/* Subscription Status (SUBS-01, SUBS-07) */}
      <div className="border border-border bg-surface p-4 rounded-xl space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-green-600 dark:text-green-400" />
            <h2 className="text-sm font-semibold">Active Plan</h2>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full font-bold bg-green-100 text-green-900 dark:bg-green-900/30 dark:text-green-300">
            14-Day Free Trial
          </span>
        </div>
        <p className="text-xs text-muted">
          Your trial is active with unlimited billing, offline sync, and staff seats. No credit card required.
        </p>
      </div>
    </div>
  );
};
