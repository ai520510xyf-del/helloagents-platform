# 前端统一错误处理文档

## 目录

- [概述](#概述)
- [架构设计](#架构设计)
- [核心组件](#核心组件)
- [使用指南](#使用指南)
- [API 文档](#api-文档)
- [错误类型](#错误类型)
- [最佳实践](#最佳实践)
- [测试](#测试)
- [故障排查](#故障排查)

---

## 概述

本文档描述了 HelloAgents 平台前端统一错误处理机制的实现。该机制提供了完整的错误捕获、处理和用户反馈能力。

### 设计目标

- 统一的错误处理流程
- 用户友好的错误提示
- 完整的错误日志记录
- React 错误边界保护
- 自动的 API 错误处理

### 技术栈

- React 19
- TypeScript 5+
- Axios (HTTP 客户端)
- React Toastify (通知组件)

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     Application                          │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │            ErrorBoundary (React)                  │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │         ToastProvider                        │ │  │
│  │  │  ┌───────────────────────────────────────┐  │ │  │
│  │  │  │     Application Components            │  │ │  │
│  │  │  │  ┌─────────────────────────────────┐  │  │ │  │
│  │  │  │  │  API Calls (Axios)               │  │ │  │
│  │  │  │  │  - Request Interceptor           │  │ │  │
│  │  │  │  │  - Response Interceptor          │  │ │  │
│  │  │  │  └─────────────────────────────────┘  │  │ │  │
│  │  │  └───────────────────────────────────────┘  │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │     Global Error Handlers (window events)         │  │
│  │  - window.addEventListener('error')                │  │
│  │  - window.addEventListener('unhandledrejection')   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Support Systems                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │   Logger   │  │   Toast    │  │ ErrorMsg   │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 错误处理流程

```
Error Occurs
    │
    ├──> React Error ──────> ErrorBoundary
    │                             │
    │                             ├──> Log Error (logger)
    │                             ├──> Show Toast (optional)
    │                             └──> Render Fallback UI
    │
    ├──> API Error ────────> Axios Interceptor
    │                             │
    │                             ├──> GlobalErrorHandler
    │                             ├──> Log Error (logger)
    │                             ├──> Show Toast
    │                             └──> Return Rejected Promise
    │
    ├──> Unhandled Rejection ──> Global Handler
    │                             │
    │                             ├──> Log Error (logger)
    │                             ├──> Show Toast
    │                             └──> Prevent Default
    │
    └──> Global JS Error ──────> Global Handler
                                  │
                                  ├──> Log Error (logger)
                                  ├──> Show Toast
                                  └──> Prevent Default
```

---

## 核心组件

### 1. ErrorBoundary

React 错误边界组件，捕获子组件树中的 JavaScript 错误。

**文件位置:** `frontend/src/components/ErrorBoundary.tsx`

**特性:**
- 捕获组件渲染错误
- 显示降级 UI
- 记录错误日志
- 支持自定义 fallback UI
- 支持错误回调

**示例:**

```tsx
<ErrorBoundary
  onError={handleError}
  fallback={<CustomErrorUI />}
>
  <App />
</ErrorBoundary>
```

### 2. GlobalErrorHandler

全局错误处理器类，提供统一的错误处理方法。

**文件位置:** `frontend/src/utils/errorHandler.ts`

**方法:**

| 方法 | 说明 |
|------|------|
| `handleAPIError()` | 处理 API 错误 |
| `handleReactError()` | 处理 React 错误 |
| `handleUnhandledRejection()` | 处理未捕获的 Promise rejection |
| `handleGlobalError()` | 处理全局 JS 错误 |
| `init()` | 初始化全局错误处理器 |
| `cleanup()` | 清理全局错误处理器 |

### 3. Axios Instance

配置了统一错误处理的 Axios 实例。

**文件位置:** `frontend/src/api/axios.ts`

**特性:**
- 自动添加认证 token
- 请求/响应日志记录
- 性能监控
- 统一错误处理
- 请求超时配置

### 4. ErrorMessage Component

可复用的错误提示组件。

**文件位置:** `frontend/src/components/ErrorMessage.tsx`

**Props:**

```typescript
interface ErrorMessageProps {
  error: string | Error | null;
  onRetry?: () => void;
  showDetails?: boolean;
  className?: string;
}
```

### 5. Toast System

基于 react-toastify 的通知系统。

**文件位置:** `frontend/src/components/Toast.tsx`

**方法:**

```typescript
notify.success(message: string)
notify.error(message: string)
notify.warning(message: string)
notify.info(message: string)
notify.loading(message: string)
notify.promise(promise, messages)
```

### 6. Logger

统一的日志记录工具。

**文件位置:** `frontend/src/utils/logger.ts`

**方法:**

```typescript
logger.debug(message: string, data?: any)
logger.info(message: string, data?: any)
logger.warn(message: string, data?: any)
logger.error(message: string, data?: any)
logger.performance(metric: string, value: number)
logger.userAction(action: string, details?: any)
```

---

## 使用指南

### 1. 在组件中使用错误处理

#### 显示错误消息

```tsx
import { ErrorMessage } from '@/components/ErrorMessage';
import { useState } from 'react';

function MyComponent() {
  const [error, setError] = useState<Error | null>(null);

  const handleAction = async () => {
    try {
      await someAsyncOperation();
      setError(null);
    } catch (err) {
      setError(err as Error);
    }
  };

  return (
    <div>
      <ErrorMessage
        error={error}
        onRetry={handleAction}
        showDetails={import.meta.env.DEV}
      />
      {/* 组件内容 */}
    </div>
  );
}
```

#### API 调用

```tsx
import api from '@/api/axios';
import { notify } from '@/components/Toast';

async function fetchData() {
  try {
    const response = await api.get('/api/v1/data');
    return response.data;
  } catch (error) {
    // 错误已被 Axios 拦截器处理
    // 可以选择性地添加额外的错误处理
    throw error;
  }
}
```

#### 使用 Toast 通知

```tsx
import { notify } from '@/components/Toast';

// 简单通知
notify.success('操作成功');
notify.error('操作失败');
notify.warning('注意事项');
notify.info('提示信息');

// Promise 通知
notify.promise(
  fetchData(),
  {
    pending: '加载中...',
    success: '加载成功',
    error: '加载失败',
  }
);

// 加载状态
const toastId = notify.loading('处理中...');
// ... 异步操作
notify.update(toastId, {
  render: '处理完成',
  type: 'success',
  isLoading: false,
  autoClose: 3000,
});
```

### 2. 日志记录

```tsx
import { logger } from '@/utils/logger';

// 调试日志 (仅开发环境)
logger.debug('Debug info', { data: 'test' });

// 信息日志
logger.info('User logged in', { userId: '123' });

// 警告日志
logger.warn('Deprecated API used', { api: '/old-endpoint' });

// 错误日志
logger.error('Failed to fetch data', {
  error: error.message,
  endpoint: '/api/data',
});

// 性能日志
logger.performance('API Request', 1500, 'ms');

// 用户行为日志
logger.userAction('Button Click', {
  button: 'submit',
  page: 'form',
});
```

### 3. 自定义错误处理

```tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { GlobalErrorHandler } from '@/utils/errorHandler';

function App() {
  const handleError = (error: Error, errorInfo: any) => {
    // 自定义错误处理逻辑
    console.log('Custom error handling', error, errorInfo);

    // 可以发送到错误跟踪服务
    // sendToSentry(error, errorInfo);
  };

  return (
    <ErrorBoundary onError={handleError}>
      <YourApp />
    </ErrorBoundary>
  );
}
```

---

## API 文档

### ErrorBoundary Props

```typescript
interface ErrorBoundaryProps {
  children: ReactNode;           // 子组件
  fallback?: ReactNode;          // 自定义降级 UI
  onError?: (                    // 错误回调
    error: Error,
    errorInfo: ErrorInfo
  ) => void;
}
```

### ErrorMessage Props

```typescript
interface ErrorMessageProps {
  error: string | Error | null;  // 错误对象或字符串
  onRetry?: () => void;          // 重试回调
  showDetails?: boolean;         // 是否显示详情
  className?: string;            // 自定义样式类
}
```

### Logger Methods

```typescript
class Logger {
  debug(message: string, data?: any): void;
  info(message: string, data?: any): void;
  warn(message: string, data?: any): void;
  error(message: string, data?: any): void;
  performance(metric: string, value: number, unit?: string): void;
  userAction(action: string, details?: any): void;
}
```

### GlobalErrorHandler Methods

```typescript
class GlobalErrorHandler {
  static handleAPIError(error: AxiosError): void;
  static handleReactError(error: Error, errorInfo?: any): void;
  static handleUnhandledRejection(event: PromiseRejectionEvent): void;
  static handleGlobalError(event: ErrorEvent): void;
  static init(): void;
  static cleanup(): void;
}
```

---

## 错误类型

### API 错误代码

| 错误代码 | HTTP 状态 | 说明 | 用户提示 |
|---------|-----------|------|---------|
| `VALIDATION_ERROR` | 400 | 输入验证失败 | 输入验证失败: {message} |
| `AUTHENTICATION_ERROR` | 401 | 未认证 | 请先登录 |
| `AUTHORIZATION_ERROR` | 403 | 无权限 | 没有权限执行此操作 |
| `RESOURCE_NOT_FOUND` | 404 | 资源不存在 | 请求的资源不存在 |
| `RATE_LIMIT_ERROR` | 429 | 请求过于频繁 | 请求过于频繁，请稍后再试 |
| `SANDBOX_EXECUTION_ERROR` | 500 | 代码执行错误 | 代码执行错误: {message} |
| `CONTAINER_POOL_ERROR` | 503 | 容器池错误 | 服务暂时不可用，请稍后重试 |
| `TIMEOUT_ERROR` | 504 | 请求超时 | 请求超时，请重试 |

### 网络错误

| 错误代码 | 说明 | 用户提示 |
|---------|------|---------|
| `ERR_NETWORK` | 网络连接失败 | 网络连接失败，请检查网络 |
| `ECONNABORTED` | 请求超时 | 请求超时，请检查网络连接 |
| `ERR_CANCELED` | 请求被取消 | (无提示，仅日志记录) |

---

## 最佳实践

### 1. 错误处理原则

✅ **推荐做法:**

```tsx
// 在组件层面捕获特定错误
try {
  await api.post('/api/data', data);
  notify.success('保存成功');
} catch (error) {
  // API 错误已被自动处理
  // 只需要处理组件特定的逻辑
  setFormError(error);
}
```

❌ **不推荐做法:**

```tsx
// 不要重复处理错误
try {
  await api.post('/api/data', data);
} catch (error) {
  // 错误已被 Axios 拦截器处理，不要再次显示 toast
  notify.error('保存失败'); // 重复提示
}
```

### 2. 日志记录最佳实践

✅ **推荐做法:**

```tsx
// 记录有意义的上下文信息
logger.error('Failed to save user profile', {
  userId: user.id,
  error: error.message,
  stack: error.stack,
  timestamp: Date.now(),
});
```

❌ **不推荐做法:**

```tsx
// 不要记录无用信息
logger.error('Error'); // 信息不足
console.log(error);    // 应使用 logger
```

### 3. 用户提示最佳实践

✅ **推荐做法:**

```tsx
// 提供明确、可操作的错误信息
notify.error('保存失败，请检查网络连接后重试');

// 为用户提供重试选项
<ErrorMessage
  error={error}
  onRetry={handleRetry}
/>
```

❌ **不推荐做法:**

```tsx
// 不要显示技术细节给用户
notify.error(error.stack); // 用户无法理解
notify.error('Error 500'); // 不友好
```

### 4. ErrorBoundary 使用

✅ **推荐做法:**

```tsx
// 在应用顶层使用
<ErrorBoundary>
  <App />
</ErrorBoundary>

// 在关键模块使用
<ErrorBoundary
  fallback={<ModuleFallback />}
>
  <CriticalModule />
</ErrorBoundary>
```

❌ **不推荐做法:**

```tsx
// 不要过度使用
<ErrorBoundary>
  <div>
    <ErrorBoundary>
      <Component /> {/* 嵌套过多 */}
    </ErrorBoundary>
  </div>
</ErrorBoundary>
```

---

## 测试

### 测试文件

`frontend/tests/errorHandling.test.tsx`

### 运行测试

```bash
cd frontend

# 运行所有测试
npm test

# 运行错误处理测试
npm test errorHandling

# 运行测试并查看覆盖率
npm run test:coverage
```

### 测试覆盖

- ErrorBoundary 组件测试
- ErrorMessage 组件测试
- GlobalErrorHandler 测试
- Logger 测试
- Axios 拦截器测试

### 测试示例

```tsx
describe('ErrorBoundary', () => {
  it('should catch errors and display fallback UI', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('抱歉，出现了一些问题')).toBeInTheDocument();
  });
});
```

---

## 故障排查

### 常见问题

#### 1. Toast 通知不显示

**问题:** 调用 `notify.error()` 但没有显示通知

**解决方案:**

```tsx
// 确保在 App 组件中添加了 ToastProvider
import { ToastProvider } from '@/components/Toast';

function App() {
  return (
    <>
      <ToastProvider />
      <YourApp />
    </>
  );
}
```

#### 2. ErrorBoundary 不捕获错误

**问题:** ErrorBoundary 没有捕获到错误

**原因及解决:**

- ErrorBoundary 只能捕获子组件的错误，不能捕获：
  - 事件处理器中的错误 (使用 try-catch)
  - 异步代码中的错误 (使用 try-catch 或 .catch())
  - 服务端渲染的错误
  - ErrorBoundary 自身的错误

```tsx
// ❌ ErrorBoundary 无法捕获
<button onClick={() => {
  throw new Error('Event error');
}}>
  Click
</button>

// ✅ 正确处理
<button onClick={() => {
  try {
    riskyOperation();
  } catch (error) {
    handleError(error);
  }
}}>
  Click
</button>
```

#### 3. API 错误处理不生效

**问题:** API 错误没有显示友好的错误提示

**解决方案:**

```tsx
// 确保使用配置好的 axios 实例
import api from '@/api/axios';  // ✅ 正确

// 而不是
import axios from 'axios';      // ❌ 错误
```

#### 4. 日志不记录

**问题:** `logger.debug()` 没有输出

**原因:** debug 日志仅在开发环境输出

**解决方案:**

```tsx
// 开发环境
logger.debug('Debug info');  // ✅ 会输出

// 生产环境
logger.debug('Debug info');  // ❌ 不会输出
logger.info('Info');         // ✅ 会输出
```

---

## 配置

### 环境变量

```env
# API 基础 URL
VITE_API_URL=http://localhost:8000

# 日志级别
VITE_LOG_LEVEL=debug
```

### Toast 配置

在 `frontend/src/components/Toast.tsx` 中修改默认配置:

```tsx
const defaultOptions: ToastOptions = {
  position: 'top-right',      // 位置
  autoClose: 5000,            // 自动关闭时间
  hideProgressBar: false,     // 是否隐藏进度条
  closeOnClick: true,         // 点击关闭
  pauseOnHover: true,         // 悬停暂停
  draggable: true,            // 可拖拽
};
```

### Axios 配置

在 `frontend/src/api/axios.ts` 中修改配置:

```tsx
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000,             // 超时时间
  headers: {
    'Content-Type': 'application/json',
  },
});
```

---

## 性能考虑

### 1. 日志性能

- Debug 日志仅在开发环境启用
- 生产环境仅记录 warn 和 error 级别
- 异步发送日志到服务器，不阻塞主线程

### 2. ErrorBoundary 性能

- 使用 React.memo 优化 fallback UI
- 避免在 ErrorBoundary 中进行复杂计算

### 3. Toast 性能

- 限制同时显示的 Toast 数量
- 使用 toast.isActive() 避免重复显示

---

## 未来优化

### 计划中的功能

1. **错误上报服务集成**
   - Sentry 集成
   - 自定义错误上报接口
   - 错误统计和分析

2. **离线错误缓存**
   - 离线时缓存错误日志
   - 网络恢复后批量上报

3. **智能错误恢复**
   - 自动重试机制
   - 降级策略
   - 错误预测

4. **错误分类和过滤**
   - 错误严重级别分类
   - 错误去重
   - 错误过滤规则

---

## 参考资源

- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [Axios Documentation](https://axios-http.com/docs/intro)
- [React Toastify](https://fkhadra.github.io/react-toastify/introduction)
- [Error Handling Best Practices](https://kentcdodds.com/blog/error-handling-in-react)

---

## 更新日志

### v1.0.0 (2026-01-08)

- ✅ 实现 ErrorBoundary 组件
- ✅ 实现 GlobalErrorHandler
- ✅ 实现 Axios 统一错误处理
- ✅ 实现 ErrorMessage 组件
- ✅ 实现 Toast 通知系统
- ✅ 实现 Logger 工具
- ✅ 编写完整的单元测试
- ✅ 集成到 App 组件

---

## 联系方式

如有问题或建议，请联系前端团队或在项目仓库提交 Issue。

**维护者:** Frontend Team
**最后更新:** 2026-01-08
