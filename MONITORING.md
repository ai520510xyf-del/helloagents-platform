# HelloAgents Platform - 监控系统

## 📊 概览

HelloAgents Platform 采用现代化的可观测性栈,提供全面的监控、告警和性能追踪能力。

### 监控目标

- ✅ **系统可用性** > 99.5%
- ✅ **API P95 响应时间** < 200ms
- ✅ **错误率** < 0.1%
- ✅ **完整的错误追踪和性能分析**

---

## 🏗️ 监控架构

```
┌────────────────────────────────────────────────────────────┐
│                     告警和通知层                              │
│         Alertmanager → Slack/Email/PagerDuty               │
└────────────────────────────────────────────────────────────┘
                            ↑
┌────────────────────────────────────────────────────────────┐
│                     可视化层                                 │
│         Grafana Dashboards + Sentry Dashboard              │
└────────────────────────────────────────────────────────────┘
                            ↑
┌────────────────────────────────────────────────────────────┐
│                   聚合分析层                                 │
│       Prometheus (指标) + Sentry (错误追踪/APM)             │
└────────────────────────────────────────────────────────────┘
                            ↑
┌────────────────────────────────────────────────────────────┐
│                   数据采集层                                 │
│  FastAPI Middleware + Prometheus Client + Sentry SDK       │
└────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 启动监控系统

```bash
# 1. 启动监控栈 (Prometheus + Grafana + Alertmanager)
docker-compose -f docker-compose.monitoring.yml up -d

# 2. 安装 Python 依赖
cd backend
pip install prometheus-client

# 3. 访问监控界面
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/admin)
# Alertmanager: http://localhost:9093
```

### 配置 Sentry (可选,生产环境推荐)

```bash
# 1. 获取 Sentry DSN
# 访问 https://sentry.io/ 创建项目

# 2. 配置后端
echo "SENTRY_DSN=https://your-dsn@sentry.io/project-id" >> backend/.env

# 3. 配置前端
echo "VITE_SENTRY_DSN=https://your-dsn@sentry.io/project-id" >> frontend/.env
```

---

## 📋 监控组件

### 1. Prometheus (指标收集)

**功能:**
- 时间序列数据库
- 指标采集和存储
- 强大的查询语言 (PromQL)

**关键指标:**
- HTTP 请求 (总数、延迟、错误率)
- 沙箱执行 (执行次数、时间、成功率)
- AI 助手 (请求数、响应时间、Token 消耗)
- 数据库 (查询时间、连接数)
- 系统资源 (CPU、内存、文件描述符)

**访问地址:** http://localhost:9090

### 2. Grafana (可视化)

**功能:**
- 监控仪表板
- 数据可视化
- 告警管理界面

**预置仪表板:**
- **HelloAgents Overview** - 系统总览
- **API Performance** - API 性能分析
- **Sandbox Metrics** - 沙箱执行指标
- **SLO Dashboard** - 服务等级目标追踪

**访问地址:** http://localhost:3000

**默认凭证:**
- 用户名: `admin`
- 密码: `admin` (首次登录后修改)

### 3. Alertmanager (告警路由)

**功能:**
- 告警去重和分组
- 告警路由和静默
- 多渠道通知 (Slack, Email, PagerDuty)

**告警级别:**
- **Critical** - 服务不可用或严重降级 → PagerDuty + Slack
- **Warning** - 性能下降或潜在问题 → Slack + Email
- **Info** - 信息性通知 → Slack

**访问地址:** http://localhost:9093

### 4. Sentry (错误追踪 + APM)

**功能:**
- 前后端错误追踪
- 性能监控 (APM)
- 用户会话追踪
- 发布版本追踪

**集成:**
- ✅ 后端: FastAPI + Sentry Python SDK
- ✅ 前端: React + Sentry JavaScript SDK

**访问地址:** https://sentry.io/

---

## 📊 关键指标

### 黄金信号 (Golden Signals)

| 指标 | 描述 | 目标 | Prometheus 查询 |
|------|------|------|----------------|
| **延迟 (Latency)** | API 响应时间 | P95 < 200ms | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` |
| **流量 (Traffic)** | 请求速率 | - | `rate(http_requests_total[5m])` |
| **错误 (Errors)** | 错误率 | < 0.1% | `rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m])` |
| **饱和度 (Saturation)** | 资源使用率 | < 80% | `process_memory_usage / process_memory_limit` |

### 业务指标

