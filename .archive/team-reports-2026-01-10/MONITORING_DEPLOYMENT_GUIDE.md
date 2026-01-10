# HelloAgents Platform - 监控系统部署和运维指南

## 📋 目录

- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [配置指南](#配置指南)
- [运维操作](#运维操作)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)

---

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (后端)
- Node.js 18+ (前端)

### 5 分钟启动监控系统

```bash
# 1. 克隆项目
git clone https://github.com/your-org/helloagents-platform.git
cd helloagents-platform

# 2. 启动监控栈
docker-compose -f docker-compose.monitoring.yml up -d

# 3. 安装 Prometheus 客户端库
cd backend
pip install prometheus-client

# 4. 访问监控界面
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Alertmanager: http://localhost:9093
```

---

## 详细部署步骤

### Step 1: 后端集成 Prometheus

#### 1.1 安装依赖

```bash
cd backend
pip install prometheus-client
```

添加到 `requirements.txt`:
```txt
prometheus-client==0.19.0
```

#### 1.2 集成 Prometheus 中间件

编辑 `backend/app/main.py`,添加 Prometheus 中间件:

```python
from app.middleware.prometheus_middleware import (
    PrometheusMiddleware,
    get_metrics
)
from prometheus_client import CONTENT_TYPE_LATEST
from fastapi.responses import Response

# 添加 Prometheus 中间件
app.add_middleware(PrometheusMiddleware)

# 添加 /metrics 端点
@app.get("/metrics")
async def metrics():
    """
    Prometheus 指标导出端点
    """
    return Response(
        content=get_metrics(),
        media_type=CONTENT_TYPE_LATEST
    )
```

#### 1.3 集成业务指标

在代码执行处添加指标记录:

```python
from app.middleware.prometheus_middleware import record_sandbox_execution

# 在沙箱执行后
record_sandbox_execution(
    language="python",
    duration=execution_time,
    success=success
)
```

在 AI 聊天处添加指标记录:

```python
from app.middleware.prometheus_middleware import record_ai_chat_request

# 在 AI 聊天完成后
record_ai_chat_request(
    duration=response_time,
    success=True,
    tokens=response.usage.total_tokens,
    model="deepseek-chat"
)
```

### Step 2: 前端集成 Sentry

#### 2.1 安装 Sentry SDK

```bash
cd frontend
npm install @sentry/react @sentry/tracing
```

#### 2.2 初始化 Sentry

编辑 `frontend/src/main.tsx`:

```typescript
import { initSentry } from './config/sentry';

// 初始化 Sentry
initSentry();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

#### 2.3 配置环境变量

编辑 `.env.production`:

```env
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
VITE_APP_VERSION=1.0.0
```

### Step 3: 启动监控栈

#### 3.1 启动 Docker Compose

```bash
# 启动所有监控组件
docker-compose -f docker-compose.monitoring.yml up -d

# 查看服务状态
docker-compose -f docker-compose.monitoring.yml ps

# 查看日志
docker-compose -f docker-compose.monitoring.yml logs -f
```

#### 3.2 验证服务

```bash
# 检查 Prometheus
curl http://localhost:9090/-/healthy

# 检查 Grafana
curl http://localhost:3000/api/health

# 检查 Alertmanager
curl http://localhost:9093/-/healthy

# 检查后端指标
curl http://localhost:8000/metrics
```

### Step 4: 配置 Grafana

#### 4.1 登录 Grafana

访问 http://localhost:3000

- 用户名: `admin`
- 密码: `admin` (首次登录后修改)

#### 4.2 验证数据源

1. 导航到 **Configuration** → **Data Sources**
2. 确认 Prometheus 数据源已配置
3. 点击 **Test** 确认连接成功

#### 4.3 导入仪表板

仪表板已自动加载到 `/var/lib/grafana/dashboards`:

1. 导航到 **Dashboards** → **Browse**
2. 打开 **HelloAgents** 文件夹
3. 选择 **HelloAgents Platform - Overview**

或手动导入:

1. 点击 **+** → **Import**
2. 上传 `monitoring/grafana/dashboards/helloagents-overview.json`
3. 选择 Prometheus 数据源
4. 点击 **Import**

### Step 5: 配置告警

#### 5.1 验证告警规则

访问 Prometheus 规则页面:
http://localhost:9090/rules

确认所有告警规则已加载。

#### 5.2 配置 Slack 通知 (可选)

1. 创建 Slack Incoming Webhook:
   - 访问 https://api.slack.com/messaging/webhooks
   - 创建新的 Webhook URL

2. 编辑 `monitoring/alertmanager/alertmanager.yml`:

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

receivers:
  - name: 'slack-critical'
    slack_configs:
      - channel: '#incidents'
        # ... (取消注释配置)
```

3. 重启 Alertmanager:

```bash
docker-compose -f docker-compose.monitoring.yml restart alertmanager
```

#### 5.3 配置 Email 通知 (可选)

编辑 `monitoring/alertmanager/alertmanager.yml`:

```yaml
receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@helloagents.com'
        from: 'alertmanager@helloagents.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'your-email@gmail.com'
        auth_password: 'your-app-password'
```

### Step 6: 配置 Sentry (生产环境)

#### 6.1 创建 Sentry 项目

1. 访问 https://sentry.io/
2. 创建新项目 (React + Python)
3. 获取 DSN

#### 6.2 配置后端

编辑 `backend/.env`:

```env
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

#### 6.3 配置前端

编辑 `frontend/.env.production`:

```env
VITE_SENTRY_DSN=https://your-frontend-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
```

---

## 配置指南

### Prometheus 配置

#### 修改抓取间隔

编辑 `monitoring/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s  # 改为 30s 降低负载
  evaluation_interval: 15s
```

#### 添加新的抓取目标

```yaml
scrape_configs:
  - job_name: 'my-service'
    static_configs:
      - targets: ['my-service:9090']
        labels:
          service: 'my-service'
```

#### 配置远程存储 (Grafana Cloud)

```yaml
remote_write:
  - url: "https://prometheus-prod-us-central-0.grafana.net/api/prom/push"
    basic_auth:
      username: YOUR_USERNAME
      password: YOUR_PASSWORD
```

### 告警规则调优

#### 减少噪音

编辑 `monitoring/prometheus/alerts/helloagents.yml`:

```yaml
# 增加 for 时长
- alert: HighErrorRate
  expr: ...
  for: 10m  # 从 5m 改为 10m
```

#### 添加自定义告警

```yaml
- alert: CustomAlert
  expr: your_metric > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Your alert summary"
    description: "Your alert description"
```

### Grafana 仪表板定制

#### 修改刷新间隔

仪表板设置 → Time picker → Refresh interval → 选择 30s 或 1m

#### 添加新面板

1. 点击 **Add panel**
2. 选择 **Add new panel**
3. 配置查询:
   ```promql
   rate(your_metric[5m])
   ```
4. 保存仪表板

---

## 运维操作

### 日常检查清单

#### 每日检查

```bash
# 1. 检查服务健康
docker-compose -f docker-compose.monitoring.yml ps

# 2. 检查磁盘空间
df -h | grep prometheus
df -h | grep grafana

# 3. 查看活跃告警
curl http://localhost:9093/api/v2/alerts | jq .

# 4. 检查 SLO 达成率
# 访问 Grafana SLO 仪表板
```

#### 每周检查

- 审查告警历史和解决情况
- 检查错误预算消耗
- 优化慢查询和性能瓶颈
- 更新 Runbook 文档

#### 每月检查

- 生成可用性报告
- 审查 SLA 合规性
- 容量规划和资源优化
- 监控系统升级

### 常用命令

#### 查看 Prometheus 指标

```bash
# 查看所有指标
curl http://localhost:9090/api/v1/label/__name__/values | jq .

# 执行 PromQL 查询
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="helloagents-backend"}'

# 查看告警规则
curl http://localhost:9090/api/v1/rules | jq .
```

#### 管理告警

```bash
# 查看活跃告警
curl http://localhost:9093/api/v2/alerts

# 创建静默规则
curl -X POST http://localhost:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "alertname", "value": "HighErrorRate", "isRegex": false}],
    "startsAt": "2024-01-01T00:00:00Z",
    "endsAt": "2024-01-01T01:00:00Z",
    "createdBy": "admin",
    "comment": "Maintenance window"
  }'
