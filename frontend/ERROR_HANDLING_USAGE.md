# 前端错误处理使用指南

## 快速开始

HelloAgents 平台前端已经集成了完整的统一错误处理机制。本指南将帮助您快速上手。

## 📋 已实现的功能

✅ **ErrorBoundary** - React 错误边界，捕获组件错误
✅ **GlobalErrorHandler** - 全局错误处理器，统一处理各类错误
✅ **Axios 拦截器** - 自动处理 API 错误
✅ **ErrorMessage 组件** - 可复用的错误提示组件
✅ **Toast 通知系统** - 用户友好的消息提示
✅ **Logger 工具** - 统一的日志记录系统

## 🚀 使用方法

### 1. ErrorBoundary - 捕获 React 错误

ErrorBoundary 已经在 `App.tsx` 中全局配置，无需额外设置。

```tsx
// frontend/src/App.tsx
<ErrorBoundary
  onError={GlobalErrorHandler.handleReactError}
>
  <ToastProvider />
  <YourApp />
</ErrorBoundary>
```

如果需要在特定模块使用 ErrorBoundary：

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';

<ErrorBoundary fallback={<div>模块加载失败</div>}>
  <YourModule />
</ErrorBoundary>
```

### 2. API 调用 - 自动错误处理

使用配置好的 Axios 实例，错误会自动处理：

```tsx
import api from './api/axios';

// GET 请求
const fetchData = async () => {
  try {
    const response = await api.get('/api/v1/data');
    return response.data;
  } catch (error) {
    // 错误已被拦截器自动处理（显示 Toast）
    // 这里可以添加组件特定的错误处理逻辑
  }
};

// POST 请求
const submitData = async (data) => {
  try {
    const response = await api.post('/api/v1/submit', data);
    notify.success('提交成功');
    return response.data;
  } catch (error) {
    // 错误已被自动处理
  }
};
```

### 3. ErrorMessage 组件 - 显示错误信息

在组件中显示错误消息：

```tsx
import { ErrorMessage } from './components/ErrorMessage';
import { useState } from 'react';

function MyComponent() {
  const [error, setError] = useState(null);

  const handleAction = async () => {
    try {
      await someOperation();
    } catch (err) {
      setError(err);
    }
  };

  return (
    <div>
      <ErrorMessage
        error={error}
        onRetry={handleAction}
        showDetails={false}
      />
      {/* 其他内容 */}
    </div>
  );
}
```

### 4. Toast 通知 - 用户提示

```tsx
import { notify } from './components/Toast';

// 成功提示
notify.success('操作成功');

// 错误提示
notify.error('操作失败');

// 警告提示
notify.warning('请注意');

// 信息提示
notify.info('提示信息');

// Promise 提示（自动根据结果显示）
notify.promise(
  fetchData(),
  {
    pending: '加载中...',
    success: '加载成功',
    error: '加载失败',
  }
);
```

### 5. Logger - 日志记录

```tsx
import { logger } from './utils/logger';

// Debug 日志（仅开发环境）
logger.debug('调试信息', { data: 'value' });

// Info 日志
logger.info('用户登录', { userId: '123' });

// Warning 日志
logger.warn('使用了废弃的 API', { api: '/old' });

// Error 日志
logger.error('操作失败', { error: error.message });

// 性能日志
logger.performance('API 请求', 1500, 'ms');

// 用户行为日志
logger.userAction('点击按钮', { button: 'submit' });
```

## 📝 完整示例

### 表单提交示例

```tsx
import { useState } from 'react';
import { ErrorMessage } from './components/ErrorMessage';
import { notify } from './components/Toast';
import { logger } from './utils/logger';
import api from './api/axios';

