# API 规范化实施行动计划

本文档提供 HelloAgents Platform API 规范化的分阶段实施计划。

---

## 概览

**目标**: 将现有 API 改造为完全符合 RESTful 规范的、文档完善的、易于维护的 API

**时间线**: 6-8 周

**优先级**:
1. **高优先级（1-2周）**: 统一响应格式、完善文档、规范状态码
2. **中优先级（3-4周）**: 实现分页、速率限制、清理废弃端点
3. **低优先级（5-8周）**: 完成 v2 迁移、集成 API 网关

---

## 阶段 1: 快速改进（第 1-2 周）

### Week 1: 统一响应格式和文档

#### **任务 1.1: 创建统一响应模型** (2 天)

**文件**: `backend/app/schemas/response.py`

```python
"""
统一 API 响应格式模块
"""

from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """
    统一的 API 响应格式

    所有成功响应都应该使用这个格式
    """
    data: T


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int
    limit: int
    total: int
    totalPages: int


class PaginationLinks(BaseModel):
    """分页链接"""
    self: str
    first: str
    prev: Optional[str] = None
    next: Optional[str] = None
    last: str


class PaginatedAPIResponse(BaseModel, Generic[T]):
    """分页 API 响应格式"""
    data: List[T]
    meta: PaginationMeta
    links: PaginationLinks


# 使用示例
# @router.get("/users", response_model=PaginatedAPIResponse[UserResponse])
# async def list_users(...):
#     return {
#         "data": [...],
#         "meta": {...},
#         "links": {...}
#     }
```

**验收标准**:
- [ ] 创建 `APIResponse` 泛型模型
- [ ] 创建 `PaginatedAPIResponse` 模型
- [ ] 添加使用文档和示例
- [ ] 单元测试覆盖

#### **任务 1.2: 更新 v1 Lessons 端点** (1 天)

**文件**: `backend/app/api/v1/routes/lessons.py`

**当前**:
```python
@router.get("/lessons")
async def get_all_lessons():
    return {"success": True, "lessons": lessons}
```

**改为**:
```python
from app.schemas.response import APIResponse

class LessonSummary(BaseModel):
    lesson_id: str
    title: str
    difficulty: str
    duration: int

@router.get(
    "/lessons",
    response_model=APIResponse[List[LessonSummary]],
    summary="获取课程列表",
    description="返回所有可用的课程列表",
    responses={
        200: {
            "description": "成功返回课程列表",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "lesson_id": "1",
                                "title": "第1章：Agent 基础",
                                "difficulty": "beginner",
                                "duration": 30
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器错误"}
    }
)
async def get_all_lessons():
    lessons = course_manager.get_all_lessons()
    return {"data": lessons}
```

**验收标准**:
- [ ] 使用 `APIResponse` 包装响应
- [ ] 添加完整的 OpenAPI 注解
- [ ] 添加请求/响应示例
- [ ] 测试通过

#### **任务 1.3: 更新 v1 Code Execute 端点** (1 天)

**文件**: `backend/app/api/v1/routes/code.py`

```python
from app.schemas.response import APIResponse

class CodeExecutionResult(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:8]}")
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float
    status: str

@router.post(
    "/execute",
    response_model=APIResponse[CodeExecutionResult],
    summary="执行代码",
    description="""
    在 Docker 容器沙箱中安全执行用户代码

    **安全限制:**
    - 禁止使用危险函数
    - 代码长度限制: 10KB
    - 执行超时: 30秒

    **速率限制:** 10 请求/分钟
    """,
    responses={
        200: {
            "description": "代码执行完成",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "执行成功",
                            "value": {
                                "data": {
                                    "execution_id": "exec_abc123",
                                    "success": True,
                                    "output": "Hello, World!\n",
                                    "error": None,
                                    "execution_time": 0.05,
                                    "status": "success"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def execute_code(request: CodeExecutionRequest, ...):
    success, output, execution_time = sandbox.execute_python(request.code)

    result = CodeExecutionResult(
        success=success,
        output=output if success else "",
        error=output if not success else None,
        execution_time=execution_time,
        status="success" if success else "failed"
    )

    return {"data": result}
```

