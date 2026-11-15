# Phase 8 Research: PWA Frontend, Android & Go-Live

## Technical & Architecture Analysis

### 1. Requirements Matrix
- **PWA-01**: React 18 + TypeScript + Vite + Tailwind CSS PWA with service worker and manifest.
- **PWA-02**: Offline-first service worker caching app shell and static assets.
- **PWA-03**: Offline storage with Dexie.js (IndexedDB).
- **PWA-04**: Builds to static files in `backend/static_pwa/` served by Django Whitenoise.
- **PWA-05 & PWA-06**: Grayscale design system (WCAG AA), 3 theme modes (Light, Dark, System) via CSS variables, no flash on reload.
- **PWA-07**: Bilingual English & Hindi support using i18next.
- **PWA-08 & PWA-09**: Touch targets >= 44px (POS action buttons >= 56px), sub-3s load on 3G budget.
- **PWA-10**: All 10 Screens:
  1. Login (Phone + OTP)
  2. Home Dashboard (Daily sales, cash in hand, udhaar due, low stock alert)
  3. POS Billing (Item search, quick add grid, payment selector, WhatsApp receipt)
  4. Customer Ledger (List sorted by highest balance, details, WhatsApp reminders)
  5. Item Master (Categories, items, variants, soft delete)
  6. Stock Management (Ledger history, quick stock adjustment)
  7. Cash Book (Opening cash, cash-in, cash-out, closing count, mismatch flag)
  8. Reports (Date range picker, gross profit, Excel/PDF exports)
  9. Settings (Shop profile, staff list, theme & language toggles, subscription status)
  10. Sync Status Bar / Indicator (Synced, N pending, Offline, Sync error)
- **ANDR-01, ANDR-02, ANDR-03**: Capacitor Android project configuration, Gradle build scripts, signed AAB build instructions, Google Play billing plugin integration.

### 2. Frontend Directory Structure
- Monorepo directory: `d:\SmokerKhata\frontend`
- Vite build output target: `d:\SmokerKhata\backend\static_pwa`
- Django configuration: serve `static_pwa` via Whitenoise or SPA fallback view.
