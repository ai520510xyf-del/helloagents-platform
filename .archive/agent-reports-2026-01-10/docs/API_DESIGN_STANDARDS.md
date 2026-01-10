# HelloAgents Platform - RESTful API 设计规范

**版本**: 1.0.0
**生效日期**: 2026-01-10
**所有权**: API Architect Team

---

## 目录

1. [设计原则](#1-设计原则)
2. [URL 设计规范](#2-url-设计规范)
3. [HTTP 方法使用](#3-http-方法使用)
4. [请求格式](#4-请求格式)
5. [响应格式](#5-响应格式)
6. [错误处理](#6-错误处理)
7. [分页和过滤](#7-分页和过滤)
8. [版本管理](#8-版本管理)
9. [安全和认证](#9-安全和认证)
10. [性能优化](#10-性能优化)

---

## 1. 设计原则

### 1.1 核心原则

**1. 一致性优先**
- 所有 API 端点遵循统一的命名规范
- 响应格式保持一致
- 错误处理标准化

**2. 开发者友好**
- 清晰的命名（见名知意）
- 完整的 API 文档
- 详细的错误消息

**3. 可扩展性**
- 支持版本管理
- 支持字段选择和扩展
- 预留扩展字段

**4. 安全第一**
- 输入验证
- 速率限制
- 敏感信息保护

### 1.2 RESTful 成熟度模型

HelloAgents Platform API 目标达到 **Level 2**（HTTP 动词和状态码），并逐步向 **Level 3**（HATEOAS）演进。

```
Level 0: 单一 URI，单一 HTTP 方法 (RPC)
Level 1: 多个 URI，单一 HTTP 方法
Level 2: 多个 URI，多个 HTTP 方法 + 状态码 ✅ 当前目标
Level 3: 超媒体控制 (HATEOAS) 🎯 未来目标
```

---

## 2. URL 设计规范

### 2.1 基本规则

#### **规则 1: 使用名词，避免动词**

```
✅ 正确
GET    /api/v1/users
GET    /api/v1/users/123
POST   /api/v1/users
PUT    /api/v1/users/123
DELETE /api/v1/users/123

❌ 错误
GET    /api/v1/getUsers
POST   /api/v1/createUser
POST   /api/v1/users/123/delete
```

#### **规则 2: 使用复数名词**

```
✅ 正确
/api/v1/users
/api/v1/lessons
/api/v1/submissions

❌ 错误
/api/v1/user
/api/v1/lesson
/api/v1/submission
```

#### **规则 3: 使用小写和连字符（kebab-case）**

```
✅ 正确
/api/v1/code-submissions
/api/v1/user-progress
/api/v1/chat-messages

❌ 错误
/api/v1/CodeSubmissions    # 大写
/api/v1/code_submissions   # 下划线
/api/v1/codesubmissions    # 难以阅读
```

#### **规则 4: 嵌套资源限制在 2 层**

```
✅ 正确
/api/v1/users/123/submissions
/api/v1/lessons/1/comments

✅ 可接受（特殊情况）
/api/v1/users/123/submissions/456/reviews

❌ 避免（嵌套过深）
/api/v1/courses/1/lessons/2/exercises/3/submissions/4/comments
```

超过 2 层嵌套时，考虑使用查询参数：

```
✅ 替代方案
/api/v1/comments?lesson_id=2&exercise_id=3
```

### 2.2 资源命名示例

#### **2.2.1 课程相关**

```
GET    /api/v1/lessons              # 课程列表
GET    /api/v1/lessons/1            # 课程详情
POST   /api/v1/lessons              # 创建课程（管理员）
PUT    /api/v1/lessons/1            # 更新课程
DELETE /api/v1/lessons/1            # 删除课程
GET    /api/v1/lessons/1/progress   # 课程学习进度
```

#### **2.2.2 代码执行**

```
POST   /api/v1/code/execute         # 执行代码
POST   /api/v1/code/hint            # 获取 AI 提示
GET    /api/v1/code/executions      # 执行历史
GET    /api/v1/code/executions/123  # 执行详情
```

#### **2.2.3 用户相关**

```
GET    /api/v1/users                # 用户列表
GET    /api/v1/users/123            # 用户详情
GET    /api/v1/users/current        # 当前用户
PUT    /api/v1/users/123            # 更新用户
DELETE /api/v1/users/123            # 删除用户
GET    /api/v1/users/123/progress   # 用户学习进度
GET    /api/v1/users/123/submissions # 用户提交记录
```

#### **2.2.4 AI 聊天**

```
POST   /api/v1/chat                 # 发送消息
GET    /api/v1/chat/history         # 聊天历史
DELETE /api/v1/chat/history         # 清空历史
```

### 2.3 特殊动作端点

对于不符合 CRUD 的操作，可以使用动词：

```
✅ 特殊动作（在资源后添加动作）
POST   /api/v1/users/123/login      # 用户登录
POST   /api/v1/users/123/logout     # 用户登出
POST   /api/v1/code/execute         # 执行代码
POST   /api/v1/lessons/1/complete   # 完成课程
POST   /api/v1/sandbox/restart      # 重启沙箱
```

### 2.4 URL 示例总结

```
# 资源 URL 模式
/api/{version}/{resource}              # 资源集合
/api/{version}/{resource}/{id}         # 单个资源
/api/{version}/{resource}/{id}/{action} # 资源动作
/api/{version}/{resource}/{id}/{sub-resource} # 子资源

# 实际示例
/api/v1/lessons                        # 课程列表
/api/v1/lessons/1                      # 课程详情
/api/v1/lessons/1/complete             # 完成课程
/api/v1/users/123/submissions          # 用户提交记录
```

---

## 3. HTTP 方法使用

### 3.1 标准 CRUD 操作

| HTTP 方法 | 操作 | 幂等性 | 安全性 | 示例 |
|-----------|------|--------|--------|------|
| `GET` | 读取 | ✅ 是 | ✅ 是 | 获取资源 |
| `POST` | 创建 | ❌ 否 | ❌ 否 | 创建资源 |
| `PUT` | 完整更新 | ✅ 是 | ❌ 否 | 替换资源 |
| `PATCH` | 部分更新 | ❌ 否 | ❌ 否 | 更新部分字段 |
| `DELETE` | 删除 | ✅ 是 | ❌ 否 | 删除资源 |

**幂等性**: 多次相同请求的结果与单次请求相同
**安全性**: 不修改资源状态

### 3.2 GET - 查询资源

**用途**: 获取资源信息，不修改服务器状态

```http
# 获取资源列表
GET /api/v1/lessons HTTP/1.1
Accept: application/json

# 获取单个资源
GET /api/v1/lessons/1 HTTP/1.1
Accept: application/json

# 带查询参数
GET /api/v1/lessons?page=1&limit=20&difficulty=beginner HTTP/1.1
Accept: application/json
```

**规范**:
- ✅ 使用查询参数过滤、分页、排序
- ✅ 支持缓存（ETag, Last-Modified）
- ❌ 不要在 GET 请求中修改数据
- ❌ 不要使用请求体（body）

### 3.3 POST - 创建资源

**用途**: 创建新资源或执行非幂等操作

```http
# 创建用户
POST /api/v1/users HTTP/1.1
Content-Type: application/json

{
  "username": "alice",
  "full_name": "Alice Wang",
  "email": "alice@example.com"
}

# 响应
HTTP/1.1 201 Created
Location: /api/v1/users/123
Content-Type: application/json

{
  "data": {
    "id": 123,
    "username": "alice",
    "full_name": "Alice Wang",
    "email": "alice@example.com",
    "created_at": "2024-01-09T10:00:00Z"
  }
}
```

**规范**:
- ✅ 成功创建返回 `201 Created`
- ✅ 响应头包含 `Location` 指向新资源
- ✅ 响应体包含完整的资源对象
- ❌ 不是幂等操作（多次调用创建多个资源）

### 3.4 PUT - 完整更新资源

**用途**: 替换整个资源

```http
# 完整更新用户
PUT /api/v1/users/123 HTTP/1.1
Content-Type: application/json

{
  "username": "alice",
  "full_name": "Alice Wang (Updated)",
  "email": "alice.new@example.com",
  "settings": {"theme": "dark"}
}

# 响应
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": {
    "id": 123,
    "username": "alice",
    "full_name": "Alice Wang (Updated)",
    "email": "alice.new@example.com",
    "settings": {"theme": "dark"},
    "updated_at": "2024-01-09T11:00:00Z"
  }
}
```

**规范**:
- ✅ 必须提供资源的所有字段
- ✅ 幂等操作（多次相同请求结果相同）
- ✅ 成功返回 `200 OK` 或 `204 No Content`
- ⚠️ 缺失字段将被删除或重置为默认值

### 3.5 PATCH - 部分更新资源

**用途**: 只更新资源的部分字段

```http
# 部分更新用户
PATCH /api/v1/users/123 HTTP/1.1
Content-Type: application/json

{
  "full_name": "Alice Wang (Patched)"
}

# 响应
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": {
    "id": 123,
    "username": "alice",  # 未修改
    "full_name": "Alice Wang (Patched)",  # 已修改
    "email": "alice@example.com",  # 未修改
    "updated_at": "2024-01-09T12:00:00Z"
  }
}
```

**规范**:
- ✅ 只需提供要更新的字段
- ✅ 未提供的字段保持不变
- ✅ 成功返回 `200 OK`
- ⚠️ 不完全幂等（取决于实现）

### 3.6 DELETE - 删除资源

**用途**: 删除指定资源

```http
# 删除用户
DELETE /api/v1/users/123 HTTP/1.1

# 响应
HTTP/1.1 204 No Content
```

**规范**:
- ✅ 成功删除返回 `204 No Content`（无响应体）
- ✅ 或返回 `200 OK` + 被删除的资源信息
- ✅ 幂等操作（多次删除同一资源返回相同结果）
- ✅ 资源不存在时返回 `404 Not Found`

```http
# 删除不存在的资源
DELETE /api/v1/users/999 HTTP/1.1

# 响应
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User not found: 999"
  }
}
```

---

## 4. 请求格式

### 4.1 Content-Type

**推荐使用**:
```
Content-Type: application/json
```

**特殊场景**:
```
Content-Type: multipart/form-data    # 文件上传
Content-Type: application/x-www-form-urlencoded  # 表单提交
```

### 4.2 请求头规范

#### **必需头部**

```http
POST /api/v1/users HTTP/1.1
Content-Type: application/json         # 必需
Accept: application/json                # 推荐
Content-Length: 123                     # 自动添加
```

#### **可选头部**

```http
Authorization: Bearer <token>           # 认证（未来）
X-Request-ID: req_abc123                # 请求追踪
X-API-Version: 1                        # 版本选择（备用方案）
User-Agent: HelloAgents-Web/1.0         # 客户端标识
```

### 4.3 查询参数规范

#### **命名规范**

```
✅ 使用 snake_case
?page=1&limit=20&sort_by=created_at&order=desc

❌ 避免 camelCase
?pageNumber=1&itemsPerPage=20
```

#### **常用查询参数**

```
# 分页
?page=1&limit=20              # 页码分页
?offset=0&limit=20            # 偏移分页

# 排序
?sort=created_at&order=desc   # 单字段排序
?sort=created_at:desc,title:asc  # 多字段排序

# 过滤
?status=published             # 简单过滤
?filter[status]=published&filter[difficulty]=beginner  # 复杂过滤

# 搜索
?search=agent                 # 全文搜索
?q=react+agent                # URL 编码搜索

# 字段选择
?fields=id,title,created_at   # 只返回指定字段

# 关系扩展
?expand=author,comments       # 扩展关联资源
```

### 4.4 请求体规范

#### **JSON 格式**

```json
{
  "username": "alice",
  "full_name": "Alice Wang",
  "settings": {
    "theme": "dark",
    "language": "zh-CN"
  },
  "tags": ["developer", "python"]
}
```

**规范**:
- ✅ 使用 `snake_case` 字段命名
- ✅ 避免嵌套过深（最多 3 层）
- ✅ 必填字段明确标注
- ✅ 提供字段验证规则

#### **Pydantic 模型示例**

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List

class UserSettings(BaseModel):
    theme: str = Field(default="light", regex="^(light|dark)$")
    language: str = Field(default="zh-CN")

class UserCreateRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        regex="^[a-zA-Z0-9_]+$",
        description="用户名（3-50字符，只能包含字母、数字、下划线）"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="全名（可选）"
    )
    email: str = Field(
        ...,
        regex="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
        description="邮箱地址"
    )
    settings: Optional[UserSettings] = Field(
        default_factory=UserSettings,
        description="用户设置"
    )
    tags: List[str] = Field(
        default=[],
        max_items=10,
        description="用户标签（最多10个）"
    )

    @validator('username')
    def username_must_not_be_reserved(cls, v):
        reserved = ['admin', 'root', 'system']
        if v.lower() in reserved:
            raise ValueError('Username is reserved')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "alice",
                "full_name": "Alice Wang",
                "email": "alice@example.com",
                "settings": {
                    "theme": "dark",
                    "language": "zh-CN"
                },
                "tags": ["developer", "python"]
            }
        }
```

---

## 5. 响应格式

### 5.1 统一响应结构

#### **成功响应 (2xx)**

```typescript
interface APIResponse<T> {
  data: T;                    // 实际数据
  meta?: PaginationMeta;      // 分页元数据（可选）
  links?: PaginationLinks;    // 分页链接（可选）
}
```

#### **错误响应 (4xx/5xx)**

```typescript
interface ErrorResponse {
  error: {
    code: string;             // 错误代码
    message: string;          // 人类可读消息
    path: string;             // 请求路径
    timestamp: number;        // 时间戳
    requestId?: string;       // 请求ID（可选）
    details?: object;         // 额外详情（可选）
  };
}
```

### 5.2 成功响应示例

#### **单个资源**

```json
GET /api/v1/lessons/1

{
  "data": {
    "lesson_id": "1",
    "title": "第1章：Agent 基础概念",
    "content": "# Agent 基础概念\n\n什么是 Agent？...",
    "code_template": "class ReActAgent:\n    pass",
    "difficulty": "beginner",
    "duration": 30,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-09T10:00:00Z"
  }
}
```

#### **资源列表（带分页）**

```json
GET /api/v1/lessons?page=1&limit=20

{
  "data": [
    {
      "lesson_id": "1",
      "title": "第1章：Agent 基础概念",
      "difficulty": "beginner",
      "duration": 30
    },
    {
      "lesson_id": "2",
      "title": "第2章：ReAct Agent 实现",
      "difficulty": "intermediate",
      "duration": 45
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "totalPages": 3
  },
  "links": {
    "self": "/api/v1/lessons?page=1&limit=20",
    "first": "/api/v1/lessons?page=1&limit=20",
    "prev": null,
    "next": "/api/v1/lessons?page=2&limit=20",
    "last": "/api/v1/lessons?page=3&limit=20"
  }
}
```

#### **资源创建**

```json
POST /api/v1/users
Status: 201 Created
Location: /api/v1/users/123

{
  "data": {
    "id": 123,
    "username": "alice",
    "full_name": "Alice Wang",
    "email": "alice@example.com",
    "created_at": "2024-01-09T10:00:00Z",
    "updated_at": "2024-01-09T10:00:00Z"
  }
}
```

#### **空响应（删除成功）**

```json
DELETE /api/v1/users/123
Status: 204 No Content
(无响应体)
```

### 5.3 错误响应示例

#### **验证错误 (422)**

```json
POST /api/v1/users
Status: 422 Unprocessable Entity

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "path": "/api/v1/users",
    "timestamp": 1704878400.0,
    "requestId": "req_abc123",
    "details": {
      "validation_errors": [
        {
          "field": "username",
          "message": "Field required",
          "type": "missing"
        },
        {
          "field": "email",
          "message": "Invalid email format",
          "type": "value_error"
        }
      ]
    }
  }
}
```

#### **资源未找到 (404)**

```json
GET /api/v1/lessons/999
Status: 404 Not Found

{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Lesson not found: 999",
    "path": "/api/v1/lessons/999",
    "timestamp": 1704878400.0,
    "details": {
      "resource": "lesson",
      "resource_id": "999"
    }
  }
}
```

#### **速率限制 (429)**

```json
POST /api/v1/code/execute
Status: 429 Too Many Requests
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704878460
Retry-After: 60

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 60 seconds.",
    "path": "/api/v1/code/execute",
    "timestamp": 1704878400.0,
    "details": {
      "limit": 10,
      "window": "1 minute",
      "retry_after": 60
    }
  }
}
```

#### **服务器错误 (500)**

```json
GET /api/v1/lessons
Status: 500 Internal Server Error

{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred",
    "path": "/api/v1/lessons",
    "timestamp": 1704878400.0,
    "requestId": "req_abc123"
  }
}
```

### 5.4 响应头规范

#### **标准响应头**

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 1234
Date: Tue, 09 Jan 2024 10:00:00 GMT
```

#### **分页响应头（备选方案）**

```http
X-Total-Count: 150
X-Page-Count: 8
Link: <https://api.helloagents.com/api/v1/lessons?page=2>; rel="next",
      <https://api.helloagents.com/api/v1/lessons?page=8>; rel="last"
```

#### **速率限制头**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704878460
```

#### **缓存控制头**

```http
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Tue, 09 Jan 2024 09:00:00 GMT
```

---

## 6. 错误处理

### 6.1 HTTP 状态码完整列表

#### **成功 (2xx)**

| 状态码 | 名称 | 使用场景 |
|--------|------|----------|
| 200 | OK | 成功处理请求（GET, PUT, PATCH） |
| 201 | Created | 成功创建资源（POST） |
| 202 | Accepted | 请求已接受，异步处理中 |
| 204 | No Content | 成功处理请求，无返回内容（DELETE） |

#### **客户端错误 (4xx)**

| 状态码 | 名称 | 使用场景 |
|--------|------|----------|
| 400 | Bad Request | 请求格式错误、参数无效 |
| 401 | Unauthorized | 未认证（缺少或无效 Token） |
| 403 | Forbidden | 已认证但无权限 |
| 404 | Not Found | 资源不存在 |
| 405 | Method Not Allowed | HTTP 方法不支持 |
| 409 | Conflict | 资源冲突（如用户名已存在） |
| 422 | Unprocessable Entity | 语义错误、验证失败 |
| 429 | Too Many Requests | 速率限制超出 |

#### **服务端错误 (5xx)**

| 状态码 | 名称 | 使用场景 |
|--------|------|----------|
| 500 | Internal Server Error | 未预期的服务器错误 |
| 502 | Bad Gateway | 外部服务错误（如 AI API） |
| 503 | Service Unavailable | 服务暂时不可用（如容器池耗尽） |
| 504 | Gateway Timeout | 请求超时 |

### 6.2 错误代码规范

错误代码格式：`CATEGORY_ERROR_NAME`

```python
# 客户端错误
VALIDATION_ERROR             # 验证失败
AUTHENTICATION_ERROR         # 认证失败
AUTHORIZATION_ERROR          # 授权失败
RESOURCE_NOT_FOUND           # 资源未找到
CONFLICT_ERROR               # 资源冲突
RATE_LIMIT_EXCEEDED          # 速率限制

# 服务端错误
INTERNAL_SERVER_ERROR        # 服务器内部错误
DATABASE_ERROR               # 数据库错误
SANDBOX_EXECUTION_ERROR      # 沙箱执行错误
CONTAINER_POOL_ERROR         # 容器池错误
EXTERNAL_SERVICE_ERROR       # 外部服务错误
CONFIGURATION_ERROR          # 配置错误
TIMEOUT_ERROR                # 超时错误
SERVICE_UNAVAILABLE          # 服务不可用
```

### 6.3 错误响应最佳实践

#### **DO: 提供详细的错误信息**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Username validation failed",
    "path": "/api/v1/users",
    "timestamp": 1704878400.0,
    "requestId": "req_abc123",
    "details": {
      "validation_errors": [
        {
          "field": "username",
          "message": "Username must be between 3 and 50 characters",
          "type": "string_too_short",
          "constraint": {"min_length": 3}
        }
      ]
    }
  }
}
```

#### **DON'T: 暴露敏感信息**

```json
❌ 错误示例
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "ERROR: duplicate key value violates unique constraint \"users_username_key\" DETAIL: Key (username)=(alice) already exists.",
    "stack_trace": "Traceback (most recent call last):\n  File..."
  }
}

✅ 正确示例
{
  "error": {
    "code": "CONFLICT_ERROR",
    "message": "Username already exists",
    "path": "/api/v1/users",
    "timestamp": 1704878400.0,
    "details": {
      "field": "username"
    }
  }
}
```

---

## 7. 分页和过滤

### 7.1 分页规范

#### **页码分页（推荐）**

```
GET /api/v1/lessons?page=1&limit=20

参数:
- page: 页码（从 1 开始）
- limit: 每页数量（默认 20，最大 100）
```

**响应**:

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  },
  "links": {
    "self": "/api/v1/lessons?page=1&limit=20",
    "first": "/api/v1/lessons?page=1&limit=20",
    "prev": null,
    "next": "/api/v1/lessons?page=2&limit=20",
    "last": "/api/v1/lessons?page=8&limit=20"
  }
}
```

#### **偏移分页（备选）**

```
GET /api/v1/lessons?offset=0&limit=20

