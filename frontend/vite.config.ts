import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import compression from 'vite-plugin-compression'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  plugins: [
    react(),

    // Bundle 分析 - 生成可视化报告
    visualizer({
      filename: 'dist/stats.html',
      open: false, // 构建后自动打开报告
      gzipSize: true,
      brotliSize: true,
      template: 'treemap', // 使用树状图模板
    }),

    // Gzip 压缩
    compression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 1024, // 只压缩大于 1KB 的文件
      deleteOriginFile: false,
    }),

    // Brotli 压缩 (更高压缩率)
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 1024,
      deleteOriginFile: false,
    }),
  ],

  server: {
    hmr: {
      protocol: 'ws',
      host: 'localhost',
    },
  },

  build: {
    // 启用 CSS 代码分割
    cssCodeSplit: true,

    // 优化 Chunk 分割策略
    rollupOptions: {
      output: {
        // 手动分块，提取第三方库
        manualChunks: {
          // React 核心库
          'react-vendor': ['react', 'react-dom'],

          // Monaco Editor (代码编辑器 - 较大)
          'monaco-editor': ['monaco-editor', '@monaco-editor/react'],

          // Markdown 相关
          'markdown': ['react-markdown', 'remark-gfm', 'rehype-raw'],

          // UI 组件库
          'ui-vendor': [
            'lucide-react',
            'react-resizable-panels',
            'react-toastify',
          ],

          // 工具库
          'utils': ['axios', 'zustand', 'socket.io-client', 'clsx', 'tailwind-merge'],
        },

        // 优化文件命名
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },

    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 生产环境移除 console
        drop_debugger: true, // 移除 debugger
        pure_funcs: ['console.log', 'console.info', 'console.debug'], // 移除指定函数
      },
      format: {
        comments: false, // 移除注释
      },
    },

    // 调整 chunk 大小警告阈值
    chunkSizeWarningLimit: 500, // 500KB

    // 生产环境关闭 sourcemap
    sourcemap: false,

    // 优化构建性能
    target: 'es2015',

    // 报告压缩后的大小
    reportCompressedSize: true,
  },

  // 优化依赖预构建
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'axios',
      'zustand',
    ],
    exclude: [
      'monaco-editor', // Monaco 已经过优化，不需要预构建
    ],
  },

  // Vitest 测试配置
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        '**/*.spec.tsx',
      ],
    },
  },
})
