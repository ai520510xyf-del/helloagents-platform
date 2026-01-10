# 🎉 监控系统部署完成！

## ✅ 已部署组件

| 组件 | 状态 | 访问地址 | 凭据 |
|------|------|---------|------|
| Prometheus | ✅ 运行中 | http://localhost:9090 | 无需认证 |
| Grafana | ✅ 运行中 | http://localhost:3000 | admin/admin |

## 🚀 快速操作

### 1. 启动监控系统

```bash
./start-monitoring.sh
```

### 2. 停止监控系统

```bash
./stop-monitoring.sh
```

### 3. 测试监控系统

```bash
./test-monitoring.sh
```

### 4. 启动后端服务（启用指标收集）

```bash
cd backend
uvicorn app.main:app --reload
```

后端启动后，访问 http://localhost:8000/metrics 查看指标。

## 📊 访问监控仪表板

### Prometheus

1. 访问 http://localhost:9090
2. 点击 **Status** → **Targets** 查看抓取目标
3. 确认 `helloagents-backend` 状态为 **UP**（需要先启动后端）

### Grafana

1. 访问 http://localhost:3000
2. 使用 `admin` / `admin` 登录
3. 首次登录会提示修改密码

## 🔧 配置 Grafana 数据源

### 方法一：Web UI 配置

1. 登录 Grafana
2. 点击左侧菜单 ⚙️ **Configuration** → **Data Sources**
3. 点击 **Add data source**
4. 选择 **Prometheus**
5. 配置:
   - Name: `Prometheus`
   - URL: `http://localhost:9090`
6. 点击 **Save & Test** 验证连接

### 方法二：命令行配置（快速）

```bash
# 使用 Grafana API 自动配置
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Prometheus",
    "type":"prometheus",
    "url":"http://localhost:9090",
    "access":"proxy",
    "isDefault":true
  }' \
  http://admin:admin@localhost:3000/api/datasources
```

## 📈 导入仪表板

1. 在 Grafana 中，点击左侧菜单 **+** → **Import**
2. 点击 **Upload JSON file**
3. 选择: `monitoring/grafana/dashboards/helloagents-overview.json`
4. 选择 Prometheus 数据源
5. 点击 **Import**

## 🧪 验证监控工作

### 1. 检查后端指标端点

```bash
curl http://localhost:8000/metrics
```

应该看到类似输出：

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/",status_code="200"} 10.0

# HELP http_request_duration_seconds HTTP request latency in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/",le="0.005"} 8.0
...
```

### 2. 在 Prometheus 中查询指标

访问 http://localhost:9090 并输入查询：

```promql
# 查看所有 HTTP 请求
http_requests_total

# 查看请求速率
rate(http_requests_total[1m])

# 查看 P95 延迟
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### 3. 生成测试流量

```bash
# 发送一些测试请求
for i in {1..20}; do
  curl -s http://localhost:8000/ > /dev/null
  curl -s http://localhost:8000/health > /dev/null
done
```

稍等片刻，指标会在 Prometheus 中更新。

## 📊 关键指标说明

### HTTP 请求指标

| 指标 | 说明 | 查询示例 |
|------|------|---------|
| `http_requests_total` | 总请求数 | `sum(rate(http_requests_total[5m]))` |
| `http_request_duration_seconds` | 请求延迟分布 | `histogram_quantile(0.95, ...)` |
| `http_requests_in_progress` | 进行中的请求数 | `http_requests_in_progress` |

### 沙箱指标

| 指标 | 说明 | 查询示例 |
|------|------|---------|
| `sandbox_executions_total` | 代码执行总数 | `rate(sandbox_executions_total[5m])` |
| `sandbox_execution_duration_seconds` | 执行时间 | `histogram_quantile(0.95, ...)` |
| `sandbox_pool_available` | 可用容器数 | `sandbox_pool_available` |

### AI 助手指标

| 指标 | 说明 | 查询示例 |
|------|------|---------|
| `ai_chat_requests_total` | AI 请求总数 | `rate(ai_chat_requests_total[5m])` |
| `ai_chat_duration_seconds` | AI 响应时间 | `histogram_quantile(0.95, ...)` |
| `ai_chat_tokens_total` | Token 消耗 | `sum(ai_chat_tokens_total)` |

## 🔍 常用 PromQL 查询

### 可用性

```promql
# 成功率（非 5xx 错误）
sum(rate(http_requests_total{status_code!~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

### 性能

```promql
# P50, P95, P99 延迟
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### 流量

```promql
# 按端点分组的请求速率
sum(rate(http_requests_total[5m])) by (endpoint)
```

## 🚨 故障排除

### Prometheus 无法抓取后端指标

1. 确认后端正在运行: `curl http://localhost:8000/health`
2. 确认 metrics 端点可访问: `curl http://localhost:8000/metrics`
3. 检查 Prometheus targets: http://localhost:9090/targets
4. 查看 Prometheus 日志: `tail -f /tmp/prometheus.log`

### Grafana 无法连接 Prometheus

1. 确认 Prometheus 运行正常: `curl http://localhost:9090/-/healthy`
2. 在 Grafana 数据源配置中使用 `http://localhost:9090`
3. 点击 **Save & Test** 测试连接

### 后端指标未更新

1. 确认 PrometheusMiddleware 已加载（查看后端启动日志）
2. 发送一些测试请求: `curl http://localhost:8000/`
3. 等待 15-30 秒（Prometheus 抓取间隔）
4. 刷新 Prometheus 查询

## 📝 配置文件位置

| 文件 | 路径 |
|------|------|
| Prometheus 配置 | `prometheus-local.yml` |
| 告警规则 | `monitoring/prometheus/alerts/` |
| Grafana 仪表板 | `monitoring/grafana/dashboards/` |
| 后端中间件 | `backend/app/middleware/prometheus_middleware.py` |

## 🎯 下一步

1. ✅ 监控系统已部署并运行
2. ⏳ 启动后端服务启用指标收集
3. ⏳ 在 Grafana 中配置数据源
4. ⏳ 导入预配置的仪表板
5. ⏳ 配置告警规则（见 `MONITORING.md`）
6. ⏳ 设置 Alertmanager 通知

## 📚 相关文档

- [完整监控文档](MONITORING.md) - 详细的监控配置和最佳实践
- [快速启动指南](MONITORING_QUICK_START.md) - 5分钟快速上手
- [告警配置](monitoring/prometheus/alerts/helloagents.yml) - 预配置的告警规则

## 💡 提示

- Prometheus 数据存储在 `/tmp/prometheus-data`（临时，重启后丢失）
- 生产环境请使用 `docker-compose.monitoring.yml` 部署
- 记得在 Grafana 中修改默认密码
- 定期检查磁盘空间（Prometheus 数据会增长）

---

**部署时间**: $(date)
**部署人员**: SRE Team
**环境**: 本地开发环境
