# HelloAgents Platform - API 架构审查报告

**审查日期**: 2026-01-10
**审查人**: API Architect
**项目**: HelloAgents Learning Platform
**后端框架**: FastAPI 0.x

---

## 执行摘要

本报告对 HelloAgents Platform 的 RESTful API 进行了全面审查，涵盖 API 设计、文档、错误处理、版本管理四个方面。总体评估：**现有 API 基础良好，但需要规范化改进**。

**关键发现**：
- ✅ **优点**: 已有 v1/v2 版本分离、统一异常处理、详细日志记录
- ⚠️ **待改进**: OpenAPI 文档不完整、响应格式不一致、缺少速率限制和分页规范
- 🔴 **问题**: 向后兼容端点混乱、部分端点缺少 HTTP 状态码使用规范

**改进优先级**：
1. **高优先级**: 统一响应格式、完善 OpenAPI 文档、规范 HTTP 状态码
2. **中优先级**: 添加分页和过滤规范、实现速率限制、优化版本管理
3. **低优先级**: API 性能优化、增加批量操作端点

---

## 1. 现有 API 架构分析

### 1.1 API 端点概览

#### **核心端点**

```
# v1 API (当前主版本)
GET    /api/v1/lessons              # 课程列表
GET    /api/v1/lessons/{lesson_id}  # 课程详情
POST   /api/v1/code/execute         # 代码执行
POST   /api/v1/code/hint            # AI 代码提示
POST   /api/v1/chat                 # AI 助手聊天
GET    /api/v1/sandbox/pool/stats   # 沙箱统计

# v2 API (Clean Architecture 重构版)
POST   /api/v2/users                # 创建用户
GET    /api/v2/users/current        # 当前用户
GET    /api/v2/users/{user_id}      # 用户详情
PUT    /api/v2/users/{user_id}      # 更新用户
POST   /api/v2/users/{user_id}/login # 记录登录
POST   /api/v2/code/execute         # 代码执行（重构版）
GET    /api/v2/code/stats           # 执行统计

# 向后兼容端点 (已弃用，待移除)
POST   /api/execute                 # 代码执行
GET    /api/lessons                 # 课程列表
GET    /api/lessons/{lesson_id}     # 课程详情
POST   /api/chat                    # AI 聊天
POST   /api/hint                    # AI 提示
GET    /api/sandbox/pool/stats      # 沙箱统计

# 健康检查端点
GET    /                            # 根端点
GET    /health                      # 完整健康检查
GET    /health/ready                # 就绪检查 (Readiness Probe)
GET    /health/live                 # 存活检查 (Liveness Probe)

# API 文档
GET    /api/v1/docs                 # Swagger UI
GET    /api/v1/redoc                # ReDoc
GET    /api/v1/openapi.json         # OpenAPI 规范
```

### 1.2 架构优点

#### ✅ **1. 版本管理已到位**

```python
# 中间件实现版本控制
app.add_middleware(APIVersionMiddleware, default_version="v1")

# 版本化路由
app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")
```

**优点**：
- 清晰的版本隔离（v1 单体设计 vs v2 Clean Architecture）
- 支持向后兼容（保留旧端点）
- 便于逐步迁移

#### ✅ **2. 统一异常处理**

```python
# 自定义异常体系
class HelloAgentsException(Exception):
    def __init__(self, message, code, status_code, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

# 统一异常响应格式
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "path": "/api/v1/code/execute",
    "timestamp": 1704878400.0,
    "details": {
      "validation_errors": [...]
    }
  }
}
```

**优点**：
- 完整的异常类型体系（ValidationError, AuthenticationError, ResourceNotFoundError 等）
- 统一的错误响应格式
- 详细的错误上下文信息

#### ✅ **3. 详细的日志记录**

```python
logger.info(
    "code_execution_started",
    user_id=user_id,
    lesson_id=lesson_id,
    code_length=len(request.code),
    language=request.language
)
```

**优点**：
- 结构化日志（JSON 格式）
- 关键操作全覆盖
- 性能监控中间件

#### ✅ **4. Pydantic 数据验证**

```python
class CodeExecutionRequest(BaseModel):
    code: str = Field(..., min_length=1, description="要执行的代码")
    language: str = Field(default="python", description="编程语言")
    timeout: int = Field(default=30, ge=1, le=60, description="超时时间（秒）")
```

**优点**：
- 自动参数验证
- 类型安全
- 生成 OpenAPI 文档

### 1.3 存在的问题

#### 🔴 **1. 响应格式不一致**

**问题描述**：不同端点的成功响应格式不统一。

```python
# v1 课程列表 - 包装格式
{
  "success": true,
  "lessons": [...]
}

# v1 课程详情 - 直接返回对象
{
  "lesson_id": "1",
  "title": "...",
  "content": "...",
  "code_template": "..."
}

# v2 用户创建 - 直接返回对象
{
  "id": 1,
  "username": "alice",
  "full_name": "Alice Wang",
  ...
}

# v2 执行统计 - 嵌套 data 字段
{
  "success": true,
  "data": {
    "pool_enabled": true,
    ...
  }
}
```

