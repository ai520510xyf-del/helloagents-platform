import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import compression from 'vite-plugin-compression'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
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
        // 手动分块，提取第三方库 - 优化版
        manualChunks: (id) => {
          // React 核心库
          if (id.includes('node_modules/react') || id.includes('node_modules/react-dom')) {
            return 'react-vendor';
          }

          // Monaco Editor - 单独分块，懒加载
          if (id.includes('node_modules/monaco-editor') || id.includes('node_modules/@monaco-editor')) {
            return 'monaco-editor';
          }

          // Markdown 相关 - 拆分为独立块
          if (id.includes('node_modules/react-markdown')) {
            return 'markdown-renderer';
          }
          if (id.includes('node_modules/remark-gfm') || id.includes('node_modules/rehype-raw')) {
            return 'markdown-plugins';
          }

          // UI 组件库
          if (id.includes('node_modules/lucide-react')) {
            return 'icons';
          }
          if (id.includes('node_modules/react-resizable-panels') ||
              id.includes('node_modules/react-toastify')) {
            return 'ui-vendor';
          }

          // 网络和状态管理
          if (id.includes('node_modules/axios')) {
            return 'network';
          }
          if (id.includes('node_modules/zustand')) {
            return 'state';
          }
          if (id.includes('node_modules/socket.io-client')) {
            return 'websocket';
          }

          // Web Vitals
          if (id.includes('node_modules/web-vitals')) {
            return 'web-vitals';
          }

          // 工具库
          if (id.includes('node_modules/clsx') || id.includes('node_modules/tailwind-merge')) {
            return 'utils';
          }

          // 其他 node_modules
          if (id.includes('node_modules')) {
            return 'vendor';
          }
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
      '@monaco-editor/react', // Monaco React 包装器也排除
    ],
  },

  // Monaco Editor 优化配置
  define: {
    // 只加载需要的语言，减少 Monaco Worker 体积
    'process.env.MONACO_LANGUAGES': JSON.stringify(['python']),
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