```

#### 备份和恢复

```bash
# 备份 Prometheus 数据
docker run --rm -v prometheus_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup-$(date +%Y%m%d).tar.gz /data

# 备份 Grafana 数据
docker run --rm -v grafana_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/grafana-backup-$(date +%Y%m%d).tar.gz /data

# 恢复数据
docker run --rm -v prometheus_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/prometheus-backup-20240101.tar.gz -C /
```

### 性能优化

#### Prometheus 查询优化

```promql
# 避免高基数标签
sum(rate(http_requests_total[5m])) by (method, status_code)
# 而不是
sum(rate(http_requests_total[5m])) by (method, status_code, user_id)

# 使用 recording rules 预计算
# 在 prometheus.yml 中定义
groups:
  - name: example
    rules:
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)
```

#### 数据保留策略

```bash
# 修改保留时间 (默认 30 天)
docker-compose -f docker-compose.monitoring.yml up -d prometheus \
  --storage.tsdb.retention.time=15d
```

---

## 故障排查

### Prometheus 无法抓取指标

**症状:** Targets 显示 "Down"

**排查步骤:**

```bash
# 1. 检查后端 /metrics 端点
curl http://localhost:8000/metrics

# 2. 检查网络连通性
docker exec helloagents-prometheus ping host.docker.internal