function LoginForm() {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // 表单验证
      if (!formData.email || !formData.password) {
        throw new Error('请填写完整信息');
      }

      // API 调用
      const response = await api.post('/api/v1/auth/login', formData);

      // 成功处理
      notify.success('登录成功');
      logger.userAction('用户登录', { email: formData.email });

      // 跳转等操作...

    } catch (err) {
      // 错误处理
      setError(err);
      logger.error('登录失败', {
        error: err.message,
        email: formData.email,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <ErrorMessage error={error} onRetry={handleSubmit} />

      <input
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        placeholder="邮箱"
      />

      <input
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        placeholder="密码"
      />

      <button type="submit" disabled={loading}>
        {loading ? '登录中...' : '登录'}
      </button>
    </form>
  );
}
```

### 数据加载示例

```tsx
import { useState, useEffect } from 'react';
import { ErrorMessage } from './components/ErrorMessage';
import api from './api/axios';

function DataList() {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get('/api/v1/data');
      setData(response.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <div>加载中...</div>;

  return (
    <div>
      <ErrorMessage error={error} onRetry={fetchData} />
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}
```

## 🎯 错误类型处理

### API 错误代码

后端返回的错误会自动被识别并显示友好的提示：

| 错误代码 | 用户提示 |
|---------|---------|
| `VALIDATION_ERROR` | 输入验证失败: {详细信息} |
| `AUTHENTICATION_ERROR` | 请先登录（2秒后跳转登录页） |
| `AUTHORIZATION_ERROR` | 没有权限执行此操作 |
| `RESOURCE_NOT_FOUND` | 请求的资源不存在 |
| `RATE_LIMIT_ERROR` | 请求过于频繁，请稍后再试 |
| `SANDBOX_EXECUTION_ERROR` | 代码执行错误: {详细信息} |
| `CONTAINER_POOL_ERROR` | 服务暂时不可用，请稍后重试 |
| `TIMEOUT_ERROR` | 请求超时，请重试 |

### 网络错误

| 错误 | 用户提示 |
|------|---------|
| 网络连接失败 | 网络连接失败，请检查网络 |
| 请求超时 | 请求超时，请检查网络连接 |

## 📚 查看示例代码

完整的使用示例请查看：

```
frontend/src/examples/ErrorHandlingExample.tsx
```

该文件包含了所有功能的完整示例，可以直接运行查看效果。

## 🧪 测试

运行错误处理相关测试：

```bash
cd frontend

# 运行所有测试
npm test

# 运行错误处理测试
npm test errorHandling

# 查看测试覆盖率
npm run test:coverage
```

## 📖 详细文档

完整的技术文档请查看：

```
frontend/reports/ERROR_HANDLING_FRONTEND.md
```

该文档包含：
- 架构设计
- API 文档
- 最佳实践
- 故障排查
- 性能优化建议

## ⚠️ 注意事项

### DO's ✅

- 使用 `import api from './api/axios'` 进行 API 调用
- 在组件中使用 ErrorMessage 显示错误
- 使用 notify 提供用户反馈
- 使用 logger 记录重要操作
- 在开发环境启用 `showDetails` 查看错误详情

### DON'Ts ❌

- 不要直接使用 `import axios from 'axios'`（会绕过错误处理）
- 不要重复显示错误提示（API 错误已自动处理）
- 不要在生产环境显示技术细节给用户
- 不要忽略 console 中的错误日志
- 不要过度嵌套 ErrorBoundary

## 🔧 配置

### 环境变量

在 `.env` 中配置：

```env
# API 基础 URL
VITE_API_URL=http://localhost:8000

# 日志级别
VITE_LOG_LEVEL=debug
```

### Toast 配置

修改 `frontend/src/components/Toast.tsx` 中的 `defaultOptions`：

```tsx
const defaultOptions = {
  position: 'top-right',  // 位置
  autoClose: 5000,        // 自动关闭时间（毫秒）
  hideProgressBar: false, // 显示进度条
  // ... 其他配置
};
```

## 🐛 常见问题

### Toast 不显示

确保在 App 组件中添加了 `<ToastProvider />`。

### ErrorBoundary 不捕获错误

ErrorBoundary 只能捕获组件渲染错误，不能捕获：
- 事件处理器中的错误（使用 try-catch）
- 异步代码中的错误（使用 try-catch）
- 服务端渲染的错误

### API 错误没有提示

确保使用 `import api from './api/axios'` 而不是 `axios`。

## 📞 支持

如有问题，请：
1. 查看详细文档：`frontend/reports/ERROR_HANDLING_FRONTEND.md`
2. 查看示例代码：`frontend/src/examples/ErrorHandlingExample.tsx`
3. 查看测试用例：`frontend/src/errorHandling.test.tsx`
4. 联系前端团队

---

**维护者:** Frontend Team
**最后更新:** 2026-01-08
