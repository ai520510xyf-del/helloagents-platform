# HelloAgents API 快速参考

**版本**: v1.0.0
**基础URL**: `http://localhost:8000` (开发) / `https://helloagents-platform.onrender.com` (生产)

---

## 快速测试

```bash
# 健康检查
curl http://localhost:8000/health

# 获取课程列表
curl http://localhost:8000/api/lessons

# 执行代码
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"print(\"Hello, World!\")","language":"python"}'

# AI聊天
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"什么是ReAct Agent?"}'
```

---

## API端点总览

### 健康检查

| 方法 | 端点 | 说明 | 状态 |
|-----|------|------|------|
| GET | `/` | 根端点 | ✅ |
| GET | `/health` | 完整健康检查 | ✅ |
| GET | `/health/ready` | 就绪检查 | ✅ |
| GET | `/health/live` | 存活检查 | ✅ |

### 课程管理

| 方法 | 端点 | 说明 | 版本 |
|-----|------|------|------|
| GET | `/api/lessons` | 获取课程列表 | 旧版 ✅ |
| GET | `/api/lessons/{id}` | 获取课程详情 | 旧版 ✅ |
| GET | `/api/v1/lessons` | 获取课程列表 | v1 ✅ |
| GET | `/api/v1/lessons/{id}` | 获取课程详情 | v1 ✅ |

### 代码执行

| 方法 | 端点 | 说明 | 版本 |
|-----|------|------|------|
| POST | `/api/execute` | 执行代码 | 旧版 ✅ |
| POST | `/api/v1/code/execute` | 执行代码 | v1 ✅ |
| POST | `/api/hint` | 获取AI提示 | 旧版 ✅ |
| POST | `/api/v1/code/hint` | 获取AI提示 | v1 ✅ |

### AI助手

| 方法 | 端点 | 说明 | 版本 |
|-----|------|------|------|
| POST | `/api/chat` | AI聊天 | 旧版 ✅ |
| POST | `/api/v1/chat` | AI聊天 | v1 ✅ |

### 沙箱管理

| 方法 | 端点 | 说明 | 版本 |
|-----|------|------|------|
| GET | `/api/sandbox/pool/stats` | 容器池统计 | 旧版 ✅ |
| GET | `/api/v1/sandbox/pool/stats` | 容器池统计 | v1 ✅ |

### 用户管理

| 方法 | 端点 | 说明 | 状态 |
|-----|------|------|------|
| POST | `/api/users/` | 创建用户 | ✅ |
| GET | `/api/users/current` | 获取当前用户 | ✅ |
| GET | `/api/users/{id}` | 获取用户信息 | ✅ |
| PUT | `/api/users/{id}` | 更新用户信息 | ✅ |
| POST | `/api/users/{id}/login` | 记录登录 | ✅ |

---

## 请求/响应示例

### 1. 执行代码

**请求**:
```bash
POST /api/execute
Content-Type: application/json

{
  "code": "print('Hello, World!')",
  "language": "python",
  "timeout": 30
}
```

**响应**:
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "execution_time": 0.123
}
```

### 2. 获取课程内容

**请求**:
```bash
GET /api/lessons/1
```

**响应**:
```json
{
  "lesson_id": "1",
  "title": "第1章: Agent 基础",
  "content": "# Agent 基础\n\n本章介绍...",
  "code_template": "class SimpleAgent:\n    def __init__(self):\n        pass"
}
```

### 3. AI聊天

**请求**:
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "什么是ReAct Agent?",
  "conversation_history": [],
  "lesson_id": "1",
  "code": "# 当前代码"
}
```

**响应**:
```json
{
  "message": "ReAct Agent 是一种结合推理(Reasoning)和行动(Acting)的 AI Agent 范式...",
  "success": true
}
```

### 4. 健康检查

**请求**:
```bash
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-10T12:00:00.000000",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "sandbox_pool": {
      "status": "healthy",
      "available_containers": 3,
      "in_use_containers": 0
    },
    "ai_service": {
      "status": "configured",
      "message": "AI service API key is configured"
    }
  }
}
```

---

## 错误响应格式

所有错误响应遵循统一格式:

```json
{
  "error": {
    "code": "LESSON_NOT_FOUND",
    "message": "课程 99 不存在",
    "path": "/api/lessons/99",
    "timestamp": 1736532000.0,
    "details": {
      "validation_errors": []
    }
  }
}
```

### 常见错误码

| HTTP状态码 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | `VALIDATION_ERROR` | 请求参数验证失败 |
| 404 | `LESSON_NOT_FOUND` | 课程不存在 |
| 404 | `USER_NOT_FOUND` | 用户不存在 |
| 500 | `CODE_EXECUTION_FAILED` | 代码执行失败 |
| 500 | `AI_SERVICE_ERROR` | AI服务错误 |
| 503 | `SERVICE_UNAVAILABLE` | 服务不可用 |

---

## 测试工具

### 1. 快速测试脚本

```bash
cd backend
python test_api_routes.py
```

### 2. 综合诊断工具

```bash
cd backend
python diagnose_api.py
```

生成 `api_diagnostic_report.json` 详细报告。

### 3. API文档

**Swagger UI**: http://localhost:8000/api/v1/docs
**ReDoc**: http://localhost:8000/api/v1/redoc

### 4. 手动测试集合

Postman Collection: (待创建)

---

## 环境变量

```bash
# 数据库
DATABASE_URL=sqlite:///./helloagents.db

# DeepSeek API
DEEPSEEK_API_KEY=your_api_key_here

# Sentry (可选)
SENTRY_DSN=your_sentry_dsn
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# 服务器配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
```

---

## 性能指标

| 指标 | 目标 | 当前 |
|-----|------|------|
| P50响应时间 | <200ms | ~280ms |
| P95响应时间 | <500ms | ~700ms |
| P99响应时间 | <1000ms | ~900ms |
| 错误率 | <0.1% | ~0% |

---

## CORS配置

允许的来源:
- `http://localhost:5173` (开发)
- `https://helloagents-platform.pages.dev` (生产)

---

## 速率限制

当前: **未启用**

建议配置:
- 代码执行: 10次/分钟
- AI聊天: 20次/分钟
- 其他API: 100次/分钟

---

## 联系支持

- **文档**: [API_ROUTES_FIX_REPORT.md](./API_ROUTES_FIX_REPORT.md)
- **问题报告**: GitHub Issues
- **紧急支持**: 联系后端团队

---

**最后更新**: 2026-01-10
**维护者**: Senior Backend Developer
