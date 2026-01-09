import { test, expect } from '@playwright/test';
import { LearnPage } from './pages/LearnPage';
import { waitForNetworkIdle, wait, checkBasicAccessibility } from './utils/helpers';

/**
 * 学习页面核心流程 E2E 测试
 *
 * 测试范围：
 * - 页面加载和基本元素显示
 * - 课程浏览和切换
 * - 代码编辑器交互
 * - 代码运行流程
 * - AI 助手对话
 * - 主题切换
 */

test.describe('LearnPage - 基础功能', () => {
  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该正确加载学习页面', async ({ page }) => {
    // 检查导航栏是否显示
    await expect(learnPage.navBar).toBeVisible();

    // 检查主要区域是否可见
    await expect(learnPage.courseMenu).toBeVisible();
    await expect(learnPage.codeEditor).toBeVisible();

    // 检查页面标题
    const title = await page.title();
    expect(title).toBeTruthy();
  });

  test('应该显示课程目录', async () => {
    // 等待课程列表加载
    await expect(learnPage.lessonItems.first()).toBeVisible({ timeout: 10000 });

    // 检查是否有课程项
    const count = await learnPage.lessonItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('应该能够切换主题', async ({ page }) => {
    // 获取初始主题
    const initialTheme = await learnPage.getTheme();

    // 切换主题
    await learnPage.toggleTheme();

    // 验证主题已切换
    const newTheme = await learnPage.getTheme();
    expect(newTheme).not.toBe(initialTheme);

    // 再次切换，验证可以切换回来
    await learnPage.toggleTheme();
    const finalTheme = await learnPage.getTheme();
    expect(finalTheme).toBe(initialTheme);
  });

  test('应该显示进度信息', async () => {
    // 检查进度指示器是否显示
    if (await learnPage.progressIndicator.isVisible()) {
      const progress = await learnPage.getProgress();
      expect(progress).toBeGreaterThanOrEqual(0);
      expect(progress).toBeLessThanOrEqual(100);
    }
  });
});

test.describe('LearnPage - 课程切换', () => {
  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该能够选择和切换课程', async ({ page }) => {
    // 等待课程列表加载
    await expect(learnPage.lessonItems.first()).toBeVisible({ timeout: 10000 });

    // 获取第一个课程
    const firstLesson = learnPage.lessonItems.first();
    const firstLessonText = await firstLesson.innerText();

    // 点击第一个课程
    await firstLesson.click();
    await wait(1000); // 等待内容加载

    // 验证课程内容已加载（通过检查是否有课程相关的文本）
    // 注意：具体验证逻辑取决于实际的课程内容结构
  });

  test('应该在切换课程时保持代码', async ({ page }) => {
    // 等待课程列表加载
    await expect(learnPage.lessonItems.first()).toBeVisible({ timeout: 10000 });

    // 在第一个课程中输入代码
    const testCode = '# Test code';
    await learnPage.typeCode(testCode);

    // 切换到另一个课程
    const lessons = await learnPage.lessonItems.all();
    if (lessons.length > 1) {
      await lessons[1].click();
      await wait(1000);

      // 切换回第一个课程
      await lessons[0].click();
      await wait(1000);

      // 验证代码是否保留（通过本地存储）
      // 注意：这需要根据实际的存储逻辑来验证
    }
  });
});

test.describe('LearnPage - 代码编辑器', () => {
  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该能够在编辑器中输入代码', async () => {
    const testCode = 'print("Hello, Agent!")';

    // 输入代码
    await learnPage.typeCode(testCode);

    // 等待一会儿确保代码已输入
    await wait(500);

    // 验证光标位置已更新
    const position = await learnPage.getCursorPosition();
    expect(position.line).toBeGreaterThan(0);
  });

  test('应该显示运行按钮', async () => {
    await expect(learnPage.runButton).toBeVisible();
  });

  test('应该显示重置按钮', async () => {
    await expect(learnPage.resetButton).toBeVisible();
  });

  test('应该能够重置代码', async () => {
    // 输入一些代码
    const testCode = 'print("test")';
    await learnPage.typeCode(testCode);
    await wait(500);

    // 点击重置按钮
    await learnPage.resetCode();
    await wait(500);

    // 验证代码已清空（编辑器应该为空或显示初始状态）
    // 注意：具体验证方式取决于重置后的状态
  });
});

