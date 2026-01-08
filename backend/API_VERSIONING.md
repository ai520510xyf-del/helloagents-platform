# API 版本控制实现文档

## 概述

HelloAgents 平台已实现完整的 RESTful API 版本控制机制，采用 URL 版本控制策略，支持 `/api/v1/...` 结构。

## 版本信息

- **当前版本**: v1
- **状态**: stable
- **发布日期**: 2026-01-08

## 目录结构

```
backend/app/
├── api/
│   ├── __init__.py              # API 模块初始化
│   ├── dependencies.py          # 共享依赖（版本验证等）
│   ├── version.py               # 版本信息端点
│   └── v1/
│       ├── __init__.py          # v1 路由聚合
│       └── routes/
│           ├── __init__.py
│           ├── code.py          # 代码执行和 AI 提示
│           ├── lessons.py       # 课程内容管理
│           ├── sandbox.py       # 沙箱监控
│           └── chat.py          # AI 聊天助手
├── middleware/
│   └── version_middleware.py   # 版本控制中间件
└── main.py                      # 应用入口（已更新）
```

## API 端点映射

### v1 版本化端点

| 旧端点 | 新端点（v1） | 说明 |
|--------|-------------|------|
| `/api/execute` | `/api/v1/code/execute` | 代码执行 |
| `/api/hint` | `/api/v1/code/hint` | AI 智能提示 |
| `/api/lessons` | `/api/v1/lessons` | 课程列表 |
| `/api/lessons/{id}` | `/api/v1/lessons/{id}` | 课程详情 |
| `/api/chat` | `/api/v1/chat` | AI 聊天 |
| `/api/sandbox/pool/stats` | `/api/v1/sandbox/pool/stats` | 沙箱统计 |

### 版本管理端点

- `GET /api/version` - 获取 API 版本信息
- `GET /health` - 健康检查（无版本）

### OpenAPI 文档

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 核心特性

### 1. URL 版本控制

所有 API 端点采用 URL 路径版本控制：

```
/api/v1/code/execute
/api/v1/lessons
/api/v1/sandbox/pool/stats
```

### 2. 版本响应头

所有响应包含版本信息头：

```http
X-API-Version: v1
X-Supported-Versions: v1
```

### 3. 向后兼容

保留旧端点（无版本前缀），标记为已弃用但仍然可用：

```python
# 旧端点仍然工作
GET /api/lessons

# 文档中标记为已弃用
"""
获取所有课程列表

**已弃用**: 请使用 `/api/v1/lessons`
"""
```

### 4. 版本信息 API

```bash
curl http://localhost:8000/api/version
```

响应示例：

```json
{
  "current_version": "v1",
  "supported_versions": ["v1"],
  "deprecated_versions": [],
  "latest_version": "v1",
  "version_info": {
    "v1": {
      "status": "stable",
      "release_date": "2026-01-08",
      "deprecation_date": null,
      "end_of_life_date": null,
      "description": "Initial stable release with code execution, lessons, sandbox monitoring, and AI chat features."
    }
  }
}
```

### 5. 版本协商（可选）

支持通过请求头指定 API 版本：

```http
GET /api/v1/lessons
X-API-Version: v1
```

## 实现细节

### 1. 中间件层

**APIVersionMiddleware** (`app/middleware/version_middleware.py`):

- 自动检测请求路径中的版本
- 支持请求头 `X-API-Version` 指定版本
- 为所有响应添加版本信息头

### 2. 路由聚合

**v1 API Router** (`app/api/v1/__init__.py`):

```python
from fastapi import APIRouter
from .routes import code, lessons, sandbox, chat

api_router = APIRouter()
api_router.include_router(code.router)
api_router.include_router(lessons.router)
api_router.include_router(sandbox.router)
api_router.include_router(chat.router)
```

### 3. 主应用配置

**main.py** 更新：

```python
# 注册版本化路由
app.include_router(api_v1_router, prefix="/api/v1")

# 注册版本信息路由
app.include_router(version_router)

# 注册现有路由（保持向后兼容）
app.include_router(users.router)
# ...
```

## 数据模型改进

所有 v1 端点的数据模型使用 Pydantic 增强验证：

```python
class CodeExecutionRequest(BaseModel):
    code: str = Field(..., min_length=1, description="要执行的代码")
    language: str = Field(default="python", description="编程语言")
    timeout: int = Field(default=30, ge=1, le=60, description="超时时间（秒）")
```

## 测试

### 运行测试脚本

```bash
# 启动后端服务
cd backend
uvicorn app.main:app --reload

# 在另一个终端运行测试
cd backend
python3 test_api_versioning.py
```

### 测试覆盖

