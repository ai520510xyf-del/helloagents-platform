import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E 测试配置
 *
 * 测试范围：
 * - 课程浏览和切换
 * - 代码编辑器交互
 * - 代码运行流程
 * - AI 助手对话
 * - 主题切换
 * - 移动端响应式布局
 *
 * 在线地址: https://helloagents-platform.pages.dev
 */

export default defineConfig({
  // 测试目录
  testDir: './e2e',

  // 测试匹配模式
  testMatch: '**/*.e2e.ts',

  // 超时设置
  timeout: 60000,
  expect: {
    timeout: 10000,
  },

  // 失败处理
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,

  // 并行工作线程
  workers: process.env.CI ? 1 : undefined,

  // 报告器配置
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list'],
  ],

  // 全局配置
  use: {
    // Base URL - 优先使用环境变量，本地开发用 localhost，CI 用生产地址
    baseURL: process.env.BASE_URL || (process.env.CI ? 'https://helloagents-platform.pages.dev' : 'http://localhost:5173'),

    // 追踪配置
    trace: 'on-first-retry',

    // 截图配置
    screenshot: 'only-on-failure',

    // 视频配置
    video: 'retain-on-failure',

    // 导航超时
    navigationTimeout: 30000,

    // 动作超时
    actionTimeout: 15000,

    // 视口大小（桌面端）
    viewport: { width: 1920, height: 1080 },
  },

  // 多浏览器和设备配置
  projects: [
    // 桌面浏览器
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        viewport: { width: 1920, height: 1080 },
      },
    },

    // 移动设备
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
      },
    },
    {
      name: 'mobile-safari',
      use: {
        ...devices['iPhone 12'],
      },
    },

    // 平板设备
    {
      name: 'tablet-ipad',
      use: {
        ...devices['iPad Pro'],
      },
    },
  ],

  // 开发服务器配置（仅本地开发时使用）
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120000,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});
