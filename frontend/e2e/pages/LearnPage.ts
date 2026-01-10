import { Page, Locator, expect } from '@playwright/test';

/**
 * LearnPage - 学习页面对象模型 (Page Object Model)
 *
 * 封装学习页面的所有交互操作和元素定位
 */
export class LearnPage {
  readonly page: Page;

  // 导航栏元素
  readonly navBar: Locator;
  readonly themeToggleButton: Locator;
  readonly progressIndicator: Locator;

  // 课程目录元素
  readonly courseMenu: Locator;
  readonly lessonItems: Locator;

  // 代码编辑器元素
  readonly codeEditor: Locator;
  readonly runButton: Locator;
  readonly stopButton: Locator;
  readonly resetButton: Locator;
  readonly cursorPosition: Locator;

  // 内容面板元素
  readonly contentPanel: Locator;
  readonly contentTab: Locator;
  readonly aiTab: Locator;
  readonly lessonContent: Locator;

  // AI 助手元素
  readonly chatMessages: Locator;
  readonly chatInput: Locator;
  readonly sendButton: Locator;

  // 终端输出元素
  readonly terminalOutput: Locator;
  readonly clearOutputButton: Locator;

  constructor(page: Page) {
    this.page = page;

    // 导航栏
    this.navBar = page.locator('nav, [role="navigation"]').first();
    this.themeToggleButton = page.locator('button[title*="主题"], button[aria-label*="theme"]');
    this.progressIndicator = page.locator('text=/\\d+%|进度/');

    // 课程目录
    this.courseMenu = page.locator('[class*="course"], [class*="menu"]').first();
    this.lessonItems = page.locator('[class*="lesson"], [role="menuitem"]');

    // 代码编辑器
    this.codeEditor = page.locator('.monaco-editor, [class*="editor"]').first();
    this.runButton = page.locator('button:has-text("运行"), button:has-text("Run"), button[title*="运行"]');
    this.stopButton = page.locator('button:has-text("停止"), button:has-text("Stop")');
    this.resetButton = page.locator('button:has-text("重置"), button:has-text("Reset")');
    this.cursorPosition = page.locator('text=/行:\\s*\\d+.*列:\\s*\\d+/');

    // 内容面板
    this.contentPanel = page.locator('[class*="content-panel"], [class*="ContentPanel"]');
    this.contentTab = page.locator('button:has-text("课程内容"), button:has-text("Content"), button:has-text("内容")').first();
    this.aiTab = page.locator('button:has-text("AI 助手"), button:has-text("AI"), button:has-text("助手")').first();
    this.lessonContent = page.locator('[class*="markdown"], [class*="content"], [class*="lesson"]');

    // AI 助手
    this.chatMessages = page.locator('[class*="chat"], [class*="message"], [class*="Message"]');
    this.chatInput = page.locator('textarea[placeholder*="问题"], input[placeholder*="问题"], textarea[placeholder*="输入"]');
    this.sendButton = page.locator('button:has-text("发送"), button:has-text("Send"), [aria-label*="发送"]').first();

    // 终端输出
    this.terminalOutput = page.locator('[class*="terminal"], [class*="output"], [class*="Terminal"]').first();
    this.clearOutputButton = page.locator('button:has-text("清空"), button:has-text("Clear"), button:has-text("清除")').first();
  }

  /**
   * 导航到学习页面
   */
  async goto() {
    await this.page.goto('/');
    await this.waitForPageLoad();
  }

  /**
   * 等待页面加载完成
   */
  async waitForPageLoad() {
    // 等待页面主要元素加载 - 使用 domcontentloaded 代替 networkidle 避免超时
    await this.page.waitForLoadState('domcontentloaded');
    await expect(this.navBar).toBeVisible({ timeout: 15000 });
    // 等待一下让页面稳定
    await this.page.waitForTimeout(1000);
  }

  /**
   * 切换主题
   */
  async toggleTheme() {
    await this.themeToggleButton.click();
    // 等待主题切换动画完成
    await this.page.waitForTimeout(300);
  }