参数:
- offset: 偏移量（从 0 开始）
- limit: 数量限制
```

#### **游标分页（大数据集）**

```
GET /api/v1/lessons?cursor=abc123&limit=20

参数:
- cursor: 游标（base64 编码）
- limit: 数量限制

响应:
{
  "data": [...],
  "meta": {
    "has_more": true,
    "next_cursor": "def456"
  }
}
```

### 7.2 排序规范

#### **单字段排序**

```
GET /api/v1/lessons?sort=created_at&order=desc

参数:
- sort: 排序字段
- order: 排序方向 (asc, desc)
```

#### **多字段排序**

```
GET /api/v1/lessons?sort=difficulty:asc,created_at:desc
```

### 7.3 过滤规范

#### **简单过滤**

```
GET /api/v1/lessons?status=published&difficulty=beginner
```

#### **复杂过滤（推荐）**

```
GET /api/v1/lessons?filter[status]=published&filter[difficulty]=beginner
```

#### **范围过滤**

```
GET /api/v1/lessons?filter[created_at][gte]=2024-01-01&filter[created_at][lte]=2024-12-31
```

#### **搜索**

```
GET /api/v1/lessons?search=agent
GET /api/v1/lessons?q=react+agent
```

### 7.4 字段选择

```
# 只返回指定字段（减少响应体积）
GET /api/v1/lessons?fields=id,title,created_at