| 指标 | 描述 | 重要性 |
|------|------|--------|
| **代码执行成功率** | 沙箱执行成功百分比 | 高 |
| **AI 响应时间** | AI 助手平均响应时间 | 高 |
| **用户活跃度** | 活跃用户数和会话数 | 中 |
| **功能使用率** | 各功能模块使用频率 | 中 |

---

## 🎯 SLI/SLO/SLA

### Service Level Indicators (SLI)

```yaml
# API 可用性
api_availability:
  query: "sum(rate(http_requests_total{status_code!~'5..'}[30d])) / sum(rate(http_requests_total[30d]))"
  target: 99.5%

# API 延迟
api_latency_p95:
  query: "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[30d]))"
  target: 200ms
```

### Service Level Objectives (SLO)

| SLO | 目标 | 测量窗口 | 错误预算 |
|-----|------|----------|----------|
| API 可用性 | 99.5% | 30 天 | 3.6 小时/月 |
| API P95 延迟 | < 200ms | 7 天 | - |
| 沙箱成功率 | > 95% | 7 天 | 5% |

### Service Level Agreements (SLA)

面向用户的承诺:
- **可用性承诺**: 99.5% (3.6 小时停机/月)
- **API 响应时间**: P95 < 500ms
- **页面加载时间**: < 3s
- **支持响应时间**: Critical < 1小时, High < 4小时

**详细定义:** 查看 [SLO_DEFINITIONS.yml](./monitoring/SLO_DEFINITIONS.yml)

---

## 🚨 告警规则

### 可用性告警

| 告警名称 | 触发条件 | 级别 | 持续时间 |
|---------|---------|------|----------|
| ServiceDown | 服务不响应 | Critical | 2m |
| HighErrorRate | 5xx 错误率 > 5% | Critical | 5m |
| MediumErrorRate | 5xx 错误率 > 1% | Warning | 10m |

### 性能告警

| 告警名称 | 触发条件 | 级别 | 持续时间 |
|---------|---------|------|----------|
| HighLatency | P95 > 500ms | Warning | 10m |
| VeryHighLatency | P95 > 2s | Critical | 5m |
| SlowSandboxExecution | 沙箱 P95 > 10s | Warning | 10m |

### 资源告警

| 告警名称 | 触发条件 | 级别 | 持续时间 |
|---------|---------|------|----------|
| HighMemoryUsage | 内存 > 85% | Warning | 5m |
| HighCPUUsage | CPU > 80% | Warning | 10m |
| SandboxPoolDepleted | 可用容器 < 2 | Warning | 5m |

**完整规则:** 查看 [alerts/helloagents.yml](./monitoring/prometheus/alerts/helloagents.yml)

---

## 📈 Grafana 仪表板

### 预置仪表板

#### 1. HelloAgents Overview (总览)
- 服务可用性 (30天)
- 请求速率
- P95 响应时间
- 错误率趋势
- 沙箱执行统计
- AI 助手性能

#### 2. API Performance (API 性能)
- 按端点的请求分布
- 响应时间热力图
- 错误率按状态码
- 慢查询追踪

#### 3. Sandbox Metrics (沙箱指标)
- 执行成功率
- 执行时间分布
- 容器池使用情况
- 错误类型分析

#### 4. SLO Dashboard (SLO 追踪)
- SLO 达成率
- 错误预算消耗
- SLI 趋势图
- 合规性报告

**导入仪表板:**
```bash
# 仪表板位于 monitoring/grafana/dashboards/
# 启动 Docker Compose 时自动加载
```

---

## 🔧 配置指南

### 通知渠道配置

#### Slack 集成

1. 创建 Slack Incoming Webhook
2. 编辑 `monitoring/alertmanager/alertmanager.yml`:

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

receivers:
  - name: 'slack-critical'
    slack_configs:
      - channel: '#incidents'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
```

3. 重启 Alertmanager:

```bash
docker-compose -f docker-compose.monitoring.yml restart alertmanager
```

#### Email 通知

编辑 `monitoring/alertmanager/alertmanager.yml`:

```yaml
receivers:
  - name: 'email-alerts'
    email_configs:
      - to: 'oncall@helloagents.com'
        from: 'alertmanager@helloagents.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'your-email@gmail.com'
        auth_password: 'your-app-password'
