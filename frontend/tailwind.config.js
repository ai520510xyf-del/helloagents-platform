/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{ts,tsx,js,jsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['IBM Plex Sans', 'sans-serif'],
      },
      colors: {
        primary: '#3B82F6',
        secondary: '#1E293B',
        cta: '#2563EB',

        // Dark theme colors (default)
        bg: {
          dark: '#0F172A',
          surface: '#1E293B',
          elevated: '#334155',
        },

        text: {
          primary: '#F1F5F9',
          secondary: '#94A3B8',
          muted: '#64748B',
        },

        border: {
          DEFAULT: '#334155',
          light: '#475569',
        },

        // Light theme colors (to be used with dark: prefix)
        'bg-light': {
          DEFAULT: '#FFFFFF',
          surface: '#F8FAFC',
          elevated: '#F1F5F9',
        },

        'text-light': {
          primary: '#0F172A',
          secondary: '#475569',
          muted: '#64748B',
        },

        'border-light': {
          DEFAULT: '#E2E8F0',
          dark: '#CBD5E1',
        },

        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#3B82F6',
        ai: '#A855F7',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in': {
          '0%': { transform: 'translateX(20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-in': 'slide-in 0.3s ease-out',
      },
    },
  },
  plugins: [],
}