1. ✅ 版本信息端点
2. ✅ 版本响应头
3. ✅ v1 课程列表
4. ✅ v1 沙箱统计
5. ✅ v1 代码执行
6. ✅ 向后兼容性
7. ✅ OpenAPI 文档

### 手动测试示例

```bash
# 测试版本信息
curl http://localhost:8000/api/version

# 测试 v1 课程列表
curl http://localhost:8000/api/v1/lessons

# 测试 v1 代码执行
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, World!\")", "language": "python"}'

# 测试向后兼容
curl http://localhost:8000/api/lessons

# 测试沙箱统计
curl http://localhost:8000/api/v1/sandbox/pool/stats

# 查看响应头
curl -I http://localhost:8000/health
```

## 最佳实践

### 1. 客户端使用建议

```javascript
// 推荐：使用版本化端点
const response = await fetch('/api/v1/lessons');

// 不推荐：使用旧端点（已弃用）
const response = await fetch('/api/lessons');
```

### 2. 添加新版本步骤

当需要添加 v2 时：

1. 创建 `app/api/v2/` 目录
2. 复制 v1 结构并修改
3. 在 `main.py` 中注册 v2 路由
4. 更新 `app/api/version.py` 配置
5. 标记 v1 为 deprecated（如需）
6. 更新文档

### 3. 版本弃用流程

```python
# 更新版本配置
VERSION_CONFIG = {
    "current": "v2",
    "latest": "v2",
    "supported": ["v1", "v2"],
    "deprecated": ["v1"],
    "info": {
        "v1": {
            "status": "deprecated",
            "release_date": "2026-01-08",
            "deprecation_date": "2026-06-01",
            "end_of_life_date": "2026-12-31"
        },
        "v2": {
            "status": "stable",
            "release_date": "2026-06-01"
        }
    }
}
```

## 迁移指南

### 前端迁移

更新所有 API 调用从旧端点到 v1：

```diff
- fetch('/api/execute', ...)
+ fetch('/api/v1/code/execute', ...)

- fetch('/api/lessons')
+ fetch('/api/v1/lessons')

- fetch('/api/chat')
+ fetch('/api/v1/chat')
```

### 配置常量

创建 API 配置常量：

```typescript
// frontend/src/config/api.ts
export const API_VERSION = 'v1';
export const API_BASE_URL = `/api/${API_VERSION}`;

export const API_ENDPOINTS = {
  CODE_EXECUTE: `${API_BASE_URL}/code/execute`,
  CODE_HINT: `${API_BASE_URL}/code/hint`,
  LESSONS: `${API_BASE_URL}/lessons`,
  CHAT: `${API_BASE_URL}/chat`,
  SANDBOX_STATS: `${API_BASE_URL}/sandbox/pool/stats`,
};
```

## 性能影响

- **零性能损耗**: 版本控制通过路由前缀实现，不增加额外开销
- **中间件开销**: < 1ms（仅添加响应头）
- **向后兼容**: 旧端点保持原有性能

## 安全考虑

1. **版本验证**: 中间件自动验证版本号格式
2. **输入验证**: 所有端点使用 Pydantic 模型验证
3. **错误处理**: 统一错误响应格式
4. **日志记录**: 完整的请求日志包含版本信息

## 未来扩展

### 计划功能

1. **版本协商**: 支持 `Accept` 头版本选择
   ```http
   Accept: application/vnd.helloagents.v1+json
   ```

2. **自动重定向**: 旧版本自动重定向到新版本（可配置）

3. **版本分析**: 统计各版本使用情况

4. **API 变更日志**: 自动生成版本变更文档

## 常见问题

### Q: 为什么选择 URL 版本控制而不是 Header 版本控制？

A: URL 版本控制更直观、易于测试，符合 RESTful 最佳实践。

### Q: 旧端点会一直保留吗？

A: 旧端点目前保持向后兼容，未来会根据使用情况决定弃用时间。

### Q: 如何知道哪个版本是推荐的？

A: 查询 `/api/version` 端点的 `current_version` 字段。

### Q: 能否在同一个应用中混用不同版本？

A: 可以，但不推荐。建议统一迁移到最新稳定版本。

## 参考资料

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [RESTful API 版本控制最佳实践](https://restfulapi.net/versioning/)
- [Semantic Versioning](https://semver.org/)

## 更新日志

### v1.0.0 (2026-01-08)

- ✅ 实现 URL 版本控制结构
- ✅ 创建 v1 API 端点
- ✅ 添加版本信息端点
- ✅ 实现版本响应头中间件
- ✅ 保持向后兼容性
- ✅ 更新 OpenAPI 文档配置
- ✅ 编写测试脚本

## 维护者

- Backend Lead
- 2026-01-08
