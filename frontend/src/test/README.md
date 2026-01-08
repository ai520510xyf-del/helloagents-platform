# HelloAgents 前端测试指南

## 测试框架

- **测试运行器**: Vitest 2.x
- **测试库**: @testing-library/react
- **断言库**: Vitest (兼容 Jest API)
- **覆盖率**: Vitest Coverage (V8)

## 安装依赖

```bash
cd frontend
npm install
```

测试相关依赖已在 `package.json` 中定义。

## 运行测试

### 运行所有测试
```bash
npm test
# 或
npm run test
```

### 监视模式（推荐开发时使用）
```bash
npm run test:watch
```

### UI 模式（交互式测试界面）
```bash
npm run test:ui
```

### 生成覆盖率报告
```bash
npm run test:coverage
```

### 运行特定测试文件
```bash
npm test -- Button.spec.tsx
```

### 运行特定测试用例
```bash
npm test -- -t "应该渲染按钮文本"
```

## 测试文件结构

```
src/
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   └── Button.spec.tsx          # 组件测试
│   └── MigrationPrompt.tsx
├── utils/
│   ├── migrationHelper.ts
│   └── migrationHelper.spec.ts      # 工具函数测试
├── services/
│   └── api.ts                       # API 服务（可测试）
└── test/
    ├── setup.ts                     # 测试环境设置
    ├── utils.ts                     # 测试工具函数
    └── README.md                    # 本文档
```

## 测试命名约定

- 测试文件：`*.spec.ts` 或 `*.spec.tsx`
- 放在被测试文件的旁边
- 例如：`Button.tsx` → `Button.spec.tsx`

## 编写测试

### 基本组件测试

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('应该渲染按钮文本', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})
```

### 测试用户交互

```typescript
import { fireEvent } from '@testing-library/react'
import { vi } from 'vitest'

it('应该处理点击事件', () => {
  const handleClick = vi.fn()
  render(<Button onClick={handleClick}>Click me</Button>)

  fireEvent.click(screen.getByText('Click me'))

  expect(handleClick).toHaveBeenCalledTimes(1)
})
```

### 测试异步操作

```typescript
import { waitFor } from '@testing-library/react'

it('应该加载数据', async () => {
  render(<DataComponent />)

  await waitFor(() => {
    expect(screen.getByText('Loaded data')).toBeInTheDocument()
  })
})
```

### 模拟 API 调用

```typescript
import { vi } from 'vitest'

// 方式 1：模拟整个模块
vi.mock('../services/api', () => ({
  executeCode: vi.fn(() => Promise.resolve({
    success: true,
    output: 'Hello, World!'
  }))
}))

// 方式 2：使用 MSW (Mock Service Worker)
// 见下方 MSW 部分
```

### 测试工具函数

```typescript
import { describe, it, expect } from 'vitest'
import { needsMigration } from './migrationHelper'

describe('needsMigration', () => {
  it('应该检测 localStorage 中的数据', () => {
    localStorage.setItem('helloagents_progress', '{}')
    expect(needsMigration()).toBe(true)
  })
})
```

## Mock Service Worker (MSW)

使用 MSW 模拟 API 请求（推荐用于集成测试）：

### 安装
```bash
npm install -D msw
```

### 设置
```typescript
// src/test/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/api/execute', () => {
    return HttpResponse.json({
      success: true,
      output: 'Mocked output'
    })
  }),

  http.get('/api/lessons/:id', ({ params }) => {
    return HttpResponse.json({
      lesson_id: params.id,
      title: 'Test Lesson',
      content: '# Test Content'
    })
  })
]

// src/test/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)

// src/test/setup.ts
import { beforeAll, afterEach, afterAll } from 'vitest'
import { server } from './mocks/server'

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### 使用
```typescript
it('应该获取课程内容', async () => {
  render(<LessonView lessonId="1" />)

  await waitFor(() => {
    expect(screen.getByText('Test Lesson')).toBeInTheDocument()
  })
})
```

## 测试覆盖率

### 查看覆盖率报告
```bash
npm run test:coverage
```

### HTML 报告
运行后会生成 `coverage/index.html`，在浏览器中打开查看。