**影响**：
- 前端需要处理多种响应格式
- 增加客户端复杂度
- 难以统一错误处理

#### ⚠️ **2. OpenAPI 文档不完整**

**问题描述**：部分端点缺少详细的 OpenAPI 注解。

```python
# ❌ 缺少完整的响应文档
@router.get("/lessons")
async def get_all_lessons():
    """获取所有课程列表"""
    # 没有定义响应示例、错误码说明
    ...

# ✅ 良好的文档示例 (v2)
@router.post(
    "",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户，用户名必须唯一",
    responses={
        201: {"description": "用户创建成功", ...},
        409: {"description": "用户名已存在"},
        422: {"description": "请求参数验证失败"}
    }
)
def create_user(...):
    ...
```

**影响**：
- API 文档可读性差
- 开发者难以理解 API 行为
- 缺少错误处理指导

#### ⚠️ **3. 缺少分页和过滤规范**

**问题描述**：列表端点没有标准化的分页和过滤参数。

```python
# ❌ 当前实现 - 返回全部数据
@router.get("/lessons")
async def get_all_lessons():
    lessons = course_manager.get_all_lessons()
    return {"success": True, "lessons": lessons}
```

**缺失功能**：
- 分页参数（page, limit, offset）
- 排序参数（sort, order）
- 过滤参数（filter, search）
- 分页元数据（total, totalPages）

#### ⚠️ **4. 缺少速率限制**

**问题描述**：未实现 API 速率限制，容易被滥用。

**风险**：
- 代码执行端点可能被滥用
- AI 聊天端点消耗 API 配额
- 缺少访问控制

#### ⚠️ **5. 向后兼容端点混乱**

**问题描述**：同时存在 v1、v2 和无版本号的端点，增加维护负担。

```python
# 同一功能有三个端点
POST /api/execute          # 向后兼容（已弃用）
POST /api/v1/code/execute  # v1 版本
POST /api/v2/code/execute  # v2 版本（Clean Architecture）
```

**影响**：
- 维护成本高
- 容易引入 Bug
- 文档混乱

#### ⚠️ **6. HTTP 状态码使用不规范**

**问题描述**：部分端点的 HTTP 状态码使用不符合 RESTful 规范。

```python
# ❌ 代码执行失败返回 200
@router.post("/execute")
async def execute_code(...):
    if success:
        return CodeExecutionResponse(success=True, output=output, ...)
    else:
        # 应该返回 400 或 422，而不是 200
        return CodeExecutionResponse(success=False, error=output, ...)
```

**问题**：
- 用户代码错误应该返回 200（业务逻辑成功）
- 但响应体中 `success=False` 会让客户端误解
- 应该在响应体中明确区分"服务成功执行"和"代码执行结果"

---

## 2. RESTful API 规范建议

### 2.1 统一响应格式

#### **2.1.1 标准响应结构**

所有 API 响应应遵循统一的结构：

```typescript
// 成功响应 (2xx)
{
  "data": T,           // 实际数据（对象、数组、基本类型）
  "meta"?: {           // 元数据（可选）
    "page"?: number,
    "limit"?: number,
    "total"?: number,
    "totalPages"?: number
  },
  "links"?: {          // HATEOAS 链接（可选）
    "self": string,
    "next"?: string,
    "prev"?: string
  }
}

// 错误响应 (4xx/5xx)
{
  "error": {
    "code": string,          // 错误代码 (VALIDATION_ERROR, NOT_FOUND 等)
    "message": string,       // 人类可读的错误消息
    "path": string,          // 请求路径
    "timestamp": number,     // 时间戳
    "requestId"?: string,    // 请求ID（可选，用于追踪）
    "details"?: object       // 额外的错误详情（可选）
  }
}
```

#### **2.1.2 具体示例**

```python
# ✅ 单个资源
GET /api/v1/lessons/1
{
  "data": {
    "lesson_id": "1",
    "title": "第1章：Agent 基础概念",
    "content": "...",
    "code_template": "..."
  }
}

# ✅ 资源列表（带分页）
GET /api/v1/lessons?page=1&limit=20
{
  "data": [
    {"lesson_id": "1", "title": "..."},
    {"lesson_id": "2", "title": "..."}
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "totalPages": 3
  },
  "links": {
    "self": "/api/v1/lessons?page=1&limit=20",
    "next": "/api/v1/lessons?page=2&limit=20"
  }
}

# ✅ 资源创建
POST /api/v1/users
Status: 201 Created
{
  "data": {
    "id": 1,
    "username": "alice",
    "created_at": "2024-01-09T10:00:00Z"
  }
}

# ✅ 空响应（删除成功）
DELETE /api/v1/users/1
Status: 204 No Content
(无响应体)

# ✅ 特殊业务逻辑：代码执行
# 注意：代码执行失败是预期行为，不是 API 错误
POST /api/v1/code/execute
Status: 200 OK
{
  "data": {
    "execution_id": "exec_123",
    "success": false,           // 代码执行结果
    "output": "",
    "error": "NameError: name 'x' is not defined",
    "execution_time": 0.05,
    "status": "failed"
  }
}

# ✅ 错误响应
POST /api/v1/code/execute
Status: 400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Code contains forbidden operations",
    "path": "/api/v1/code/execute",
    "timestamp": 1704878400.0,
    "requestId": "req_abc123",
    "details": {
      "forbidden_patterns": ["os.system", "subprocess"]
    }
  }
}
```

