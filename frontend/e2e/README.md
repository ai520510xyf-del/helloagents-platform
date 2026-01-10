# E2E Testing Documentation

完整的端到端测试体系，使用 Playwright 框架验证前后端集成，覆盖多浏览器和多设备场景。

## 目录结构

```
e2e/
├── pages/                    # 页面对象模型 (POM)
│   └── LearnPage.ts         # 学习页面对象
├── utils/                   # 测试工具函数
│   ├── helpers.ts           # 通用辅助函数
│   └── test-helpers.ts      # 原有助手类
├── fixtures/                # 测试数据和固定装置
│   └── test-data.ts        # 测试数据常量
├── learn-page.e2e.ts        # 学习页面核心流程测试（新）
├── mobile.e2e.ts            # 移动端响应式测试（新）
├── code-execution.e2e.ts    # 代码执行流程测试
├── ai-assistant.e2e.ts      # AI 助手交互测试
├── course-navigation.e2e.ts # 课程导航测试
├── error-handling.e2e.ts    # 错误处理测试
└── README.md               # 本文档
```

## 测试场景

### 新增测试（2026-01-09）

#### 学习页面核心流程 (learn-page.e2e.ts)

全面测试学习页面的核心功能：

**基础功能**
- ✅ 页面加载和基本元素显示
- ✅ 课程目录显示
- ✅ 主题切换（明暗模式）
- ✅ 进度信息显示

**课程切换**
- ✅ 选择和切换课程
- ✅ 切换课程时保持代码
- ✅ 课程内容加载

**代码编辑器**
- ✅ 在编辑器中输入代码
- ✅ 显示运行/重置按钮
- ✅ 重置代码功能
- ✅ 光标位置显示

**代码执行**
- ✅ 运行 Python 代码
- ✅ 清空终端输出
- ✅ 等待执行完成

**内容面板**
- ✅ 切换内容/AI 标签
- ✅ 显示课程内容
- ✅ AI 助手界面

**可访问性和性能**
- ✅ 基本可访问性检查
- ✅ 键盘导航支持
- ✅ 页面加载性能测试
- ✅ 控制台错误监控

#### 移动端响应式测试 (mobile.e2e.ts)

全面测试移动端和响应式布局：

**iPhone 12 测试**
- ✅ 移动端布局适配
- ✅ 课程浏览
- ✅ 代码编辑器使用
- ✅ 代码运行
- ✅ 主题切换
- ✅ 触摸滑动

**Android (Pixel 5) 测试**
- ✅ Android 设备显示
- ✅ 垂直滚动
- ✅ 屏幕旋转处理

**平板 (iPad Pro) 测试**
- ✅ 平板布局适配
- ✅ 优化的布局显示
- ✅ 所有功能可用

**响应式断点测试**
- ✅ iPhone SE (375x667)
- ✅ iPhone 12 Pro (390x844)
- ✅ iPad Mini (768x1024)
- ✅ iPad Landscape (1024x768)
- ✅ Laptop (1280x720)
- ✅ Desktop (1920x1080)

**移动端交互**
- ✅ 双指缩放支持
- ✅ 长按操作
- ✅ 弹窗和提示

**移动端性能**
- ✅ 页面加载时间
- ✅ 内存泄漏检测

**移动端可访问性**
- ✅ 屏幕阅读器支持
- ✅ 按钮点击区域大小

**关键特性：**
- 使用页面对象模型 (POM) 设计
- 多设备和多浏览器覆盖
- 性能和可访问性测试
- 详细的断言和验证

### 原有测试场景

### 1. 代码执行流程 (code-execution.e2e.ts)

测试代码编辑和执行的完整流程：

- ✅ 执行简单 Python 代码
- ✅ 执行循环代码显示多行输出
- ✅ 处理代码执行错误
- ✅ 清空终端输出
- ✅ 停止长时间运行的代码
- ✅ 切换标签时保留代码
- ✅ 显示执行时间
- ✅ 处理多次连续执行
- ✅ 显示行号和光标位置

**关键测试点：**
- Monaco Editor 集成
- WebSocket 代码执行
- 终端输出渲染
- 执行状态管理

### 2. AI 助手交互 (ai-assistant.e2e.ts)

测试 AI 助手的交互功能：

- ✅ 打开 AI 助手面板
- ✅ 发送消息并接收回复
- ✅ 显示加载指示器
- ✅ 保留对话历史
- ✅ 处理代码相关问题
- ✅ 区分用户和 AI 消息样式
- ✅ 处理空消息输入
- ✅ 自动滚动到底部
- ✅ 处理 API 错误
- ✅ Markdown 渲染支持
- ✅ 显示消息时间戳
- ✅ 处理长回复

**关键测试点：**
- WebSocket 实时通信
- 消息渲染和格式化
- 对话历史持久化
- 错误状态处理

