# HelloAgents Platform API 文档

完整的后端 API 参考文档，适用于前端开发和第三方集成。

**Base URL**: `https://helloagents-platform.onrender.com`

**开发环境**: `http://localhost:8000`

**API 版本**: v1

**文档更新时间**: 2026-01-09

---

## 目录

- [认证说明](#认证说明)
- [通用响应格式](#通用响应格式)
- [错误码说明](#错误码说明)
- [API 端点](#api-端点)
  - [健康检查](#健康检查)
  - [版本信息](#版本信息)
  - [课程管理](#课程管理)
  - [代码执行](#代码执行)
  - [AI 聊天助手](#ai-聊天助手)
  - [沙箱管理](#沙箱管理)
  - [用户管理](#用户管理)
  - [学习进度](#学习进度)
  - [代码提交记录](#代码提交记录)
- [速率限制](#速率限制)
- [最佳实践](#最佳实践)

---

## 认证说明

当前版本的 API **暂不需要认证**。

未来版本将支持：
- JWT Token 认证
- API Key 认证

认证方式（计划中）：
```http
Authorization: Bearer YOUR_JWT_TOKEN
```

或

```http
X-API-Key: YOUR_API_KEY
```

---

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "path": "/api/v1/...",
    "timestamp": 1704844800.123,
    "details": {
      "validation_errors": [...]
    }
  }
}
```

---

## 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| `VALIDATION_ERROR` | 422 | 请求参数验证失败 |
| `HTTP_404` | 404 | 资源不存在 |
| `HTTP_500` | 500 | 服务器内部错误 |
| `TIMEOUT_ERROR` | 408 | 请求超时 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超出速率限制 |

---

## API 端点

### 健康检查

#### GET /

根端点 - 健康检查

**响应示例**:
```json
{
  "status": "ok",
  "message": "HelloAgents Learning Platform API",
  "version": "1.0.0",
  "timestamp": "2026-01-09T12:00:00.000000"
}
```

#### GET /health

详细健康检查端点

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-09T12:00:00.000000"
}
```

---

### 版本信息

#### GET /api/version

获取所有支持的 API 版本信息

**响应示例**:
```json
{
  "current_version": "v1",
  "supported_versions": ["v1"],
  "deprecated_versions": [],
  "latest_version": "v1"
}
```

---

### 课程管理

#### GET /api/v1/lessons

获取所有课程列表

**响应示例**:
```json
{
  "success": true,
  "lessons": [
    {
      "id": "1",
      "title": "第一章 初识智能体",
      "description": "了解 AI Agent 的基本概念",
      "type": "chapter",
      "children": []
    },
    {
      "id": "4",
      "title": "第四章 智能体经典范式构建",
      "type": "chapter",
      "children": [
        {
          "id": "4.1",
          "title": "4.1 ReAct Agent",
          "description": "实现 Reasoning + Acting 范式",
          "type": "lesson"
        }
      ]
    }
  ]
}
```

**字段说明**:
- `id`: 课程ID（字符串类型，如 "1", "4.1"）
- `title`: 课程标题
- `description`: 课程描述
- `type`: 课程类型（"chapter" 或 "lesson"）
- `children`: 子课程列表（仅章节有）

---

#### GET /api/v1/lessons/{lesson_id}

获取指定课程的完整内容

**路径参数**:
- `lesson_id` (string, 必需): 课程ID，如 "1", "2", "4.1"

**响应示例**:
```json
{
  "lesson_id": "4.1",
  "title": "4.1 ReAct Agent",
  "content": "# ReAct Agent\n\nReAct 是一种结合推理（Reasoning）和行动（Acting）的 Agent 范式...",
  "code_template": "class ReActAgent:\n    def __init__(self, llm_client, tool_executor):\n        pass"
}
```

**字段说明**:
- `lesson_id`: 课程ID
- `title`: 课程标题
- `content`: Markdown 格式的课程内容
- `code_template`: 初始代码模板

**错误响应**:
```json
{
  "error": {
    "code": "HTTP_404",
    "message": "课程 99 不存在",
    "path": "/api/v1/lessons/99",
    "timestamp": 1704844800.123
  }
}
```

---

### 代码执行

#### POST /api/v1/code/execute

在安全沙箱环境中执行用户代码

**请求体**:
```json
{
  "code": "print('Hello, Agent!')",
  "language": "python",
  "timeout": 30
}
```

**请求参数**:
- `code` (string, 必需): 要执行的代码
- `language` (string, 可选): 编程语言，默认 "python"
- `timeout` (integer, 可选): 超时时间（秒），范围 1-60，默认 30

**响应示例（成功）**:
```json
{
  "success": true,
  "output": "Hello, Agent!\n",
  "error": null,
  "execution_time": 0.123
}
```

**响应示例（代码错误）**:
```json
{
  "success": false,
  "output": "",
  "error": "NameError: name 'undefined_var' is not defined",
  "execution_time": 0.05
}
```

**字段说明**:
- `success`: 执行是否成功
- `output`: 标准输出（成功时）
- `error`: 错误信息（失败时）
- `execution_time`: 执行时间（秒）

**使用示例（JavaScript）**:
```javascript
const response = await fetch('https://helloagents-platform.onrender.com/api/v1/code/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    code: 'print("Hello, Agent!")',
    language: 'python',
    timeout: 30
  })
});

const result = await response.json();
console.log(result);
```

**使用示例（Python）**:
```python
import requests

response = requests.post(
    'https://helloagents-platform.onrender.com/api/v1/code/execute',
    json={
        'code': 'print("Hello, Agent!")',
        'language': 'python',
        'timeout': 30
    }
)

result = response.json()
print(result)
```

**使用示例（cURL）**:
```bash
curl -X POST "https://helloagents-platform.onrender.com/api/v1/code/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, Agent!\")",
    "language": "python",
    "timeout": 30
  }'
```

---

#### POST /api/v1/code/hint

获取 AI 智能编程提示（基于光标位置）

**请求体**:
```json
{
  "code": "class ReActAgent:\n    def __init__(self",
  "cursor_line": 2,
  "cursor_column": 18,
  "language": "python"
}
```

**请求参数**:
- `code` (string, 必需): 当前代码
- `cursor_line` (integer, 必需): 光标所在行号（从1开始）
- `cursor_column` (integer, 必需): 光标所在列号（从0开始）
- `language` (string, 可选): 编程语言，默认 "python"

**响应示例**:
```json
{
  "current_context": "ReActAgent.__init__() 初始化方法",
  "hint": "你正在编写 ReAct Agent 的初始化方法。需要接收 llm_client 和 tool_executor 两个参数，分别代表大脑（推理）和手脚（执行）。",
  "reference_code": "def __init__(self, llm_client, tool_executor):\n    self.llm_client = llm_client\n    self.tool_executor = tool_executor\n    self.history = []\n    self.max_steps = 5",
  "key_concepts": [
    "llm_client: LLM 客户端，负责推理和决策",
    "tool_executor: 工具执行器，负责执行具体操作",
    "history: 记录执行历史",
    "max_steps: 防止无限循环"
  ]
}
```

**字段说明**:
- `current_context`: 当前位置上下文描述
- `hint`: 智能提示内容
- `reference_code`: 参考代码（可选）
- `key_concepts`: 关键概念列表

---

### AI 聊天助手

#### POST /api/v1/chat

与 AI 学习助手进行对话

**请求体**:
```json
{
  "message": "什么是 ReAct Agent？",
  "conversation_history": [
    {
      "role": "user",
      "content": "我想学习 Agent 开发"
    },
    {
      "role": "assistant",
      "content": "很高兴帮助你学习 Agent 开发！让我们从基础开始..."
    }
  ],
  "lesson_id": "4.1",
  "code": "class ReActAgent:\n    pass"
}
```

**请求参数**:
- `message` (string, 必需): 用户消息（至少1个字符）
- `conversation_history` (array, 可选): 对话历史（最多保留最近10轮）
  - `role`: 消息角色（"user" 或 "assistant"）
  - `content`: 消息内容
- `lesson_id` (string, 可选): 当前课程ID（用于提供上下文）
- `code` (string, 可选): 当前代码（用于提供上下文）

**响应示例**:
```json
{
  "message": "ReAct Agent 是一种结合推理（Reasoning）和行动（Acting）的智能体范式。它的核心思想是让 AI 边思考边执行，通过 Thought-Action-Observation 循环来解决问题...",
  "success": true
}
```

**响应示例（失败）**:
```json
{
  "message": "抱歉，AI 助手暂时无法回复。请稍后再试。",
  "success": false
}
```

**字段说明**:
- `message`: AI 助手的回复
- `success`: 请求是否成功

**注意事项**:
- AI 助手需要配置 `DEEPSEEK_API_KEY` 环境变量
- 对话历史会自动截取最近10轮，避免上下文过长
- 提供 `lesson_id` 和 `code` 可以让 AI 提供更精准的回答

---

### 沙箱管理

#### GET /api/v1/sandbox/pool/stats

获取容器池统计信息

**响应示例（容器池启用）**:
```json
{
  "pool_enabled": true,
  "available_containers": 3,
  "in_use_containers": 2,
  "total_executions": 156,
  "timestamp": "2026-01-09T12:00:00.000000",
  "message": null
}
```

**响应示例（容器池未启用）**:
```json
{
  "pool_enabled": false,
  "available_containers": null,
  "in_use_containers": null,
  "total_executions": null,
  "timestamp": "2026-01-09T12:00:00.000000",
  "message": "Container pool is not enabled"
}
```

**字段说明**:
- `pool_enabled`: 容器池是否启用
- `available_containers`: 可用容器数量
- `in_use_containers`: 使用中的容器数量
- `total_executions`: 总执行次数
- `timestamp`: 统计时间戳（ISO 8601 格式）
- `message`: 附加信息

---

### 用户管理

#### POST /api/users

创建新用户

**请求体**:
```json
{
  "username": "student001",
  "email": "student@example.com",
  "password": "SecurePass123!"
}
```

**响应示例**:
```json
{
  "id": 1,
  "username": "student001",
  "email": "student@example.com",
  "created_at": "2026-01-09T12:00:00.000000"
}
```

---

#### GET /api/users/{user_id}

获取用户信息

**路径参数**:
- `user_id` (integer, 必需): 用户ID

**响应示例**:
```json
{
  "id": 1,
  "username": "student001",
  "email": "student@example.com",
  "created_at": "2026-01-09T12:00:00.000000"
}
```

---

### 学习进度

#### GET /api/progress/{user_id}

获取用户的学习进度

**路径参数**:
- `user_id` (integer, 必需): 用户ID

**响应示例**:
```json
{
  "user_id": 1,
  "completed_lessons": ["1", "2", "3", "4.1"],
  "current_lesson": "4.2",
  "total_lessons": 50,
  "completion_percentage": 8.0
}
```

---

#### POST /api/progress/{user_id}

更新用户学习进度

**路径参数**:
- `user_id` (integer, 必需): 用户ID

**请求体**:
```json
{
  "lesson_id": "4.1",
  "status": "completed"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "学习进度已更新"
}
```

---

### 代码提交记录

#### GET /api/submissions/{user_id}

获取用户的代码提交记录

**路径参数**:
- `user_id` (integer, 必需): 用户ID

**查询参数**:
- `lesson_id` (string, 可选): 课程ID（筛选特定课程的提交）
- `limit` (integer, 可选): 返回记录数量，默认 20
- `offset` (integer, 可选): 偏移量，默认 0

**响应示例**:
```json
{
  "total": 45,
  "submissions": [
    {
      "id": 123,
      "user_id": 1,
      "lesson_id": "4.1",
      "code": "class ReActAgent:\n    ...",
      "status": "success",
      "output": "测试通过\n",
      "execution_time": 0.234,
      "created_at": "2026-01-09T11:30:00.000000"
    }
  ]
}
```

---

#### POST /api/submissions

提交代码

**请求体**:
```json
{
  "user_id": 1,
  "lesson_id": "4.1",
  "code": "class ReActAgent:\n    def __init__(self, llm_client, tool_executor):\n        self.llm_client = llm_client\n        self.tool_executor = tool_executor"
}
```

**响应示例**:
```json
{
  "id": 124,
  "user_id": 1,
  "lesson_id": "4.1",
  "status": "success",
  "output": "代码执行成功\n",
  "execution_time": 0.156,
  "created_at": "2026-01-09T12:00:00.000000"
}
```

---

## 速率限制

当前版本**暂无速率限制**。

未来版本将实施：
- 每个 IP 地址：100 请求/分钟
- 每个用户：1000 请求/小时
- 代码执行：20 次/分钟

超出限制时返回：
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "超出速率限制，请稍后再试",
    "retry_after": 60
  }
}
```

---

## 最佳实践

### 1. 错误处理

始终检查响应的 `success` 字段或 HTTP 状态码：

```javascript
async function executeCode(code) {
  try {
    const response = await fetch('/api/v1/code/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('API错误:', error);
      return null;
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('网络错误:', error);
    return null;
  }
}
```

### 2. 超时设置

为网络请求设置合理的超时时间：

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 35000); // 35秒超时

fetch('/api/v1/code/execute', {
  method: 'POST',
  signal: controller.signal,
  body: JSON.stringify({ code, timeout: 30 })
})
  .finally(() => clearTimeout(timeoutId));
```

### 3. 对话历史管理

限制对话历史长度，避免上下文过长：

```javascript
function trimConversationHistory(history, maxLength = 10) {
  return history.slice(-maxLength);
}

const history = trimConversationHistory(conversationHistory);
```

### 4. 代码安全

用户代码在 Docker 容器中隔离执行，但仍需注意：
- 不要执行不受信任的代码
- 设置合理的超时时间
- 监控执行时间和资源使用

### 5. API 版本管理

始终使用版本化的 API 端点（`/api/v1/...`），避免使用向后兼容端点（`/api/...`），因为它们可能在未来版本中被移除。

---

## 联系与反馈

- **GitHub Issues**: [https://github.com/ai520510xyf-del/helloagents-platform/issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)
- **API文档**: [https://helloagents-platform.onrender.com/api/v1/docs](https://helloagents-platform.onrender.com/api/v1/docs)
- **项目主页**: [https://github.com/ai520510xyf-del/helloagents-platform](https://github.com/ai520510xyf-del/helloagents-platform)

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-09