```

#### PagerDuty 集成

```yaml
receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
```

---

## 📚 文档和资源

### 核心文档

- **[监控系统架构](./MONITORING_ARCHITECTURE.md)** - 架构设计和工具选型
- **[部署指南](./MONITORING_DEPLOYMENT_GUIDE.md)** - 详细部署步骤和配置
- **[SLO 定义](./monitoring/SLO_DEFINITIONS.yml)** - SLI/SLO/SLA 详细定义
- **[Runbook 模板](./monitoring/RUNBOOK_TEMPLATE.md)** - 事故响应手册模板

### 配置文件

- `monitoring/prometheus/prometheus.yml` - Prometheus 配置
- `monitoring/prometheus/alerts/` - 告警规则
- `monitoring/alertmanager/alertmanager.yml` - 告警路由配置
- `monitoring/grafana/dashboards/` - Grafana 仪表板

### 快速链接

| 服务 | URL | 凭证 |
|------|-----|------|
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Alertmanager | http://localhost:9093 | - |
| Backend Metrics | http://localhost:8000/metrics | - |
| Backend Health | http://localhost:8000/health | - |

---

## 🛠️ 常用操作

### 查看指标

```bash
# 查看所有指标
curl http://localhost:8000/metrics

# 执行 PromQL 查询
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=http_requests_total'
```

### 管理告警

```bash
# 查看活跃告警
curl http://localhost:9093/api/v2/alerts

# 创建静默规则 (维护窗口)
curl -X POST http://localhost:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{"matchers":[{"name":"alertname","value":"HighErrorRate"}]}'
```

### 备份和恢复

```bash
# 备份 Prometheus 数据
docker run --rm -v prometheus_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz /data

# 备份 Grafana 配置
docker run --rm -v grafana_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/grafana-backup.tar.gz /data
```

---

## 🔍 故障排查

### Prometheus 无法抓取指标

```bash
# 检查后端 /metrics 端点
curl http://localhost:8000/metrics

# 查看 Prometheus 日志
docker logs helloagents-prometheus | grep error

# 验证配置
docker exec helloagents-prometheus promtool check config /etc/prometheus/prometheus.yml
```

### Grafana 无数据

1. 检查数据源: Configuration → Data Sources → Prometheus → Test
2. 验证查询: Explore → 输入查询 → Run
3. 检查时间范围: 确保有数据的时间段

### 告警未触发

```bash
# 检查告警规则
curl http://localhost:9090/api/v1/rules

# 检查 Alertmanager 配置
docker exec helloagents-alertmanager amtool check-config
```

---

## 📊 性能指标

### 监控系统资源消耗

| 组件 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| Prometheus | 0.5-1 核 | 512MB-1GB | 10GB/月 |
| Grafana | 0.1-0.5 核 | 256MB | 100MB |
| Alertmanager | 0.1 核 | 128MB | 50MB |

### 数据保留策略

- **Prometheus**: 30 天 (可配置)
- **Grafana**: 永久 (仪表板和配置)
- **Sentry**: 根据计划 (免费层 30 天)

---

## 🎓 最佳实践

### 1. 监控金字塔

```
      告警 (Alerts)
        ↑
    仪表板 (Dashboards)
        ↑
      日志 (Logs)
        ↑
    指标 (Metrics)
        ↑
    追踪 (Traces)
```

### 2. 告警设计原则

- ✅ **可操作**: 每个告警都有明确的处理步骤
- ✅ **降噪**: 避免告警疲劳
- ✅ **分级**: Critical/Warning/Info 明确区分
- ✅ **Runbook**: 关联处理文档

### 3. 仪表板设计

- ✅ **黄金信号优先**: 延迟、流量、错误、饱和度
- ✅ **时间范围**: 提供 1h/6h/24h/7d 选项
- ✅ **关键指标醒目**: 使用大号 Stat 面板
- ✅ **趋势可见**: 使用图表展示历史数据

---

## 🆘 支持

如遇到问题,请联系:

- **GitHub Issues**: https://github.com/your-org/helloagents-platform/issues
- **Email**: support@helloagents.com
- **Discord**: https://discord.gg/helloagents
- **文档**: https://docs.helloagents.com

---

## 📝 更新日志

### v1.0.0 (2026-01-10)

- ✅ 完整监控系统架构
- ✅ Prometheus + Grafana + Alertmanager 集成
- ✅ Sentry 错误追踪和 APM
- ✅ 预置仪表板和告警规则
- ✅ SLI/SLO/SLA 定义
- ✅ 完整文档和 Runbook

---

**文档版本:** 1.0.0
**最后更新:** 2026-01-10
**维护者:** SRE Team
