# Architecture Decision Records (ADR) 索引

**HelloAgents Platform - 架构决策记录**

本文档维护所有重要的架构决策记录,确保技术选型和设计决策可追溯。

---

## 📋 ADR 清单

| ID | 标题 | 状态 | 日期 | 决策者 | 优先级 |
|----|------|------|------|--------|--------|
| [ADR-001](#adr-001-实施-jwt-认证和-rbac-授权) | 实施 JWT 认证和 RBAC 授权 | 提议 | 2026-01-10 | 技术架构师 | 🔴 紧急 |
| [ADR-002](#adr-002-实施-api-速率限制) | 实施 API 速率限制 | 提议 | 2026-01-10 | 技术架构师 | 🔴 高 |
| [ADR-003](#adr-003-引入服务层-service-layer) | 引入服务层 (Service Layer) | 提议 | 2026-01-10 | 技术架构师 | 🟡 中 |
| [ADR-004](#adr-004-实施-alembic-数据库迁移) | 实施 Alembic 数据库迁移 | 提议 | 2026-01-10 | 技术架构师 | 🔴 高 |
| [ADR-005](#adr-005-异步数据库操作) | 异步数据库操作 | 提议 | 2026-01-10 | 技术架构师 | 🟡 中 |
| [ADR-006](#adr-006-集成-prometheus-监控) | 集成 Prometheus 监控 | 提议 | 2026-01-10 | 技术架构师 | 🟡 中 |

---

## ADR-001: 实施 JWT 认证和 RBAC 授权

**状态**: 提议 (Proposed)
**日期**: 2026-01-10
**决策者**: 技术架构师
**优先级**: 🔴 紧急

### 背景

当前系统所有 API 端点公开访问,存在严重安全风险:
- 任何人都可以执行代码 → 资源滥用
- 任何人都可以访问用户数据 → 隐私泄露
- 任何人都可以调用 AI API → 成本失控

### 决策

采用 **JWT (JSON Web Token)** 认证 + **RBAC (基于角色的访问控制)** 授权。

### 理由

1. JWT 是业界标准,无状态,支持水平扩展
2. RBAC 简单清晰,满足当前需求
3. 兼容现有架构,无需大规模重构

### 技术选型

- `python-jose[cryptography]` - JWT 生成和验证
- `passlib[bcrypt]` - 密码哈希
- `python-multipart` - 表单数据解析

### 角色定义

```python
class Role(str, Enum):
    ADMIN = "admin"      # 管理员 (所有权限)
    USER = "user"        # 普通用户 (学习功能)
    GUEST = "guest"      # 访客 (只读)

class Permission(str, Enum):
    EXECUTE_CODE = "execute:code"
    VIEW_LESSONS = "view:lessons"
    MANAGE_USERS = "manage:users"
    VIEW_POOL_STATS = "view:pool_stats"
```

### 实施计划

- 后端实现: 3 天
- 前端实现: 2 天
- 测试和文档: 1 天
- **总计**: 6 天

### 影响

- **数据库**: 需添加 `users` 表
- **前端**: 需实现登录页面,Token 存储
- **API**: 所有端点需添加认证中间件
- **测试**: 需更新所有 API 测试

### 相关文档

- [详细实施方案](../ARCHITECTURE_ASSESSMENT_AND_EVOLUTION.md#adr-001-实施-jwt-认证和-rbac-授权)

---

## ADR-002: 实施 API 速率限制

**状态**: 提议 (Proposed)
**日期**: 2026-01-10
**决策者**: 技术架构师
**优先级**: 🔴 高

### 背景

当前 API 无速率限制,存在资源滥用风险。

### 决策

使用 **Slowapi** (FastAPI 的速率限制库)。

### 限制规则

| 端点 | 限制 | 理由 |
|------|------|------|
| `/api/v1/code/execute` | 10/分钟 | 代码执行消耗资源 |
| `/api/v1/chat` | 20/分钟 | AI API 调用成本高 |
| `/api/v1/lessons` | 100/分钟 | 读操作,限制宽松 |
| `/api/auth/login` | 5/分钟 | 防止暴力破解 |
| 全局 | 100/分钟 | 兜底限制 |

### 实施计划

- 实现: 1 天
- 测试: 0.5 天
- **总计**: 1.5 天

### 相关文档

- [详细实施方案](../ARCHITECTURE_ASSESSMENT_AND_EVOLUTION.md#adr-002-实施-api-速率限制)

---

## ADR-003: 引入服务层 (Service Layer)

**状态**: 提议 (Proposed)
**日期**: 2026-01-10
**决策者**: 技术架构师
**优先级**: 🟡 中

### 背景

当前业务逻辑直接耦合在路由中,难以测试和维护。

### 决策

采用 **服务层模式 (Service Layer Pattern)**。

### 架构设计

```
路由层 (Routes)
    ↓
服务层 (Services) - 业务逻辑
    ↓
仓库层 (Repositories) - 数据访问抽象
    ↓
ORM 层 (SQLAlchemy)
```

### 实施计划

- 设计和实现基础架构: 2 天
- 迁移现有路由: 3 天
- 单元测试: 2 天
- **总计**: 7 天

### 影响

**优点**:
- 业务逻辑易于单元测试
- 代码复用性高
- 关注点分离清晰

**缺点**:
- 增加代码层次
- 需要重构现有代码

### 相关文档

- [详细实施方案](../ARCHITECTURE_ASSESSMENT_AND_EVOLUTION.md#adr-003-引入服务层-service-layer)

---

## ADR-004: 实施 Alembic 数据库迁移

**状态**: 提议 (Proposed)
**日期**: 2026-01-10
**决策者**: 技术架构师
**优先级**: 🔴 高

### 背景

当前使用手动迁移脚本,无法追踪 schema 变更历史。

### 决策

采用 **Alembic** (SQLAlchemy 的迁移工具)。

### 理由

1. SQLAlchemy 官方推荐
2. 支持自动生成迁移脚本
3. 版本控制友好
4. 支持回滚

### 实施计划

- 初始化和配置: 0.5 天
- 创建初始迁移: 1 天
- 文档和培训: 0.5 天
- **总计**: 2 天

### CI/CD 集成

```yaml
- name: Run Database Migrations
  run: |
    cd backend
    alembic upgrade head
```

### 相关文档

- [详细实施方案](../ARCHITECTURE_ASSESSMENT_AND_EVOLUTION.md#adr-004-实施-alembic-数据库迁移)

---

## ADR-005: 异步数据库操作

**状态**: 提议 (Proposed)
**日期**: 2026-01-10
**决策者**: 技术架构师
**优先级**: 🟡 中

### 背景

当前 SQLAlchemy 使用同步模式,FastAPI 的异步优势未充分发挥。

### 决策

迁移到 **SQLAlchemy 2.0 异步模式**。

### 理由

1. 充分利用 FastAPI 异步性能
2. 数据库查询不再阻塞事件循环
3. 提升并发处理能力

### 技术选型

- `sqlalchemy[asyncio]` - 异步支持
- `asyncpg` - PostgreSQL 异步驱动
- `aiosqlite` - SQLite 异步驱动

### 迁移策略

**阶段 1**: 建立异步基础设施 (2 天)
**阶段 2**: 逐步迁移路由 (5 天)
**阶段 3**: 完全迁移 (3 天)

**总计**: 10 天

### 预期效果

- 性能提升 30-50%
- 并发能力提升

### 相关文档

- [详细实施方案](../ARCHITECTURE_ASSESSMENT_AND_EVOLUTION.md#adr-005-异步数据库操作)

---

## ADR-006: 集成 Prometheus 监控

**状态**: 提议 (Proposed)
**日期**: 2026-01-10
**决策者**: 技术架构师
**优先级**: 🟡 中

### 背景

当前只有 Sentry 错误追踪,缺少性能指标监控。

### 决策

集成 **Prometheus** + **Grafana**。

### 理由

1. Prometheus 是业界标准
2. 时间序列数据库,适合指标存储
3. 与 Grafana 集成,可视化强大

### 技术选型

- `prometheus-client` - Python 客户端
- `prometheus-fastapi-instrumentator` - FastAPI 集成

### 关键指标

- API 请求速率 (`http_requests_total`)
- API 响应时间 (`http_request_duration_seconds`)
- 代码执行次数 (`code_executions_total`)
- 容器池利用率 (`container_pool_available_containers`)

### 实施计划

- 集成 Prometheus: 1 天
- 添加自定义指标: 1 天
- 配置 Grafana 仪表板: 1 天
- **总计**: 3 天

### 相关文档

- [详细实施方案](../ARCHITECTURE_ASSESSMENT_AND_EVOLUTION.md#adr-006-集成-prometheus-监控)

---

## 📝 ADR 模板

创建新的 ADR 时,请使用以下模板:

```markdown
## ADR-XXX: 决策标题

**状态**: 提议 / 接受 / 已弃用 / 已替代
**日期**: YYYY-MM-DD
**决策者**: 名字/角色
**优先级**: 🔴 紧急 / 🔴 高 / 🟡 中 / 🟢 低

### 背景
(描述问题和上下文)

### 决策
(描述决策内容)

### 理由
(解释为什么做出这个决策)

### 备选方案
(列出考虑过但未采纳的方案)

### 影响
(描述决策的影响范围)

### 实施计划
(描述实施步骤和时间表)

### 相关文档
(链接到相关文档)
```

---

## 📊 ADR 统计

### 按状态分类

| 状态 | 数量 |
|------|------|
| 提议 (Proposed) | 6 |
| 接受 (Accepted) | 0 |
| 已弃用 (Deprecated) | 0 |
| 已替代 (Superseded) | 0 |
| **总计** | **6** |

### 按优先级分类

| 优先级 | 数量 | 预估工作量 |
|--------|------|-----------|
| 🔴 紧急 | 1 | 6 天 |
| 🔴 高 | 2 | 3.5 天 |
| 🟡 中 | 3 | 20 天 |
| 🟢 低 | 0 | 0 天 |
| **总计** | **6** | **29.5 天** |

---

## 🔗 相关文档

- [系统架构评估报告](../ARCHITECTURE_ASSESSMENT_AND_EVOLUTION.md) - 完整的技术评估
- [架构评估执行摘要](../ARCHITECTURE_EXECUTIVE_SUMMARY.md) - 管理层摘要
- [技术债务清单](../TECHNICAL_DEBT.md) - 所有技术债务
- [架构文档](./ARCHITECTURE.md) - 当前系统架构

---

## 📅 更新历史

| 日期 | 更新内容 | 更新人 |
|------|---------|--------|
| 2026-01-10 | 创建 ADR 索引,添加 6 个架构决策记录 | 技术架构师 |

---

**维护者**: 技术架构师
**最后更新**: 2026-01-10
**版本**: v1.0
