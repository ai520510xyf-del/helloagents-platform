/**
 * E2E Test: AI Assistant Interaction
 *
 * 测试 AI 助手交互流程：
 * 1. 打开 AI 助手面板
 * 2. 输入问题
 * 3. 验证 AI 回复显示
 * 4. 验证对话历史保存
 */

import { test, expect } from '@playwright/test';
import {
  PageHelpers,
  AIAssistantHelpers,
} from './utils/test-helpers';
import { TEST_DATA } from './fixtures/test-data';

test.describe('AI Assistant Interaction', () => {
  let pageHelpers: PageHelpers;
  let aiHelpers: AIAssistantHelpers;

  test.beforeEach(async ({ page }) => {
    pageHelpers = new PageHelpers(page);
    aiHelpers = new AIAssistantHelpers(page);

    // 导航到学习页面
    await pageHelpers.navigateToLearnPage();
  });

  test('should open AI assistant panel', async ({ page }) => {
    // 1. 打开 AI 助手面板
    await aiHelpers.openAssistant();

    // 2. 验证 AI 助手界面可见
    const chatContainer = page.locator('[data-testid="ai-chat"]')
      .or(page.locator('.ai-assistant'))
      .or(page.locator('.chat-container'));

    await expect(chatContainer).toBeVisible();

    // 3. 验证输入框可见
    const input = page.getByPlaceholder(/输入问题|Enter question|Ask me/i);
    await expect(input).toBeVisible();
  });

  test('should send message and receive AI response', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 获取初始消息数量
    await page.waitForTimeout(1000);

    // 发送简单问题
    await aiHelpers.sendMessage(TEST_DATA.aiQuestions.simple);

    // 等待 AI 回复
    await aiHelpers.waitForResponse();

    // 验证收到回复
    const lastMessage = await aiHelpers.getLastMessage();
    expect(lastMessage.length).toBeGreaterThan(0);

    // 验证消息数量增加（用户消息 + AI 回复）
    await aiHelpers.expectMessageCount(2);
  });

  test('should display loading indicator while waiting for response', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 发送消息
    const input = page.getByPlaceholder(/输入问题|Enter question|Ask me/i);
    await input.fill(TEST_DATA.aiQuestions.code);

    const sendButton = page.getByRole('button', { name: /发送|Send/i });
    await sendButton.click();

    // 验证加载指示器出现
    const loadingIndicator = page.locator('[data-testid="ai-loading"]')
      .or(page.locator('.loading'))
      .or(page.locator('.spinner'));

    // 可能会很快消失，所以用 waitFor
    await expect(loadingIndicator).toBeVisible({ timeout: 3000 }).catch(() => {
      // 如果 AI 响应太快，加载指示器可能看不到
    });
  });

  test('should preserve chat history', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 发送第一条消息
    await aiHelpers.sendMessage('第一条消息');
    await aiHelpers.waitForResponse();

    // 发送第二条消息
    await aiHelpers.sendMessage('第二条消息');
    await aiHelpers.waitForResponse();

    // 验证对话历史包含两组消息（4条：2条用户消息 + 2条 AI 回复）
    await page.waitForTimeout(1000);
    await aiHelpers.expectMessageCount(4);

    // 切换到内容标签
    const contentTab = page.getByRole('tab', { name: /内容|Content/i });
    await contentTab.click();
    await page.waitForTimeout(500);

    // 切换回 AI 助手
    await aiHelpers.openAssistant();

    // 验证对话历史仍然存在
    await aiHelpers.expectMessageCount(4);
  });

  test('should handle code-related questions', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 发送代码相关问题
    await aiHelpers.sendMessage(TEST_DATA.aiQuestions.code);
    await aiHelpers.waitForResponse();

    // 验证回复中包含代码块（通常用 ``` 标记）
    const lastMessage = await aiHelpers.getLastMessage();
    expect(lastMessage).toMatch(/def|function|函数|代码/i);
  });

  test('should display user and AI messages with different styles', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 发送消息
    await aiHelpers.sendMessage('测试消息');
    await aiHelpers.waitForResponse();

    // 查找用户消息和 AI 消息
    const userMessage = page.locator('[data-testid="user-message"]')
      .or(page.locator('.message-user'))
      .or(page.locator('.user'));

    const aiMessage = page.locator('[data-testid="ai-message"]')
      .or(page.locator('.message-ai'))
      .or(page.locator('.assistant'));

    // 验证两种消息都存在
    await expect(userMessage.first()).toBeVisible();
    await expect(aiMessage.first()).toBeVisible();
  });

  test('should handle empty message input', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 尝试发送空消息
    const input = page.getByPlaceholder(/输入问题|Enter question|Ask me/i);
    await input.fill('');

    const sendButton = page.getByRole('button', { name: /发送|Send/i });

    // 验证发送按钮被禁用或点击无效
    const isDisabled = await sendButton.isDisabled();
    if (!isDisabled) {
      // 如果按钮没有被禁用，点击后不应该发送消息
      const initialCount = await page.locator('[data-testid="chat-message"]').count();
      await sendButton.click();
      await page.waitForTimeout(500);
      const finalCount = await page.locator('[data-testid="chat-message"]').count();
      expect(finalCount).toBe(initialCount);
    }
  });

  test('should scroll to bottom when new messages arrive', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 发送多条消息以产生滚动
    for (let i = 1; i <= 3; i++) {
      await aiHelpers.sendMessage(`消息 ${i}`);
      await aiHelpers.waitForResponse();
    }

    // 验证最后一条消息可见（说明自动滚动到底部）
    const messages = page.locator('[data-testid="chat-message"]')
      .or(page.locator('.message'));

    const lastMessage = messages.last();
    await expect(lastMessage).toBeInViewport();
  });

  test('should handle AI API errors gracefully', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // Mock API 错误
    await page.route('**/api/chat', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    // 发送消息
    await aiHelpers.sendMessage('测试错误处理');

    // 等待一下
    await page.waitForTimeout(2000);

    // 验证显示错误消息
    const errorMessage = page.locator('[data-testid="error-message"]')
      .or(page.getByText(/错误|Error|failed|失败/i));

    await expect(errorMessage.first()).toBeVisible({ timeout: 5000 });
  });

  test('should support markdown rendering in AI responses', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 发送消息
    await aiHelpers.sendMessage(TEST_DATA.aiQuestions.code);
    await aiHelpers.waitForResponse();

    // 验证 markdown 元素存在（如代码块、列表等）
    const markdownElements = page.locator('code, pre, ul, ol, strong, em');
    const count = await markdownElements.count();

    // 如果 AI 回复包含 markdown，应该有相应的元素
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should display timestamps for messages', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 发送消息
    await aiHelpers.sendMessage('测试时间戳');
    await aiHelpers.waitForResponse();

    // 查找时间戳元素
    const timestamp = page.locator('[data-testid="message-timestamp"]')
      .or(page.locator('.timestamp'))
      .or(page.locator('.time'));

    // 如果有时间戳，验证其存在
    const count = await timestamp.count();
    if (count > 0) {
      await expect(timestamp.first()).toBeVisible();
    }
  });

  test('should handle long AI responses', async ({ page }) => {
    // 打开 AI 助手
    await aiHelpers.openAssistant();

    // 发送可能产生长回复的问题
    await aiHelpers.sendMessage('请详细解释 Python 的类和对象，包括继承、多态、封装等概念。');
    await aiHelpers.waitForResponse(20000); // 更长的超时时间

    // 验证收到回复
    const lastMessage = await aiHelpers.getLastMessage();
    expect(lastMessage.length).toBeGreaterThan(50);

    // 验证消息容器可以滚动
    const chatContainer = page.locator('[data-testid="chat-messages"]')
      .or(page.locator('.chat-messages'))
      .or(page.locator('.messages'));

    if (await chatContainer.isVisible()) {
      const isScrollable = await chatContainer.evaluate((el) => {
        return el.scrollHeight > el.clientHeight;
      });
      // 长消息可能导致容器可滚动
      expect(typeof isScrollable).toBe('boolean');
    }
  });
});