### 2.2 HTTP 状态码规范

#### **2.2.1 成功响应 (2xx)**

| 状态码 | 使用场景 | 示例 |
|--------|----------|------|
| `200 OK` | 成功处理请求（查询、更新） | `GET /api/v1/lessons/1` |
| `201 Created` | 成功创建资源 | `POST /api/v1/users` |
| `204 No Content` | 成功删除资源（无返回内容） | `DELETE /api/v1/users/1` |
| `202 Accepted` | 请求已接受，异步处理中 | `POST /api/v1/code/execute-async` |

#### **2.2.2 客户端错误 (4xx)**

| 状态码 | 使用场景 | 示例 |
|--------|----------|------|
| `400 Bad Request` | 请求格式错误、参数无效 | 代码包含危险操作 |
| `401 Unauthorized` | 未认证 | 缺少或无效的 Token |
| `403 Forbidden` | 已认证但无权限 | 访问其他用户的数据 |
| `404 Not Found` | 资源不存在 | `GET /api/v1/lessons/999` |
| `409 Conflict` | 资源冲突 | 用户名已存在 |
| `422 Unprocessable Entity` | 语义错误、验证失败 | 必填字段缺失 |
| `429 Too Many Requests` | 速率限制 | 超过每分钟100次限制 |

#### **2.2.3 服务端错误 (5xx)**

| 状态码 | 使用场景 | 示例 |
|--------|----------|------|
| `500 Internal Server Error` | 未预期的服务器错误 | 数据库连接失败 |
| `502 Bad Gateway` | 外部服务错误 | DeepSeek API 调用失败 |
| `503 Service Unavailable` | 服务暂时不可用 | 容器池资源耗尽 |
| `504 Gateway Timeout` | 超时 | 代码执行超时 |

### 2.3 URL 设计规范

#### **2.3.1 资源命名**

```
✅ 好的实践：
GET    /api/v1/lessons              # 复数形式
GET    /api/v1/lessons/{id}         # 路径参数
GET    /api/v1/users/{id}/progress  # 嵌套资源
POST   /api/v1/code/execute         # 动作型端点（特殊场景）

❌ 避免：
GET    /api/v1/getLesson            # 不要在 URL 中使用动词
GET    /api/v1/lesson               # 使用复数形式
POST   /api/v1/lessons/{id}/delete  # 使用 HTTP 方法而不是 URL
```

#### **2.3.2 查询参数规范**

```
# ✅ 分页
GET /api/v1/lessons?page=1&limit=20

# ✅ 排序
GET /api/v1/lessons?sort=created_at&order=desc

# ✅ 过滤
GET /api/v1/lessons?filter[status]=published&filter[difficulty]=beginner

# ✅ 搜索
GET /api/v1/lessons?search=agent

# ✅ 字段选择（减少响应体积）
GET /api/v1/lessons?fields=id,title,created_at

# ✅ 关系扩展
GET /api/v1/users/1?expand=progress,submissions
```

### 2.4 分页规范

#### **2.4.1 分页参数**

```python
# 查询参数
page: int = 1      # 页码（从1开始）
limit: int = 20    # 每页数量（默认20，最大100）

# 或者使用 offset
offset: int = 0    # 偏移量
limit: int = 20    # 数量限制
```

#### **2.4.2 分页响应**

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

### 2.5 速率限制规范

#### **2.5.1 限流策略**

```python
# 不同端点的限流策略
rate_limits = {
    "default": "100/minute",           # 默认：每分钟100次
    "/api/v1/code/execute": "10/minute",  # 代码执行：每分钟10次
    "/api/v1/chat": "30/minute",          # AI 聊天：每分钟30次
}

# 响应头
X-RateLimit-Limit: 100          # 限流上限
X-RateLimit-Remaining: 95       # 剩余次数
X-RateLimit-Reset: 1704878460   # 重置时间戳
```

#### **2.5.2 限流响应**

```json
Status: 429 Too Many Requests
X-RateLimit-Limit: 100
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

---

## 3. OpenAPI 3.0 规范设计

### 3.1 完整的 OpenAPI 定义

创建 `/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/backend/openapi.yaml`

```yaml
openapi: 3.0.3
info:
  title: HelloAgents Learning Platform API
  description: |
    AI Agent 互动学习平台后端 API

    ## 功能特性
    - 📚 课程内容管理
    - 💻 安全代码执行沙箱
    - 🤖 AI 学习助手聊天
    - 📊 学习进度跟踪

    ## 认证
    当前版本使用本地模式，未来将支持 JWT 认证。

    ## 速率限制
    - 默认: 100 请求/分钟
    - 代码执行: 10 请求/分钟
    - AI 聊天: 30 请求/分钟

  version: 1.0.0
  contact:
    name: HelloAgents Team
    email: support@helloagents.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.helloagents.com/api/v1
    description: Production
  - url: https://staging-api.helloagents.com/api/v1
    description: Staging
  - url: http://localhost:8000/api/v1
    description: Local Development

