# E2E 测试使用指南

## 目录

1. [快速开始](#快速开始)
2. [测试架构](#测试架构)
3. [页面对象模型](#页面对象模型)
4. [编写测试](#编写测试)
5. [运行测试](#运行测试)
6. [调试技巧](#调试技巧)
7. [最佳实践](#最佳实践)
8. [CI/CD 集成](#cicd-集成)

## 快速开始

### 安装和配置

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 安装 Playwright 浏览器
npx playwright install

# 3. 运行测试
npm run test:e2e
```

### 第一个测试

```bash
# 以 UI 模式运行（推荐用于开发）
npm run test:e2e:ui

# 运行特定测试文件
npx playwright test learn-page.e2e.ts

# 运行特定浏览器
npm run test:e2e:chromium
```

## 测试架构

### 架构概览

```
┌─────────────────────────────────────────┐
│          E2E Test Suite                  │
│  ┌────────────────────────────────────┐ │
│  │      Test Files (*.e2e.ts)         │ │
│  │  - learn-page.e2e.ts               │ │
│  │  - mobile.e2e.ts                   │ │
│  │  - code-execution.e2e.ts           │ │
│  └──────────────┬──────────────────────┘ │
│                 │                         │
│  ┌──────────────▼──────────────────────┐ │
│  │     Page Objects (pages/)           │ │
│  │  - LearnPage.ts                     │ │
│  │  封装页面元素和交互                    │ │
│  └──────────────┬──────────────────────┘ │
│                 │                         │
│  ┌──────────────▼──────────────────────┐ │
│  │     Helpers (utils/)                │ │
│  │  - helpers.ts                       │ │
│  │  通用工具函数                          │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 设计模式

1. **页面对象模型 (POM)**
   - 封装页面元素和操作
   - 提高测试可维护性
   - 减少代码重复

2. **测试隔离**
   - 每个测试独立运行
   - 使用 beforeEach 初始化
   - 避免测试间依赖

3. **辅助函数**
   - 封装通用操作
   - 提供可重用组件
   - 简化测试代码

## 页面对象模型

### 什么是 POM？

页面对象模型是一种设计模式，将页面元素和操作封装到类中。

### 示例：LearnPage

```typescript
// e2e/pages/LearnPage.ts
export class LearnPage {
  readonly page: Page;
  readonly runButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.runButton = page.locator('button:has-text("运行")');
  }

  async goto() {
    await this.page.goto('/');
  }

  async runCode() {
    await this.runButton.click();
  }
}
```

### 使用 POM

```typescript
// 在测试中使用
test('运行代码', async ({ page }) => {
  const learnPage = new LearnPage(page);
  await learnPage.goto();
  await learnPage.runCode();
});
```

### POM 最佳实践

1. **只暴露必要的方法**
   - 封装实现细节
   - 提供语义化的接口

2. **返回其他页面对象**
   - 导航操作返回目标页面
   - 支持方法链式调用

3. **不在 POM 中写断言**
   - POM 只负责操作
   - 断言在测试文件中

## 编写测试

### 测试结构

```typescript
import { test, expect } from '@playwright/test';
import { LearnPage } from './pages/LearnPage';

test.describe('功能组', () => {
  let learnPage: LearnPage;

  test.beforeEach(async ({ page }) => {
    // 每个测试前的准备
    learnPage = new LearnPage(page);
    await learnPage.goto();
  });

  test('测试用例名称', async ({ page }) => {
    // 执行操作
    await learnPage.typeCode('print("test")');
    await learnPage.runCode();

    // 断言
    const output = await learnPage.getTerminalOutput();
    expect(output).toContain('test');
  });
});
```

### 选择器策略

优先级顺序：

1. **用户可见文本**
   ```typescript
   page.locator('text=登录')
   page.locator('button:has-text("提交")')
   ```

2. **Role 和 Accessibility**
   ```typescript
   page.getByRole('button', { name: '提交' })
   page.getByLabel('用户名')
   ```

3. **Test ID**
   ```typescript
   page.locator('[data-testid="submit-button"]')
   ```

4. **CSS 选择器**（最后选择）
   ```typescript
   page.locator('.submit-button')
   page.locator('#login-form')
   ```

### 等待策略

```typescript
// ✅ 推荐：自动等待
await expect(element).toBeVisible();
await element.click();

// ✅ 等待特定状态
await page.waitForLoadState('networkidle');
await page.waitForSelector('.content');

// ❌ 避免：固定等待
await page.waitForTimeout(5000); // 不推荐
```

### 断言

```typescript
// 元素断言
await expect(element).toBeVisible();
await expect(element).toHaveText('Expected text');
await expect(element).toHaveAttribute('class', 'active');

// 页面断言
await expect(page).toHaveURL(/dashboard/);
await expect(page).toHaveTitle('Dashboard');

// 自定义断言
expect(value).toBe(expected);
expect(array).toHaveLength(3);
expect(output).toContain('success');
```

## 运行测试

### 基本命令

```bash
# 运行所有测试
npm run test:e2e

# UI 模式（推荐开发使用）
npm run test:e2e:ui

# 显示浏览器窗口
npm run test:e2e:headed

# Debug 模式
npm run test:e2e:debug
```

### 选择性运行

```bash
# 运行特定文件
npx playwright test learn-page.e2e.ts

# 运行特定测试
npx playwright test -g "应该能够切换主题"

# 运行特定项目
npx playwright test --project=chromium
npx playwright test --project=mobile-chrome

# 并行运行
npx playwright test --workers=4
```

### 查看报告

```bash
# 查看 HTML 报告
npm run test:e2e:report

# 或直接打开
npx playwright show-report
```

## 调试技巧

### 1. UI 模式（推荐）

```bash
npm run test:e2e:ui
```

**特性：**
- 可视化测试步骤
- 时间旅行调试
- DOM 快照查看
- 网络请求监控
- 实时重新运行

### 2. Debug 模式

```bash
npm run test:e2e:debug
```

**特性：**
- 暂停在每个操作
- 支持断点
- 浏览器开发者工具
- Playwright Inspector

### 3. Trace Viewer

```bash
# 生成 trace
npx playwright test --trace on

# 查看 trace
npx playwright show-trace trace.zip
```

**包含信息：**
- 测试步骤
- 网络请求
- 控制台日志
- 截图
- DOM 快照

### 4. 截图和视频

```typescript
// 手动截图
await page.screenshot({ path: 'screenshot.png' });

// 全页截图
await page.screenshot({ path: 'full.png', fullPage: true });
```

失败的测试会自动保存截图和视频。

### 5. 控制台日志

```typescript
// 监听控制台消息
page.on('console', msg => console.log(msg.text()));

// 监听页面错误
page.on('pageerror', error => console.log(error));

// 监听请求
page.on('request', request => console.log(request.url()));
```

### 6. 暂停执行

```typescript
// 在测试中暂停
await page.pause();

// 条件暂停
if (process.env.DEBUG) {
  await page.pause();
}
```

## 最佳实践

### 1. 测试独立性

```typescript
// ✅ 每个测试独立
test.beforeEach(async ({ page }) => {
  await page.goto('/');
  // 重置状态
});

// ❌ 测试间有依赖
test('test 1', async () => {
  // 创建数据
});
test('test 2', async () => {
  // 依赖 test 1 的数据
});
```

### 2. 避免硬编码等待

```typescript
// ✅ 使用自动等待
await expect(element).toBeVisible();

// ❌ 硬编码等待
await page.waitForTimeout(5000);
```

### 3. 使用语义化的测试名称

```typescript
// ✅ 描述性强
test('用户应该能够成功登录并看到仪表盘', async () => {});

// ❌ 含糊不清
test('test login', async () => {});
```

### 4. 分组相关测试

```typescript
test.describe('登录功能', () => {
  test.describe('成功场景', () => {
    test('使用正确凭据登录', async () => {});
  });

  test.describe('失败场景', () => {
    test('使用错误密码登录', async () => {});
  });
});
```

### 5. 清理和准备

```typescript
test.beforeEach(async ({ page }) => {
  // 准备测试环境
  await setupTestData();
});

test.afterEach(async ({ page }) => {
  // 清理测试数据
  await cleanupTestData();
});
```

### 6. 处理不稳定的测试

```typescript
// 增加重试次数
test.describe.configure({ retries: 2 });

// 增加超时
test.setTimeout(60000);

// 使用更可靠的选择器
await page.waitForSelector('.loaded', { state: 'visible' });
```

## CI/CD 集成

### GitHub Actions 配置

测试已集成到 `.github/workflows/e2e-tests.yml`。

### 触发条件

- Push 到 `main` 或 `develop`
- Pull Request 到 `main` 或 `develop`
- 手动触发

### 环境变量

```yaml
env:
  CI: true
  BASE_URL: https://helloagents-platform.pages.dev
```

### 查看结果

1. 进入 GitHub Actions
2. 选择 "E2E Tests" workflow
3. 查看测试报告
4. 下载失败的截图和视频

### 本地模拟 CI

```bash
# 设置 CI 环境变量
CI=true npm run test:e2e

# 使用生产 URL
BASE_URL=https://helloagents-platform.pages.dev npm run test:e2e
```

## 常见问题

### Q: 测试超时怎么办？

A: 增加超时时间：

```typescript
test.setTimeout(120000); // 120 秒

// 或在配置文件中全局设置
// playwright.config.ts
timeout: 60000
```

### Q: 元素找不到？

A: 检查选择器和等待条件：

```typescript
// 使用 Playwright Inspector 检查
npx playwright test --debug

// 增加等待时间
await page.waitForSelector(selector, { timeout: 30000 });

// 使用更宽松的匹配
page.locator('text=/部分文本/')
```

### Q: 测试不稳定（Flaky）？

A: 常见原因和解决方案：

1. **网络请求未完成**
   ```typescript
   await page.waitForLoadState('networkidle');
   ```

2. **动画未完成**
   ```typescript
   await page.waitForTimeout(300); // 等待动画
   ```

3. **选择器不准确**
   ```typescript
   // 使用更具体的选择器
   page.locator('button').filter({ hasText: '提交' })
   ```

### Q: Monaco Editor 如何操作？

A: Monaco Editor 需要特殊处理：

```typescript
// 等待编辑器加载
await page.waitForSelector('.monaco-editor');

// 通过 evaluate 操作
await page.evaluate((code) => {
  const monaco = window.monaco;
  const editor = monaco.editor.getModels()[0];
  editor.setValue(code);
}, 'print("hello")');
```

## 资源链接

- [Playwright 官方文档](https://playwright.dev)
- [测试最佳实践](https://playwright.dev/docs/best-practices)
- [API 参考](https://playwright.dev/docs/api/class-playwright)
- [选择器指南](https://playwright.dev/docs/selectors)

## 总结

遵循本指南可以：

1. 编写稳定可靠的 E2E 测试
2. 提高测试可维护性
3. 加快调试速度
4. 确保测试覆盖全面

记住：**好的测试是投资，不是成本。**

---

**版本**: 1.0.0
**最后更新**: 2026-01-09
**维护者**: QA Automation Team
