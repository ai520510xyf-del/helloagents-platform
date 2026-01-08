import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration
 *
 * 支持功能：
 * - 多浏览器测试 (Chromium, Firefox)
 * - Headless 和 Headed 模式
 * - 测试报告和截图
 * - 并行执行
 * - 失败重试
 */

export default defineConfig({
  // 测试目录
  testDir: './e2e',

  // 测试匹配模式
  testMatch: '**/*.e2e.ts',

  // 超时设置
  timeout: 30000,
  expect: {
    timeout: 5000,
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
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['junit', { outputFile: 'playwright-report/results.xml' }],
    ['list'],
  ],

  // 全局配置
  use: {
    // Base URL
    baseURL: process.env.BASE_URL || 'http://localhost:5173',

    // 追踪配置
    trace: 'on-first-retry',

    // 截图配置
    screenshot: 'only-on-failure',

    // 视频配置
    video: 'retain-on-failure',

    // 导航超时
    navigationTimeout: 10000,

    // 动作超时
    actionTimeout: 5000,

    // 视口大小
    viewport: { width: 1280, height: 720 },
  },

  // 多浏览器配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    // 可选：移动端测试
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],

  // 开发服务器配置
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});
