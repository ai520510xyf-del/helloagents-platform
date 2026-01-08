# HelloAgents 后端统一错误处理实现文档

## 概述

本文档描述 HelloAgents 项目后端统一错误处理机制的实现，包括自定义异常类、错误中间件、异常处理器和标准化的错误响应格式。

**实施日期**: 2026-01-08
**负责人**: Backend Lead
**版本**: v1.0

---

## 目录

1. [实现目标](#实现目标)
2. [架构设计](#架构设计)
3. [核心组件](#核心组件)
4. [错误响应格式](#错误响应格式)
5. [使用指南](#使用指南)
6. [测试验证](#测试验证)
7. [最佳实践](#最佳实践)

---

## 实现目标

### 问题背景

在实施统一错误处理之前，HelloAgents 后端存在以下问题：

- **错误处理分散**：错误处理逻辑散落在各个模块中
- **响应格式不统一**：不同端点返回的错误格式各异
- **缺乏异常类型**：使用通用 Exception，难以分类处理
- **难以追踪错误**：缺少请求 ID 和详细日志

### 解决方案

实现统一的错误处理机制，包括：

1. 定义清晰的异常类层次结构
2. 实现错误处理中间件，捕获所有异常
3. 提供标准化的错误响应格式
4. 集成结构化日志，记录错误详情
5. 为每个请求分配唯一 ID，便于追踪

---

## 架构设计

### 错误处理流程

```
┌─────────────┐
│  客户端请求  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ ErrorHandlerMiddleware │  ← 捕获所有异常
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   路由处理器         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   业务逻辑           │  ← 抛出自定义异常
│  (sandbox, pool)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ HelloAgentsException │  ← 自定义异常类
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 异常处理器           │  ← 转换为标准响应
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  标准错误响应        │
└─────────────────────┘
```

### 组件关系

```
app/
├── exceptions.py           # 自定义异常类定义
├── error_codes.py          # 错误代码常量
├── middleware/
│   └── error_handler.py    # 错误处理中间件
├── main.py                 # 异常处理器注册
├── sandbox.py              # 使用新异常
├── container_pool.py       # 使用新异常
└── tests/
    └── test_error_handling.py  # 错误处理测试
```

---

## 核心组件

### 1. 自定义异常类 (`exceptions.py`)

#### 异常类层次结构

```python
Exception
└── HelloAgentsException (基类)
    ├── ValidationError (400)
    ├── AuthenticationError (401)
    ├── AuthorizationError (403)
    ├── ResourceNotFoundError (404)
    ├── ConflictError (409)
    ├── RateLimitError (429)
    ├── SandboxExecutionError (500)
    ├── ContainerPoolError (503)
    ├── DatabaseError (500)
    ├── ExternalServiceError (502)
    ├── ConfigurationError (500)
    ├── TimeoutError (504)
    └── ServiceUnavailableError (503)
```

#### 基类特性

```python
class HelloAgentsException(Exception):
    def __init__(
        self,
        message: str,           # 人类可读的错误消息
        code: str,              # 错误代码 (程序化处理)
        status_code: int,       # HTTP 状态码
        details: Optional[Dict] # 额外的错误详情
    ):
        ...
```

#### 使用示例

```python
# 抛出验证错误
raise ValidationError(
    message="代码长度超过限制",
    field="code",
    details={
        "code_length": 12000,
        "max_length": 10000
    }
)

# 抛出容器池错误
raise ContainerPoolError(
    message="无法获取容器",
    pool_status={
        "available_containers": 0,
        "in_use_containers": 10
    }
)
```

### 2. 错误代码定义 (`error_codes.py`)

#### 错误代码常量

定义所有标准化的错误代码，便于程序化处理：

```python
# 客户端错误 (4xx)
VALIDATION_ERROR = "VALIDATION_ERROR"
AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

# 服务端错误 (5xx)
SANDBOX_EXECUTION_ERROR = "SANDBOX_EXECUTION_ERROR"
CONTAINER_POOL_ERROR = "CONTAINER_POOL_ERROR"
DATABASE_ERROR = "DATABASE_ERROR"
EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
```

#### 错误代码分组

```python
CLIENT_ERRORS = {VALIDATION_ERROR, AUTHENTICATION_ERROR, ...}
SERVER_ERRORS = {SANDBOX_EXECUTION_ERROR, DATABASE_ERROR, ...}
RETRYABLE_ERRORS = {RATE_LIMIT_EXCEEDED, CONTAINER_UNAVAILABLE, ...}
```

#### 辅助函数

```python
def is_client_error(error_code: str) -> bool:
    """检查是否为客户端错误"""
    return error_code in CLIENT_ERRORS

def is_retryable_error(error_code: str) -> bool:
    """检查是否为可重试错误"""
    return error_code in RETRYABLE_ERRORS
```

### 3. 错误处理中间件 (`error_handler.py`)

#### 功能

- 捕获所有未处理的异常
- 为每个请求生成唯一 ID
- 记录详细的错误日志
- 返回标准化的错误响应

#### 实现

```python
class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            return response

        except HelloAgentsException as e:
            # 处理自定义异常
            return self._handle_helloagents_exception(request, e, request_id)

        except Exception as e:
            # 处理未捕获的异常
            return self._handle_unexpected_exception(request, e, request_id)
```

### 4. 异常处理器注册 (`main.py`)

#### HelloAgents 异常处理器

```python
@app.exception_handler(HelloAgentsException)
async def helloagents_exception_handler(request: Request, exc: HelloAgentsException):
    """处理 HelloAgents 自定义异常"""
    # 根据状态码决定日志级别
    if exc.status_code >= 500:
        logger.error(...)
    else:
        logger.warning(...)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "path": str(request.url),
                "timestamp": time.time(),
                **({"details": exc.details} if exc.details else {})
            }
        }
    )
```

#### 验证错误处理器

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "path": str(request.url),
                "timestamp": time.time(),
                "details": {"validation_errors": errors}
            }
        }
    )
```

---

## 错误响应格式

### 标准格式

所有错误响应遵循统一格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "path": "/api/v1/resource",
    "timestamp": 1704700000.0,
    "request_id": "uuid",
    "details": {}
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `code` | string | 是 | 错误代码 (用于程序化处理) |
| `message` | string | 是 | 人类可读的错误消息 |
| `path` | string | 是 | 请求路径 |
| `timestamp` | float | 是 | 错误发生时间戳 |
| `request_id` | string | 否 | 请求唯一 ID (用于追踪) |
| `details` | object | 否 | 额外的错误详情 |

### 示例

#### 验证错误 (400)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "代码长度超过限制（最大 10KB）",
    "path": "/api/execute",
    "timestamp": 1704700000.0,
    "details": {
      "code_length": 12000,
      "max_length": 10000
    }
  }
}
```

#### 资源未找到 (404)

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User not found: 123",
    "path": "/api/users/123",
    "timestamp": 1704700000.0,
    "details": {
      "resource": "User",
      "resource_id": "123"
    }
  }
}
```

#### 容器池错误 (503)

```json
{
  "error": {
    "code": "CONTAINER_POOL_ERROR",
    "message": "无法获取容器 (池已满或超时)",
    "path": "/api/execute",
    "timestamp": 1704700000.0,
    "details": {
      "pool_status": {
        "available_containers": 0,
        "in_use_containers": 10,
        "total_containers": 10
      }
    }
  }
}
```

---

## 使用指南

### 在业务代码中使用自定义异常

#### 1. 导入异常类

```python
from app.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    SandboxExecutionError,
    ContainerPoolError
)
```

#### 2. 抛出异常

```python
def validate_code(code: str):
    """验证代码"""
    if len(code) > 10000:
        raise ValidationError(
            message="代码长度超过限制（最大 10KB）",
            field="code",
            details={
                "code_length": len(code),
                "max_length": 10000
            }
        )

def get_user(user_id: int):
    """获取用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ResourceNotFoundError(
            resource="User",
            resource_id=str(user_id)
        )
    return user

def execute_code(code: str):
    """执行代码"""
    container = pool.get_container(timeout=30)
    if not container:
        raise ContainerPoolError(
            message="无法获取容器",
            pool_status=pool.get_stats()
        )
    # 执行代码...
```

#### 3. 不需要手动捕获

自定义异常会被错误处理中间件自动捕获并转换为标准响应：

```python
@app.post("/api/execute")
async def execute_code(request: CodeExecutionRequest):
    # 不需要 try-except，异常会自动处理
    sandbox.execute_python(request.code)
    return {"success": True}
```

### 向后兼容

对于返回 `Tuple[bool, str, float]` 的现有函数，保持不变：

```python
# sandbox.execute_python() 仍然返回 (success, output, time)
success, output, execution_time = sandbox.execute_python(code)

if success:
    return {"output": output}
else:
    return {"error": output}  # 不会触发异常处理
```

仅在内部逻辑中抛出异常，不改变外部接口。

---

## 测试验证

### 测试覆盖

创建了全面的测试套件 `test_error_handling.py`，覆盖：

1. **异常类测试**
   - 所有异常类的初始化和属性
   - `to_dict()` 方法
   - 状态码和错误代码

2. **错误代码测试**
   - 错误代码常量定义
   - 错误代码分组
   - 辅助函数

3. **API 错误响应测试**
   - 验证错误响应
   - 资源未找到响应
   - 代码安全检查错误

4. **错误中间件测试**
   - 捕获自定义异常
   - 捕获未预期异常
   - 响应格式一致性

### 运行测试

```bash
# 运行所有错误处理测试
pytest backend/tests/test_error_handling.py -v

# 运行特定测试
pytest backend/tests/test_error_handling.py::test_validation_error -v

# 运行测试并生成覆盖率报告
pytest backend/tests/test_error_handling.py --cov=app --cov-report=html
```

### 测试结果预期

- 所有测试通过 (20+ 测试用例)
- 异常类覆盖率 > 90%
- 错误处理中间件覆盖率 > 85%
- API 错误响应格式 100% 一致

---

## 最佳实践

### 1. 选择合适的异常类型

| 场景 | 异常类型 | 状态码 |
|------|----------|--------|
| 输入参数无效 | `ValidationError` | 400 |
| 用户未登录 | `AuthenticationError` | 401 |
| 权限不足 | `AuthorizationError` | 403 |
| 资源不存在 | `ResourceNotFoundError` | 404 |
| 资源已存在 | `ConflictError` | 409 |
| 请求频率过高 | `RateLimitError` | 429 |
| 代码执行失败 | `SandboxExecutionError` | 500 |
| 容器池不可用 | `ContainerPoolError` | 503 |
| 数据库错误 | `DatabaseError` | 500 |
| 外部 API 调用失败 | `ExternalServiceError` | 502 |
| 操作超时 | `TimeoutError` | 504 |

### 2. 提供详细的错误信息

```python
# ✅ 好的做法
raise ValidationError(
    message="代码长度超过限制（最大 10KB）",
    field="code",
    details={
        "code_length": len(code),
        "max_length": 10000,
        "suggestion": "请减少代码长度或拆分为多个文件"
    }
)

# ❌ 避免
raise ValidationError(message="Invalid code")
```

### 3. 不要暴露敏感信息

```python
# ✅ 好的做法
raise DatabaseError(
    message="数据库查询失败",
    operation="SELECT"
)

# ❌ 避免 (暴露数据库结构)
raise DatabaseError(
    message=f"SELECT * FROM users WHERE id = {user_id} failed"
)
```

### 4. 使用错误代码进行程序化处理

```python
# 客户端代码
try:
    response = api.execute_code(code)
except APIError as e:
    if e.code == "RATE_LIMIT_EXCEEDED":
        # 等待 retry_after 秒后重试
        time.sleep(e.details.get("retry_after", 60))
        response = api.execute_code(code)
    elif e.code in RETRYABLE_ERRORS:
        # 自动重试
        response = api.execute_code(code)
    else:
        # 显示错误给用户
        show_error(e.message)
```

### 5. 记录完整的错误上下文

错误处理中间件会自动记录：

- 错误类型和消息
- 请求路径和方法
- 请求 ID (用于追踪)
- 堆栈跟踪 (服务端错误)

```python
# 日志示例
logger.error(
    "sandbox_execution_error",
    error="Container execution failed",
    error_type="SandboxExecutionError",
    path="/api/execute",
    method="POST",
    request_id="a1b2c3d4",
    code_snippet="print('test')",
    exc_info=True
)
```

---

## 监控与告警

### 错误指标

建议监控以下错误指标：

1. **错误率**
   - 总错误率 (4xx + 5xx)
   - 客户端错误率 (4xx)
   - 服务端错误率 (5xx)

2. **错误类型分布**
   - 验证错误数量
   - 沙箱执行错误数量
   - 容器池错误数量

3. **错误趋势**
   - 错误率变化趋势
   - 特定错误激增告警

### 集成 Sentry

错误自动上报到 Sentry (如果配置了 DSN)：

```python
# main.py 中已配置
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ]
    )
```

Sentry 会捕获：
- 所有未处理的异常
- 错误堆栈跟踪
- 请求上下文
- 用户信息 (如果有)

---

## 附录

### 错误代码完整列表

#### 客户端错误 (4xx)

| 错误代码 | 状态码 | 说明 |
|---------|--------|------|
| `VALIDATION_ERROR` | 400 | 输入验证失败 |
| `INVALID_PARAMETER` | 400 | 请求参数无效 |
| `MISSING_PARAMETER` | 400 | 缺少必需参数 |
| `AUTHENTICATION_ERROR` | 401 | 认证失败 |
| `INVALID_CREDENTIALS` | 401 | 用户名或密码错误 |
| `TOKEN_EXPIRED` | 401 | 令牌已过期 |
| `TOKEN_INVALID` | 401 | 令牌无效 |
| `AUTHORIZATION_ERROR` | 403 | 授权失败 |
| `INSUFFICIENT_PERMISSIONS` | 403 | 权限不足 |
| `RESOURCE_NOT_FOUND` | 404 | 资源未找到 |
| `USER_NOT_FOUND` | 404 | 用户未找到 |
| `LESSON_NOT_FOUND` | 404 | 课程未找到 |
| `CONFLICT_ERROR` | 409 | 资源冲突 |
| `RESOURCE_ALREADY_EXISTS` | 409 | 资源已存在 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超过限制 |

#### 服务端错误 (5xx)

| 错误代码 | 状态码 | 说明 |
|---------|--------|------|
| `INTERNAL_SERVER_ERROR` | 500 | 服务器内部错误 |
| `SANDBOX_EXECUTION_ERROR` | 500 | 代码沙箱执行错误 |
| `CODE_SAFETY_CHECK_FAILED` | 500 | 代码安全检查失败 |
| `DATABASE_ERROR` | 500 | 数据库错误 |
| `CONFIGURATION_ERROR` | 500 | 配置错误 |
| `EXTERNAL_SERVICE_ERROR` | 502 | 外部服务错误 |
| `AI_SERVICE_ERROR` | 502 | AI 服务错误 |
| `CONTAINER_POOL_ERROR` | 503 | 容器池错误 |
| `CONTAINER_UNAVAILABLE` | 503 | 无法获取容器 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |
| `TIMEOUT_ERROR` | 504 | 操作超时 |

---

## 总结

本次实现成功建立了 HelloAgents 后端统一的错误处理机制，包括：

1. **清晰的异常类层次结构** - 覆盖所有常见错误场景
2. **标准化的错误响应格式** - 便于前端处理和用户理解
3. **完善的错误日志记录** - 便于问题追踪和调试
4. **全面的测试覆盖** - 确保错误处理的可靠性
5. **详细的使用文档** - 便于团队协作和维护

### 验收标准

- [x] 所有异常类型都已定义
- [x] 错误中间件正常工作
- [x] 错误响应格式统一
- [x] 现有代码已更新使用新异常
- [x] 错误日志记录完整
- [x] 测试覆盖所有异常类型

### 后续优化

1. 添加更多业务特定的异常类型
2. 实现错误重试机制 (针对可重试错误)
3. 添加错误率监控和告警
4. 国际化错误消息 (支持多语言)
5. 前端错误展示组件优化

---

**文档版本**: v1.0
**最后更新**: 2026-01-08
**维护者**: Backend Team
