# E2E Testing Quick Reference Card

## 🚀 快速命令

### 常用命令
```bash
# 运行所有测试 (推荐用于 CI)
npm run test:e2e

# UI 模式 (推荐用于开发)
npm run test:e2e:ui

# 查看浏览器运行
npm run test:e2e:headed

# 调试模式
npm run test:e2e:debug

# 查看报告
npm run test:e2e:report
```

### 浏览器选择
```bash
# 只运行 Chromium
npm run test:e2e:chromium

# 只运行 Firefox
npm run test:e2e:firefox
```

### 使用脚本
```bash
# 基本运行
./scripts/run-e2e-tests.sh

# 有头模式 + Chromium
./scripts/run-e2e-tests.sh --headed --chromium

# UI 模式
./scripts/run-e2e-tests.sh --ui
```

## 📊 测试统计

- **总测试数**: 52 个
- **测试文件**: 4 个
- **Helper 类**: 7 个
- **工具方法**: 50+
- **浏览器**: 2 个 (Chromium, Firefox)
- **总执行**: 104 次测试

## 📁 文件位置

```
e2e/
├── code-execution.e2e.ts      # 代码执行 (10 测试)
├── ai-assistant.e2e.ts        # AI 助手 (12 测试)
├── course-navigation.e2e.ts   # 课程导航 (15 测试)
├── error-handling.e2e.ts      # 错误处理 (15 测试)
├── fixtures/test-data.ts      # 测试数据
└── utils/test-helpers.ts      # Helper 类
```

## 🛠️ Helper 类

### PageHelpers
```typescript
await pageHelpers.navigateToLearnPage();
await pageHelpers.waitForPageLoad();
await pageHelpers.waitForElement(selector);
await pageHelpers.takeScreenshot(name);
```

### CodeEditorHelpers
```typescript
await editorHelpers.setCode(code);
const code = await editorHelpers.getCode();
await editorHelpers.clearCode();
```

### CodeExecutionHelpers
```typescript
await executionHelpers.clickRunButton();
await executionHelpers.waitForExecution();
await executionHelpers.expectOutputContains(text);
await executionHelpers.clearTerminal();
```

### AIAssistantHelpers
```typescript
await aiHelpers.openAssistant();
await aiHelpers.sendMessage(message);
await aiHelpers.waitForResponse();
const lastMessage = await aiHelpers.getLastMessage();
```

### CourseNavigationHelpers
```typescript
await navigationHelpers.selectCourse(courseName);
const title = await navigationHelpers.getCurrentCourseTitle();
await navigationHelpers.expectCourseContentLoaded();
```

### ToastHelpers
```typescript
await toastHelpers.waitForToast();
await toastHelpers.expectToastContains(text);
await toastHelpers.closeToast();
```

### APIMockHelpers
```typescript
await apiMockHelpers.mockAPIResponse(endpoint, response);
await apiMockHelpers.mockAPIError(endpoint, status);
await apiMockHelpers.mockNetworkError(endpoint);
await apiMockHelpers.clearAllMocks();
```

## 🧪 测试模板

```typescript
import { test, expect } from '@playwright/test';
import { PageHelpers, CodeEditorHelpers } from './utils/test-helpers';

test.describe('My Feature', () => {
  let pageHelpers: PageHelpers;
  let editorHelpers: CodeEditorHelpers;

  test.beforeEach(async ({ page }) => {
    pageHelpers = new PageHelpers(page);
    editorHelpers = new CodeEditorHelpers(page);
    await pageHelpers.navigateToLearnPage();
  });

  test('should do something', async ({ page }) => {
    await editorHelpers.setCode('print("test")');
    const code = await editorHelpers.getCode();
    expect(code).toBe('print("test")');
  });
});
```

## 🐛 调试技巧

### 1. UI 模式（最推荐）
```bash
npm run test:e2e:ui
```
- 可视化界面
- 时间旅行
- DOM 快照
- 网络请求

### 2. Debug 模式
```bash
npm run test:e2e:debug
```
- 逐步执行
- 支持断点

### 3. 查看 Trace
```bash
npx playwright show-trace trace.zip
```

### 4. 增加超时
```typescript
test('my test', async ({ page }) => {
  test.setTimeout(60000); // 60 秒
});
```

### 5. 只运行特定测试
```bash
npx playwright test code-execution
npx playwright test --grep "should execute"
```

## 📝 测试数据

```typescript
// 从 fixtures/test-data.ts 导入
TEST_DATA.codeExamples.simple
TEST_DATA.aiQuestions.simple
TEST_DATA.timeouts.codeExecution
ERROR_SCENARIOS.apiErrors
EXPECTED_RESULTS.codeExecution
```

## 🔧 常见问题

### 测试不稳定？
1. 检查硬编码等待
2. 增加超时时间
3. 使用更可靠选择器

### 找不到元素？
1. 验证选择器
2. 等待元素加载
3. 使用 `data-testid`

### Monaco Editor？
使用 `CodeEditorHelpers`，已处理特殊情况。

### Mock API？
```typescript
await apiMockHelpers.mockAPIResponse('/api/execute', {
  success: true,
  output: 'Hello'
});
```

## 📈 性能

- 单测试: 5-10 秒
- 完整套件: 5-10 分钟
- 并行: 支持
- 重试: CI 中 2 次

## 📚 文档

- **快速开始**: `E2E_TESTING_GUIDE.md`
- **详细文档**: `e2e/README.md`
- **测试总结**: `TEST_SUMMARY.md`
- **本参考卡**: `E2E_QUICK_REFERENCE.md`

## 🎯 CI/CD

- **触发**: Push, PR, 手动
- **浏览器**: Chromium, Firefox
- **报告**: 保留 30 天
- **截图**: 保留 7 天

## ⚡ 最佳实践

✅ 使用 Helper 类
✅ 避免硬编码等待
✅ 测试独立性
✅ 清晰的测试描述
✅ 适当的错误处理

## 📞 支持

1. 查看文档
2. 使用 UI 模式
3. 查看截图/视频
4. [Playwright 文档](https://playwright.dev/)

---

**快速打印此卡片作为参考！**
