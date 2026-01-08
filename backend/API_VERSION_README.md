# HelloAgents API 版本控制

> **Sprint 3 - Task 3.3**: RESTful API 版本控制实现

## 概述

HelloAgents 平台现已实现完整的 API 版本控制机制，所有端点迁移至 `/api/v1/...` 结构，同时保持向后兼容性。

## 核心特性

- ✅ **URL 版本控制**: 清晰的 `/api/v1/` 路径结构
- ✅ **版本信息 API**: 查询当前和支持的版本
- ✅ **响应头标识**: 自动添加版本信息到响应头
- ✅ **向后兼容**: 旧端点继续工作，平滑迁移
- ✅ **OpenAPI 文档**: 完整的 Swagger/ReDoc 文档
- ✅ **类型安全**: Pydantic 模型验证
- ✅ **日志完整**: 结构化日志记录

## 快速开始

### 1. 查看文档

```bash
# 启动服务
cd backend
uvicorn app.main:app --reload

# 访问 Swagger UI
open http://localhost:8000/api/v1/docs
```

### 2. 测试 API

```bash
# 版本信息
curl http://localhost:8000/api/version

# v1 课程列表
curl http://localhost:8000/api/v1/lessons

# v1 代码执行
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, World!\")"}'
```

### 3. 运行测试

```bash
cd backend
python3 test_api_versioning.py
```

## 端点对照表

| 功能 | 旧端点 | 新端点 (v1) |
|------|--------|------------|
| 代码执行 | `/api/execute` | `/api/v1/code/execute` |
| AI 提示 | `/api/hint` | `/api/v1/code/hint` |
| 课程列表 | `/api/lessons` | `/api/v1/lessons` |
| 课程详情 | `/api/lessons/{id}` | `/api/v1/lessons/{id}` |
| AI 聊天 | `/api/chat` | `/api/v1/chat` |
| 沙箱统计 | `/api/sandbox/pool/stats` | `/api/v1/sandbox/pool/stats` |

## 目录结构

```
backend/app/
├── api/
│   ├── dependencies.py          # 共享依赖
│   ├── version.py               # 版本信息端点
│   └── v1/
│       ├── __init__.py          # v1 路由聚合
│       └── routes/
│           ├── code.py          # 代码执行 + AI 提示
│           ├── lessons.py       # 课程管理
│           ├── sandbox.py       # 沙箱监控
│           └── chat.py          # AI 聊天
├── middleware/
│   └── version_middleware.py   # 版本控制中间件
└── main.py                      # 应用入口
```

## 文档资源

| 文档 | 说明 |
|------|------|
| `API_VERSIONING.md` | 完整的版本控制文档 |
| `IMPLEMENTATION_SUMMARY.md` | 实现总结和验证清单 |
| `QUICK_START.md` | 快速参考指南 |
| `test_api_versioning.py` | 自动化测试脚本 |

## 响应示例

### 版本信息

```json
GET /api/version

{
  "current_version": "v1",
  "supported_versions": ["v1"],
  "deprecated_versions": [],
  "latest_version": "v1",
  "version_info": {
    "v1": {
      "status": "stable",
      "release_date": "2026-01-08",
      "description": "Initial stable release..."
    }
  }
}
```

### 响应头

```http
HTTP/1.1 200 OK
X-API-Version: v1
X-Supported-Versions: v1
Content-Type: application/json
```

## 前端集成

### 推荐配置

```typescript
// config/api.ts
export const API_CONFIG = {
  BASE_URL: '/api/v1',
  VERSION: 'v1',
  TIMEOUT: 30000,
};

export const API_ENDPOINTS = {
  CODE_EXECUTE: `${API_CONFIG.BASE_URL}/code/execute`,
  LESSONS: `${API_CONFIG.BASE_URL}/lessons`,
  CHAT: `${API_CONFIG.BASE_URL}/chat`,
  SANDBOX_STATS: `${API_CONFIG.BASE_URL}/sandbox/pool/stats`,
};
```

### 使用示例

```typescript
// 代码执行
const response = await fetch(API_ENDPOINTS.CODE_EXECUTE, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: 'print("Hello")',
    language: 'python'
  })
});

const result = await response.json();
console.log(result.output); // "Hello"
```

## 测试覆盖

自动化测试脚本验证:

- ✅ 版本信息端点
- ✅ 版本响应头
- ✅ v1 课程列表
- ✅ v1 沙箱统计
- ✅ v1 代码执行
- ✅ 向后兼容性
- ✅ OpenAPI 文档

## 向后兼容性

所有旧端点保持可用，标记为 **已弃用**:

```python
@app.get("/api/lessons")
async def get_all_lessons():
    """
    获取所有课程列表

    **已弃用**: 请使用 `/api/v1/lessons`
    """
    # 实现保持不变
```

客户端可以继续使用旧端点，但建议逐步迁移到 v1。

## 性能影响

- **路由开销**: 无影响
- **中间件开销**: < 1ms
- **向后兼容开销**: 无额外开销

## 技术栈

- **框架**: FastAPI
- **验证**: Pydantic
- **日志**: structlog
- **文档**: OpenAPI 3.0

## 开发指南

### 添加新端点

```python
# 1. 在 app/api/v1/routes/ 中创建新模块
# app/api/v1/routes/feature.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/feature", tags=["feature"])

@router.get("/")
async def get_feature():
    return {"status": "ok"}

# 2. 在 app/api/v1/__init__.py 中注册
from .routes import code, lessons, sandbox, chat, feature

api_router.include_router(feature.router)
```

### 添加新版本

参考 `API_VERSIONING.md` 中的"添加新版本步骤"章节。

## 常见问题

### Q: 为什么选择 URL 版本控制？

A: URL 版本控制最直观、易于测试、符合 RESTful 最佳实践，且浏览器缓存友好。

### Q: 旧端点何时会移除？

A: 目前保持向后兼容，移除时间将根据使用情况决定，并会提前通知。

### Q: 如何指定使用特定版本？

A: 通过 URL 路径（推荐）或 `X-API-Version` 请求头。

### Q: v1 和旧端点有什么区别？

A: 功能完全相同，v1 端点有更好的文档、类型验证和日志记录。

## 维护者

- **Backend Lead**
- **实现日期**: 2026-01-08
- **版本**: v1.0.0

## 许可

与 HelloAgents 项目主许可证保持一致。

---

**相关链接**:
- [API 完整文档](./API_VERSIONING.md)
- [实现总结](./IMPLEMENTATION_SUMMARY.md)
- [快速参考](./QUICK_START.md)
- [Swagger UI](http://localhost:8000/api/v1/docs)
- [ReDoc](http://localhost:8000/api/v1/redoc)