**验收标准**:
- [ ] 使用 `APIResponse` 包装响应
- [ ] 添加 `execution_id` 字段
- [ ] 完善 OpenAPI 文档
- [ ] 添加多个响应示例
- [ ] 测试成功和失败场景

#### **任务 1.4: 更新 v1 Chat 端点** (1 天)

**文件**: `backend/app/api/v1/routes/chat.py`

```python
from app.schemas.response import APIResponse

@router.post(
    "",
    response_model=APIResponse[ChatResponse],
    summary="AI 学习助手聊天",
    description="""
    与 AI 学习助手对话，获取学习指导

    **上下文支持:**
    - 自动识别当前课程
    - 分析当前代码
    - 保留对话历史

    **速率限制:** 30 请求/分钟
    """,
    responses={
        200: {
            "description": "AI 助手回复",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "message": "ReAct Agent 是...",
                            "success": True
                        }
                    }
                }
            }
        },
        502: {"description": "AI 服务不可用"}
    }
)
async def chat_with_ai(request: ChatRequest, ...):
    assistant_message = # ... AI 调用

    return {
        "data": {
            "message": assistant_message,
            "success": True
        }
    }
```

**验收标准**:
- [ ] 使用 `APIResponse` 包装响应
- [ ] 完善 OpenAPI 文档
- [ ] 测试通过

### Week 2: 规范 HTTP 状态码和错误处理

#### **任务 2.1: 审查所有端点的状态码** (1 天)

创建检查脚本：`backend/scripts/check_status_codes.py`

```python
"""
检查所有 API 端点的 HTTP 状态码是否符合规范
"""

import ast
import os
from pathlib import Path

def check_route_status_codes(file_path):
    """检查路由文件的状态码使用"""
    with open(file_path) as f:
        content = f.read()

    # 检查 POST 端点是否返回 201
    # 检查 DELETE 端点是否返回 204
    # 等等...

    # 输出不符合规范的端点

if __name__ == "__main__":
    routes_dir = Path("backend/app/api")
    for py_file in routes_dir.rglob("*.py"):
        check_route_status_codes(py_file)
```

**验收标准**:
- [ ] 脚本能检测所有路由文件
- [ ] 识别不规范的状态码使用
- [ ] 生成检查报告

#### **任务 2.2: 修复不规范的状态码** (2 天)

**常见问题修复**:

```python
# ❌ 错误：POST 创建返回 200
@router.post("/users")
async def create_user(...):
    return user

# ✅ 正确：POST 创建返回 201
@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(response: Response, ...):
    user = create_user_in_db(...)
    response.headers["Location"] = f"/api/v1/users/{user.id}"
    return {"data": user}

# ❌ 错误：DELETE 返回 200 + 响应体
@router.delete("/users/{id}")
async def delete_user(id: int):
    return {"message": "User deleted"}

# ✅ 正确：DELETE 返回 204 无响应体
@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int):
    delete_user_from_db(id)
    return
```

**验收标准**:
- [ ] 所有 POST 创建端点返回 201
- [ ] 所有 DELETE 端点返回 204
- [ ] 所有 PUT 端点返回 200
- [ ] 错误场景返回正确状态码

#### **任务 2.3: 完善错误响应格式** (1 天)

确保所有错误响应符合统一格式：

```python
# 在 app/middleware/error_handler.py 中

@app.exception_handler(HelloAgentsException)
async def helloagents_exception_handler(request: Request, exc: HelloAgentsException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "path": str(request.url.path),
                "timestamp": time.time(),
                "requestId": request.state.request_id,  # 添加请求ID
                **({"details": exc.details} if exc.details else {})
            }
        }
    )
```