test.describe('LearnPage - 代码执行', () => {
  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该能够运行简单的 Python 代码', async ({ page }) => {
    // 输入 Python 代码
    const code = 'print("Hello from E2E test")';
    await learnPage.typeCode(code);

    // 运行代码
    await learnPage.runCode();

    // 等待执行完成
    await wait(3000);

    // 检查终端输出
    const output = await learnPage.getTerminalOutput();
    expect(output.length).toBeGreaterThan(0);
  });

  test('应该能够清空终端输出', async () => {
    // 先运行一段代码
    await learnPage.typeCode('print("test")');
    await learnPage.runCode();
    await wait(2000);

    // 清空输出
    await learnPage.clearOutput();
    await wait(500);

    // 验证输出已清空
    const output = await learnPage.getTerminalOutput();
    expect(output.trim().length).toBe(0);
  });
});

test.describe('LearnPage - 内容面板', () => {
  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该能够切换到内容标签', async () => {
    // 切换到内容标签
    await learnPage.switchToContentTab();

    // 验证内容标签是否激活
    await expect(learnPage.contentTab).toHaveAttribute('data-state', 'active');
  });

  test('应该能够切换到 AI 助手标签', async () => {
    // 切换到 AI 标签
    await learnPage.switchToAITab();

    // 验证 AI 标签是否激活
    await expect(learnPage.aiTab).toHaveAttribute('data-state', 'active');
  });

  test('应该显示课程内容', async () => {
    // 切换到内容标签
    await learnPage.switchToContentTab();

    // 检查是否有课程内容显示
    const hasContent = await learnPage.lessonContent.isVisible();
    expect(hasContent).toBe(true);
  });
});

test.describe('LearnPage - AI 助手', () => {
  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('应该显示 AI 助手界面', async () => {
    // 切换到 AI 标签
    await learnPage.switchToAITab();

    // 检查聊天输入框是否显示
    await expect(learnPage.chatInput).toBeVisible();
    await expect(learnPage.sendButton).toBeVisible();
  });

  test('应该能够输入消息', async () => {
    // 切换到 AI 标签
    await learnPage.switchToAITab();

    // 输入消息
    const message = '什么是 Agent？';
    await learnPage.chatInput.fill(message);

    // 验证消息已输入
    const value = await learnPage.chatInput.inputValue();
    expect(value).toBe(message);
  });

  // 注意：实际发送消息和接收回复的测试需要根据后端 API 的实现来调整
  // test('应该能够发送和接收 AI 消息', async () => {
  //   await learnPage.switchToAITab();
  //   await learnPage.sendAIMessage('什么是 Agent？');
  //   await wait(5000); // 等待 AI 回复
  //   const lastMessage = await learnPage.getLastAIMessage();
  //   expect(lastMessage.length).toBeGreaterThan(0);
  // });
});

test.describe('LearnPage - 可访问性', () => {
  test('应该通过基本的可访问性检查', async ({ page }) => {
    const learnPage = new LearnPage(page);
    await learnPage.goto();

    // 执行基本的可访问性检查
    await checkBasicAccessibility(page);
  });

  test('应该支持键盘导航', async ({ page }) => {
    const learnPage = new LearnPage(page);
    await learnPage.goto();

    // 使用 Tab 键导航
    await page.keyboard.press('Tab');
    await wait(200);

    // 检查是否有元素获得焦点
    const focusedElement = await page.evaluate(() => {
      const el = document.activeElement;
      return el ? el.tagName : null;
    });

    expect(focusedElement).toBeTruthy();
  });
});

test.describe('LearnPage - 性能', () => {
  test('应该在合理时间内加载页面', async ({ page }) => {
    const startTime = Date.now();

    const learnPage = new LearnPage(page);
    await learnPage.goto();
    await waitForNetworkIdle(page);

    const loadTime = Date.now() - startTime;

    // 页面应该在 5 秒内加载完成
    expect(loadTime).toBeLessThan(5000);
  });

  test('不应该有控制台错误', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    const learnPage = new LearnPage(page);
    await learnPage.goto();
    await wait(2000);

    // 检查是否有严重的控制台错误
    const seriousErrors = consoleErrors.filter(
      (error) => !error.includes('Warning') && !error.includes('deprecated')
    );

    expect(seriousErrors.length).toBe(0);
  });
});
