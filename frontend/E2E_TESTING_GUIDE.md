# E2E Testing Quick Start Guide

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

Playwright 已经作为开发依赖安装。

### 2. 安装浏览器

```bash
npx playwright install chromium firefox
```

### 3. 运行测试

#### 运行所有测试（推荐用于 CI/CD）

```bash
npm run test:e2e
```

#### UI 模式（推荐用于开发）

```bash
npm run test:e2e:ui
```

这会打开 Playwright Test UI，提供：
- 可视化测试执行
- 时间旅行调试
- DOM 快照查看
- 网络请求查看

#### Headed 模式（查看浏览器运行）

```bash
npm run test:e2e:headed
```

#### Debug 模式（逐步调试）

```bash
npm run test:e2e:debug
```

#### 运行特定浏览器

```bash
# 只运行 Chromium 测试
npm run test:e2e:chromium

# 只运行 Firefox 测试
npm run test:e2e:firefox
```

### 4. 查看测试报告

```bash
npm run test:e2e:report
```

## 使用测试脚本

我们提供了一个便捷的测试脚本：

```bash
./scripts/run-e2e-tests.sh [选项]
```

选项：
- `--headed` - 有头模式运行
- `--debug` - 调试模式运行
- `--chromium` - 只运行 Chromium
- `--firefox` - 只运行 Firefox
- `--ui` - UI 模式运行
- `--help` - 显示帮助

例如：

```bash
# 在有头模式下运行 Chromium 测试
./scripts/run-e2e-tests.sh --headed --chromium

# 在 UI 模式下运行
./scripts/run-e2e-tests.sh --ui
```

## 测试文件结构

```
e2e/
├── code-execution.e2e.ts     # 代码执行流程测试 (10 个测试)
├── ai-assistant.e2e.ts       # AI 助手交互测试 (12 个测试)
├── course-navigation.e2e.ts  # 课程导航测试 (15 个测试)
├── error-handling.e2e.ts     # 错误处理测试 (15 个测试)
├── fixtures/
│   └── test-data.ts          # 测试数据
└── utils/
    └── test-helpers.ts       # 测试工具类
```

**总计: 52 个端到端测试**

## 测试场景概览

### 1. 代码执行流程 (10 测试)

- 简单代码执行
- 循环代码执行
- 错误代码处理
- 终端输出清空
- 停止长时间运行
- 代码保留
- 执行时间显示
- 连续执行
- 行号显示

### 2. AI 助手交互 (12 测试)

- 打开 AI 面板
- 发送消息和接收回复
- 加载指示器
- 对话历史保存
- 代码问题处理
- 消息样式区分
- 空消息处理
- 自动滚动
- API 错误处理
- Markdown 渲染
- 时间戳显示
- 长回复处理

### 3. 课程导航 (15 测试)

- 课程菜单显示
- 默认课程加载
- 课程切换
- 代码模板加载
- 活动课程高亮
- 课程代码保留
- 进度显示
- 课程描述
- 键盘导航
- 课程分类
- 快速切换
- 完成状态
- 菜单滚动
- 课程元数据
- 增量加载

### 4. 错误处理 (15 测试)

- API 错误 Toast
- 网络错误处理
- 语法错误显示
- 运行时错误
- 控制台日志
- 错误重试
- AI API 错误
- 超时处理
- JavaScript 错误恢复
- 友好错误消息
- 格式错误响应
- 并发请求
- 错误边界
- 数据保留
- localStorage 错误

## 测试报告

测试完成后，报告保存在 `playwright-report/` 目录：

- `index.html` - HTML 测试报告
- `results.json` - JSON 格式结果
- `results.xml` - JUnit XML 格式
- `screenshots/` - 失败截图
- `videos/` - 失败视频（如果有）

## CI/CD 集成

GitHub Actions 工作流已配置在 `.github/workflows/e2e-tests.yml`。

触发条件：
- Push 到 main 或 develop
- Pull Request 到 main 或 develop
- 手动触发

