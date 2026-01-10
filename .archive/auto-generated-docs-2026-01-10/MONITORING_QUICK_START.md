# 监控系统快速启动指南

## 一键启动

```bash
# 启动监控系统
./start-monitoring.sh

# 停止监控系统
./stop-monitoring.sh
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Prometheus | http://localhost:9090 | 指标收集和查询 |
| Grafana | http://localhost:3000 | 可视化仪表板 (admin/admin) |
| Backend Metrics | http://localhost:8000/metrics | 后端指标端点 |

## 快速验证

### 1. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. 验证指标端点

```bash
# 访问后端指标端点
curl http://localhost:8000/metrics

# 应该看到类似输出：
# http_requests_total{...} 123
# http_request_duration_seconds{...} 0.05
```

### 3. 检查 Prometheus 目标

访问: http://localhost:9090/targets

确认 `helloagents-backend` 目标状态为 **UP**

### 4. 配置 Grafana 数据源

1. 访问 http://localhost:3000 (admin/admin)
2. 首次登录会提示修改密码
3. 点击左侧菜单 **Configuration** → **Data Sources**
4. 点击 **Add data source**
5. 选择 **Prometheus**
6. 配置:
   - URL: `http://localhost:9090`
   - 点击 **Save & Test**

### 5. 导入仪表板

1. 点击左侧菜单 **+** → **Import**
2. 上传文件: `monitoring/grafana/dashboards/helloagents-overview.json`
3. 选择 Prometheus 数据源
4. 点击 **Import**

## 关键指标

### HTTP 请求指标

```promql
# 总请求数
sum(rate(http_requests_total[5m])) by (method, endpoint)

# 错误率
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# P95 延迟
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
```

### 业务指标

```promql
# 代码执行成功率
sum(rate(sandbox_executions_total{status="success"}[5m]))
/
sum(rate(sandbox_executions_total[5m]))

# AI 聊天响应时间
histogram_quantile(0.95,
  rate(ai_chat_duration_seconds_bucket[5m])
)
```

## 故障排除

### Prometheus 无法启动

```bash
# 查看日志
tail -f /tmp/prometheus.log

# 常见问题：配置文件语法错误
promtool check config prometheus-local.yml
```

### 后端指标未收集

1. 确认后端服务运行在 8000 端口
2. 访问 http://localhost:8000/metrics 验证指标端点
3. 检查 Prometheus targets: http://localhost:9090/targets
4. 查看后端日志确认 PrometheusMiddleware 已加载

### Grafana 无法连接 Prometheus

1. 确认 Prometheus 运行正常: http://localhost:9090
2. 在 Grafana 数据源配置中点击 **Save & Test**
3. 如果报错，检查 URL 是否正确: `http://localhost:9090`

## 生产部署

### Docker Compose 方式

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### Kubernetes 方式

```bash
kubectl apply -f k8s/monitoring/
```

## 下一步

1. 配置告警规则 (见 `monitoring/prometheus/alerts/`)
2. 设置 Alertmanager 通知 (见 `monitoring/alertmanager/`)
3. 创建自定义仪表板
4. 集成 Sentry 错误追踪

## 相关文档

- [完整监控文档](MONITORING.md)
- [告警规则配置](monitoring/prometheus/alerts/helloagents.yml)
- [Grafana 仪表板](monitoring/grafana/dashboards/)