# 3. 查看 Prometheus 日志
docker logs helloagents-prometheus | grep error

# 4. 验证配置文件
docker exec helloagents-prometheus promtool check config /etc/prometheus/prometheus.yml
```

**解决方案:**

- 确认后端已添加 Prometheus 中间件
- 检查 Docker 网络配置
- 验证 `host.docker.internal` 可访问

### Grafana 无数据显示

**症状:** 仪表板面板显示 "No data"

**排查步骤:**

1. 检查数据源连接: Configuration → Data Sources → Prometheus → Test
2. 验证查询语句: Explore → 输入查询 → Run query
3. 检查时间范围: 确保选择了有数据的时间段
4. 查看 Grafana 日志:

```bash
docker logs helloagents-grafana | grep error
```

### 告警未触发

**症状:** 满足条件但没有收到告警

**排查步骤:**

```bash
# 1. 检查告警规则状态
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.name=="YourAlert")'

# 2. 检查 Alertmanager 配置
docker exec helloagents-alertmanager amtool check-config /etc/alertmanager/alertmanager.yml

# 3. 查看 Alertmanager 日志
docker logs helloagents-alertmanager

# 4. 测试告警通知
amtool alert add alertname=test severity=critical
```

### 容器重启问题

**症状:** 监控容器频繁重启

**排查步骤:**

```bash
# 查看容器状态
docker-compose -f docker-compose.monitoring.yml ps

# 查看容器日志
docker logs --tail 100 helloagents-prometheus

# 检查资源使用
docker stats helloagents-prometheus

# 检查磁盘空间
df -h
```

**解决方案:**

- 增加内存限制
- 清理旧数据
- 优化查询和告警规则

---

## 最佳实践

### 1. 指标命名规范

```python
# 好的命名
http_requests_total
http_request_duration_seconds
sandbox_executions_total

# 避免
requests  # 太模糊
api_time  # 单位不明确
sandbox_count  # 不清楚是什么计数
```

### 2. 标签使用原则

```python
# 合理的标签
http_requests_total{method="GET", status_code="200"}

# 避免高基数标签
http_requests_total{user_id="12345"}  # 用户 ID 会产生大量时间序列
```

### 3. 告警设计原则

- **可操作性**: 每个告警都应该有明确的处理步骤
- **降噪**: 避免告警疲劳,合并相关告警
- **分级**: Critical/Warning/Info 明确区分
- **附加 Runbook**: 每个告警链接到处理文档

### 4. 仪表板设计

- **按角色设计**: 不同角色看不同的仪表板
- **黄金信号**: 延迟、流量、错误、饱和度
- **关键指标**: P50/P95/P99 延迟
- **时间范围**: 提供 1h/6h/24h/7d 选项

### 5. SLO 管理

- **从用户角度**: SLO 应反映用户体验
- **可实现的目标**: 不要设定 100% 可用性
- **错误预算**: 平衡创新和稳定性
- **定期审查**: 每季度审查和调整 SLO

### 6. 事故响应流程

1. **确认**: 收到告警,确认问题
2. **沟通**: 通知相关方
3. **诊断**: 使用监控工具定位问题
4. **修复**: 执行修复措施
5. **验证**: 确认问题解决
6. **复盘**: 编写事故报告

### 7. 容量规划

定期审查以下指标:

- CPU 和内存使用趋势
- 磁盘空间增长率
- 请求量增长趋势
- 并发连接数
- 数据库连接池使用率

### 8. 安全建议

- 修改 Grafana 默认密码
- 限制监控端口的访问 (使用防火墙)
- 定期更新监控组件
- 备份监控配置和数据
- 审计告警通知渠道

---

## 资源链接

### 官方文档

- [Prometheus 文档](https://prometheus.io/docs/)
- [Grafana 文档](https://grafana.com/docs/)
- [Alertmanager 文档](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Sentry 文档](https://docs.sentry.io/)

### 社区资源

- [Prometheus Community](https://prometheus.io/community/)
- [Grafana Community](https://community.grafana.com/)
- [Awesome Prometheus](https://github.com/roaldnefs/awesome-prometheus)

### 学习资源

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [Prometheus Up & Running](https://www.oreilly.com/library/view/prometheus-up/9781492034131/)
- [Observability Engineering](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)

---

## 支持和帮助

如遇到问题,请通过以下方式获取帮助:

- **GitHub Issues**: https://github.com/your-org/helloagents-platform/issues
- **文档**: https://docs.helloagents.com
- **Email**: support@helloagents.com
- **Discord**: https://discord.gg/helloagents

---

**文档版本:** 1.0
**最后更新:** 2026-01-10
**维护者:** SRE Team