测试矩阵：
- Chromium
- Firefox

构建产物自动上传，保留期：
- 测试报告: 30 天
- 失败截图: 7 天
- 失败视频: 7 天

## 开发建议

### 编写新测试

1. 在 `e2e/` 目录创建 `.e2e.ts` 文件
2. 使用 `test.describe()` 组织测试组
3. 在 `beforeEach` 中初始化 helpers
4. 使用 helper 类进行操作
5. 使用 Playwright 的断言

示例：

```typescript
import { test, expect } from '@playwright/test';
import { PageHelpers, CodeEditorHelpers } from './utils/test-helpers';

test.describe('My New Feature', () => {
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

### 使用 Helper 类

总是使用提供的 helper 类：

```typescript
// ✅ 推荐 - 使用 helper
await codeEditorHelpers.setCode(code);

// ❌ 不推荐 - 直接操作 DOM
await page.locator('.monaco-editor').fill(code);
```

Helper 类包括：
- `PageHelpers` - 页面导航
- `CodeEditorHelpers` - 代码编辑器
- `CodeExecutionHelpers` - 代码执行
- `AIAssistantHelpers` - AI 助手
- `CourseNavigationHelpers` - 课程导航
- `ToastHelpers` - Toast 通知
- `APIMockHelpers` - API Mock

### 调试测试

1. **使用 UI 模式**（最推荐）
   ```bash
   npm run test:e2e:ui
   ```

2. **使用 Debug 模式**
   ```bash
   npm run test:e2e:debug
   ```

3. **查看 Trace**
   ```bash
   npx playwright show-trace trace.zip
   ```

4. **增加超时**
   ```typescript
   test('my test', async ({ page }) => {
     test.setTimeout(60000);
     // ...
   });
   ```

### 测试最佳实践

1. **独立性** - 每个测试应该独立运行
2. **清理** - 使用 `beforeEach` 初始化状态
3. **等待** - 避免硬编码等待，使用智能等待
4. **选择器** - 优先使用 `data-testid` 或语义化选择器
5. **断言** - 使用明确的断言消息
6. **Mock** - 为不稳定的外部依赖使用 Mock

## 常见问题

### Q: 测试运行很慢怎么办？

A:
1. 使用 `--project=chromium` 只运行一个浏览器
2. 使用 `--grep` 运行特定测试
3. 检查是否有不必要的 `waitForTimeout`

### Q: 测试不稳定（Flaky）怎么办？

A:
1. 检查是否有竞态条件
2. 增加超时时间
3. 使用更可靠的选择器
4. 等待网络请求完成

### Q: 如何 Mock API？

A:
```typescript
await apiMockHelpers.mockAPIResponse('/api/execute', {
  success: true,
  output: 'Hello'
});
```

### Q: 如何处理 Monaco Editor？

A:
使用 `CodeEditorHelpers`，它已经处理了 Monaco Editor 的特殊情况。

### Q: 测试在 CI 中失败但本地通过？

A:
1. 检查超时设置
2. 确保 CI 有足够的资源
3. 查看 CI 上传的截图和视频
4. 本地运行 `CI=true npm run test:e2e` 模拟 CI 环境

## 性能指标

- 单个测试平均时间: 5-10 秒
- 完整测试套件时间: 约 5-10 分钟
- 并行执行: 支持
- 失败重试: CI 中自动重试 2 次

## 下一步

- 查看完整文档: `e2e/README.md`
- 查看 helper 源码: `e2e/utils/test-helpers.ts`
- 查看测试数据: `e2e/fixtures/test-data.ts`
- 查看 Playwright 文档: https://playwright.dev/

## 支持

遇到问题？

1. 查看 `e2e/README.md` 详细文档
2. 使用 UI 模式调试
3. 查看测试失败的截图和视频
4. 检查 Playwright 官方文档

---

**版本**: 1.0.0
**最后更新**: 2026-01-08
