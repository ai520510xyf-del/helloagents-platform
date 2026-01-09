# 监控配置指南

## 目录

- [Sentry 错误追踪](#sentry-错误追踪)
- [日志系统](#日志系统)
- [健康检查](#健康检查)
- [性能监控](#性能监控)
- [告警配置](#告警配置)

---

## Sentry 错误追踪

### 概述

HelloAgents 后端已集成 Sentry SDK，用于自动捕获和追踪生产环境中的错误和性能问题。

### 配置步骤

#### 1. 创建 Sentry 项目

1. 访问 [sentry.io](https://sentry.io) 并登录
2. 创建新项目，选择 **Python** 平台
3. 复制 DSN（Data Source Name）

#### 2. 配置环境变量

在 Render Dashboard 或本地 `.env` 文件中添加以下环境变量：

```bash
# Sentry 配置
SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
SENTRY_ENVIRONMENT=production  # 或 staging, development
SENTRY_TRACES_SAMPLE_RATE=0.1  # 性能追踪采样率 (10%)
```

#### 3. 验证集成

后端启动时会自动初始化 Sentry。检查日志确认：

```bash
# 检查后端日志
curl https://your-backend.onrender.com/health
```

如果配置正确，Sentry 会自动捕获所有未处理的异常。

### Sentry 功能

#### 错误追踪

- 自动捕获所有 500 错误
- 记录完整的堆栈跟踪
- 关联请求上下文（URL、方法、用户信息）
- 支持错误分组和去重

#### 性能监控

- 追踪 API 请求响应时间
- 数据库查询性能分析
- 慢请求告警（> 1000ms）
- 采样率可配置（建议生产环境 10-20%）

#### 面包屑（Breadcrumbs）

自动记录：
- HTTP 请求
- 数据库查询
- 日志消息
- 用户操作

### 监控指标

#### 关键指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| Error Rate | 错误率 | < 1% |
| Response Time | 响应时间 | P95 < 500ms |
| Availability | 可用性 | > 99.9% |
| Database Query Time | 数据库查询时间 | P95 < 100ms |

#### 告警规则

建议在 Sentry 中配置以下告警规则：

1. **高错误率告警**
   - 条件：1分钟内错误数 > 10
   - 通知：Slack、Email

2. **慢请求告警**
   - 条件：P95 响应时间 > 1000ms
   - 通知：Slack

3. **数据库错误告警**
   - 条件：数据库连接失败
   - 通知：Email、PagerDuty

### 最佳实践

#### 1. 添加自定义上下文

```python
import sentry_sdk

# 添加用户上下文
sentry_sdk.set_user({"id": user_id, "email": user_email})

# 添加自定义标签
sentry_sdk.set_tag("lesson_id", lesson_id)
sentry_sdk.set_tag("feature", "code_execution")

# 添加自定义上下文
sentry_sdk.set_context("code_execution", {
    "code_length": len(code),
    "language": "python",
    "timeout": 30
})
```

#### 2. 捕获特定异常

```python
from sentry_sdk import capture_exception

try:
    result = execute_code(code)
except ValidationError as e:
    # 捕获并发送到 Sentry
    capture_exception(e)
    raise
```

#### 3. 过滤敏感信息

后端已配置 `send_default_pii=False` 防止发送个人身份信息。

额外过滤敏感字段：

```python
sentry_sdk.init(
    dsn=SENTRY_DSN,
    before_send=before_send,
)

def before_send(event, hint):
    # 过滤敏感信息
    if 'request' in event:
        event['request'].pop('cookies', None)
        if 'headers' in event['request']:
            event['request']['headers'].pop('Authorization', None)
    return event
```

---

## 日志系统

### 结构化日志

后端使用 `structlog` 提供结构化日志：

```python
from app.logger import get_logger

logger = get_logger(__name__)

logger.info(
    "code_execution_completed",
    user_id=user_id,
    lesson_id=lesson_id,
    success=True,
    execution_time_ms=123.45,
    output_length=256
)
```

### 日志级别

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 调试信息 | 变量值、函数调用 |
| INFO | 正常操作 | 请求开始、完成 |
| WARNING | 警告信息 | API 限流、慢查询 |
| ERROR | 错误信息 | 异常、失败操作 |
| CRITICAL | 严重错误 | 系统崩溃 |

### 日志查看

#### Render 日志

```bash
# 实时查看日志
render logs -s helloagents-backend --tail

# 查看最近的日志
render logs -s helloagents-backend --num 100
```

#### 搜索日志

```bash
# 搜索特定关键词
render logs -s helloagents-backend | grep "error"

# 搜索特定时间范围
render logs -s helloagents-backend --from "2024-01-01T00:00:00Z"
```

---

## 健康检查

### 端点说明

| 端点 | 用途 | 检查内容 |
|------|------|----------|
| `/health` | 完整健康检查 | 所有组件（API、数据库、沙箱、AI） |
| `/health/ready` | 就绪检查 | 数据库连接（用于 Kubernetes Readiness Probe） |
| `/health/live` | 存活检查 | 基本响应（用于 Kubernetes Liveness Probe） |

### 响应格式

#### /health 响应示例

```json
{
  "status": "healthy",
  "timestamp": "2024-01-09T10:30:00.123456",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "sandbox_pool": {
      "status": "disabled",
      "message": "Container pool is not enabled"
    },
    "ai_service": {
      "status": "configured",
      "message": "AI service API key is configured"
    }
  }
}
```

#### 不健康时的响应（HTTP 503）

```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-09T10:30:00.123456",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "unhealthy",
      "message": "Database connection failed: connection timeout"
    }
  }
}
```

### 监控脚本

创建自动化健康检查脚本：

```bash
#!/bin/bash
# scripts/health-check.sh

API_URL="${API_URL:-https://your-backend.onrender.com}"

echo "Checking API health..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
status_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$status_code" -eq 200 ]; then
    echo "✅ API is healthy"
    echo "$body" | jq '.'
    exit 0
else
    echo "❌ API is unhealthy (HTTP $status_code)"
    echo "$body" | jq '.'
    exit 1
fi
```

使用方法：

```bash
chmod +x scripts/health-check.sh
./scripts/health-check.sh
```

---

## 性能监控

### 中间件

后端已配置性能监控中间件：

- `LoggingMiddleware`: 记录所有请求
- `PerformanceMonitoringMiddleware`: 追踪慢请求（> 1000ms）
- `ErrorLoggingMiddleware`: 记录所有错误

### 慢请求告警

当请求响应时间超过阈值时，自动记录警告日志：

```json
{
  "event": "slow_request",
  "path": "/api/execute",
  "method": "POST",
  "duration_ms": 1523.45,
  "threshold_ms": 1000.0,
  "user_id": 123
}
```

### 性能优化建议

#### 1. 数据库查询优化

```python
# 使用索引
db.query(User).filter(User.email == email).first()

# 批量查询
db.query(User).filter(User.id.in_(user_ids)).all()

# 预加载关联数据
db.query(User).options(joinedload(User.submissions)).all()
```

#### 2. 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_lesson_content(lesson_id: str):
    return course_manager.get_lesson_content(lesson_id)
```

#### 3. 异步操作

```python
import asyncio

# 并行执行多个任务
results = await asyncio.gather(
    task1(),
    task2(),
    task3()
)
```

---

## 告警配置

### Render 自动告警

Render 提供以下自动告警：

1. **服务下线告警**
   - 自动检测服务崩溃
   - Email 通知

2. **部署失败告警**
   - 构建失败
   - 健康检查失败
   - Email 通知

### Sentry 告警

#### 配置步骤

1. 进入 Sentry 项目 → **Alerts** → **Create Alert Rule**

2. **高错误率告警**
   ```
   When: The issue is seen more than 10 times in 1 minute
   Then: Send notification to #alerts channel in Slack
   ```

3. **性能降级告警**
   ```
   When: The p95 of transaction duration is above 1000ms
   Then: Send notification to #performance channel in Slack
   ```

4. **数据库错误告警**
   ```
   When: Any issue with tag "component:database"
   Then: Send notification to on-call engineer via PagerDuty
   ```

### 集成 Slack

1. 在 Sentry → **Settings** → **Integrations** → 添加 **Slack**
2. 授权 Slack workspace
3. 配置告警规则发送到指定频道

### 告警响应流程

```
收到告警
  ↓
确认告警严重程度
  ↓
检查监控面板（Sentry/Render）
  ↓
查看日志定位问题
  ↓
修复问题
  ↓
验证修复
  ↓
更新事故报告
```

---

## 监控面板

### Sentry Dashboard

推荐的 Dashboard 组件：

1. **概览**
   - 错误率趋势图
   - 响应时间 P95/P99
   - 活跃用户数

2. **错误详情**
   - Top 10 错误
   - 错误分布（按端点）
   - 错误趋势

3. **性能**
   - 慢请求列表
   - 数据库查询性能
   - 外部 API 调用时间

### Render Dashboard

- 实时日志流
- CPU 使用率
- 内存使用率
- 请求/秒（RPS）
- 部署历史

---

## 故障排查

### 常见问题

#### 1. 数据库连接失败

**症状**: `/health` 返回 503，数据库组件 unhealthy

**排查步骤**:
```bash
# 1. 检查数据库服务状态
render services list

# 2. 检查数据库日志
render logs -s helloagents-db

# 3. 检查连接字符串
render env -s helloagents-backend | grep DATABASE_URL
```

**解决方案**:
- 确认数据库服务运行正常
- 验证 `DATABASE_URL` 环境变量正确
- 检查数据库防火墙规则

#### 2. Sentry 未接收到事件

**症状**: Sentry Dashboard 没有新事件

**排查步骤**:
```bash
# 1. 检查 SENTRY_DSN 配置
render env -s helloagents-backend | grep SENTRY

# 2. 检查后端日志
render logs -s helloagents-backend | grep sentry
```

**解决方案**:
- 验证 `SENTRY_DSN` 正确
- 确认 Sentry 项目未暂停
- 检查网络连接

#### 3. 健康检查超时

**症状**: 服务频繁重启

**排查步骤**:
```bash
# 1. 手动测试健康检查
curl -v https://your-backend.onrender.com/health/ready

# 2. 检查响应时间
time curl https://your-backend.onrender.com/health/ready
```

**解决方案**:
- 增加健康检查超时时间
- 优化健康检查端点（移除耗时操作）
- 升级服务计划（提升性能）

---

## 安全最佳实践

### 环境变量管理

#### ✅ 推荐做法

- 使用 Render Dashboard 或 Railway Dashboard 设置敏感环境变量
- 不要在代码中硬编码 API 密钥
- 使用 `.env.example` 文件记录需要的环境变量（不包含实际值）
- 定期轮换 API 密钥

#### ❌ 避免做法

- 不要将 `.env` 文件提交到 Git
- 不要在日志中输出敏感信息
- 不要在错误消息中暴露内部实现细节

### 日志安全

```python
# ✅ 正确：不记录敏感信息
logger.info("user_login", user_id=user.id)

# ❌ 错误：记录密码
logger.info("user_login", password=password)
```

### Sentry 配置

```python
# 过滤敏感请求头
sentry_sdk.init(
    dsn=SENTRY_DSN,
    before_send=lambda event, hint: filter_sensitive_data(event),
    send_default_pii=False,  # 不发送个人身份信息
)
```

---

## 总结

### 监控清单

- [ ] Sentry 项目已创建并配置
- [ ] `SENTRY_DSN` 环境变量已设置
- [ ] 健康检查端点正常工作
- [ ] 日志系统运行正常
- [ ] 告警规则已配置
- [ ] Slack 集成已启用
- [ ] 监控面板已创建
- [ ] 故障响应流程已制定

### 相关文档

- [Sentry 官方文档](https://docs.sentry.io/)
- [Render 监控文档](https://render.com/docs/monitoring)
- [FastAPI 日志最佳实践](https://fastapi.tiangolo.com/tutorial/logging/)

### 支持联系

- 技术支持：team@helloagents.com
- Slack 频道：#devops
- 紧急联系：on-call engineer
