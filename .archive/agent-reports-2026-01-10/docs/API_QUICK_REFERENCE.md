# API 快速参考指南

快速查找 API 设计规范和最佳实践。

---

## URL 设计速查

```bash
# ✅ 正确
GET    /api/v1/lessons              # 复数、小写
GET    /api/v1/lessons/1
POST   /api/v1/users
PUT    /api/v1/users/123
DELETE /api/v1/users/123

# ❌ 错误
GET    /api/v1/getLesson            # 不要动词
GET    /api/v1/Lessons              # 不要大写
POST   /api/v1/users/create         # 使用 HTTP 方法
```

---

## HTTP 状态码速查

| 操作 | 成功 | 失败 |
|------|------|------|
| **GET 资源** | 200 OK | 404 Not Found |
| **POST 创建** | 201 Created | 400 Bad Request / 422 Unprocessable |
| **PUT 更新** | 200 OK | 404 Not Found / 422 Unprocessable |
| **DELETE 删除** | 204 No Content | 404 Not Found |
| **验证失败** | - | 422 Unprocessable Entity |
| **速率限制** | - | 429 Too Many Requests |
| **服务器错误** | - | 500 Internal Server Error |

---

## 响应格式速查

### 成功响应

```json
// 单个资源
{"data": {...}}

// 资源列表
{
  "data": [...],
  "meta": {"page": 1, "total": 100},
  "links": {"next": "..."}
}
```

### 错误响应

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "path": "/api/v1/...",
    "timestamp": 1704878400.0
  }
}
```

---

## 查询参数速查

```bash
# 分页
?page=1&limit=20

# 排序
?sort=created_at&order=desc

# 过滤
?filter[status]=published

# 搜索
?search=keyword

# 字段选择
?fields=id,title,created_at
```

---

## Pydantic 模型速查

```python
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    username: str = Field(
        ...,                           # 必填
        min_length=3,
        max_length=50,
        regex="^[a-zA-Z0-9_]+$",
        description="用户名"
    )
    email: str = Field(
        ...,
        regex="^[^@]+@[^@]+\\.[^@]+$",
        description="邮箱"
    )
    age: int = Field(
        default=18,                    # 可选，默认18
        ge=0,                          # 大于等于0
        le=150,                        # 小于等于150
        description="年龄"
    )
```

---

## FastAPI 路由速查

```python
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get(
    "",
    response_model=List[UserResponse],
    summary="获取用户列表",
    description="返回所有用户，支持分页",
    responses={
        200: {"description": "成功"},
        500: {"description": "服务器错误"}
    }
)
async def list_users(page: int = 1, limit: int = 20):
    return {"data": [...]}

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户"
)
async def create_user(request: UserCreateRequest):
    return {"data": {...}}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {"data": user}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    return
```

---

## 错误处理速查

```python
from app.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    ConflictError
)

# 验证错误
raise ValidationError(
    message="Username is invalid",
    field="username"
)

# 资源未找到
raise ResourceNotFoundError(
    resource="user",
    resource_id="123"
)

# 资源冲突
raise ConflictError(
    message="Username already exists",
    resource="user"
)
```

---

## 日志记录速查

```python
from app.logger import get_logger

logger = get_logger(__name__)

# 信息日志
logger.info(
    "user_created",
    user_id=123,
    username="alice"
)

# 错误日志
logger.error(
    "database_error",
    operation="create_user",
    error=str(e),
    exc_info=True
)
```

---

## 测试速查

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    response = await client.get("/api/v1/users")
    assert response.status_code == 200
    assert "data" in response.json()

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "alice",
            "email": "alice@example.com"
        }
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["username"] == "alice"

@pytest.mark.asyncio
async def test_user_not_found(client: AsyncClient):
    response = await client.get("/api/v1/users/999")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "RESOURCE_NOT_FOUND"
```

---

## OpenAPI 文档速查

```python
from fastapi import FastAPI

app = FastAPI(
    title="HelloAgents API",
    description="AI Agent 学习平台 API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",         # Swagger UI
    redoc_url="/api/v1/redoc"        # ReDoc
)
```

访问文档：
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

---

## 速率限制速查

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/execute")
@limiter.limit("10/minute")
async def execute_code(request: Request):
    return {"data": {...}}
```

响应头：
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1704878460
```

---

## 常用命令

```bash
# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# 运行测试
pytest backend/tests/

# 生成 OpenAPI 文档
curl http://localhost:8000/api/v1/openapi.json > openapi.json

# 验证 OpenAPI 规范
pip install openapi-spec-validator
openapi-spec-validator openapi.yaml

# 代码格式化
black backend/
ruff check backend/

# 类型检查
mypy backend/
```

---

## 开发流程检查清单

创建新 API 端点时：

- [ ] URL 使用复数名词、小写、连字符
- [ ] 使用正确的 HTTP 方法和状态码
- [ ] 定义 Pydantic 请求/响应模型
- [ ] 添加参数验证（长度、范围、格式）
- [ ] 使用统一响应格式 `{data}`
- [ ] 添加完整的 OpenAPI 注解
- [ ] 记录关键操作日志
- [ ] 编写单元测试
- [ ] 更新 API 文档

---

**快速查找**: 按 `Ctrl+F` 搜索关键词
**完整文档**: 查看 `/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/docs/API_DESIGN_STANDARDS.md`