tags:
  - name: lessons
    description: 课程内容管理
  - name: code
    description: 代码执行和智能提示
  - name: chat
    description: AI 学习助手
  - name: users
    description: 用户管理
  - name: progress
    description: 学习进度跟踪

paths:
  /lessons:
    get:
      tags: [lessons]
      summary: 获取课程列表
      description: 返回所有可用的课程列表，支持分页和过滤
      operationId: listLessons
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/LimitParam'
        - name: difficulty
          in: query
          description: 难度过滤
          schema:
            type: string
            enum: [beginner, intermediate, advanced]
      responses:
        '200':
          description: 成功返回课程列表
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/LessonSummary'
                  meta:
                    $ref: '#/components/schemas/PaginationMeta'
                  links:
                    $ref: '#/components/schemas/PaginationLinks'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /lessons/{lessonId}:
    get:
      tags: [lessons]
      summary: 获取课程详情
      description: 获取指定课程的完整内容，包括标题、Markdown 内容和代码模板
      operationId: getLesson
      parameters:
        - name: lessonId
          in: path
          required: true
          description: 课程ID（如 "1", "2", "4.1"）
          schema:
            type: string
            pattern: '^[0-9]+(\\.[0-9]+)?$'
            example: "1"
      responses:
        '200':
          description: 成功返回课程详情
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    $ref: '#/components/schemas/LessonDetail'
        '404':
          $ref: '#/components/responses/NotFound'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /code/execute:
    post:
      tags: [code]
      summary: 执行代码
      description: |
        在 Docker 容器沙箱中安全执行用户代码

        **安全限制:**
        - 禁止使用 `os.system`, `subprocess`, `eval`, `exec` 等危险函数
        - 代码长度限制: 10KB
        - 执行超时: 默认30秒，最大60秒
        - 内存限制: 128MB
        - CPU限制: 50%核心
        - 禁用网络访问

        **速率限制:** 10 请求/分钟
      operationId: executeCode
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CodeExecutionRequest'
            examples:
              simple:
                summary: 简单的 print 语句
                value:
                  code: "print('Hello, World!')"
                  language: "python"
                  timeout: 30
              complex:
                summary: 带循环的代码
                value:
                  code: |
                    for i in range(5):
                        print(f"Iteration {i}")
                  language: "python"
                  timeout: 30
      responses:
        '200':
          description: 代码执行完成（成功或失败）
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    $ref: '#/components/schemas/CodeExecutionResult'
              examples:
                success:
                  summary: 执行成功
                  value:
                    data:
                      execution_id: "exec_abc123"
                      success: true
                      output: "Hello, World!\n"
                      error: null
                      execution_time: 0.05
                      status: "success"
                failure:
                  summary: 执行失败（用户代码错误）
                  value:
                    data:
                      execution_id: "exec_def456"
                      success: false
                      output: ""
                      error: "NameError: name 'x' is not defined"
                      execution_time: 0.02
                      status: "failed"
        '400':
          description: 代码验证失败（包含危险操作）
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                error:
                  code: "VALIDATION_ERROR"
                  message: "Code contains forbidden operations"
                  path: "/api/v1/code/execute"
                  timestamp: 1704878400.0
                  details:
                    forbidden_patterns: ["os.system"]
        '422':
          $ref: '#/components/responses/ValidationError'
        '429':
          $ref: '#/components/responses/RateLimitExceeded'
        '500':
          $ref: '#/components/responses/InternalServerError'
        '503':
          description: 沙箱服务不可用
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                error:
                  code: "SERVICE_UNAVAILABLE"
                  message: "Sandbox container pool exhausted"
                  path: "/api/v1/code/execute"
                  timestamp: 1704878400.0
                  details:
                    retry_after: 30

  /chat:
    post:
      tags: [chat]
      summary: AI 学习助手聊天
      description: |
        与 AI 学习助手对话，获取学习指导和问题解答

        **上下文支持:**
        - 自动识别当前课程
        - 分析当前代码
        - 保留对话历史（最近10轮）

        **速率限制:** 30 请求/分钟
      operationId: chatWithAI
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
            example:
              message: "什么是 ReAct Agent？"
              conversation_history:
                - role: "user"
                  content: "我想学习 Agent 开发"
                - role: "assistant"
                  content: "很好！我们从基础概念开始..."
              lesson_id: "1"
              code: "# 我的代码\nprint('Hello')"
      responses:
        '200':
          description: AI 助手回复
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    $ref: '#/components/schemas/ChatResponse'
        '422':
          $ref: '#/components/responses/ValidationError'
        '429':
          $ref: '#/components/responses/RateLimitExceeded'
        '500':
          $ref: '#/components/responses/InternalServerError'
        '502':
          description: AI 服务调用失败
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                error:
                  code: "EXTERNAL_SERVICE_ERROR"
                  message: "AI service temporarily unavailable"
                  path: "/api/v1/chat"
                  timestamp: 1704878400.0
                  details:
                    service_name: "DeepSeek"

