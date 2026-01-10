# Runbook: [告警名称]

## 基本信息

- **告警名称**: `ServiceDown` / `HighErrorRate` / etc.
- **严重级别**: Critical / Warning / Info
- **组件**: Backend / Frontend / Database / Sandbox
- **负责团队**: SRE / Backend / DevOps
- **最后更新**: YYYY-MM-DD

---

## 告警描述

### 什么触发了这个告警?

简要描述触发条件,例如:
- 后端服务 5 分钟内持续返回 HTTP 500 错误
- 错误率超过 5%
- API 响应时间 P95 超过 2 秒

### 为什么这个告警重要?

说明对用户和业务的影响:
- 用户无法访问服务
- 影响关键业务流程
- 可能导致数据丢失

---

## 初步诊断

### 1. 确认问题

快速验证告警是否真实:

```bash
# 检查服务健康状态
curl http://api.helloagents.com/health

# 检查最近的错误日志
docker logs --tail 100 helloagents-backend | grep ERROR

# 查看 Grafana 仪表板
open http://localhost:3000/d/helloagents-overview
```

### 2. 确定影响范围

```bash
# 检查错误率
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(http_requests_total{status_code=~"5.."}[5m])'

# 查看受影响的端点
# 在 Grafana 中查看 "Request Rate by Status Code" 面板
```

### 3. 收集基本信息

- 告警开始时间
- 最近的部署或变更
- 相关的其他告警
- 外部依赖状态 (AI API, Database)

---

## 常见原因和解决方案

### 原因 1: [服务崩溃/内存溢出]

**症状:**
- 容器不断重启
- 日志显示 OOM (Out of Memory) 错误

**诊断步骤:**
```bash
# 检查容器状态
docker ps -a | grep helloagents-backend

# 查看资源使用
docker stats helloagents-backend

# 检查 OOM 事件
docker inspect helloagents-backend | grep -i oom
```

**解决方案:**
```bash
# 临时: 重启服务
docker restart helloagents-backend

# 短期: 增加内存限制
# 编辑 docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G

# 长期: 优化代码,修复内存泄漏
# 分析内存使用,优化数据库查询,添加缓存
```

---

### 原因 2: [数据库连接耗尽]

**症状:**
- 日志显示 "connection pool exhausted"
- 数据库查询超时

**诊断步骤:**
```bash
# 检查数据库连接数
psql -c "SELECT count(*) FROM pg_stat_activity;"

# 查看活跃查询
psql -c "SELECT pid, now() - query_start as duration, query
         FROM pg_stat_activity
         WHERE state = 'active'
         ORDER BY duration DESC;"
```

**解决方案:**
```bash
# 临时: 重启应用释放连接
docker restart helloagents-backend

# 短期: 终止长时间运行的查询
psql -c "SELECT pg_terminate_backend(PID);"

# 长期: 优化连接池配置
# 编辑 backend/app/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # 增加连接池大小
    max_overflow=10,     # 增加溢出连接数
    pool_timeout=30,     # 连接超时
    pool_pre_ping=True   # 连接前 ping
)
```

---

### 原因 3: [外部依赖不可用]

**症状:**
- 日志显示 API 调用超时
- 特定功能失败 (如 AI 助手)

**诊断步骤:**
```bash
# 检查外部服务健康
curl -v https://api.deepseek.com/health

# 检查 DNS 解析
nslookup api.deepseek.com

# 检查网络连接
ping api.deepseek.com
```

**解决方案:**
```bash
# 临时: 启用降级模式 (如果已实现)
kubectl set env deployment/backend FALLBACK_MODE=true

# 短期: 使用备用服务
# 编辑 .env
DEEPSEEK_API_KEY=backup_key
# 或切换到备用 AI 服务

# 长期: 实现降级策略和重试机制
# - 添加超时和重试逻辑
# - 实现降级响应
# - 添加服务熔断器
```

---