# 排除字段
GET /api/v1/lessons?exclude=content,code_template
```

### 7.5 关系扩展

```
# 扩展关联资源
GET /api/v1/users/123?expand=progress,submissions

响应:
{
  "data": {
    "id": 123,
    "username": "alice",
    "progress": [
      {"lesson_id": 1, "completed": true}
    ],
    "submissions": [
      {"id": 456, "lesson_id": 1, "status": "success"}
    ]
  }
}
```

---

## 8. 版本管理

### 8.1 版本控制策略

**推荐方式: URL 版本控制**

```
https://api.helloagents.com/api/v1/lessons
https://api.helloagents.com/api/v2/lessons
```

**优点**:
- 清晰直观
- 易于测试和文档
- 支持浏览器直接访问
- 便于缓存

**备选方案: Header 版本控制**

```http
GET /api/lessons HTTP/1.1
Accept: application/vnd.helloagents.v1+json
```

### 8.2 版本废弃流程

**第 1 步: 发布新版本**

```
发布 v2
- 完整功能
- 完整文档
- 迁移指南
```

**第 2 步: 标记旧版本废弃**

```python
@app.get("/api/v1/lessons")
@deprecated(
    version="2.0.0",
    reason="请迁移到 /api/v2/lessons",
    removal_date="2027-01-01"
)
async def get_lessons_v1(response: Response):
    # 添加废弃响应头
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2027-01-01"
    response.headers["Link"] = '</api/v2/lessons>; rel="alternate"'
    ...