### 3. 课程导航 (course-navigation.e2e.ts)

测试课程列表和导航功能：

- ✅ 显示课程菜单
- ✅ 加载默认课程内容
- ✅ 切换不同课程
- ✅ 加载课程特定代码模板
- ✅ 高亮活动课程
- ✅ 切换课程时保留代码
- ✅ 显示课程进度
- ✅ 显示课程描述
- ✅ 键盘导航支持
- ✅ 显示课程分类
- ✅ 处理快速切换
- ✅ 显示完成状态
- ✅ 课程菜单滚动
- ✅ 显示课程元数据
- ✅ 增量加载内容

**关键测试点：**
- 课程数据加载
- 路由状态管理
- 本地存储集成
- UI 响应性能

### 4. 错误处理 (error-handling.e2e.ts)

测试各种错误场景的处理：

- ✅ API 错误显示 Toast 通知
- ✅ 网络错误处理
- ✅ 语法错误显示
- ✅ 运行时错误显示
- ✅ 控制台错误日志
- ✅ 错误后重试
- ✅ AI 助手 API 错误
- ✅ 超时错误处理
- ✅ JavaScript 错误恢复
- ✅ 用户友好错误消息
- ✅ 格式错误的响应处理
- ✅ 并发请求处理
- ✅ 错误边界回退
- ✅ 错误后数据保留
- ✅ localStorage 错误处理

**关键测试点：**
- 错误边界实现
- Toast 通知系统
- API 错误处理
- 用户数据保护

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 运行所有 E2E 测试

```bash
npm run test:e2e
```

### 运行特定浏览器测试

```bash
# Chromium only
npm run test:e2e:chromium

# Firefox only
npm run test:e2e:firefox
```

### UI 模式（推荐用于开发）

```bash
npm run test:e2e:ui
```

### Headed 模式（查看浏览器）

```bash
npm run test:e2e:headed
```

### Debug 模式

```bash
npm run test:e2e:debug
```

### 查看测试报告

```bash
npm run test:e2e:report
```

## 测试工具类

### PageHelpers

页面导航和通用操作：

```typescript
await pageHelpers.navigateToLearnPage();
await pageHelpers.waitForPageLoad();
await pageHelpers.waitForElement(selector);
await pageHelpers.takeScreenshot(name);
```

### CodeEditorHelpers

代码编辑器操作：

```typescript
await editorHelpers.setCode(code);
const code = await editorHelpers.getCode();
await editorHelpers.clearCode();
```

### CodeExecutionHelpers

代码执行操作：

```typescript
await executionHelpers.clickRunButton();
await executionHelpers.waitForExecution();
await executionHelpers.expectOutputContains(text);
await executionHelpers.clearTerminal();
```

### AIAssistantHelpers

AI 助手操作：

```typescript
await aiHelpers.openAssistant();
await aiHelpers.sendMessage(message);
await aiHelpers.waitForResponse();
const lastMessage = await aiHelpers.getLastMessage();
```

### CourseNavigationHelpers

课程导航操作：

```typescript
await navigationHelpers.selectCourse(courseName);
const title = await navigationHelpers.getCurrentCourseTitle();
await navigationHelpers.expectCourseContentLoaded();
```

### ToastHelpers

Toast 通知操作：

```typescript
await toastHelpers.waitForToast();
await toastHelpers.expectToastContains(text);
await toastHelpers.closeToast();
```

### APIMockHelpers

API Mock 操作：

```typescript
await apiMockHelpers.mockAPIResponse(endpoint, response);
await apiMockHelpers.mockAPIError(endpoint, status);
await apiMockHelpers.mockNetworkError(endpoint);
await apiMockHelpers.clearAllMocks();
```

## 测试数据

测试数据定义在 `fixtures/test-data.ts` 中：

```typescript
TEST_DATA.codeExamples.simple      // 简单代码示例
TEST_DATA.codeExamples.loop        // 循环代码示例
TEST_DATA.aiQuestions.simple       // 简单 AI 问题
TEST_DATA.timeouts.codeExecution   // 执行超时时间
ERROR_SCENARIOS.apiErrors          // API 错误场景
EXPECTED_RESULTS.codeExecution     // 期望的执行结果
```

## CI/CD 集成

GitHub Actions 工作流配置在 `.github/workflows/e2e-tests.yml`。

### 触发条件

- Push 到 main 或 develop 分支
- Pull Request 到 main 或 develop 分支
- 手动触发

### 测试矩阵

- Chromium
- Firefox

### 构建产物

- 测试报告（保留 30 天）
- 测试结果 JSON（保留 30 天）
- 失败截图（保留 7 天）
- 失败视频（保留 7 天）

## 最佳实践

### 1. 使用 Helper 类