### 覆盖率目标
- **语句覆盖率**: ≥80%
- **分支覆盖率**: ≥75%
- **函数覆盖率**: ≥80%
- **行覆盖率**: ≥80%

## 最佳实践

### 1. AAA 模式（Arrange-Act-Assert）
```typescript
it('示例测试', () => {
  // Arrange: 准备测试数据
  const data = { value: 42 }

  // Act: 执行操作
  const result = processData(data)

  // Assert: 验证结果
  expect(result).toBe(84)
})
```

### 2. 使用 describe 分组
```typescript
describe('Button', () => {
  describe('渲染', () => {
    it('应该渲染文本', () => {})
    it('应该渲染图标', () => {})
  })

  describe('交互', () => {
    it('应该处理点击', () => {})
    it('应该处理悬停', () => {})
  })
})
```

### 3. 避免测试实现细节
```typescript
// ❌ 不好：测试实现细节
expect(component.state.count).toBe(1)

// ✅ 好：测试用户可见的行为
expect(screen.getByText('Count: 1')).toBeInTheDocument()
```

### 4. 使用数据驱动测试
```typescript
it.each([
  { input: 1, expected: 2 },
  { input: 2, expected: 4 },
  { input: 3, expected: 6 }
])('应该将 $input 加倍为 $expected', ({ input, expected }) => {
  expect(double(input)).toBe(expected)
})
```

### 5. 清理副作用
```typescript
import { afterEach } from 'vitest'

afterEach(() => {
  localStorage.clear()
  vi.clearAllMocks()
})
```

## 常用断言

### 基本断言
```typescript
expect(value).toBe(expected)           // 严格相等
expect(value).toEqual(expected)        // 深度相等
expect(value).toBeTruthy()             // 真值
expect(value).toBeFalsy()              // 假值
expect(value).toBeNull()               // null
expect(value).toBeUndefined()          // undefined
```

### 数字断言
```typescript
expect(value).toBeGreaterThan(3)       // > 3
expect(value).toBeGreaterThanOrEqual(3) // >= 3
expect(value).toBeLessThan(5)          // < 5
expect(value).toBeCloseTo(0.3, 5)      // 浮点数比较
```

### 字符串断言
```typescript
expect(str).toMatch(/pattern/)         // 正则匹配
expect(str).toContain('substring')     // 包含子串
```

### 数组/对象断言
```typescript
expect(array).toContain(item)          // 包含元素
expect(array).toHaveLength(3)          // 长度
expect(obj).toHaveProperty('key')      // 有属性
expect(obj).toMatchObject({ a: 1 })    // 部分匹配
```

### DOM 断言（jest-dom）
```typescript
expect(element).toBeInTheDocument()    // 在文档中
expect(element).toBeVisible()          // 可见
expect(element).toBeDisabled()         // 禁用
expect(element).toHaveClass('active')  // 有类名
expect(element).toHaveTextContent('text') // 有文本
```

## 调试测试

### 打印 DOM
```typescript
import { screen, debug } from '@testing-library/react'

debug()                                 // 打印整个 DOM
debug(screen.getByRole('button'))      // 打印特定元素
```

### 使用 VSCode 调试
在 `.vscode/launch.json` 中添加：
```json
{
  "type": "node",
  "request": "launch",
  "name": "Vitest",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["test", "--", "--run"],
  "console": "integratedTerminal",
  "internalConsoleOptions": "neverOpen"
}
```

## 持续集成

在 CI/CD 中运行测试：

```yaml
# .github/workflows/test.yml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test -- --run
      - run: npm run test:coverage
```

## 故障排查

### 测试超时
增加超时时间：
```typescript
it('慢速测试', async () => {
  // ...
}, 10000) // 10 秒
```

### 找不到元素
使用 `screen.debug()` 查看当前 DOM：
```typescript
render(<Component />)
screen.debug()  // 打印 DOM
```

### Mock 不生效
确保 mock 在 import 之前：
```typescript
vi.mock('./module')  // ✅ 在 import 之前

import { something } from './module'
```

## 参考资料

- [Vitest 文档](https://vitest.dev/)
- [Testing Library 文档](https://testing-library.com/react)
- [MSW 文档](https://mswjs.io/)
- [Jest DOM 匹配器](https://github.com/testing-library/jest-dom)
