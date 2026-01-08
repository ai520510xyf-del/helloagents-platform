import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitest.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    // 测试环境
    environment: 'jsdom',

    // 全局变量
    globals: true,

    // 测试文件匹配模式
    include: ['src/**/*.{test,spec}.{ts,tsx}'],

    // 排除文件
    exclude: [
      'node_modules',
      'dist',
      '.idea',
      '.git',
      '.cache'
    ],

    // 设置文件
    setupFiles: ['./src/test/setup.ts'],

    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.ts',
        '**/index.ts',
        '**/main.tsx'
      ]
    },

    // 模拟模块
    mockReset: true,
    restoreMocks: true,

    // UI 模式
    ui: false,

    // 测试超时
    testTimeout: 10000
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