components:
  parameters:
    PageParam:
      name: page
      in: query
      description: 页码（从1开始）
      schema:
        type: integer
        minimum: 1
        default: 1
        example: 1

    LimitParam:
      name: limit
      in: query
      description: 每页数量
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20
        example: 20

  headers:
    X-RateLimit-Limit:
      description: 速率限制上限
      schema:
        type: integer
        example: 100

    X-RateLimit-Remaining:
      description: 剩余请求次数
      schema:
        type: integer
        example: 95

    X-RateLimit-Reset:
      description: 速率限制重置时间（Unix 时间戳）
      schema:
        type: integer
        example: 1704878460

  schemas:
    # ============ 课程相关 ============
    LessonSummary:
      type: object
      properties:
        lesson_id:
          type: string
          description: 课程ID
          example: "1"
        title:
          type: string
          description: 课程标题
          example: "第1章：Agent 基础概念"
        difficulty:
          type: string
          enum: [beginner, intermediate, advanced]
          description: 难度等级
        duration:
          type: integer
          description: 预计学习时长（分钟）
          example: 30
        completed:
          type: boolean
          description: 是否已完成
          example: false

    LessonDetail:
      allOf:
        - $ref: '#/components/schemas/LessonSummary'
        - type: object
          properties:
            content:
              type: string
              description: Markdown 格式的课程内容
              example: "# Agent 基础概念\n\n什么是 Agent？..."
            code_template:
              type: string
              description: 初始代码模板
              example: "# TODO: 实现你的 Agent\nclass ReActAgent:\n    pass"

    # ============ 代码执行相关 ============
    CodeExecutionRequest:
      type: object
      required:
        - code
      properties:
        code:
          type: string
          minLength: 1
          maxLength: 10240
          description: 要执行的代码
          example: "print('Hello, World!')"
        language:
          type: string
          enum: [python]
          default: python
          description: 编程语言
        timeout:
          type: integer
          minimum: 1
          maximum: 60
          default: 30
          description: 超时时间（秒）
        user_id:
          type: integer
          nullable: true
          description: 用户ID（可选）
        lesson_id:
          type: integer
          nullable: true
          description: 课程ID（可选）

    CodeExecutionResult:
      type: object
      properties:
        execution_id:
          type: string
          description: 执行ID
          example: "exec_abc123"
        success:
          type: boolean
          description: 执行是否成功
        output:
          type: string
          description: 标准输出
        error:
          type: string
          nullable: true
          description: 错误信息（如果失败）
        execution_time:
          type: number
          format: float
          description: 执行时间（秒）
          example: 0.05
        status:
          type: string
          enum: [success, failed, timeout]
          description: 执行状态

    # ============ AI 聊天相关 ============
    ChatMessage:
      type: object
      required:
        - role
        - content
      properties:
        role:
          type: string
          enum: [user, assistant]
          description: 消息角色
        content:
          type: string
          description: 消息内容

    ChatRequest:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          minLength: 1
          description: 用户消息
          example: "什么是 ReAct Agent？"
        conversation_history:
          type: array
          items:
            $ref: '#/components/schemas/ChatMessage'
          description: 对话历史（最多保留10轮）
          default: []
        lesson_id:
          type: string
          nullable: true
          description: 当前课程ID（提供上下文）
        code:
          type: string
          nullable: true
          description: 当前代码（提供上下文）

    ChatResponse:
      type: object
      properties:
        message:
          type: string
          description: AI 助手回复
          example: "ReAct (Reasoning + Acting) 是一种结合推理和行动的 Agent 范式..."
        success:
          type: boolean
          description: 请求是否成功
          default: true

    # ============ 分页相关 ============
    PaginationMeta:
      type: object
      properties:
        page:
          type: integer
          description: 当前页码
          example: 1
        limit:
          type: integer
          description: 每页数量
          example: 20
        total:
          type: integer
          description: 总记录数
          example: 150
        totalPages:
          type: integer
          description: 总页数
          example: 8

    PaginationLinks:
      type: object
      properties:
        self:
          type: string
          format: uri
          description: 当前页链接
        first:
          type: string
          format: uri
          description: 首页链接
        prev:
          type: string
          format: uri
          nullable: true
          description: 上一页链接
        next:
          type: string
          format: uri
          nullable: true
          description: 下一页链接
        last:
          type: string
          format: uri
          description: 末页链接

    # ============ 错误相关 ============
    ErrorResponse:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              description: 错误代码
              example: "VALIDATION_ERROR"
            message:
              type: string
              description: 错误消息
              example: "Request validation failed"
            path:
              type: string
              description: 请求路径
              example: "/api/v1/code/execute"
            timestamp:
              type: number
              format: float
              description: 时间戳
              example: 1704878400.0
            requestId:
              type: string
              description: 请求ID（用于追踪）
              example: "req_abc123"
            details:
              type: object
              description: 额外的错误详情
              additionalProperties: true

  responses:
    ValidationError:
      description: 请求验证失败
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error:
              code: "VALIDATION_ERROR"
              message: "Request validation failed"
              path: "/api/v1/code/execute"
              timestamp: 1704878400.0
              details:
                validation_errors:
                  - field: "code"
                    message: "Field required"
                    type: "missing"

    NotFound:
      description: 资源未找到
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error:
              code: "RESOURCE_NOT_FOUND"
              message: "Lesson not found: 999"
              path: "/api/v1/lessons/999"
              timestamp: 1704878400.0
              details:
                resource: "lesson"
                resource_id: "999"

    RateLimitExceeded:
      description: 速率限制超出
      headers:
        X-RateLimit-Limit:
          $ref: '#/components/headers/X-RateLimit-Limit'
        X-RateLimit-Remaining:
          schema:
            type: integer
            example: 0
        X-RateLimit-Reset:
          $ref: '#/components/headers/X-RateLimit-Reset'
        Retry-After:
          description: 重试等待时间（秒）
          schema:
            type: integer
            example: 60
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error:
              code: "RATE_LIMIT_EXCEEDED"
              message: "Rate limit exceeded. Please try again in 60 seconds."
              path: "/api/v1/code/execute"
              timestamp: 1704878400.0
              details:
                limit: 10
                window: "1 minute"
                retry_after: 60

    InternalServerError:
      description: 服务器内部错误
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error:
              code: "INTERNAL_SERVER_ERROR"
              message: "An unexpected error occurred"
              path: "/api/v1/lessons"
              timestamp: 1704878400.0
              requestId: "req_abc123"
