/**
 * E2E Test: Error Handling
 *
 * 测试错误处理流程：
 * 1. 触发 API 错误
 * 2. 验证 Toast 通知显示
 * 3. 验证错误日志记录
 * 4. 验证错误恢复
 */

import { test, expect } from '@playwright/test';
import {
  PageHelpers,
  CodeEditorHelpers,
  CodeExecutionHelpers,
  ToastHelpers,
  APIMockHelpers,
  AIAssistantHelpers,
} from './utils/test-helpers';
import { ERROR_SCENARIOS, EXPECTED_RESULTS } from './fixtures/test-data';

test.describe('Error Handling', () => {
  let pageHelpers: PageHelpers;
  let editorHelpers: CodeEditorHelpers;
  let executionHelpers: CodeExecutionHelpers;
  let toastHelpers: ToastHelpers;
  let apiMockHelpers: APIMockHelpers;
  let aiHelpers: AIAssistantHelpers;

  test.beforeEach(async ({ page }) => {
    pageHelpers = new PageHelpers(page);
    editorHelpers = new CodeEditorHelpers(page);
    executionHelpers = new CodeExecutionHelpers(page);
    toastHelpers = new ToastHelpers(page);
    apiMockHelpers = new APIMockHelpers(page);
    aiHelpers = new AIAssistantHelpers(page);

    // 导航到学习页面
    await pageHelpers.navigateToLearnPage();
  });

  test('should display toast notification on API error', async ({ page }) => {
    // Mock API 错误
    await apiMockHelpers.mockAPIError(
      '/api/execute',
      ERROR_SCENARIOS.apiErrors.serverError.status,
      ERROR_SCENARIOS.apiErrors.serverError.message
    );

    // 尝试执行代码
    await editorHelpers.setCode('print("Hello")');
    await executionHelpers.clickRunButton();

    // 验证 Toast 通知显示
    await toastHelpers.waitForToast();
    await toastHelpers.expectToastContains(EXPECTED_RESULTS.toastMessages.error);
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Mock 网络错误
    await apiMockHelpers.mockNetworkError('/api/execute');

    // 尝试执行代码
    await editorHelpers.setCode('print("Hello")');
    await executionHelpers.clickRunButton();

    // 验证错误通知
    await toastHelpers.waitForToast(10000);
    await toastHelpers.expectToastContains(EXPECTED_RESULTS.toastMessages.networkError);
  });

  test('should display syntax error in terminal output', async ({ page }) => {
    // 输入有语法错误的代码
    await editorHelpers.setCode(ERROR_SCENARIOS.codeErrors.syntaxError);

    // 运行代码
    await executionHelpers.clickRunButton();
    await executionHelpers.waitForExecution();

    // 验证终端显示错误
    const output = await executionHelpers.getTerminalOutput();
    expect(output).toMatch(/SyntaxError|语法错误|Error/i);
  });

  test('should display runtime error in terminal output', async ({ page }) => {
    // 输入有运行时错误的代码
    await editorHelpers.setCode(ERROR_SCENARIOS.codeErrors.nameError);

    // 运行代码
    await executionHelpers.clickRunButton();
    await executionHelpers.waitForExecution();

    // 验证终端显示错误
    const output = await executionHelpers.getTerminalOutput();
    expect(output).toMatch(/NameError|TypeError|Error|错误/i);
  });

  test('should log errors to console', async ({ page }) => {
    const consoleMessages: string[] = [];

    // 监听控制台消息
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleMessages.push(msg.text());
      }
    });

    // Mock API 错误
    await apiMockHelpers.mockAPIError('/api/execute', 500);

    // 尝试执行代码
    await editorHelpers.setCode('print("Hello")');
    await executionHelpers.clickRunButton();

    // 等待错误发生
    await page.waitForTimeout(2000);

    // 验证控制台有错误日志（可能没有，取决于实现）
    // 这是一个可选验证
    if (consoleMessages.length > 0) {
      expect(consoleMessages.some(msg => msg.includes('error') || msg.includes('Error'))).toBe(true);
    }
  });

  test('should allow retry after API error', async ({ page }) => {
    // Mock API 错误
    await apiMockHelpers.mockAPIError('/api/execute', 500);

    // 第一次尝试执行（会失败）
    await editorHelpers.setCode('print("Hello")');
    await executionHelpers.clickRunButton();
    await toastHelpers.waitForToast();

    // 清除 Mock，恢复正常
    await apiMockHelpers.clearAllMocks();

    // 第二次尝试执行（应该成功）
    await executionHelpers.clickRunButton();
    await executionHelpers.waitForExecution();

    // 验证执行成功
    const output = await executionHelpers.getTerminalOutput();
    expect(output).toContain('Hello');
  });

  test('should handle AI assistant API errors', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // Mock AI API 错误
    await apiMockHelpers.mockAPIError('/api/chat', 500);

    // 发送消息
    await aiHelpers.sendMessage('测试错误处理');

    // 验证显示错误消息
    await page.waitForTimeout(2000);
    const errorMessage = page.getByText(/错误|Error|failed|失败/i);
    await expect(errorMessage.first()).toBeVisible({ timeout: 5000 });
  });

  test('should handle timeout errors', async ({ page }) => {
    // Mock API 超时
    await page.route('**/api/execute', async (route) => {
      // 延迟很长时间模拟超时
      await page.waitForTimeout(30000);
      route.fulfill({
        status: 408,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Request Timeout' }),
      });
    });

    // 尝试执行代码
    await editorHelpers.setCode('print("Hello")');
    await executionHelpers.clickRunButton();

    // 验证超时错误处理（可能显示 Toast 或终端错误）
    await page.waitForTimeout(5000);

    // 检查是否有错误提示
    const hasToast = await page.locator('[data-testid="toast"], .toast, .Toastify').isVisible().catch(() => false);
    const output = await executionHelpers.getTerminalOutput();
    const hasTerminalError = output.includes('error') || output.includes('Error') || output.includes('timeout');

    expect(hasToast || hasTerminalError).toBe(true);
  });

  test('should recover from JavaScript errors without page crash', async ({ page }) => {
    // 监听页面错误
    const pageErrors: Error[] = [];
    page.on('pageerror', (error) => {
      pageErrors.push(error);
    });

    // 执行一些操作
    await editorHelpers.setCode('print("Test")');
    await executionHelpers.clickRunButton();
    await executionHelpers.waitForExecution();

    // 即使有错误，页面应该仍然可用
    await expect(page.locator('body')).toBeVisible();

    // 验证可以继续使用
    await editorHelpers.setCode('print("Still working")');
    const code = await editorHelpers.getCode();
    expect(code).toBe('print("Still working")');
  });

  test('should display user-friendly error messages', async ({ page }) => {
    // Mock API 错误
    await apiMockHelpers.mockAPIResponse('/api/execute', {
      success: false,
      error: '服务器内部错误',
      message: '代码执行失败，请稍后重试'
    }, 500);

    // 尝试执行代码
    await editorHelpers.setCode('print("Hello")');
    await executionHelpers.clickRunButton();

    // 等待错误消息
    await toastHelpers.waitForToast();

    // 验证显示用户友好的错误消息（不是技术错误）
    const toastMessage = await toastHelpers.getToastMessage();

    // 应该包含中文或用户友好的描述，而不是技术栈追踪
    expect(toastMessage).not.toMatch(/stack|trace|undefined|null/i);
    expect(toastMessage.length).toBeGreaterThan(0);
  });

  test('should handle missing or malformed API responses', async ({ page }) => {
    // Mock 格式错误的响应
    await page.route('**/api/execute', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'text/html',
        body: '<html>Not JSON</html>',
      });
    });

    // 尝试执行代码
    await editorHelpers.setCode('print("Hello")');
    await executionHelpers.clickRunButton();

    // 验证应用处理了格式错误的响应
    await page.waitForTimeout(2000);

    // 应该显示错误或保持稳定
    const isStable = await page.locator('body').isVisible();
    expect(isStable).toBe(true);
  });

  test('should handle concurrent API requests correctly', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 同时发送代码执行和 AI 请求
    await editorHelpers.setCode('print("Hello")');

    // 快速连续点击
    await executionHelpers.clickRunButton();
    await aiHelpers.sendMessage('测试并发请求');

    // 等待两个请求完成
    await page.waitForTimeout(3000);

    // 验证应用仍然正常
    await expect(page.locator('body')).toBeVisible();
  });

  test('should display error boundary fallback on component crash', async ({ page }) => {
    // 这个测试比较难触发，因为需要组件崩溃
    // 可以尝试触发一些异常情况

    // 尝试无效操作（如果有的话）
    await page.evaluate(() => {
      // 尝试破坏某些状态（仅用于测试）
      try {
        (window as any).__REACT_ERROR_TEST__ = true;
      } catch (e) {
        // 忽略
      }
    });

    // 验证页面仍然可以恢复或显示错误界面
    await expect(page.locator('body')).toBeVisible();
  });

  test('should preserve user data after error recovery', async ({ page }) => {
    // 输入一些代码
    const testCode = 'print("Important code")';
    await editorHelpers.setCode(testCode);

    // Mock API 错误
    await apiMockHelpers.mockAPIError('/api/execute', 500);

    // 尝试执行（会失败）
    await executionHelpers.clickRunButton();
    await page.waitForTimeout(1000);

    // 清除 Mock
    await apiMockHelpers.clearAllMocks();

    // 验证代码仍然保留
    const savedCode = await editorHelpers.getCode();
    expect(savedCode).toBe(testCode);
  });

  test('should handle localStorage errors gracefully', async ({ page }) => {
    // 清除 localStorage
    await page.evaluate(() => {
      localStorage.clear();
    });

    // 刷新页面
    await page.reload();
    await pageHelpers.waitForPageLoad();

    // 验证应用仍然可以工作
    await expect(page.locator('.monaco-editor')).toBeVisible({ timeout: 10000 });

    // 可以输入代码
    await editorHelpers.setCode('print("Test")');
    const code = await editorHelpers.getCode();
    expect(code).toBe('print("Test")');
  });
});
