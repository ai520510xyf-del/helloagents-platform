# E2E 测试快速参考

## 5 分钟快速开始

### 1. 安装和配置
```bash
cd frontend
npm install
npx playwright install
```

### 2. 运行测试
```bash
# 🎨 UI 模式（最推荐）
npm run test:e2e:ui

# 🚀 运行所有测试
npm run test:e2e

# 👀 显示浏览器窗口
npm run test:e2e:headed
```

### 3. 查看结果
```bash
# 📊 查看测试报告
npm run test:e2e:report
```

## 常用命令速查

### 运行测试
```bash
npm run test:e2e              # 所有测试
npm run test:e2e:ui          # UI 模式
npm run test:e2e:headed      # 显示浏览器
npm run test:e2e:debug       # 调试模式
npm run test:e2e:chromium    # 仅 Chromium
npm run test:e2e:firefox     # 仅 Firefox
```

### 高级命令
```bash
# 运行特定文件
npx playwright test learn-page.e2e.ts

# 运行特定测试
npx playwright test -g "应该能够切换主题"

# 运行特定设备
npx playwright test --project=mobile-chrome

# 查看 trace
npx playwright show-trace trace.zip
```

## 文件位置速查

```
e2e/
├── pages/LearnPage.ts        # 页面对象
├── utils/helpers.ts          # 工具函数
├── learn-page.e2e.ts         # 核心流程测试
├── mobile.e2e.ts            # 移动端测试
├── README.md                # 完整文档
├── TESTING_GUIDE.md         # 使用指南
└── QUICK_START.md           # 本文件
```

## 编写测试速查

### 基本模板
```typescript
import { test, expect } from '@playwright/test';
import { LearnPage } from './pages/LearnPage';

test('测试名称', async ({ page }) => {
  const learnPage = new LearnPage(page);
  await learnPage.goto();

  // 执行操作
  await learnPage.runCode();

  // 断言
  const output = await learnPage.getTerminalOutput();
  expect(output).toContain('期望的输出');
});
```

### LearnPage 常用方法
```typescript
// 导航
await learnPage.goto()

// 主题
await learnPage.toggleTheme()
const theme = await learnPage.getTheme()

// 代码
await learnPage.typeCode('print("hello")')
await learnPage.runCode()
await learnPage.resetCode()

// 输出
const output = await learnPage.getTerminalOutput()
await learnPage.clearOutput()

// 课程
await learnPage.selectLesson('课程名')

// AI
await learnPage.switchToAITab()
await learnPage.sendAIMessage('问题')
```

### 辅助函数速查
```typescript
import {
  waitAndClick,
  takeScreenshot,
  checkBasicAccessibility
} from './utils/helpers';

await waitAndClick(page, 'button')
await takeScreenshot(page, 'name')
await checkBasicAccessibility(page)
```

## 选择器优先级

1. ✅ 用户可见文本: `text=登录`
2. ✅ Role: `role=button[name="提交"]`
3. ✅ Test ID: `[data-testid="submit"]`
4. ⚠️ CSS: `.submit-button`

## 断言速查

```typescript
// 元素
await expect(element).toBeVisible()
await expect(element).toHaveText('text')
await expect(element).toHaveAttribute('class', 'active')

// 页面
await expect(page).toHaveURL(/dashboard/)
await expect(page).toHaveTitle('Title')

// 值
expect(value).toBe(expected)
expect(array).toHaveLength(3)
expect(output).toContain('success')
```

## 调试速查

### 问题：测试超时
```typescript
test.setTimeout(120000); // 增加超时
```

### 问题：元素找不到
```bash
# 使用 Inspector
npx playwright test --debug

# 增加等待
await page.waitForSelector(selector, { timeout: 30000 })
```

### 问题：测试不稳定
```typescript
// 等待网络空闲
await page.waitForLoadState('networkidle')

// 增加重试
test.describe.configure({ retries: 2 })
```

## CI 环境

### 本地模拟 CI
```bash
CI=true npm run test:e2e
BASE_URL=https://helloagents-platform.pages.dev npm run test:e2e
```

### 查看 CI 结果
1. 进入 GitHub Actions
2. 选择 "E2E Tests"
3. 查看报告和截图

## 测试覆盖范围

✅ 桌面浏览器: Chromium, Firefox, WebKit
✅ 移动设备: iPhone 12, Pixel 5
✅ 平板设备: iPad Pro
✅ 响应式: 6 种屏幕尺寸

## 帮助资源

- 📖 完整文档: `e2e/README.md`
- 📚 使用指南: `e2e/TESTING_GUIDE.md`
- 🌐 官方文档: https://playwright.dev
- 💬 Slack: #qa 频道

## 常见场景

### 场景 1: 测试代码执行
```typescript
await learnPage.typeCode('print("Hello")')
await learnPage.runCode()
await learnPage.waitForCodeExecution()
const output = await learnPage.getTerminalOutput()
expect(output).toContain('Hello')
```

### 场景 2: 测试主题切换
```typescript
const initialTheme = await learnPage.getTheme()
await learnPage.toggleTheme()
const newTheme = await learnPage.getTheme()
expect(newTheme).not.toBe(initialTheme)
```

### 场景 3: 测试移动端
```typescript
test.use({ ...devices['iPhone 12'] })
const isMobile = await learnPage.isMobileLayout()
expect(isMobile).toBe(true)
```

## 记住这 3 条

1. **使用 UI 模式开发**: `npm run test:e2e:ui`
2. **使用页面对象**: `const learnPage = new LearnPage(page)`
3. **查看文档**: 遇到问题先看 `TESTING_GUIDE.md`

---

准备好了吗？运行你的第一个测试：

```bash
npm run test:e2e:ui
```

🚀 Happy Testing!