```

### 3.2 生成和验证 OpenAPI 文档

```bash
# 1. 安装 OpenAPI 工具
pip install openapi-spec-validator

# 2. 验证 OpenAPI 文档
openapi-spec-validator backend/openapi.yaml

# 3. 生成 Swagger UI（FastAPI 内置）
# 访问 http://localhost:8000/api/v1/docs

# 4. 生成 ReDoc（FastAPI 内置）
# 访问 http://localhost:8000/api/v1/redoc

# 5. 导出 JSON 格式
# 访问 http://localhost:8000/api/v1/openapi.json
```

---

## 4. API 版本管理策略

### 4.1 版本管理原则

1. **语义化版本控制**: 使用 v1, v2, v3... 表示主版本
2. **URL 版本控制**: 推荐方式，清晰直观
3. **向后兼容期**: 新版本发布后，旧版本保持 6-12 个月
4. **废弃通知**: 通过响应头和文档通知废弃信息

### 4.2 版本演进路线

#### **当前状态**

```
v1 (稳定版) - 单体设计，生产环境使用
├── /api/v1/lessons
├── /api/v1/code/execute
├── /api/v1/code/hint
├── /api/v1/chat
└── /api/v1/sandbox/pool/stats

v2 (开发中) - Clean Architecture 重构
├── /api/v2/users
├── /api/v2/code/execute
└── /api/v2/code/stats

向后兼容端点 (已废弃)
├── /api/execute
├── /api/lessons
├── /api/chat
└── /api/hint
```

#### **推荐演进策略**

**阶段 1: 清理废弃端点 (2026 Q1)**

```python
# 1. 添加废弃警告
@app.post("/api/execute")
@deprecated(
    version="1.0.0",
    reason="请使用 /api/v1/code/execute",
    removal_date="2026-06-01"
)
async def execute_code_legacy(...):
    # 添加响应头
    headers = {
        "Deprecation": "true",
        "Sunset": "2026-06-01",
        "Link": '<http://localhost:8000/api/v1/code/execute>; rel="alternate"'
    }
    ...

# 2. 记录使用情况
logger.warning(
    "deprecated_endpoint_used",
    path="/api/execute",
    recommended_path="/api/v1/code/execute"
)

# 3. 2026-06-01 完全移除
```

**阶段 2: v1 功能冻结 (2026 Q2)**

```
v1 (维护模式)
- 只修复严重 Bug
- 不添加新功能
- 计划 2027-01-01 废弃

v2 (主版本)
- 所有新功能在 v2 开发
- Clean Architecture
- 完整的 OpenAPI 文档
```

**阶段 3: v1 废弃 (2026 Q3-Q4)**

```
# 添加废弃通知
@app.get("/api/v1/lessons")
@deprecated(
    version="2.0.0",
    reason="请迁移到 /api/v2/lessons",
    removal_date="2027-01-01"
)
async def get_lessons_v1(...):
    ...

# 响应头
Deprecation: true
Sunset: 2027-01-01
Link: <http://localhost:8000/api/v2/lessons>; rel="alternate"
```

**阶段 4: v1 移除 (2027 Q1)**

```
移除 v1 所有端点
v2 成为唯一稳定版本
```

### 4.3 版本废弃通知机制

#### **4.3.1 响应头通知**

```python
from datetime import datetime, timedelta

def add_deprecation_headers(
    response,
    deprecated_version: str,
    removal_date: str,
    alternate_url: str
):
    """添加废弃通知响应头"""
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = removal_date
    response.headers["Link"] = f'<{alternate_url}>; rel="alternate"'
    response.headers["X-API-Warn"] = (
        f"API version {deprecated_version} is deprecated. "
        f"It will be removed on {removal_date}. "
        f"Please migrate to {alternate_url}"
    )
    return response