### 原因 4: [代码部署问题]

**症状:**
- 告警在部署后立即触发
- 新功能导致错误

**诊断步骤:**
```bash
# 查看最近的部署
git log -n 5 --oneline

# 对比代码变更
git diff HEAD~1 HEAD

# 查看部署日志
# 在 CI/CD 系统中查看构建和部署日志
```

**解决方案:**
```bash
# 立即回滚到上一个稳定版本
./scripts/deployment/rollback.sh

# 或使用 Git
git revert HEAD
git push origin main

# 验证回滚成功
curl http://api.helloagents.com/health
```

---

## 升级路径

### 何时升级告警?

如果以下情况,升级到 Critical:
- 问题持续超过 15 分钟
- 影响超过 10% 的用户
- 无法在 30 分钟内解决

### 升级联系人

- **Team Lead**: name@helloagents.com / +1-xxx-xxx-xxxx
- **On-Call Engineer**: oncall@helloagents.com / PagerDuty
- **CTO**: cto@helloagents.com (仅 Critical)

---

## 恢复验证

问题修复后,验证以下内容:

```bash
# 1. 健康检查通过
curl http://api.helloagents.com/health
# 预期: HTTP 200, status: "healthy"

# 2. 错误率恢复正常
# 在 Grafana 中检查错误率 < 1%

# 3. 响应时间恢复
# P95 延迟 < 500ms

# 4. 告警已解决
# 在 Alertmanager 中确认告警状态

# 5. 关键功能测试
# 手动测试核心功能 (代码执行、AI 助手)
```

---

## 事后行动

### 立即行动 (24 小时内)

- [ ] 通知相关方问题已解决
- [ ] 更新事故追踪系统
- [ ] 收集事故时间线和日志

### 短期行动 (1 周内)

- [ ] 编写事故报告
- [ ] 进行事故复盘会议
- [ ] 识别根本原因
- [ ] 制定预防措施

### 长期行动 (1 个月内)

- [ ] 实施预防措施
- [ ] 更新监控和告警
- [ ] 改进文档和 Runbook
- [ ] 进行混沌工程测试

---

## 相关资源

### 监控链接

- **Grafana Dashboard**: http://localhost:3000/d/helloagents-overview
- **Prometheus Alerts**: http://localhost:9090/alerts
- **Alertmanager**: http://localhost:9093/#/alerts
- **Sentry**: https://sentry.io/organizations/helloagents/issues/

### 文档

- [监控系统架构](../MONITORING_ARCHITECTURE.md)
- [部署指南](../MONITORING_DEPLOYMENT_GUIDE.md)
- [SLO 定义](./SLO_DEFINITIONS.yml)

### 代码仓库

- **GitHub**: https://github.com/your-org/helloagents-platform
- **相关 PR**: [链接到相关的修复或功能 PR]

---

## 历史事故

### 2024-01-15: ServiceDown - 数据库连接耗尽

- **持续时间**: 45 分钟
- **根本原因**: 数据库连接池配置过小
- **解决方案**: 增加连接池大小,优化慢查询
- **预防措施**: 添加连接数监控告警

### 2024-01-20: HighErrorRate - 部署错误

- **持续时间**: 15 分钟
- **根本原因**: 新代码引入 bug
- **解决方案**: 快速回滚
- **预防措施**: 增强 CI/CD 测试覆盖率

---

## Runbook 维护

### 更新频率

- 每次事故后更新
- 每季度审查一次
- 系统架构变更时更新

### 责任人

- **Primary**: SRE Team
- **Reviewers**: Backend Team, DevOps Team

### 反馈

如有改进建议,请联系:
- Email: sre@helloagents.com
- Slack: #sre-team
- GitHub Issue: [创建 Runbook 改进建议]

---

**文档版本:** 1.0
**创建日期:** 2026-01-10
**最后更新:** 2026-01-10
**下次审查:** 2026-04-10
