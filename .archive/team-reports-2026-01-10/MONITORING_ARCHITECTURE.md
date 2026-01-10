# HelloAgents Platform - 监控和可靠性系统架构

## 📋 目录

- [系统架构概览](#系统架构概览)
- [监控工具选型](#监控工具选型)
- [关键指标定义](#关键指标定义)
- [SLI/SLO/SLA 定义](#slislosla-定义)
- [告警策略](#告警策略)
- [实施路线图](#实施路线图)

---

## 系统架构概览

### 监控层次结构

```
┌─────────────────────────────────────────────────────────────┐
│                    告警和通知层                                │
│  Alertmanager → Slack/Email/PagerDuty                       │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│                    可视化层                                    │
│  Grafana Dashboards + Sentry Dashboard                      │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│                    聚合分析层                                  │
│  Prometheus (指标) + Sentry (错误追踪/APM)                    │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│                    数据采集层                                  │
│  FastAPI Middleware + Prometheus Client + Sentry SDK        │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│                    应用层                                      │
│  Backend API + Frontend + Docker Sandbox                    │
└─────────────────────────────────────────────────────────────┘
```

### 部署架构

```
Production Environment:
┌─────────────────────────────────────────────────────────────┐
│ Cloudflare Pages (Frontend)                                 │
│  └─ Sentry Browser SDK (RUM + Error Tracking)              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Render (Backend)                                             │
│  ├─ FastAPI + Prometheus Client                             │
│  ├─ Sentry Python SDK (APM + Error Tracking)               │
│  └─ Docker Sandbox (执行指标)                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 监控基础设施 (单独部署或使用托管服务)                           │
│  ├─ Prometheus (自托管 or Grafana Cloud)                     │
│  ├─ Grafana (自托管 or Grafana Cloud)                        │
│  ├─ Sentry (sentry.io SaaS)                                 │
│  └─ Alertmanager (自托管 or Grafana Cloud)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 监控工具选型

### 1. Prometheus + Grafana (指标监控)

**为什么选择:**
- ✅ 开源免费,社区活跃
- ✅ 强大的时间序列数据库
- ✅ 灵活的查询语言 (PromQL)
- ✅ 支持多种部署方式 (自托管/Grafana Cloud)
- ✅ 与 FastAPI 集成简单

**部署方式:**
- **开发环境:** Docker Compose 本地部署
- **生产环境:** Grafana Cloud (免费层) 或自托管

### 2. Sentry (错误追踪 + APM)

**为什么选择:**
- ✅ 行业标准的错误追踪平台
- ✅ 支持前后端统一监控
- ✅ 性能监控 (APM) 功能
- ✅ 免费层足够小型项目使用
- ✅ 已集成到项目中

**功能:**
- 前端错误追踪和崩溃报告
- 后端异常监控和堆栈追踪
- API 性能监控 (响应时间、吞吐量)
- 用户会话重放 (可选)
- 发布版本追踪

### 3. 健康检查系统

**已实现:**
- ✅ `/health` - 完整健康检查
- ✅ `/health/ready` - 就绪检查
- ✅ `/health/live` - 存活检查
- ✅ `health-check.sh` - 部署后验证脚本

**增强点:**
- 添加详细的组件健康状态
- 定期健康检查调度
- 健康检查指标导出到 Prometheus

---

## 关键指标定义

### 1. 前端指标 (Core Web Vitals)

| 指标 | 描述 | 目标 | 工具 |
|------|------|------|------|
| **LCP** (Largest Contentful Paint) | 最大内容绘制时间 | < 2.5s | Sentry RUM |
| **FID** (First Input Delay) | 首次输入延迟 | < 100ms | Sentry RUM |
| **CLS** (Cumulative Layout Shift) | 累积布局偏移 | < 0.1 | Sentry RUM |
| **TTI** (Time to Interactive) | 可交互时间 | < 3.5s | Sentry RUM |
| **Page Load Time** | 页面加载时间 | < 3s | Sentry RUM |

### 2. 后端 API 指标

| 指标 | 描述 | 采集方式 | 告警阈值 |
|------|------|----------|----------|
| **http_requests_total** | 请求总数 | Prometheus Counter | - |
| **http_request_duration_seconds** | 请求响应时间 | Prometheus Histogram | P95 > 200ms |
| **http_requests_in_progress** | 进行中的请求数 | Prometheus Gauge | > 100 |
| **http_request_errors_total** | 错误请求数 | Prometheus Counter | 错误率 > 1% |

### 3. Docker 沙箱指标

| 指标 | 描述 | 采集方式 | 告警阈值 |
|------|------|----------|----------|
| **sandbox_execution_duration_seconds** | 代码执行时间 | Prometheus Histogram | P95 > 5s |
| **sandbox_executions_total** | 执行总次数 | Prometheus Counter | - |
| **sandbox_execution_errors_total** | 执行错误总数 | Prometheus Counter | 错误率 > 5% |
| **sandbox_pool_available** | 可用容器数 | Prometheus Gauge | < 2 |
| **sandbox_pool_in_use** | 使用中容器数 | Prometheus Gauge | - |

### 4. AI 助手指标

| 指标 | 描述 | 采集方式 | 告警阈值 |
|------|------|----------|----------|
| **ai_chat_requests_total** | AI 聊天请求总数 | Prometheus Counter | - |
| **ai_chat_duration_seconds** | AI 响应时间 | Prometheus Histogram | P95 > 10s |
| **ai_chat_errors_total** | AI 错误总数 | Prometheus Counter | 错误率 > 2% |
| **ai_chat_tokens_total** | 消耗 Token 总数 | Prometheus Counter | - |

### 5. 数据库指标

| 指标 | 描述 | 采集方式 | 告警阈值 |
|------|------|----------|----------|
| **db_query_duration_seconds** | 查询响应时间 | Prometheus Histogram | P95 > 100ms |
| **db_connections_active** | 活跃连接数 | Prometheus Gauge | > 80% |
| **db_query_errors_total** | 查询错误总数 | Prometheus Counter | - |

### 6. 系统资源指标

| 指标 | 描述 | 采集方式 | 告警阈值 |
|------|------|----------|----------|
| **process_cpu_usage** | CPU 使用率 | Prometheus Gauge | > 80% |
| **process_memory_usage_bytes** | 内存使用量 | Prometheus Gauge | > 80% |
| **process_open_fds** | 打开文件描述符数 | Prometheus Gauge | > 90% limit |

---

## SLI/SLO/SLA 定义

### Service Level Indicators (SLI)

#### 1. 可用性 SLI

```yaml
name: api_availability
description: "API 服务可用性"
query: |
  sum(rate(http_requests_total{status_code!~"5.."}[30d]))
  /
  sum(rate(http_requests_total[30d]))
target: 99.5%
```

#### 2. 延迟 SLI

```yaml
name: api_latency_p95
description: "95分位 API 响应时间"
query: |
  histogram_quantile(0.95,
    rate(http_request_duration_seconds_bucket[30d])
  )
target: 200ms
```

#### 3. 错误率 SLI

```yaml
name: api_error_rate
description: "API 错误率"
query: |
  sum(rate(http_requests_total{status_code=~"5.."}[30d]))
  /
  sum(rate(http_requests_total[30d]))
target: < 0.1%
```

### Service Level Objectives (SLO)

| SLO | 目标 | 测量窗口 | 错误预算 |
|-----|------|----------|----------|
| **API 可用性** | 99.5% | 30天 | 3.6小时/月 |
| **API P95 延迟** | < 200ms | 7天 | - |
| **API 错误率** | < 0.1% | 7天 | - |
| **沙箱执行成功率** | > 95% | 7天 | 5% 失败率 |
| **AI 响应时间 P95** | < 10s | 7天 | - |

### Service Level Agreements (SLA)

#### 客户承诺 (面向最终用户)

```yaml
availability:
  commitment: 99.5%
  measurement_period: "monthly"
  downtime_allowance: "3.6 hours/month"

performance:
  api_response_time_p95: "< 500ms"
  page_load_time: "< 3s"

support:
  response_time: "< 24 hours"
  resolution_time: "< 48 hours"

penalties:
  - availability < 99.5%: "服务积分补偿"
  - availability < 99.0%: "退款 10%"
```

---

## 告警策略

### 告警级别定义

| 级别 | 描述 | 响应时间 | 通知方式 |
|------|------|----------|----------|
| **Critical** | 服务完全不可用或严重降级 | 立即 | PagerDuty + Slack + Email |
| **Warning** | 服务性能下降或潜在问题 | 30分钟 | Slack + Email |
| **Info** | 信息性通知 | 最佳努力 | Slack |

### 告警规则

#### 1. 可用性告警

```yaml
# Critical: 服务不可用
- alert: ServiceDown
  expr: up{job="helloagents-backend"} == 0
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "HelloAgents 后端服务不可用"
    description: "服务已停机超过 2 分钟"

# Critical: 高错误率
- alert: HighErrorRate
  expr: |
    rate(http_requests_total{status_code=~"5.."}[5m])
    /
    rate(http_requests_total[5m]) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "API 错误率过高"
    description: "5xx 错误率为 {{ $value | humanizePercentage }} (阈值: 5%)"
```

#### 2. 性能告警

```yaml
# Warning: 高延迟
- alert: HighLatency
  expr: |
    histogram_quantile(0.95,
      rate(http_request_duration_seconds_bucket[5m])
    ) > 0.5
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "API 响应时间过高"
    description: "P95 延迟为 {{ $value }}s (阈值: 0.5s)"

# Warning: 沙箱执行慢
- alert: SlowSandboxExecution
  expr: |
    histogram_quantile(0.95,
      rate(sandbox_execution_duration_seconds_bucket[5m])
    ) > 10
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "代码沙箱执行缓慢"
    description: "P95 执行时间为 {{ $value }}s (阈值: 10s)"
```

#### 3. 资源告警

```yaml
# Warning: 高内存使用
- alert: HighMemoryUsage
  expr: |
    process_memory_usage_bytes / process_memory_limit_bytes > 0.85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "内存使用率过高"
    description: "内存使用率为 {{ $value | humanizePercentage }} (阈值: 85%)"

# Warning: 容器池耗尽
- alert: SandboxPoolDepleted
  expr: sandbox_pool_available < 2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "沙箱容器池资源不足"
    description: "可用容器数仅剩 {{ $value }} 个"
```

#### 4. 业务告警

```yaml
# Info: AI 服务错误率上升
- alert: AIServiceErrors
  expr: |
    rate(ai_chat_errors_total[5m])
    /
    rate(ai_chat_requests_total[5m]) > 0.1
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "AI 助手错误率上升"
    description: "错误率为 {{ $value | humanizePercentage }} (阈值: 10%)"
```

### 告警路由配置

```yaml
# Alertmanager 配置
route:
  receiver: 'slack-general'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 12h

  routes:
    # Critical 告警 -> PagerDuty + Slack
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true

    - match:
        severity: critical
      receiver: 'slack-incidents'

    # Warning 告警 -> Slack
    - match:
        severity: warning
      receiver: 'slack-alerts'

    # Info 告警 -> Slack (低优先级)
    - match:
        severity: info
      receiver: 'slack-general'

receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_KEY>'

  - name: 'slack-incidents'
    slack_configs:
      - api_url: '<SLACK_WEBHOOK_URL>'
        channel: '#incidents'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'

  - name: 'slack-alerts'
    slack_configs:
      - api_url: '<SLACK_WEBHOOK_URL>'
        channel: '#alerts'
        title: '⚠️ WARNING: {{ .GroupLabels.alertname }}'

  - name: 'slack-general'
    slack_configs:
      - api_url: '<SLACK_WEBHOOK_URL>'
        channel: '#monitoring'
        title: 'ℹ️ INFO: {{ .GroupLabels.alertname }}'
```

---

## 实施路线图

### Phase 1: 基础监控 (1周)

**目标:** 建立基本的指标收集和可视化

- [x] Sentry 错误追踪已集成
- [ ] 添加 Prometheus 指标导出
- [ ] 部署 Prometheus (Docker Compose)
- [ ] 部署 Grafana
- [ ] 创建基础仪表板

**产出:**
- FastAPI Prometheus 中间件
- Docker Compose 监控栈
- 基础 Grafana 仪表板

### Phase 2: 告警系统 (1周)

**目标:** 建立自动化告警机制

- [ ] 配置 Alertmanager
- [ ] 定义告警规则
- [ ] 集成 Slack 通知
- [ ] 测试告警流程

**产出:**
- Alertmanager 配置
- 告警规则文件
- Slack 集成
- 告警测试报告

### Phase 3: APM 增强 (1周)

**目标:** 深化性能监控

- [ ] Sentry APM 启用
- [ ] 前端性能监控 (RUM)
- [ ] 数据库查询监控
- [ ] AI 调用追踪

**产出:**
- Sentry Performance 配置
- 前端 RUM 集成
- 性能优化建议

### Phase 4: SLO/SLA 体系 (3天)

**目标:** 建立可靠性目标和度量

- [ ] 定义 SLI/SLO
- [ ] 创建 SLO 仪表板
- [ ] 错误预算计算
- [ ] SLA 文档

**产出:**
- SLI/SLO 定义文档
- SLO Dashboard
- 错误预算追踪表
- 客户 SLA 协议

### Phase 5: 优化和自动化 (持续)

**目标:** 持续优化和自动化

- [ ] 告警规则调优 (减少噪音)
- [ ] 容量规划报告
- [ ] 自动化运维脚本
- [ ] 监控数据分析

**产出:**
- 月度监控报告
- 容量规划建议
- 自动化工具集
- 监控最佳实践文档

---

## 成本分析

### 开发环境 (本地)

| 组件 | 成本 | 资源需求 |
|------|------|----------|
| Prometheus | 免费 | 512MB RAM, 1 CPU |
| Grafana | 免费 | 256MB RAM, 1 CPU |
| Alertmanager | 免费 | 128MB RAM, 0.5 CPU |
| **总计** | **$0/月** | **~1GB RAM** |

### 生产环境 (推荐方案)

| 服务 | 方案 | 成本 | 说明 |
|------|------|------|------|
| **Sentry** | 免费层 | $0/月 | 5K errors/月 |
| **Grafana Cloud** | 免费层 | $0/月 | 10K metrics, 50GB logs |
| **Slack** | 免费层 | $0/月 | 告警通知 |
| **PagerDuty** | 免费层 (可选) | $0/月 | 1 用户, 25 服务 |
| **总计** | - | **$0/月** | **足够小型项目** |

### 扩展方案 (未来增长)

| 服务 | 方案 | 成本 | 功能 |
|------|------|------|------|
| Sentry | Team | $26/月 | 50K errors/月 |
| Grafana Cloud | Pro | $49/月 | 100K metrics |
| PagerDuty | Professional | $25/月/用户 | 全功能 |
| **总计** | - | **~$100/月** | **支持更大规模** |

---

## 参考资料

### 官方文档
- [Prometheus 文档](https://prometheus.io/docs/)
- [Grafana 文档](https://grafana.com/docs/)
- [Sentry 文档](https://docs.sentry.io/)
- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/monitoring/)

### 最佳实践
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [Site Reliability Workbook](https://sre.google/workbook/table-of-contents/)
- [The Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)

### 工具和库
- [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [structlog](https://www.structlog.org/)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Sentry JavaScript SDK](https://docs.sentry.io/platforms/javascript/)

---

**文档版本:** 1.0
**最后更新:** 2026-01-10
**负责人:** SRE Team
