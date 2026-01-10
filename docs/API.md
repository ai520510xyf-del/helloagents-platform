# API 参考文档

**HelloAgents 学习平台 REST API v1**

本文档提供完整的 API 接口说明和示例，帮助开发者快速集成和使用平台功能。

---

## 📋 目录

- [基础信息](#基础信息)
- [认证与授权](#认证与授权)
- [通用响应格式](#通用响应格式)
- [错误处理](#错误处理)
- [API 端点](#api-端点)
  - [健康检查](#健康检查)
  - [代码执行](#代码执行)
  - [课程管理](#课程管理)
  - [AI 助手](#ai-助手)
  - [沙箱管理](#沙箱管理)
  - [用户管理](#用户管理)
  - [学习进度](#学习进度)
- [速率限制](#速率限制)
- [Webhook 通知](#webhook-通知)
- [SDK 和客户端库](#sdk-和客户端库)

---

## 基础信息

### Base URL

**生产环境:**
```
https://helloagents-backend.onrender.com
```

**本地开发:**
```
http://localhost:8000
```

### API 版本

当前版本：**v1**

所有 API 端点都使用版本前缀：`/api/v1`

### 内容类型

- **请求**: `application/json`
- **响应**: `application/json`

### 交互式文档

访问以下地址查看自动生成的交互式 API 文档：

- **Swagger UI**: `https://helloagents-backend.onrender.com/api/v1/docs`
- **ReDoc**: `https://helloagents-backend.onrender.com/api/v1/redoc`
- **OpenAPI JSON**: `https://helloagents-backend.onrender.com/api/v1/openapi.json`

---

## 认证与授权

当前版本暂不需要认证，所有端点都可以公开访问。未来版本将支持：

- API Key 认证
- JWT Token 认证
- OAuth 2.0

---

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // 响应数据
  }
}
```

### 错误响应

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "path": "/api/v1/endpoint",
    "timestamp": 1704067200.0,
    "details": {
      // 可选的错误详情
    }
  }
}
```

---

## 错误处理

### HTTP 状态码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| `200` | 请求成功 | 正常处理响应数据 |
| `201` | 资源创建成功 | 正常处理响应数据 |
| `400` | 请求参数错误 | 检查请求参数格式和内容 |
| `401` | 未认证 | 提供有效的认证凭证 |
| `403` | 无权限 | 联系管理员获取权限 |
| `404` | 资源不存在 | 检查资源ID或路径 |
| `422` | 请求验证失败 | 检查请求体中的字段 |
| `429` | 请求过于频繁 | 等待后重试或降低请求频率 |
| `500` | 服务器内部错误 | 联系技术支持 |
| `503` | 服务不可用 | 稍后重试 |

### 错误代码

| 错误代码 | HTTP 状态码 | 说明 |
|---------|-------------|------|
| `VALIDATION_ERROR` | 422 | 请求参数验证失败 |
| `CODE_EXECUTION_ERROR` | 500 | 代码执行失败 |
| `SANDBOX_UNAVAILABLE` | 503 | 沙箱服务不可用 |
| `LESSON_NOT_FOUND` | 404 | 课程不存在 |
| `AI_SERVICE_ERROR` | 500 | AI 服务调用失败 |
| `DATABASE_ERROR` | 500 | 数据库操作失败 |

### 错误响应示例

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "path": "/api/v1/code/execute",
    "timestamp": 1704067200.0,
    "details": {
      "validation_errors": [
        {
          "field": "code",
          "message": "Field required",
          "type": "missing"
        }
      ]
    }
  }
}
```

---

## API 端点

### 健康检查

#### 完整健康检查

检查所有系统组件的健康状态。

**请求:**

```http
GET /health
```

**响应:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "sandbox_pool": {
      "status": "healthy",
      "available_containers": 5,
      "in_use_containers": 2
    },
    "ai_service": {
      "status": "configured",
      "message": "AI service API key is configured"
    }
  }
}
```

#### 就绪检查（Readiness Probe）

检查应用是否准备好接收流量。

**请求:**

```http
GET /health/ready
```

**响应:**

```json
{
  "status": "ready",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### 存活检查（Liveness Probe）

检查应用是否还在运行。

**请求:**

```http
GET /health/live
```

**响应:**

```json
{
  "status": "alive",
  "timestamp": "2024-01-01T00:00:00"
}
```

---

### 代码执行

#### 执行代码

在安全沙箱环境中执行 Python 代码。

**请求:**

```http
POST /api/v1/code/execute
Content-Type: application/json
```

**请求体:**

```json
{
  "code": "print('Hello, World!')",
  "language": "python",
  "timeout": 30
}
```

**参数说明:**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `code` | string | 是 | - | 要执行的代码 |
| `language` | string | 否 | `"python"` | 编程语言（当前仅支持 python） |
| `timeout` | integer | 否 | `30` | 超时时间（1-60秒） |

**响应:**

```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "execution_time": 0.123
}
```

**错误示例:**

```json
{
  "success": false,
  "output": "",
  "error": "SyntaxError: invalid syntax",
  "execution_time": 0.001
}
```

**示例代码:**

```bash
# cURL
curl -X POST "https://helloagents-backend.onrender.com/api/v1/code/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "language": "python",
    "timeout": 30
  }'
```

```javascript
// JavaScript (Fetch API)
const response = await fetch('https://helloagents-backend.onrender.com/api/v1/code/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    code: 'print("Hello, World!")',
    language: 'python',
    timeout: 30
  })
});

const result = await response.json();
console.log(result);
```

```python
# Python (requests)
import requests

response = requests.post(
    'https://helloagents-backend.onrender.com/api/v1/code/execute',
    json={
        'code': 'print("Hello, World!")',
        'language': 'python',
        'timeout': 30
    }
)

result = response.json()
print(result)
```

#### 获取 AI 智能提示

根据当前代码和光标位置，提供实时的编程提示。

**请求:**

```http
POST /api/v1/code/hint
Content-Type: application/json
```

**请求体:**

```json
{
  "code": "class ReActAgent:\n    def __init__(self,",
  "cursor_line": 2,
  "cursor_column": 20,
  "language": "python"
}
```

**参数说明:**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `code` | string | 是 | 当前代码 |
| `cursor_line` | integer | 是 | 光标所在行号（从1开始） |
| `cursor_column` | integer | 是 | 光标所在列号（从0开始） |
| `language` | string | 否 | 编程语言（默认 python） |

**响应:**

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

---

### 课程管理

#### 获取所有课程列表

获取完整的课程目录结构。

**请求:**

```http
GET /api/v1/lessons
```

**响应:**

```json
{
  "success": true,
  "lessons": [
    {
      "id": "1",
      "title": "Agent 是什么？",
      "description": "理解 AI Agent 的基本概念",
      "difficulty": "beginner",
      "duration": "10分钟"
    },
    {
      "id": "2",
      "title": "ReAct Agent",
      "description": "学习 ReAct (Reasoning + Acting) 范式",
      "difficulty": "beginner",
      "duration": "20分钟"
    }
  ]
}
```

**示例代码:**

```bash
# cURL
curl "https://helloagents-backend.onrender.com/api/v1/lessons"
```

```javascript
// JavaScript
const response = await fetch('https://helloagents-backend.onrender.com/api/v1/lessons');
const data = await response.json();
console.log(data.lessons);
```

#### 获取课程内容

获取指定课程的完整内容。

**请求:**

```http
GET /api/v1/lessons/{lesson_id}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `lesson_id` | string | 课程ID，如 "1", "2", "4.1" |

**响应:**

```json
{
  "lesson_id": "1",
  "title": "Agent 是什么？",
  "content": "# Agent 是什么？\n\n## 概念介绍\n\nAI Agent 是...",
  "code_template": "# 课程代码模板\nclass Agent:\n    pass\n"
}
```

**错误响应（404）:**

```json
{
  "error": {
    "code": "LESSON_NOT_FOUND",
    "message": "课程 999 不存在",
    "path": "/api/v1/lessons/999",
    "timestamp": 1704067200.0
  }
}
```

**示例代码:**

```bash
# cURL
curl "https://helloagents-backend.onrender.com/api/v1/lessons/1"
```

```javascript
// JavaScript
const lessonId = '1';
const response = await fetch(`https://helloagents-backend.onrender.com/api/v1/lessons/${lessonId}`);
const lesson = await response.json();
console.log(lesson.content);
```

---

### AI 助手

#### 与 AI 助手聊天

与 AI 学习助手进行对话，获取学习支持。

**请求:**

```http
POST /api/v1/chat
Content-Type: application/json
```

**请求体:**

```json
{
  "message": "什么是 ReAct Agent？",
  "conversation_history": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "你好！我是 HelloAgents 学习助手，有什么可以帮你的吗？"
    }
  ],
  "lesson_id": "2",
  "code": "class ReActAgent:\n    pass"
}
```

**参数说明:**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 用户消息 |
| `conversation_history` | array | 否 | 对话历史（最多保留最近10轮） |
| `lesson_id` | string | 否 | 当前课程ID（用于提供上下文） |
| `code` | string | 否 | 当前代码（用于提供上下文） |

**响应:**

```json
{
  "message": "ReAct (Reasoning + Acting) 是一种结合推理和行动的 Agent 范式。它的核心思想是让 AI 边思考边执行，通过 Thought-Action-Observation 循环来解决问题。\n\n简单来说：\n1. **Thought（思考）**: AI 分析问题，决定下一步做什么\n2. **Action（行动）**: 执行具体的工具或操作\n3. **Observation（观察）**: 观察执行结果，为下一轮思考提供信息\n\n这个循环会持续进行，直到问题解决为止。",
  "success": true
}
```

**错误响应:**

```json
{
  "message": "抱歉，AI 助手暂时无法回复。请稍后再试。",
  "success": false
}
```

**示例代码:**

```bash
# cURL
curl -X POST "https://helloagents-backend.onrender.com/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "什么是 ReAct Agent？",
    "lesson_id": "2"
  }'
```

```javascript
// JavaScript
const response = await fetch('https://helloagents-backend.onrender.com/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '什么是 ReAct Agent？',
    conversation_history: [],
    lesson_id: '2'
  })
});