**验收标准**:
- [ ] 所有错误响应包含 `error` 对象
- [ ] 包含 `code`, `message`, `path`, `timestamp`
- [ ] 添加 `requestId` 用于追踪
- [ ] 敏感信息不暴露

#### **任务 2.4: 添加请求追踪 ID** (1 天)

创建中间件：`backend/app/middleware/request_id.py`

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 生成或获取请求ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # 调用下一个中间件
        response = await call_next(request)

        # 添加响应头
        response.headers["X-Request-ID"] = request_id

        return response
```

在 `main.py` 中注册：

```python
app.add_middleware(RequestIDMiddleware)
```

**验收标准**:
- [ ] 所有响应包含 `X-Request-ID` 头
- [ ] 错误响应包含 `requestId` 字段
- [ ] 日志记录包含 `request_id`

---

## 阶段 2: 功能增强（第 3-4 周）

### Week 3: 实现分页和过滤

#### **任务 3.1: 创建分页工具** (1 天)

**文件**: `backend/app/utils/pagination.py`

```python
from typing import List, TypeVar, Generic
from pydantic import BaseModel
from app.schemas.response import PaginatedAPIResponse, PaginationMeta, PaginationLinks

T = TypeVar('T')

def paginate(
    items: List[T],
    page: int,
    limit: int,
    base_url: str
) -> PaginatedAPIResponse[T]:
    """
    分页工具函数

    Args:
        items: 数据项列表
        page: 页码（从1开始）
        limit: 每页数量
        base_url: 基础 URL

    Returns:
        分页响应对象
    """
    total = len(items)
    totalPages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit
    paginated_items = items[start:end]

    return PaginatedAPIResponse(
        data=paginated_items,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            totalPages=totalPages
        ),
        links=PaginationLinks(
            self=f"{base_url}?page={page}&limit={limit}",
            first=f"{base_url}?page=1&limit={limit}",
            prev=f"{base_url}?page={page-1}&limit={limit}" if page > 1 else None,
            next=f"{base_url}?page={page+1}&limit={limit}" if page < totalPages else None,
            last=f"{base_url}?page={totalPages}&limit={limit}"
        )
    )
```

**验收标准**:
- [ ] 分页函数实现完整
- [ ] 支持边界条件（首页、末页）
- [ ] 生成正确的分页链接
- [ ] 单元测试覆盖

#### **任务 3.2: 添加分页参数依赖** (1 天)

**文件**: `backend/app/api/dependencies.py`

```python
from fastapi import Query

class PaginationParams:
    """分页参数依赖"""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码（从1开始）"),
        limit: int = Query(20, ge=1, le=100, description="每页数量（最大100）")
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit
```

**使用示例**:

```python
from fastapi import Depends
from app.api.dependencies import PaginationParams

@router.get("/lessons", response_model=PaginatedAPIResponse[LessonSummary])
async def get_lessons(pagination: PaginationParams = Depends()):
    lessons = course_manager.get_lessons(
        offset=pagination.offset,
        limit=pagination.limit
    )
    total = course_manager.count_lessons()

    return paginate(
        items=lessons,
        page=pagination.page,
        limit=pagination.limit,
        base_url="/api/v1/lessons"
    )
```

**验收标准**:
- [ ] 创建 `PaginationParams` 依赖
- [ ] 更新课程列表端点支持分页
- [ ] 测试分页功能

#### **任务 3.3: 添加排序和过滤** (2 天)

**文件**: `backend/app/api/dependencies.py`

```python
class SortParams:
    """排序参数依赖"""
    def __init__(
        self,
        sort: Optional[str] = Query(None, description="排序字段"),
        order: str = Query("asc", regex="^(asc|desc)$", description="排序方向")
    ):
        self.sort = sort
        self.order = order


class FilterParams:
    """过滤参数依赖"""
    def __init__(
        self,
        difficulty: Optional[str] = Query(None, description="难度过滤"),
        status: Optional[str] = Query(None, description="状态过滤"),
        search: Optional[str] = Query(None, description="搜索关键词")
    ):
        self.difficulty = difficulty
        self.status = status
        self.search = search