```

#### **4.3.2 文档通知**

在 OpenAPI 文档中标记废弃端点：

```yaml
paths:
  /execute:
    post:
      deprecated: true
      summary: 执行代码（已废弃）
      description: |
        **此端点已废弃，将于 2026-06-01 移除**

        请使用 `/api/v1/code/execute` 替代。

        废弃原因: 统一版本管理，所有端点迁移到 `/api/v1` 命名空间。
```

### 4.4 v1 vs v2 差异对比

| 特性 | v1 (单体设计) | v2 (Clean Architecture) |
|------|---------------|-------------------------|
| **架构** | 单体路由 | 领域驱动设计 |
| **依赖注入** | 无 | 容器化依赖注入 |
| **响应格式** | 不统一 | 统一 `{data, meta, links}` |
| **OpenAPI 文档** | 部分 | 完整 |
| **错误处理** | 统一 | 统一（增强） |
| **分页支持** | 无 | 标准分页 |
| **速率限制** | 无 | 实现中 |
| **测试覆盖率** | ~50% | 目标 >80% |
| **性能优化** | 基础 | 容器池、缓存 |

---

## 5. 实施建议

### 5.1 短期改进（1-2周）

#### **优先级 1: 统一响应格式**

```python
# 创建 backend/app/schemas/response.py

from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """统一的 API 响应格式"""
    data: T

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int

class PaginationLinks(BaseModel):
    self: str
    first: str
    prev: Optional[str] = None
    next: Optional[str] = None
    last: str

class PaginatedAPIResponse(APIResponse[List[T]], Generic[T]):
    """分页 API 响应格式"""
    meta: PaginationMeta
    links: PaginationLinks

# 使用示例
@router.get("/lessons", response_model=PaginatedAPIResponse[LessonSummary])
async def get_lessons(page: int = 1, limit: int = 20):
    lessons = course_manager.get_lessons(page, limit)
    total = course_manager.count_lessons()

    return {
        "data": lessons,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": (total + limit - 1) // limit
        },
        "links": {
            "self": f"/api/v1/lessons?page={page}&limit={limit}",
            "first": f"/api/v1/lessons?page=1&limit={limit}",
            "prev": f"/api/v1/lessons?page={page-1}&limit={limit}" if page > 1 else None,
            "next": f"/api/v1/lessons?page={page+1}&limit={limit}" if page < totalPages else None,
            "last": f"/api/v1/lessons?page={totalPages}&limit={limit}"
        }
    }
```

#### **优先级 2: 完善 OpenAPI 文档**

1. 为每个端点添加详细的 `summary`, `description`, `responses`
2. 定义完整的请求/响应示例
3. 添加错误响应文档
4. 使用 Pydantic `Field(description=...)` 添加字段说明

#### **优先级 3: 规范 HTTP 状态码**

```python
from fastapi import status

# ✅ 正确使用
@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(...):
    ...

@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(...):
    ...

# ✅ 代码执行特殊处理
@router.post("/code/execute", status_code=status.HTTP_200_OK)
async def execute_code(...):
    # 即使用户代码失败，API 调用也是成功的（返回 200）
    # 在响应体中通过 success 字段区分代码执行结果
    ...
```

### 5.2 中期改进（3-4周）

#### **1. 实现速率限制**

```python
# 安装依赖
pip install slowapi

# 配置限流
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 应用限流
@router.post("/code/execute")
@limiter.limit("10/minute")
async def execute_code(request: Request, ...):
    ...

@router.post("/chat")
@limiter.limit("30/minute")
async def chat(request: Request, ...):
    ...
```

#### **2. 添加分页支持**

```python
# 创建通用分页参数
from fastapi import Query

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        limit: int = Query(20, ge=1, le=100, description="每页数量")
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit

# 使用
@router.get("/lessons")
async def get_lessons(pagination: PaginationParams = Depends()):
    lessons = course_manager.get_lessons(
        offset=pagination.offset,
        limit=pagination.limit
    )
    ...
```

#### **3. 清理废弃端点**

```python
# 添加废弃装饰器
from functools import wraps
from fastapi import Response

def deprecated(version: str, reason: str, removal_date: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, response: Response, **kwargs):
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = removal_date
            response.headers["X-API-Warn"] = (
                f"API version {version} is deprecated. {reason} "
                f"It will be removed on {removal_date}."
            )
            logger.warning(
                "deprecated_endpoint_used",
                endpoint=func.__name__,
                removal_date=removal_date
            )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 应用
@app.post("/api/execute")
@deprecated(
    version="1.0.0",
    reason="请使用 /api/v1/code/execute",
    removal_date="2026-06-01"
)
async def execute_code_legacy(response: Response, ...):
    ...
