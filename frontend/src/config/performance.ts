/**
 * 性能优化配置
 *
 * 集中管理所有性能相关的配置和优化策略
 */

/**
 * 资源加载策略
 */
export const RESOURCE_LOADING = {
  // Monaco Editor 延迟加载时间 (ms)
  MONACO_DELAY: 2000,

  // 慢速网络延迟加载时间 (ms)
  SLOW_NETWORK_DELAY: 5000,

  // 缓存过期时间 (ms)
  CACHE_EXPIRY: 24 * 60 * 60 * 1000, // 24小时

  // 资源预加载优先级
  PRELOAD_PRIORITY: {
    CRITICAL: 'high' as const,
    HIGH: 'high' as const,
    MEDIUM: 'low' as const,
    LOW: 'low' as const,
  },
} as const;

/**
 * Bundle 分割策略
 */
export const BUNDLE_STRATEGY = {
  // Chunk 大小阈值 (KB)
  CHUNK_SIZE_WARNING: 500,

  // 最大初始请求数
  MAX_INITIAL_REQUESTS: 3,

  // 最大异步请求数
  MAX_ASYNC_REQUESTS: 5,

  // 最小 chunk 大小 (bytes)
  MIN_CHUNK_SIZE: 20000,
} as const;

/**
 * Core Web Vitals 目标阈值
 */
export const WEB_VITALS_TARGETS = {
  // LCP (Largest Contentful Paint) - ms
  LCP: {
    GOOD: 2500,
    NEEDS_IMPROVEMENT: 4000,
    TARGET: 2000, // 我们的目标
  },

  // FID (First Input Delay) - ms
  FID: {
    GOOD: 100,
    NEEDS_IMPROVEMENT: 300,
    TARGET: 50, // 我们的目标
  },

  // CLS (Cumulative Layout Shift) - 无单位
  CLS: {
    GOOD: 0.1,
    NEEDS_IMPROVEMENT: 0.25,
    TARGET: 0.05, // 我们的目标
  },

  // INP (Interaction to Next Paint) - ms
  INP: {
    GOOD: 200,
    NEEDS_IMPROVEMENT: 500,
    TARGET: 150, // 我们的目标
  },

  // TTFB (Time to First Byte) - ms
  TTFB: {
    GOOD: 800,
    NEEDS_IMPROVEMENT: 1800,
    TARGET: 600, // 我们的目标
  },

  // FCP (First Contentful Paint) - ms
  FCP: {
    GOOD: 1800,
    NEEDS_IMPROVEMENT: 3000,
    TARGET: 1500, // 我们的目标
  },
} as const;

/**
 * 图片优化配置
 */
export const IMAGE_OPTIMIZATION = {
  // 支持的格式优先级
  FORMATS: ['webp', 'avif', 'jpg', 'png'] as const,

  // 质量设置
  QUALITY: {
    HIGH: 90,
    MEDIUM: 75,
    LOW: 60,
  },

  // 懒加载阈值 (viewport 距离)
  LAZY_LOAD_THRESHOLD: '50px',

  // 占位符策略
  PLACEHOLDER: {
    BLUR: 'blur' as const,
    LQIP: 'lqip' as const, // Low Quality Image Placeholder
    SOLID_COLOR: 'solid' as const,
  },
} as const;

/**
 * 网络优化配置
 */
export const NETWORK_OPTIMIZATION = {
  // API 请求超时 (ms)
  API_TIMEOUT: 10000,

  // 重试配置
  RETRY: {
    MAX_ATTEMPTS: 3,
    BACKOFF_MS: 1000,
  },

  // HTTP/2 服务器推送
  SERVER_PUSH: {
    ENABLED: true,
    RESOURCES: ['/src/main.tsx', '/src/index.css'],
  },

  // 连接优化
  CONNECTION: {
    KEEP_ALIVE: true,
    MAX_CONNECTIONS: 6,
  },
} as const;

/**
 * 缓存策略
 */
export const CACHE_STRATEGY = {
  // Service Worker 缓存策略
  SW_STRATEGY: {
    NETWORK_FIRST: 'networkFirst' as const,
    CACHE_FIRST: 'cacheFirst' as const,
    STALE_WHILE_REVALIDATE: 'staleWhileRevalidate' as const,
  },

  // 缓存分组
  CACHE_GROUPS: {
    STATIC: 'static-v1',
    API: 'api-v1',
    IMAGES: 'images-v1',
    MONACO: 'monaco-v1',
  },

  // IndexedDB 配置
  INDEXEDDB: {
    NAME: 'HelloAgentsCache',
    VERSION: 1,
    STORES: {
      LESSONS: 'lessons',
      ASSETS: 'assets',
    },
  },
} as const;