始终使用提供的 helper 类而不是直接操作 DOM：

```typescript
// ✅ 推荐
await codeEditorHelpers.setCode(code);

// ❌ 不推荐
await page.locator('.monaco-editor').fill(code);
```

### 2. 等待策略

使用适当的等待策略：

```typescript
// 等待元素可见
await pageHelpers.waitForElement(selector);

// 等待特定操作完成
await executionHelpers.waitForExecution();

// 避免硬编码等待
// ❌ await page.waitForTimeout(5000);
```

### 3. 测试隔离

每个测试应该独立：

```typescript
test.beforeEach(async ({ page }) => {
  // 重新初始化 helpers
  pageHelpers = new PageHelpers(page);
  // 导航到干净的页面
  await pageHelpers.navigateToLearnPage();
});
```

### 4. 错误处理

优雅处理可选元素：

```typescript
const element = page.locator(selector);
const count = await element.count();
if (count > 0) {
  await expect(element.first()).toBeVisible();
}
```

### 5. Mock API

测试错误场景时使用 API Mock：

```typescript
// Mock 错误响应
await apiMockHelpers.mockAPIError('/api/execute', 500);

// 执行测试
await executionHelpers.clickRunButton();

// 清除 Mock
await apiMockHelpers.clearAllMocks();
```

## 调试技巧

### 1. 使用 UI 模式

```bash
npm run test:e2e:ui
```

提供可视化界面，可以：
- 查看每个步骤
- 时间旅行
- 查看 DOM 快照
- 查看网络请求

### 2. 使用 Debug 模式

```bash
npm run test:e2e:debug
```

逐步执行测试，支持断点。

### 3. 查看 Trace

失败的测试会自动生成 trace 文件：

```bash
npx playwright show-trace trace.zip
```

### 4. 截图和视频

失败的测试会自动截图和录制视频，保存在 `playwright-report/` 目录。

### 5. 增加超时

调试时可以增加超时时间：

```typescript
test('my test', async ({ page }) => {
  test.setTimeout(60000); // 60 秒
  // ...
});
```

## 性能优化

### 1. 并行执行

默认配置支持并行执行多个测试。

### 2. 共享浏览器上下文

相关测试可以共享浏览器上下文以提高速度。

### 3. 选择性测试

只运行特定测试：

```bash
npx playwright test code-execution
npx playwright test --grep "should execute"
```

### 4. 跳过不必要的等待

避免使用 `waitForTimeout`，使用更精确的等待：

```typescript
// ❌ 慢
await page.waitForTimeout(5000);

// ✅ 快
await page.waitForSelector(selector);
```

## 故障排查

### 测试不稳定（Flaky）

1. 检查是否有硬编码的等待
2. 增加超时时间
3. 使用更可靠的选择器
4. 检查网络请求是否完成

### 找不到元素

1. 验证选择器是否正确
2. 检查元素是否在 iframe 中
3. 等待元素加载完成
4. 使用更宽松的匹配器

### Monaco Editor 问题

Monaco Editor 需要特殊处理：

```typescript
// 等待编辑器加载
await page.waitForSelector('.monaco-editor');

// 使用 evaluate 操作编辑器
await page.evaluate((code) => {
  const monaco = (window as any).monaco;
  const models = monaco.editor.getModels();
  if (models.length > 0) {
    models[0].setValue(code);
  }
}, code);
```

## 扩展测试

### 添加新测试场景

1. 在 `e2e/` 目录创建新的 `.e2e.ts` 文件
2. 导入必要的 helpers
3. 使用 `test.describe()` 组织测试
4. 在 `beforeEach` 中初始化 helpers
5. 编写测试用例

### 添加新的 Helper

1. 在 `utils/test-helpers.ts` 中添加新类
2. 导出该类
3. 在测试文件中导入使用

### 添加测试数据

在 `fixtures/test-data.ts` 中添加新的数据常量。

## 测试覆盖范围

当前测试覆盖：

- ✅ 代码编辑和执行
- ✅ AI 助手交互
- ✅ 课程导航
- ✅ 错误处理
- ✅ Toast 通知
- ✅ 本地存储
- ✅ 实时通信

待添加：

- ⏳ 用户认证流程
- ⏳ 课程进度保存
- ⏳ 代码分享功能
- ⏳ 性能监控
- ⏳ 无障碍访问测试

## 相关资源

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright 最佳实践](https://playwright.dev/docs/best-practices)
- [测试自动化模式](https://martinfowler.com/articles/practical-test-pyramid.html)

## 支持

如有问题，请：

1. 查看本文档
2. 检查 Playwright 官方文档
3. 查看测试失败的截图和视频
4. 使用 UI 或 Debug 模式调试

---

**最后更新**: 2026-01-08
**维护者**: Test Automation Engineer
