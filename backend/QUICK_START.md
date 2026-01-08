# API 版本控制快速参考

## 快速开始

### 1. 启动服务

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. 访问文档

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### 3. 测试 API

```bash
# 查看版本信息
curl http://localhost:8000/api/version

# 测试 v1 端点
curl http://localhost:8000/api/v1/lessons
```

## API 端点速查

### v1 端点

```bash
# 代码执行
POST /api/v1/code/execute
{
  "code": "print('Hello')",
  "language": "python",
  "timeout": 30
}

# AI 智能提示
POST /api/v1/code/hint
{
  "code": "def hello():",
  "cursor_line": 1,
  "cursor_column": 12,
  "language": "python"
}

# 课程列表
GET /api/v1/lessons

# 课程详情
GET /api/v1/lessons/{lesson_id}

# AI 聊天
POST /api/v1/chat
{
  "message": "如何实现 ReAct Agent?",
  "conversation_history": [],
  "lesson_id": "1",
  "code": "class Agent: pass"
}

# 沙箱统计
GET /api/v1/sandbox/pool/stats
```

### 版本管理

```bash
# 版本信息
GET /api/version

# 健康检查
GET /health
```

## 前端集成示例

### JavaScript/TypeScript

```typescript
// 配置
const API_BASE = '/api/v1';

// 代码执行
async function executeCode(code: string) {
  const response = await fetch(`${API_BASE}/code/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, language: 'python' })
  });
  return await response.json();
}

// 获取课程列表
async function getLessons() {
  const response = await fetch(`${API_BASE}/lessons`);
  return await response.json();
}

// AI 聊天
async function chatWithAI(message: string, lessonId?: string) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      lesson_id: lessonId,
      conversation_history: []
    })
  });
  return await response.json();
}
```

### React Hook 示例

```typescript
// hooks/useAPI.ts
import { useState } from 'react';

const API_BASE = '/api/v1';

export function useCodeExecution() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const execute = async (code: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/code/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language: 'python' })
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return { execute, loading, result, error };
}
```

## 运行测试

```bash
# 确保服务器运行在 http://localhost:8000
cd backend
python3 test_api_versioning.py
```

## 常用命令

### cURL 示例

```bash
# 带响应头
curl -i http://localhost:8000/api/v1/lessons

# 代码执行
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(2 + 2)"}'

# 指定 API 版本头
curl -H "X-API-Version: v1" http://localhost:8000/health
```

### HTTPie 示例

```bash
# 安装 HTTPie: pip install httpie

# GET 请求
http GET localhost:8000/api/v1/lessons

# POST 请求
http POST localhost:8000/api/v1/code/execute \
  code="print('Hello')" \
  language=python

# 查看响应头
http -h GET localhost:8000/health
```

## 错误处理

所有错误响应格式统一:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "详细错误信息",
    "path": "/api/v1/code/execute",
    "timestamp": 1704672000.0
  }
}
```

常见错误码:
- `VALIDATION_ERROR`: 请求参数验证失败
- `HTTP_404`: 资源不存在
- `HTTP_500`: 服务器内部错误

## 响应头

所有响应包含:
- `X-API-Version`: 当前 API 版本
- `X-Supported-Versions`: 支持的版本列表

示例:
```
X-API-Version: v1
X-Supported-Versions: v1
```

## 开发技巧

### 1. 使用环境变量

```bash
# .env
API_VERSION=v1
API_BASE_URL=http://localhost:8000
```

### 2. 创建 API 客户端类

```typescript
class HelloAgentsAPI {
  constructor(private baseURL: string = '/api/v1') {}

  async executeCode(code: string) {
    return this.post('/code/execute', { code, language: 'python' });
  }

  async getLessons() {
    return this.get('/lessons');
  }

  private async get(path: string) {
    const response = await fetch(this.baseURL + path);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  private async post(path: string, body: any) {
    const response = await fetch(this.baseURL + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

// 使用
const api = new HelloAgentsAPI();
const result = await api.executeCode('print("Hello")');
```

### 3. TypeScript 类型定义

```typescript
// types/api.ts

export interface CodeExecutionRequest {
  code: string;
  language?: string;
  timeout?: number;
}

export interface CodeExecutionResponse {
  success: boolean;
  output: string;
  error?: string;
  execution_time: number;
}

export interface LessonResponse {
  lesson_id: string;
  title: string;
  content: string;
  code_template: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
  lesson_id?: string;
  code?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
```

## 故障排查

### 问题: 404 Not Found

检查:
1. API 端点路径是否正确
2. 是否包含 `/api/v1/` 前缀
3. 服务器是否正在运行

### 问题: 422 Validation Error

检查:
1. 请求体格式是否正确
2. 必填字段是否都提供
3. 字段类型是否匹配

### 问题: CORS 错误

确认 `main.py` 中的 CORS 配置:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 性能优化建议

1. **批量请求**: 一次获取多个资源
2. **缓存响应**: 使用 HTTP 缓存头
3. **压缩传输**: 启用 gzip 压缩
4. **超时设置**: 合理设置请求超时

## 安全建议

1. **验证输入**: 始终验证用户输入
2. **限流**: 使用 rate limiting
3. **认证**: 添加 API 密钥或 JWT
4. **HTTPS**: 生产环境使用 HTTPS

## 更多资源

- 完整文档: `API_VERSIONING.md`
- 实现总结: `IMPLEMENTATION_SUMMARY.md`
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

---

**最后更新**: 2026-01-08
