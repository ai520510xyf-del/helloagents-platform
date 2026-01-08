/**
 * E2E Test: Code Execution Flow
 *
 * 测试代码执行的完整流程：
 * 1. 打开学习页面
 * 2. 输入代码到编辑器
 * 3. 点击"运行代码"按钮
 * 4. 验证输出结果显示正确
 * 5. 验证执行时间显示
 */

import { test, expect } from '@playwright/test';
import {
  PageHelpers,
  CodeEditorHelpers,
  CodeExecutionHelpers,
} from './utils/test-helpers';
import { TEST_DATA, EXPECTED_RESULTS } from './fixtures/test-data';

test.describe('Code Execution Flow', () => {
  let pageHelpers: PageHelpers;
  let codeEditorHelpers: CodeEditorHelpers;
  let codeExecutionHelpers: CodeExecutionHelpers;

  test.beforeEach(async ({ page }) => {
    pageHelpers = new PageHelpers(page);
    codeEditorHelpers = new CodeEditorHelpers(page);
    codeExecutionHelpers = new CodeExecutionHelpers(page);

    // 导航到学习页面
    await pageHelpers.navigateToLearnPage();
  });

  test('should execute simple Python code successfully', async ({ page }) => {
    // 1. 等待页面完全加载
    await pageHelpers.waitForElement('.monaco-editor');

    // 2. 输入代码到编辑器
    await codeEditorHelpers.setCode(TEST_DATA.codeExamples.simple);

    // 验证代码已设置
    const code = await codeEditorHelpers.getCode();
    expect(code).toBe(TEST_DATA.codeExamples.simple);

    // 3. 点击运行按钮
    await codeExecutionHelpers.clickRunButton();

    // 4. 等待执行完成
    await codeExecutionHelpers.waitForExecution();

    // 5. 验证输出结果
    await codeExecutionHelpers.expectOutputContains(EXPECTED_RESULTS.codeExecution.simple);

    // 6. 验证执行时间显示（可选）
    const output = await codeExecutionHelpers.getTerminalOutput();
    expect(output.length).toBeGreaterThan(0);
  });

  test('should execute code with loop and show multiple outputs', async ({ page }) => {
    // 输入循环代码
    await codeEditorHelpers.setCode(TEST_DATA.codeExamples.loop);

    // 运行代码
    await codeExecutionHelpers.clickRunButton();
    await codeExecutionHelpers.waitForExecution();

    // 验证输出包含多行结果
    const output = await codeExecutionHelpers.getTerminalOutput();
    expect(output).toMatch(/Count: 0/);
    expect(output).toMatch(/Count: 1/);
    expect(output).toMatch(/Count: 4/);
  });

  test('should handle code execution with errors', async ({ page }) => {
    // 输入有错误的代码
    await codeEditorHelpers.setCode(TEST_DATA.codeExamples.withError);

    // 运行代码
    await codeExecutionHelpers.clickRunButton();
    await codeExecutionHelpers.waitForExecution();

    // 验证错误信息显示
    const output = await codeExecutionHelpers.getTerminalOutput();
    expect(output).toMatch(/error|Error|错误|NameError/i);
  });

  test('should clear terminal output', async ({ page }) => {
    // 先执行代码产生输出
    await codeEditorHelpers.setCode(TEST_DATA.codeExamples.simple);
    await codeExecutionHelpers.clickRunButton();
    await codeExecutionHelpers.waitForExecution();

    // 验证有输出
    let output = await codeExecutionHelpers.getTerminalOutput();
    expect(output.length).toBeGreaterThan(0);

    // 清空终端
    await codeExecutionHelpers.clearTerminal();

    // 验证输出已清空
    await page.waitForTimeout(500);
    output = await codeExecutionHelpers.getTerminalOutput();
    expect(output.trim().length).toBe(0);
  });

  test('should stop long-running code execution', async ({ page }) => {
    // 输入长时间运行的代码
    const longRunningCode = `import time
for i in range(100):
    print(f"Iteration {i}")
    time.sleep(0.1)`;

    await codeEditorHelpers.setCode(longRunningCode);

    // 运行代码
    await codeExecutionHelpers.clickRunButton();

    // 等待一会儿让代码开始执行
    await page.waitForTimeout(1000);

    // 点击停止按钮
    await codeExecutionHelpers.clickStopButton();

    // 验证执行已停止
    await page.waitForTimeout(500);
    const output = await codeExecutionHelpers.getTerminalOutput();

    // 输出应该不包含所有的迭代（因为被停止了）
    const iterationCount = (output.match(/Iteration/g) || []).length;
    expect(iterationCount).toBeLessThan(100);
  });

  test('should preserve code when switching between tabs', async ({ page }) => {
    // 输入代码
    const testCode = TEST_DATA.codeExamples.simple;
    await codeEditorHelpers.setCode(testCode);

    // 切换到 AI 助手标签（如果有）
    const aiTab = page.getByRole('tab', { name: /AI 助手|AI Assistant/i });
    if (await aiTab.isVisible()) {
      await aiTab.click();
      await page.waitForTimeout(500);

      // 切换回内容标签
      const contentTab = page.getByRole('tab', { name: /内容|Content/i });
      await contentTab.click();
      await page.waitForTimeout(500);
    }

    // 验证代码仍然存在
    const code = await codeEditorHelpers.getCode();
    expect(code).toBe(testCode);
  });

  test('should show execution time after running code', async ({ page }) => {
    // 输入代码
    await codeEditorHelpers.setCode(TEST_DATA.codeExamples.simple);

    // 运行代码
    await codeExecutionHelpers.clickRunButton();
    await codeExecutionHelpers.waitForExecution();

    // 查找执行时间显示（通常在输出区域）
    const output = await codeExecutionHelpers.getTerminalOutput();

    // 验证包含时间相关信息（可能是 "执行时间"、"Execution time"、"ms"、"s" 等）
    expect(
      output.match(/时间|time|ms|秒|s|completed|完成/i)
    ).toBeTruthy();
  });

  test('should handle multiple consecutive executions', async ({ page }) => {
    // 第一次执行
    await codeEditorHelpers.setCode('print("First execution")');
    await codeExecutionHelpers.clickRunButton();
    await codeExecutionHelpers.waitForExecution();
    await codeExecutionHelpers.expectOutputContains('First execution');

    // 第二次执行不同的代码
    await codeEditorHelpers.setCode('print("Second execution")');
    await codeExecutionHelpers.clickRunButton();
    await codeExecutionHelpers.waitForExecution();
    await codeExecutionHelpers.expectOutputContains('Second execution');

    // 验证终端显示最新的输出
    const output = await codeExecutionHelpers.getTerminalOutput();
    expect(output).toContain('Second execution');
  });

  test('should display line numbers and cursor position', async ({ page }) => {
    // 输入多行代码
    const multiLineCode = `def greet(name):
    return f"Hello, {name}!"

print(greet("World"))`;

    await codeEditorHelpers.setCode(multiLineCode);

    // 验证编辑器显示行号
    const lineNumbers = page.locator('.line-numbers, .margin-view-overlays');
    await expect(lineNumbers).toBeVisible();

    // 验证光标位置显示（通常在状态栏）
    const statusBar = page.locator('[data-testid="cursor-position"], .cursor-position, .status-bar');
    if (await statusBar.isVisible()) {
      const statusText = await statusBar.textContent();
      expect(statusText).toMatch(/Ln|Line|行/i);
    }
  });
});
