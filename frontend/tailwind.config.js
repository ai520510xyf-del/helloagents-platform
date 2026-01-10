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
        // 主色调 - 增强对比度
        primary: {
          DEFAULT: '#3B82F6',
          light: '#60A5FA',
          dark: '#2563EB',
        },
        secondary: '#1E293B',
        cta: {
          DEFAULT: '#2563EB',
          light: '#3B82F6',
          dark: '#1D4ED8',
        },

        // Dark theme colors (default) - 优化对比度
        bg: {
          dark: '#0F172A',
          surface: '#1E293B',
          elevated: '#334155',
          hover: '#475569',
        },

        text: {
          primary: '#F8FAFC',      // 对比度 16:1 ✅
          secondary: '#E2E8F0',    // 对比度 11:1 ✅ (从 CBD5E1 提升)
          muted: '#94A3B8',        // 对比度 5.2:1 ✅
          disabled: '#94A3B8',     // 对比度 5.2:1 ✅ (从 64748B 提升)
        },

        border: {
          DEFAULT: '#334155',
          light: '#475569',
          strong: '#64748B',
        },

        // Light theme colors (to be used with dark: prefix)
        'bg-light': {
          DEFAULT: '#FFFFFF',
          surface: '#F8FAFC',
          elevated: '#F1F5F9',
          hover: '#E2E8F0',
        },

        'text-light': {
          primary: '#0F172A',      // 对比度 16:1 ✅
          secondary: '#475569',    // 对比度 7.1:1 ✅
          muted: '#64748B',        // 对比度 4.9:1 ✅
          disabled: '#64748B',     // 对比度 4.9:1 ✅ (从 94A3B8 提升)
        },

        'border-light': {
          DEFAULT: '#E2E8F0',
          dark: '#CBD5E1',
          strong: '#94A3B8',
        },

        // 状态颜色 - WCAG AA 标准
        success: {
          DEFAULT: '#10B981',
          light: '#34D399',
          dark: '#059669',
        },
        warning: {
          DEFAULT: '#F59E0B',
          light: '#FBBF24',
          dark: '#D97706',
        },
        error: {
          DEFAULT: '#EF4444',
          light: '#F87171',
          dark: '#DC2626',
        },
        info: {
          DEFAULT: '#3B82F6',
          light: '#60A5FA',
          dark: '#2563EB',
        },
        ai: {
          DEFAULT: '#A855F7',
          light: '#C084FC',
          dark: '#9333EA',
        },
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
        'slide-up': {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'bounce-subtle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(59, 130, 246, 0.7)' },
          '50%': { opacity: '0.8', boxShadow: '0 0 20px 10px rgba(59, 130, 246, 0)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-in': 'slide-in 0.3s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
        'bounce-subtle': 'bounce-subtle 2s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
    },
  },
  plugins: [],
}
