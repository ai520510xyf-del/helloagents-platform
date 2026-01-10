/**
 * Lighthouse CI 配置文件
 *
 * 用于自动化性能测试和 CI/CD 集成
 */

module.exports = {
  ci: {
    collect: {
      // 要测试的 URL
      url: [
        'http://localhost:5173', // 开发服务器
        'http://localhost:4173', // 预览服务器
      ],
      // 每个 URL 运行的次数
      numberOfRuns: 3,
      // Lighthouse 设置
      settings: {
        // 模拟移动设备
        emulatedFormFactor: 'mobile',
        // 使用无头 Chrome
        chromeFlags: '--no-sandbox --headless',
        // 只运行性能审计
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      },
    },
    assert: {
      // 性能预算断言
      assertions: {
        // 整体评分要求
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],

        // Core Web Vitals 要求
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
        'speed-index': ['error', { maxNumericValue: 3400 }],

        // 资源大小要求
        'resource-summary:script:size': ['error', { maxNumericValue: 300000 }], // 300KB
        'resource-summary:stylesheet:size': ['error', { maxNumericValue: 50000 }], // 50KB
        'resource-summary:image:size': ['warn', { maxNumericValue: 200000 }], // 200KB
        'resource-summary:font:size': ['warn', { maxNumericValue: 100000 }], // 100KB
        'resource-summary:total:size': ['warn', { maxNumericValue: 500000 }], // 500KB

        // 最佳实践
        'uses-responsive-images': 'warn',
        'offscreen-images': 'warn',
        'unminified-css': 'error',
        'unminified-javascript': 'error',
        'unused-css-rules': 'warn',
        'unused-javascript': 'warn',
        'modern-image-formats': 'warn',
        'uses-text-compression': 'error',
        'uses-optimized-images': 'warn',
      },
    },
    upload: {
      // 是否上传到 Lighthouse CI 服务器
      target: 'temporary-public-storage',
    },
  },
};
