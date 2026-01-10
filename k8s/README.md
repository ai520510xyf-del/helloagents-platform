# Kubernetes 部署配置

本目录包含 HelloAgents Platform 的 Kubernetes 部署配置文件（可选）。

## 文件结构

```
k8s/
├── README.md                  # 本文件
├── namespace.yaml             # 命名空间
├── configmap.yaml             # 配置映射
├── secrets.yaml               # 密钥（需手动创建）
├── backend/
│   ├── deployment.yaml        # 后端部署
│   ├── service.yaml           # 后端服务
│   ├── hpa.yaml               # 自动伸缩
│   └── ingress.yaml           # 入口规则
├── frontend/
│   ├── deployment.yaml        # 前端部署
│   ├── service.yaml           # 前端服务
│   └── ingress.yaml           # 入口规则
├── postgres/
│   ├── statefulset.yaml       # PostgreSQL
│   ├── service.yaml           # 数据库服务
│   └── pvc.yaml               # 持久卷声明
└── redis/
    ├── deployment.yaml        # Redis
    └── service.yaml           # Redis 服务
```

## 快速开始

### 1. 前置要求

- Kubernetes 集群 (1.25+)
- kubectl 命令行工具
- Helm (可选)

### 2. 创建密钥

```bash
# 创建 secrets.yaml（不要提交到 Git）
kubectl create secret generic helloagents-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=deepseek-api-key='sk-...' \
  --from-literal=secret-key='...' \
  --dry-run=client -o yaml > k8s/secrets.yaml
```

### 3. 部署应用

```bash
# 应用所有配置
kubectl apply -f k8s/

# 或者逐步部署
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/redis/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
```

### 4. 验证部署

```bash
# 查看 Pods
kubectl get pods -n helloagents-production

# 查看服务
kubectl get services -n helloagents-production

# 查看日志
kubectl logs -f deployment/backend -n helloagents-production
```

## 配置说明

### 资源限制

| 组件 | CPU 请求 | CPU 限制 | 内存请求 | 内存限制 |
|------|----------|----------|----------|----------|
| Backend | 250m | 500m | 256Mi | 512Mi |
| Frontend | 100m | 200m | 128Mi | 256Mi |
| PostgreSQL | 500m | 1000m | 512Mi | 1Gi |
| Redis | 100m | 200m | 128Mi | 256Mi |

### 自动伸缩

- **Backend**: 2-10 副本，基于 CPU 使用率（70%）
- **Frontend**: 2-5 副本，基于 CPU 使用率（70%）

### 存储

- **PostgreSQL**: 10Gi PVC
- **Redis**: 内存存储（可选持久化）

## 监控和日志

### Prometheus 指标

```bash
# 安装 Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack

# 配置 ServiceMonitor
kubectl apply -f k8s/monitoring/servicemonitor.yaml
```

### 日志收集

```bash
# 使用 Fluentd/Loki
helm install loki grafana/loki-stack

# 查看日志
kubectl logs -f deployment/backend -n helloagents-production
```

## 生产环境最佳实践

1. **高可用性**
   - 至少 2 个副本
   - 跨可用区部署
   - 使用反亲和性规则

2. **安全性**
   - 使用 NetworkPolicy 限制流量
   - 启用 Pod Security Policy
   - 定期更新镜像

3. **性能优化**
   - 配置资源限制
   - 使用 HPA 自动伸缩
   - 启用缓存

4. **监控告警**
   - 集成 Prometheus + Grafana
   - 配置 Alertmanager
   - 设置 PagerDuty/Slack 通知

## 故障排查

```bash
# 查看 Pod 状态
kubectl describe pod <pod-name> -n helloagents-production

# 查看事件
kubectl get events -n helloagents-production --sort-by='.lastTimestamp'

# 进入容器调试
kubectl exec -it <pod-name> -n helloagents-production -- /bin/bash

# 查看日志
kubectl logs <pod-name> -n helloagents-production --tail=100 -f
```

## 清理

```bash
# 删除所有资源
kubectl delete -f k8s/

# 删除命名空间
kubectl delete namespace helloagents-production
```

## 相关资源

- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Helm Charts](https://helm.sh/)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)

---

**注意**: 目前项目主要部署在 Render 和 Cloudflare Pages。Kubernetes 配置为可选的高级部署方式。
