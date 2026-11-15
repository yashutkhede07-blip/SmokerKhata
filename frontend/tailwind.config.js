/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: 'var(--color-bg)',
        surface: 'var(--color-surface)',
        surfaceHover: 'var(--color-surface-hover)',
        border: 'var(--color-border)',
        foreground: 'var(--color-text)',
        muted: 'var(--color-muted)',
        primary: 'var(--color-primary)',
        primaryForeground: 'var(--color-primary-fg)',
      },
      minHeight: {
        'touch': '44px',
        'pos': '56px',
      },
      minWidth: {
        'touch': '44px',
        'pos': '56px',
      }
    },
  },
  plugins: [],
}
