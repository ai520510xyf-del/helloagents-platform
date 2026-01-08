/**
 * E2E Test Helper Functions
 *
 * 通用测试工具函数
 */

import { Page, expect } from '@playwright/test';
import { TEST_DATA } from '../fixtures/test-data';

/**
 * 页面加载助手
 */
export class PageHelpers {
  constructor(private page: Page) {}

  /**
   * 等待页面完全加载
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {
      // 忽略网络空闲超时，某些页面可能持续有网络活动
    });
  }

  /**
   * 导航到学习页面
   */
  async navigateToLearnPage() {
    await this.page.goto('/');
    await this.waitForPageLoad();
  }

  /**
   * 等待元素可见
   */
  async waitForElement(selector: string, timeout = 5000) {
    await this.page.waitForSelector(selector, { state: 'visible', timeout });
  }

  /**
   * 截图（用于调试）
   */
  async takeScreenshot(name: string) {
    await this.page.screenshot({
      path: `playwright-report/screenshots/${name}.png`,
      fullPage: true,
    });
  }
}

/**
 * 代码编辑器助手
 */
export class CodeEditorHelpers {
  constructor(private page: Page) {}

  /**
   * 获取代码编辑器
   */
  async getEditor() {
    // Monaco Editor 通常使用 .monaco-editor 类
    return this.page.locator('.monaco-editor').first();
  }

  /**
   * 设置代码内容
   */
  async setCode(code: string) {
    // 等待编辑器加载
    await this.page.waitForSelector('.monaco-editor', { timeout: 10000 });

    // 使用 Monaco Editor API 设置代码
    await this.page.evaluate((codeText) => {
      const monaco = (window as any).monaco;
      if (monaco) {
        const models = monaco.editor.getModels();
        if (models.length > 0) {
          models[0].setValue(codeText);
        }
      }
    }, code);

    // 等待一下确保代码已设置
    await this.page.waitForTimeout(500);
  }

  /**
   * 获取代码内容
   */
  async getCode(): Promise<string> {
    return await this.page.evaluate(() => {
      const monaco = (window as any).monaco;
      if (monaco) {
        const models = monaco.editor.getModels();
        if (models.length > 0) {
          return models[0].getValue();
        }
      }
      return '';
    });
  }

  /**
   * 清空代码
   */
  async clearCode() {
    await this.setCode('');
  }
}

/**
 * 代码执行助手
 */
export class CodeExecutionHelpers {
  constructor(private page: Page) {}

  /**
   * 点击运行按钮
   */
  async clickRunButton() {
    const runButton = this.page.getByRole('button', { name: /运行|Run/i });
    await runButton.click();
  }

  /**
   * 点击停止按钮
   */
  async clickStopButton() {
    const stopButton = this.page.getByRole('button', { name: /停止|Stop/i });
    await stopButton.click();
  }

  /**
   * 等待代码执行完成
   */
  async waitForExecution(timeout = TEST_DATA.timeouts.codeExecution) {
    // 等待运行按钮重新启用（不再显示"运行中"状态）
    await this.page.waitForSelector('button:has-text("运行"), button:has-text("Run")', {
      timeout,
      state: 'visible',
    });
  }

  /**
   * 获取终端输出
   */
  async getTerminalOutput(): Promise<string> {
    const terminal = this.page.locator('[data-testid="terminal-output"]')
      .or(this.page.locator('.terminal-output'))
      .or(this.page.locator('pre')).first();

    return await terminal.textContent() || '';
  }

  /**
   * 验证输出包含文本
   */
  async expectOutputContains(text: string | RegExp) {
    const output = await this.getTerminalOutput();
    if (typeof text === 'string') {
      expect(output).toContain(text);
    } else {
      expect(output).toMatch(text);
    }
  }

  /**
   * 清空终端输出
   */
  async clearTerminal() {
    const clearButton = this.page.getByRole('button', { name: /清空|Clear/i });
    await clearButton.click();
  }
}

/**
 * AI 助手助手
 */
export class AIAssistantHelpers {
  constructor(private page: Page) {}

  /**
   * 打开 AI 助手面板
   */
  async openAssistant() {
    // 查找 AI 助手标签页
    const aiTab = this.page.getByRole('tab', { name: /AI 助手|AI Assistant/i });
    await aiTab.click();
    await this.page.waitForTimeout(500);
  }