const result = await response.json();
console.log(result.message);
```

---

### 沙箱管理

#### 获取容器池统计信息

查看容器池的当前状态、性能指标和容器详情。

**请求:**

```http
GET /api/v1/sandbox/pool/stats
```

**响应:**

```json
{
  "pool_enabled": true,
  "timestamp": "2024-01-01T00:00:00",
  "available_containers": 5,
  "in_use_containers": 2,
  "total_executions": 1234,
  "avg_execution_time": 0.456,
  "containers": [
    {
      "id": "abc123",
      "status": "available",
      "created_at": "2024-01-01T00:00:00",
      "last_used": "2024-01-01T12:00:00",
      "total_executions": 45
    }
  ]
}
```

**示例代码:**

```bash
# cURL
curl "https://helloagents-backend.onrender.com/api/v1/sandbox/pool/stats"
```

---

### 用户管理

#### 创建用户

创建新的本地用户配置。

**请求:**

```http
POST /api/users
Content-Type: application/json
```

**请求体:**

```json
{
  "username": "learner123",
  "full_name": "张三",
  "settings": {
    "theme": "dark",
    "language": "zh-CN"
  }
}
```

**响应:**

```json
{
  "id": 1,
  "username": "learner123",
  "full_name": "张三",
  "settings": {
    "theme": "dark",
    "language": "zh-CN"
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "last_login": null
}
```

#### 获取用户信息

获取指定用户的详细信息。

**请求:**

```http
GET /api/users/{user_id}
```

**响应:**

```json
{
  "id": 1,
  "username": "learner123",
  "full_name": "张三",
  "settings": {
    "theme": "dark",
    "language": "zh-CN"
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "last_login": "2024-01-01T12:00:00"
}
```

---

### 学习进度

#### 更新学习进度

记录用户的课程学习进度。

**请求:**

```http
POST /api/progress
Content-Type: application/json
```

**请求体:**

```json
{
  "user_id": 1,
  "lesson_id": 2,
  "status": "completed",
  "score": 95
}
```

**参数说明:**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `user_id` | integer | 是 | 用户ID |
| `lesson_id` | integer | 是 | 课程ID |
| `status` | string | 是 | 状态：`started`, `in_progress`, `completed` |
| `score` | integer | 否 | 分数（0-100） |

**响应:**

```json
{
  "id": 1,
  "user_id": 1,
  "lesson_id": 2,
  "status": "completed",
  "score": 95,
  "started_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T12:00:00"
}
```

#### 获取用户进度

查询用户的学习进度记录。

**请求:**

```http
GET /api/progress/{user_id}
```

**响应:**

```json
{
  "user_id": 1,
  "total_lessons": 10,
  "completed_lessons": 5,
  "in_progress_lessons": 2,
  "progress": [
    {
      "lesson_id": 1,
      "lesson_title": "Agent 是什么？",
      "status": "completed",
      "score": 90,
      "completed_at": "2024-01-01T10:00:00"
    },
    {
      "lesson_id": 2,
      "lesson_title": "ReAct Agent",
      "status": "in_progress",
      "score": null,
      "started_at": "2024-01-01T12:00:00"
    }
  ]
}
```

---

## 速率限制

当前版本暂无速率限制。未来版本计划实施：

- **默认限制**: 100 请求/分钟
- **代码执行**: 20 请求/分钟
- **AI 聊天**: 10 请求/分钟

超出限制时，API 将返回 `429 Too Many Requests` 状态码。

**响应头:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1704067260
```

---

## Webhook 通知

未来版本将支持 Webhook，允许在特定事件发生时接收通知：

- 代码执行完成
- 课程完成
- AI 助手回复

---

## SDK 和客户端库

### 官方 SDK

**JavaScript/TypeScript:**
```bash
npm install @helloagents/sdk
```

**Python:**
```bash
pip install helloagents-sdk
```

### 社区库

- **Go**: `github.com/community/helloagents-go`
- **Ruby**: `gem install helloagents-ruby`

---

## 版本历史

### v1.0.0 (2024-01-01)

- 初始版本发布
- 代码执行沙箱
- 课程管理
- AI 助手聊天
- 用户和进度管理

---

## 支持与反馈

- **文档问题**: [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)
- **API 问题**: [技术支持](mailto:support@helloagents.dev)
- **讨论社区**: [GitHub Discussions](https://github.com/ai520510xyf-del/helloagents-platform/discussions)

---

**最后更新**: 2024-01-09 | **API 版本**: v1.0.0