```

**第 3 步: 通知开发者（6-12 个月）**

- 在文档中标记废弃
- 发送邮件通知
- 记录使用情况
- 提供迁移支持

**第 4 步: 移除旧版本**

```
2027-01-01: 完全移除 v1
- 返回 410 Gone
- 或重定向到 v2
```

### 8.3 版本兼容性原则

**向后兼容**:
- ✅ 添加新端点
- ✅ 添加可选字段
- ✅ 添加新的 HTTP 方法

**破坏性变更（需要新版本）**:
- ❌ 删除端点
- ❌ 删除字段
- ❌ 修改字段类型
- ❌ 修改响应格式
- ❌ 修改认证方式

---

## 9. 安全和认证

### 9.1 认证方案（规划中）

**阶段 1: 本地模式（当前）**
- 无需认证
- 自动创建默认用户

**阶段 2: JWT 认证（未来）**

```http
POST /api/v1/auth/login HTTP/1.1
Content-Type: application/json

{
  "username": "alice",
  "password": "secret"
}

响应:
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}

使用:
GET /api/v1/users/current HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 9.2 输入验证

**代码执行安全检查**:

```python
FORBIDDEN_PATTERNS = [
    'os.system',
    'subprocess',
    'eval',
    'exec',
    '__import__',
    'open(',
    'file(',
]

def validate_code(code: str) -> None:
    """验证代码安全性"""
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in code:
            raise ValidationError(
                message=f"Code contains forbidden operation: {pattern}",
                field="code",
                details={"forbidden_pattern": pattern}
            )
```