```

**验收标准**:
- [ ] 实现排序功能
- [ ] 实现基本过滤
- [ ] 实现搜索功能
- [ ] 测试各种查询组合

### Week 4: 速率限制和安全

#### **任务 4.1: 集成 slowapi** (1 天)

**安装依赖**:

```bash
pip install slowapi
```

**配置限流**: `backend/app/main.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 初始化 limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 应用到端点
from fastapi import Request

@router.post("/code/execute")
@limiter.limit("10/minute")
async def execute_code(request: Request, ...):
    ...

@router.post("/chat")
@limiter.limit("30/minute")
async def chat(request: Request, ...):
    ...
```

**验收标准**:
- [ ] 安装和配置 slowapi
- [ ] 为关键端点添加限流
- [ ] 返回限流响应头
- [ ] 测试限流功能

#### **任务 4.2: 自定义限流错误响应** (1 天)

```python
from slowapi.errors import RateLimitExceeded
from fastapi import Request

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        headers={
            "X-RateLimit-Limit": str(exc.detail.split()[0]),
            "X-RateLimit-Remaining": "0",
            "Retry-After": "60"
        },
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded. Please try again later.",
                "path": str(request.url.path),
                "timestamp": time.time(),
                "details": {
                    "limit": exc.detail,
                    "retry_after": 60
                }
            }
        }
    )
```

**验收标准**:
- [ ] 自定义限流错误响应
- [ ] 符合统一错误格式
- [ ] 包含 Retry-After 头
- [ ] 测试限流响应

#### **任务 4.3: 清理废弃端点** (2 天)

**步骤 1: 添加废弃装饰器**

```python
# backend/app/utils/deprecated.py

from functools import wraps
from fastapi import Response
from app.logger import get_logger

logger = get_logger(__name__)