  /**
   * 发送消息
   */
  async sendMessage(message: string) {
    const input = this.page.getByPlaceholder(/输入问题|Enter question|Ask me/i);
    await input.fill(message);

    const sendButton = this.page.getByRole('button', { name: /发送|Send/i });
    await sendButton.click();
  }

  /**
   * 等待 AI 回复
   */
  async waitForResponse(timeout = TEST_DATA.timeouts.aiResponse) {
    // 等待加载指示器消失
    await this.page.waitForSelector('[data-testid="ai-loading"]', {
      state: 'hidden',
      timeout,
    }).catch(() => {
      // 如果没有加载指示器，继续
    });

    // 等待新消息出现
    await this.page.waitForTimeout(1000);
  }

  /**
   * 获取最后一条消息
   */
  async getLastMessage(): Promise<string> {
    const messages = this.page.locator('[data-testid="chat-message"]')
      .or(this.page.locator('.message'))
      .or(this.page.locator('.chat-message'));

    const count = await messages.count();
    if (count > 0) {
      return await messages.nth(count - 1).textContent() || '';
    }
    return '';
  }

  /**
   * 验证对话历史包含消息数量
   */
  async expectMessageCount(count: number) {
    const messages = this.page.locator('[data-testid="chat-message"]')
      .or(this.page.locator('.message'))
      .or(this.page.locator('.chat-message'));

    await expect(messages).toHaveCount(count);
  }
}

/**
 * 课程导航助手
 */
export class CourseNavigationHelpers {
  constructor(private page: Page) {}

  /**
   * 选择课程
   */
  async selectCourse(courseName: string) {
    const courseItem = this.page.getByText(courseName, { exact: false });
    await courseItem.click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * 获取当前课程标题
   */
  async getCurrentCourseTitle(): Promise<string> {
    const title = this.page.locator('h1, h2, [data-testid="course-title"]').first();
    return await title.textContent() || '';
  }

  /**
   * 验证课程内容已加载
   */
  async expectCourseContentLoaded() {
    // 验证内容面板可见
    await expect(this.page.locator('[data-testid="content-panel"]')
      .or(this.page.locator('.content-panel'))).toBeVisible();
  }

  /**
   * 验证代码模板已加载
   */
  async expectCodeTemplateLoaded() {
    // 验证编辑器有内容或为空（取决于课程）
    await this.page.waitForSelector('.monaco-editor', { state: 'visible' });
  }
}

/**
 * Toast 通知助手
 */
export class ToastHelpers {
  constructor(private page: Page) {}

  /**
   * 等待 Toast 出现
   */
  async waitForToast(timeout = 5000) {
    await this.page.waitForSelector('[data-testid="toast"], .toast, .Toastify', {
      state: 'visible',
      timeout,
    });
  }

  /**
   * 获取 Toast 消息
   */
  async getToastMessage(): Promise<string> {
    const toast = this.page.locator('[data-testid="toast"]')
      .or(this.page.locator('.toast'))
      .or(this.page.locator('.Toastify__toast'));

    return await toast.first().textContent() || '';
  }

  /**
   * 验证 Toast 包含文本
   */
  async expectToastContains(text: string | RegExp) {
    await this.waitForToast();
    const message = await this.getToastMessage();

    if (typeof text === 'string') {
      expect(message).toContain(text);
    } else {
      expect(message).toMatch(text);
    }
  }

  /**
   * 关闭 Toast
   */
  async closeToast() {
    const closeButton = this.page.locator('[data-testid="toast-close"], .toast-close').first();
    await closeButton.click().catch(() => {
      // 如果没有关闭按钮，忽略
    });
  }
}

/**
 * API Mock 助手
 */
export class APIMockHelpers {
  constructor(private page: Page) {}

  /**
   * Mock API 响应
   */
  async mockAPIResponse(endpoint: string, response: any, status = 200) {
    await this.page.route(`**${endpoint}`, (route) => {
      route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(response),
      });
    });
  }

  /**
   * Mock API 错误
   */
  async mockAPIError(endpoint: string, status = 500, message = 'Internal Server Error') {
    await this.page.route(`**${endpoint}`, (route) => {
      route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify({ error: message }),
      });
    });
  }

  /**
   * Mock 网络错误
   */
  async mockNetworkError(endpoint: string) {
    await this.page.route(`**${endpoint}`, (route) => {
      route.abort('failed');
    });
  }

  /**
   * 清除所有 Mock
   */
  async clearAllMocks() {
    await this.page.unroute('**/*');
  }
}