```

### 5.3 长期改进（1-2个月）

1. **完成 v2 API 迁移**
   - 将所有 v1 功能迁移到 v2
   - 使用 Clean Architecture
   - 完整的单元测试和集成测试

2. **实现 API 网关**
   - 使用 Kong 或 APISIX
   - 集中管理认证、限流、日志
   - 支持 API 监控和告警

3. **添加 API 性能监控**
   - 集成 Prometheus + Grafana
   - 监控响应时间、错误率、吞吐量
   - 设置性能告警阈值

4. **生成多语言 SDK**
   - 使用 OpenAPI Generator
   - 生成 Python, JavaScript, TypeScript SDK
   - 发布到 npm, PyPI

---

## 6. 质量检查清单

### 6.1 API 设计检查

- [ ] 所有端点遵循 RESTful 命名规范
- [ ] 使用正确的 HTTP 方法（GET, POST, PUT, DELETE）
- [ ] 路径参数使用单数资源名（`/users/{id}`）
- [ ] 查询参数使用驼峰命名（`pageSize`, `sortBy`）
- [ ] 支持标准分页参数（`page`, `limit`）
- [ ] 支持标准排序参数（`sort`, `order`）
- [ ] 列表端点返回分页元数据

### 6.2 响应格式检查

- [ ] 所有成功响应包含 `data` 字段
- [ ] 分页响应包含 `meta` 和 `links`
- [ ] 所有错误响应包含 `error` 对象
- [ ] 错误对象包含 `code`, `message`, `path`, `timestamp`
- [ ] HTTP 状态码使用正确（200, 201, 204, 400, 404, 500）
- [ ] 资源创建返回 201 + Location 头
- [ ] 资源删除返回 204 No Content

### 6.3 OpenAPI 文档检查

- [ ] 所有端点有 `summary` 和 `description`
- [ ] 所有参数有 `description` 和类型约束
- [ ] 所有请求体有 schema 定义
- [ ] 所有响应有 schema 定义
- [ ] 包含请求/响应示例（`examples`）
- [ ] 错误响应有详细说明（400, 404, 500 等）
- [ ] 使用 `tags` 分组端点
- [ ] 包含认证和授权说明

### 6.4 错误处理检查

- [ ] 所有异常使用自定义异常类
- [ ] 异常包含 `code`, `message`, `status_code`
- [ ] 验证错误返回详细字段错误信息
- [ ] 敏感信息不暴露在错误响应中
- [ ] 所有错误记录到日志
- [ ] 500 错误包含 `requestId` 用于追踪

### 6.5 版本管理检查

- [ ] 所有端点包含版本号（`/api/v1/...`）
- [ ] 废弃端点添加 `Deprecation` 响应头
- [ ] 废弃端点在文档中标记
- [ ] 废弃端点记录使用情况
- [ ] 新版本保持向后兼容或提供迁移指南

### 6.6 性能和安全检查

- [ ] 实现速率限制（防止滥用）
- [ ] 代码执行端点有严格的安全检查
- [ ] 敏感操作记录审计日志
- [ ] 响应时间 P95 < 200ms
- [ ] 大列表查询默认分页（防止内存溢出）
- [ ] 输入验证（长度限制、格式检查）

---

## 7. 总结

### 7.1 当前状态评估

**优点** ✅:
- 已有清晰的版本管理（v1/v2）
- 完善的异常处理体系
- 详细的结构化日志
- Pydantic 自动验证

**问题** ⚠️:
- 响应格式不统一（影响前端开发）
- OpenAPI 文档不完整（影响 API 可用性）
- 缺少分页和速率限制（影响性能和安全）
- 废弃端点清理不及时（增加维护负担）

### 7.2 改进优先级

**高优先级**（1-2周完成）：
1. 统一响应格式（所有端点返回 `{data}` 包装）
2. 完善 OpenAPI 文档（添加 descriptions, examples, responses）
3. 规范 HTTP 状态码（201 创建、204 删除、400 验证失败）

**中优先级**（3-4周完成）：
1. 实现速率限制（slowapi）
2. 添加分页支持（所有列表端点）
3. 清理废弃端点（添加 Deprecation 头）

**低优先级**（1-2个月完成）：
1. 完成 v2 API 迁移（Clean Architecture）
2. 集成 API 网关（Kong/APISIX）
3. 生成多语言 SDK（OpenAPI Generator）

### 7.3 预期成果

完成上述改进后，HelloAgents Platform API 将达到：
- ✅ 统一、一致的 API 设计
- ✅ 完整、详细的 OpenAPI 3.0 文档
- ✅ 规范的 HTTP 状态码和错误处理
- ✅ 清晰的版本管理和废弃策略
- ✅ 完善的速率限制和安全机制
- ✅ 优秀的开发者体验（DX）

---

**审查完成日期**: 2026-01-10
**下一次审查**: 2026-02-10（1个月后）

---

## 附录

### A. 参考资源

- [RESTful API 设计指南](https://restfulapi.net/)
- [OpenAPI 3.0 规范](https://swagger.io/specification/)
- [FastAPI 最佳实践](https://fastapi.tiangolo.com/tutorial/)
- [HTTP 状态码完整列表](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Google API 设计指南](https://cloud.google.com/apis/design)
- [Microsoft REST API 指南](https://github.com/microsoft/api-guidelines)

### B. 工具推荐

- **API 设计**: Postman, Insomnia, Swagger Editor
- **文档生成**: Swagger UI, ReDoc, Redocly
- **测试**: pytest, httpx, Postman Newman
- **监控**: Prometheus, Grafana, Sentry
- **网关**: Kong, APISIX, Traefik
- **SDK 生成**: OpenAPI Generator, swagger-codegen