def deprecated(version: str, reason: str, removal_date: str):
    """标记端点为废弃"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, response: Response, **kwargs):
            # 添加废弃响应头
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = removal_date
            response.headers["X-API-Warn"] = (
                f"This endpoint is deprecated and will be removed on {removal_date}. "
                f"{reason}"
            )

            # 记录警告日志
            logger.warning(
                "deprecated_endpoint_used",
                endpoint=func.__name__,
                removal_date=removal_date
            )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

**步骤 2: 标记废弃端点**

```python
# backend/app/main.py

@app.post("/api/execute")
@deprecated(
    version="1.0.0",
    reason="请使用 /api/v1/code/execute",
    removal_date="2026-06-01"
)
async def execute_code_legacy(response: Response, ...):
    # 重定向到新端点
    ...
```

**步骤 3: 在文档中标记**

```python
@app.post(
    "/api/execute",
    deprecated=True,
    summary="执行代码（已废弃）",
    description="""
    **此端点已废弃，将于 2026-06-01 移除**

    请使用 `/api/v1/code/execute` 替代。
    """
)
```

**验收标准**:
- [ ] 创建废弃装饰器
- [ ] 标记所有废弃端点
- [ ] 在文档中明确标注
- [ ] 记录使用情况
- [ ] 设置移除日期

---

## 阶段 3: 长期优化（第 5-8 周）

### Week 5-6: 完成 v2 API 迁移

#### **任务 5.1: 迁移 Lessons API 到 v2** (3 天)

**创建**: `backend/app/api/v2/routes/lessons.py`

使用 Clean Architecture 设计：

```
backend/app/
├── domain/
│   └── lesson.py                    # 领域模型
├── application/
│   ├── dto/
│   │   └── lesson_dto.py            # DTO
│   └── use_cases/
│       └── lesson_management.py     # 用例
├── infrastructure/
│   └── repositories/
│       └── lesson_repository.py     # 仓储
└── api/v2/routes/
    └── lessons.py                   # 路由
```

**验收标准**:
- [ ] 使用 Clean Architecture
- [ ] 完整的单元测试
- [ ] 完整的 OpenAPI 文档
- [ ] 与 v1 功能对等

#### **任务 5.2: 迁移 Chat API 到 v2** (3 天)

类似 Lessons API 的迁移流程。

**验收标准**:
- [ ] Clean Architecture 实现
- [ ] 测试覆盖率 > 80%
- [ ] 文档完整

### Week 7-8: API 网关和监控

#### **任务 7.1: 集成 Kong API 网关** (可选，5 天)

**步骤**:
1. 安装 Kong
2. 配置服务和路由
3. 配置限流插件
4. 配置认证插件（未来）
5. 配置日志插件

**验收标准**:
- [ ] Kong 正常运行
- [ ] 所有 API 通过网关访问
- [ ] 限流策略生效
- [ ] 日志收集正常

#### **任务 7.2: 添加 API 监控** (可选，3 天)

**工具**: Prometheus + Grafana

**指标**:
- 请求总数
- 响应时间（P50, P95, P99）
- 错误率
- 限流触发次数

**验收标准**:
- [ ] Prometheus 收集指标
- [ ] Grafana 可视化仪表板
- [ ] 关键指标告警

---

## 验收标准总览

### API 设计

- [ ] 所有端点遵循 RESTful 规范
- [ ] URL 使用复数名词、小写、连字符
- [ ] HTTP 方法使用正确
- [ ] HTTP 状态码使用正确

### 响应格式

- [ ] 所有成功响应使用 `{data}` 包装
- [ ] 所有错误响应使用统一格式
- [ ] 分页响应包含 `meta` 和 `links`
- [ ] 响应头包含必要信息

### 文档

- [ ] 所有端点有完整的 OpenAPI 注解
- [ ] 包含 summary, description, responses
- [ ] 包含请求/响应示例
- [ ] 参数有详细说明

### 测试

- [ ] 单元测试覆盖率 > 70%
- [ ] 集成测试覆盖关键流程
- [ ] 性能测试通过（P95 < 200ms）

### 安全

- [ ] 实现速率限制
- [ ] 输入验证完整
- [ ] 敏感信息不暴露
- [ ] 错误处理安全

---

## 进度跟踪

使用以下表格跟踪进度：

| 阶段 | 任务 | 负责人 | 状态 | 完成日期 |
|------|------|--------|------|----------|
| 阶段1 | 统一响应格式 | - | 待开始 | - |
| 阶段1 | 完善文档 | - | 待开始 | - |
| 阶段1 | 规范状态码 | - | 待开始 | - |
| 阶段2 | 实现分页 | - | 待开始 | - |
| 阶段2 | 速率限制 | - | 待开始 | - |
| 阶段2 | 清理废弃端点 | - | 待开始 | - |
| 阶段3 | v2 迁移 | - | 待开始 | - |
| 阶段3 | API 网关 | - | 待开始 | - |

---

## 风险和缓解措施

### 风险 1: 破坏现有功能

**缓解措施**:
- 先添加测试再重构
- 使用版本管理（v1 保持不变，v2 重构）
- 逐步迁移，不要一次性大改

### 风险 2: 前端兼容性问题

**缓解措施**:
- 保持 v1 端点向后兼容
- 提前通知前端团队响应格式变更
- 提供迁移指南和示例代码

### 风险 3: 性能下降

**缓解措施**:
- 添加性能测试
- 监控关键指标
- 优化慢查询

---

## 成功指标

完成后，API 应达到以下标准：

- ✅ 100% 端点符合 RESTful 规范
- ✅ OpenAPI 文档完整度 > 95%
- ✅ 单元测试覆盖率 > 70%
- ✅ 响应时间 P95 < 200ms
- ✅ 错误率 < 0.1%
- ✅ 文档可读性评分 > 90%

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-10
**负责人**: API Architect Team