/**
 * React 性能优化配置
 */
export const REACT_OPTIMIZATION = {
  // 虚拟滚动阈值
  VIRTUAL_SCROLL_THRESHOLD: 100,

  // 防抖延迟 (ms)
  DEBOUNCE_MS: 300,

  // 节流延迟 (ms)
  THROTTLE_MS: 100,

  // 批量更新大小
  BATCH_SIZE: 50,
} as const;

/**
 * 监控和报告配置
 */
export const MONITORING = {
  // 采样率 (0-1)
  SAMPLE_RATE: {
    PRODUCTION: 0.1, // 生产环境采样 10%
    DEVELOPMENT: 1.0, // 开发环境 100%
  },

  // 性能标记
  MARKS: {
    APP_START: 'app-start',
    APP_READY: 'app-ready',
    MONACO_LOAD_START: 'monaco-load-start',
    MONACO_LOAD_END: 'monaco-load-end',
    LESSON_LOAD_START: 'lesson-load-start',
    LESSON_LOAD_END: 'lesson-load-end',
  },

  // 报告端点
  ENDPOINTS: {
    WEB_VITALS: '/api/analytics/web-vitals',
    PERFORMANCE: '/api/analytics/performance',
    ERRORS: '/api/analytics/errors',
  },
} as const;

/**
 * 性能预算 (Performance Budget)
 */
export const PERFORMANCE_BUDGET = {
  // JavaScript 预算 (KB)
  JAVASCRIPT: {
    CRITICAL: 100, // 关键路径 JS
    MAIN: 300, // 主包
    VENDOR: 500, // 第三方库
    TOTAL: 1000, // 总大小
  },

  // CSS 预算 (KB)
  CSS: {
    CRITICAL: 14, // 内联关键 CSS
    MAIN: 50, // 主样式表
    TOTAL: 100, // 总大小
  },

  // 图片预算 (KB)
  IMAGES: {
    HERO: 100, // 英雄图片
    ICON: 10, // 图标
    TOTAL: 500, // 总大小
  },

  // 字体预算 (KB)
  FONTS: {
    SINGLE: 50, // 单个字体文件
    TOTAL: 200, // 总大小
  },
} as const;

/**
 * 检查性能预算
 */
export function checkPerformanceBudget(
  type: keyof typeof PERFORMANCE_BUDGET,
  size: number,
  category: string
): { passed: boolean; message: string } {
  const budget = PERFORMANCE_BUDGET[type][category as keyof typeof PERFORMANCE_BUDGET[typeof type]];

  if (typeof budget === 'number') {
    const sizeInKB = size / 1024;
    const passed = sizeInKB <= budget;

    return {
      passed,
      message: passed
        ? `✅ ${type} ${category}: ${sizeInKB.toFixed(2)}KB (预算: ${budget}KB)`
        : `❌ ${type} ${category}: ${sizeInKB.toFixed(2)}KB 超出预算 ${budget}KB`,
    };
  }

  return { passed: true, message: '' };
}

/**
 * 性能优化建议
 */
export const OPTIMIZATION_TIPS = {
  LCP: [
    '优化服务器响应时间 (TTFB)',
    '使用 CDN 加速资源加载',
    '预加载关键资源 (preload)',
    '优化图片大小和格式 (WebP)',
    '移除渲染阻塞资源',
  ],
  FID: [
    '减少 JavaScript 执行时间',
    '代码分割和懒加载',
    '使用 Web Workers 处理耗时任务',
    '优化第三方脚本',
    '避免长任务 (> 50ms)',
  ],
  CLS: [
    '为图片和视频设置尺寸',
    '避免动态插入内容',
    '使用 CSS transform 代替 top/left',
    '预留广告位空间',
    '避免使用不确定高度的 iframe',
  ],
  INP: [
    '优化事件处理函数',
    '使用 requestIdleCallback',
    '防抖和节流',
    '减少 DOM 操作',
    '使用虚拟滚动',
  ],
} as const;
