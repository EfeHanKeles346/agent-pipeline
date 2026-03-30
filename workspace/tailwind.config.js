/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          900: '#1e3a8a'
        },
        dark: {
          50: '#f8fafc',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a'
        },
        skill: {
          expert: '#10b981',
          advanced: '#3b82f6',
          intermediate: '#f59e0b',
          beginner: '#6b7280'
        }
      },
      ringColor: {
        'focus': 'var(--tw-color-primary-500)',
        'focus-dark': 'var(--tw-color-primary-400)'
      }
    }
  },
  plugins: [require('@tailwindcss/typography')]
}