  /**
   * 获取当前主题
   */
  async getTheme(): Promise<'light' | 'dark'> {
    const html = this.page.locator('html');
    const isDark = await html.evaluate((el) => el.classList.contains('dark'));
    return isDark ? 'dark' : 'light';
  }

  /**
   * 选择课程
   * @param lessonText 课程文本（部分匹配）
   */
  async selectLesson(lessonText: string) {
    const lesson = this.page.locator(`text=${lessonText}`).first();
    await lesson.click();
    await this.page.waitForTimeout(500); // 等待课程内容加载
  }

  /**
   * 在代码编辑器中输入代码
   * @param code 代码内容
   */
  async typeCode(code: string) {
    // 点击代码编辑器区域
    await this.codeEditor.click();

    // 清空现有内容
    await this.page.keyboard.press('Control+A');
    await this.page.keyboard.press('Backspace');

    // 输入代码
    await this.page.keyboard.type(code, { delay: 10 });
  }

  /**
   * 运行代码
   */
  async runCode() {
    await this.runButton.click();
  }

  /**
   * 停止代码执行
   */
  async stopCode() {
    await this.stopButton.click();
  }

  /**
   * 重置代码
   */
  async resetCode() {
    await this.resetButton.click();
  }

  /**
   * 获取终端输出文本
   */
  async getTerminalOutput(): Promise<string> {
    return await this.terminalOutput.innerText();
  }

  /**
   * 清空终端输出
   */
  async clearOutput() {
    await this.clearOutputButton.click();
  }

  /**
   * 切换到内容标签
   */
  async switchToContentTab() {
    await this.contentTab.click();
  }

  /**
   * 切换到 AI 助手标签
   */
  async switchToAITab() {
    await this.aiTab.click();
  }

  /**
   * 发送 AI 消息
   * @param message 消息内容
   */
  async sendAIMessage(message: string) {
    await this.chatInput.fill(message);
    await this.sendButton.click();
  }

  /**
   * 获取最后一条 AI 消息
   */
  async getLastAIMessage(): Promise<string> {
    const lastMessage = this.chatMessages.last();
    return await lastMessage.innerText();
  }

  /**
   * 获取光标位置
   */
  async getCursorPosition(): Promise<{ line: number; column: number }> {
    const text = await this.cursorPosition.innerText();
    const match = text.match(/行:\s*(\d+).*列:\s*(\d+)/);
    if (match) {
      return {
        line: parseInt(match[1]),
        column: parseInt(match[2]),
      };
    }
    return { line: 1, column: 1 };
  }

  /**
   * 检查页面是否为移动端布局
   */
  async isMobileLayout(): Promise<boolean> {
    const viewport = this.page.viewportSize();
    return viewport ? viewport.width < 768 : false;
  }

  /**
   * 检查页面是否为平板布局
   */
  async isTabletLayout(): Promise<boolean> {
    const viewport = this.page.viewportSize();
    return viewport ? viewport.width >= 768 && viewport.width < 1024 : false;
  }

  /**
   * 检查页面是否为桌面布局
   */
  async isDesktopLayout(): Promise<boolean> {
    const viewport = this.page.viewportSize();
    return viewport ? viewport.width >= 1024 : false;
  }

  /**
   * 获取进度百分比
   */
  async getProgress(): Promise<number> {
    const text = await this.progressIndicator.innerText();
    const match = text.match(/(\d+)%/);
    return match ? parseInt(match[1]) : 0;
  }

  /**
   * 等待代码执行完成
   * @param timeout 超时时间（毫秒）
   */
  async waitForCodeExecution(timeout = 10000) {
    await this.page.waitForTimeout(1000); // 等待代码开始执行
    await expect(this.stopButton).toBeHidden({ timeout });
  }

  /**
   * 检查是否有错误消息显示
   */
  async hasErrorMessage(): Promise<boolean> {
    const errorLocator = this.page.locator('text=/错误|Error/i');
    return await errorLocator.isVisible();
  }

  /**
   * 截图（用于调试）
   * @param name 截图名称
   */
  async screenshot(name: string) {
    await this.page.screenshot({ path: `test-results/${name}.png`, fullPage: true });
  }
}