### 9.3 速率限制

```python
# 不同端点的限流策略
RATE_LIMITS = {
    "default": "100/minute",
    "/api/v1/code/execute": "10/minute",
    "/api/v1/chat": "30/minute",
}

# 响应头
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704878460
```

---

## 10. 性能优化

### 10.1 缓存策略

**GET 请求缓存**:

```http
# 响应头
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# 条件请求
GET /api/v1/lessons/1 HTTP/1.1
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# 304 Not Modified（无响应体）
HTTP/1.1 304 Not Modified
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

### 10.2 压缩

```http
# 请求头
Accept-Encoding: gzip, deflate, br

# 响应头
Content-Encoding: gzip
```

### 10.3 字段选择

```
# 减少响应体积
GET /api/v1/lessons?fields=id,title,created_at
```

### 10.4 批量操作

```http
# 批量创建
POST /api/v1/users/batch HTTP/1.1
Content-Type: application/json

{
  "users": [
    {"username": "alice", "email": "alice@example.com"},
    {"username": "bob", "email": "bob@example.com"}
  ]
}

# 批量更新
PATCH /api/v1/users/batch HTTP/1.1
Content-Type: application/json

{
  "ids": [1, 2, 3],
  "updates": {
    "settings.theme": "dark"
  }
}
```

---

## 11. 实施检查清单

### 11.1 新端点开发检查

创建新端点时，请确认以下项目：

#### **URL 设计**
- [ ] 使用复数名词
- [ ] 使用小写和连字符（kebab-case）
- [ ] 嵌套层级不超过 2 层
- [ ] 包含版本号（`/api/v1/...`）

#### **HTTP 方法**
- [ ] 使用正确的 HTTP 方法（GET, POST, PUT, DELETE）
- [ ] GET 请求不修改数据
- [ ] POST 创建返回 201 + Location
- [ ] DELETE 成功返回 204

#### **请求验证**
- [ ] 使用 Pydantic 模型验证
- [ ] 必填字段明确标注
- [ ] 字段有长度/范围限制
- [ ] 敏感操作有安全检查

#### **响应格式**
- [ ] 使用统一的 `{data}` 包装
- [ ] 分页响应包含 `meta` 和 `links`
- [ ] 错误响应使用统一格式
- [ ] HTTP 状态码正确

#### **文档**
- [ ] 添加 `summary` 和 `description`
- [ ] 定义 `response_model`
- [ ] 添加请求/响应示例
- [ ] 文档说明所有错误码

#### **日志**
- [ ] 记录关键操作
- [ ] 记录错误和异常
- [ ] 使用结构化日志

#### **测试**
- [ ] 编写单元测试
- [ ] 测试成功场景
- [ ] 测试错误场景
- [ ] 测试边界条件

---

## 12. 参考资源

### 12.1 官方文档

- [HTTP/1.1 规范 (RFC 7231)](https://tools.ietf.org/html/rfc7231)
- [REST API 设计指南](https://restfulapi.net/)
- [OpenAPI 3.0 规范](https://swagger.io/specification/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)

### 12.2 最佳实践

- [Google API 设计指南](https://cloud.google.com/apis/design)
- [Microsoft REST API 指南](https://github.com/microsoft/api-guidelines)
- [Zalando RESTful API 指南](https://opensource.zalando.com/restful-api-guidelines/)
- [JSON API 规范](https://jsonapi.org/)

### 12.3 工具推荐

- **API 设计**: Postman, Insomnia, Swagger Editor
- **文档**: Swagger UI, ReDoc, Redocly
- **测试**: pytest, httpx, Tavern
- **监控**: Prometheus, Grafana, Sentry

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-10
**维护者**: API Architect Team
**反馈渠道**: api-feedback@helloagents.com
