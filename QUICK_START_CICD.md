# CI/CD Quick Start Guide

## 快速开始

这是一个快速参考指南，帮助你快速上手 HelloAgents Platform 的 CI/CD 流水线。

## 本地开发

### 使用 Docker Compose（推荐）

```bash
# 启动完整开发环境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# 仅启动后端
docker-compose up backend

# 仅启动前端开发服务器
docker-compose -f docker-compose.dev.yml up frontend

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止所有服务
docker-compose down
```

### 手动构建 Docker 镜像

```bash
# 构建后端镜像
docker build -t helloagents-backend:latest ./backend

# 构建前端镜像
docker build -t helloagents-frontend:latest ./frontend

# 运行后端容器
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=xxx helloagents-backend:latest

# 运行前端容器
docker run -p 80:80 helloagents-frontend:latest
```

## 测试

### 本地运行测试

```bash
# 后端测试
cd backend
pytest tests/ --cov=app

# 前端测试
cd frontend
npm test

# 前端测试（带覆盖率）
npm run test:coverage
```

### CI 测试

推送代码到 GitHub 后，CI 测试会自动运行：
- Push 到 `main` 或 `develop` 分支
- 创建 Pull Request

查看测试结果：GitHub Actions → CI Workflow

## 构建和发布

### 创建版本标签

```bash
# 创建标签触发 Docker 构建
git tag v1.0.0
git push origin v1.0.0

# 或使用语义化版本
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

### 手动触发构建

1. 进入 GitHub Actions
2. 选择 "Docker Build and Push"
3. 点击 "Run workflow"
4. 输入镜像标签
5. 点击 "Run workflow"

## 部署

### 自动部署到 Staging

当 Docker 镜像构建成功后，会自动部署到 Staging 环境。

查看部署状态：
1. GitHub Actions → Deploy Workflow
2. 监控部署日志
3. 检查 Staging 环境：https://staging.helloagents.com

### 手动部署到 Production

#### 方式 1: GitHub Actions

1. 进入 GitHub Actions
2. 选择 "Deploy" workflow
3. 点击 "Run workflow"
4. 选择 environment: `production`
5. 确认并运行

#### 方式 2: 部署脚本

```bash
# 确保有必要的访问权限
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# 部署到 Production
./scripts/deployment/deploy.sh -e production -v v1.0.0

# 带参数部署
./scripts/deployment/deploy.sh \
  -e production \
  -v v1.0.0 \
  -r ghcr.io \
  -n helloagents
```

## 健康检查

### 检查服务健康状态

```bash
# 检查 Staging
./scripts/deployment/health-check.sh -e staging

# 检查 Production
./scripts/deployment/health-check.sh -e production
```

### 手动检查端点

```bash
# Staging
curl https://staging-api.helloagents.com/health
curl https://staging.helloagents.com

# Production
curl https://api.helloagents.com/health
curl https://helloagents.com
```

## 回滚

### 快速回滚（到上一版本）

```bash
# 回滚 Production
./scripts/deployment/rollback.sh -e production

# 回滚 Staging
./scripts/deployment/rollback.sh -e staging
```

### 回滚到特定版本

```bash
# 查看部署历史
kubectl rollout history deployment/backend-deployment -n production

# 回滚到指定版本（例如第 2 版）
./scripts/deployment/rollback.sh -e production -r 2
```

### 紧急回滚（Kubernetes）

```bash
# 配置 kubectl 上下文
kubectl config use-context production-cluster

# 快速回滚
kubectl rollout undo deployment/backend-deployment -n production
kubectl rollout undo deployment/frontend-deployment -n production

# 查看回滚状态
kubectl rollout status deployment/backend-deployment -n production
```

## 监控

### 查看 Kubernetes Pod 状态

```bash
# 列出所有 Pod
kubectl get pods -n production

# 查看 Pod 详情
kubectl describe pod <pod-name> -n production

# 查看 Pod 日志
kubectl logs -f <pod-name> -n production

# 查看最近的事件
kubectl get events -n production --sort-by='.lastTimestamp'
```

### 查看 Docker 容器日志

```bash
# 本地开发环境
docker-compose logs -f backend
docker-compose logs -f frontend

# 特定容器
docker logs -f <container-id>
```

## 常见问题

### Q: Docker 构建失败怎么办？

```bash
# 清理 Docker 缓存
docker system prune -a

# 无缓存重新构建
docker build --no-cache -t helloagents-backend:latest ./backend
```

### Q: 部署后服务无法访问？

1. 检查服务状态：
```bash
kubectl get pods -n production
kubectl get services -n production
```

2. 查看日志：
```bash
kubectl logs -f deployment/backend-deployment -n production
```

3. 检查健康检查：
```bash
./scripts/deployment/health-check.sh -e production
```

### Q: 如何回滚失败的部署？

```bash
# 立即回滚
./scripts/deployment/rollback.sh -e production

# 如果脚本失败，使用 kubectl
kubectl rollout undo deployment/backend-deployment -n production
```

### Q: 如何查看构建日志？

1. 进入 GitHub Actions
2. 选择对应的 Workflow Run
3. 点击失败的 Job
4. 查看详细日志

## 环境变量配置

### 本地开发

创建 `.env` 文件：

```bash
# Backend (.env)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./helloagents.db
ENVIRONMENT=development

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

### GitHub Secrets

需要配置的 Secrets：

1. 进入 GitHub Repository Settings
2. Secrets and variables → Actions
3. 添加以下 Secrets：
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `CODECOV_TOKEN`
   - `VITE_API_URL`

### Kubernetes Secrets

```bash
# 创建 Secrets
kubectl create secret generic app-secrets \
  --from-literal=anthropic-api-key=xxx \
  --from-literal=openai-api-key=xxx \
  --from-literal=database-url=xxx \
  -n production

# 验证 Secrets
kubectl get secrets -n production
kubectl describe secret app-secrets -n production
```

## 有用的命令

### Docker Compose

```bash
# 启动服务（后台）
docker-compose up -d

# 重启服务
docker-compose restart backend

# 查看服务状态
docker-compose ps

# 进入容器 shell
docker-compose exec backend bash
docker-compose exec frontend sh

# 清理所有容器和卷
docker-compose down -v
```

### Kubernetes

```bash
# 查看所有资源
kubectl get all -n production

# 扩缩容
kubectl scale deployment/backend-deployment --replicas=5 -n production

# 更新镜像
kubectl set image deployment/backend-deployment \
  backend=ghcr.io/helloagents/backend:v1.0.1 \
  -n production

# 编辑配置
kubectl edit deployment/backend-deployment -n production

# 端口转发（本地调试）
kubectl port-forward deployment/backend-deployment 8000:8000 -n production
```

### Git 工作流

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送到远程
git push origin feature/new-feature

# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 工作流程

### 日常开发流程

1. 创建功能分支
2. 本地开发和测试
3. 提交并推送代码
4. 创建 Pull Request
5. CI 测试自动运行
6. Code Review
7. 合并到 develop 分支
8. 自动部署到 Staging
9. 在 Staging 测试
10. 合并到 main 分支
11. 创建版本标签
12. 手动部署到 Production

### 发布流程

1. 确保 Staging 测试通过
2. 创建版本标签（v1.0.0）
3. Docker 镜像自动构建
4. 安全扫描通过
5. 手动触发 Production 部署
6. 监控部署过程
7. 运行 Smoke 测试
8. 持续监控 1 小时
9. 发布完成

### 紧急修复流程

1. 创建 hotfix 分支
2. 快速修复问题
3. 运行测试
4. 创建 PR 并快速审查
5. 合并到 main
6. 创建补丁版本（v1.0.1）
7. 快速部署到 Production
8. 验证修复
9. 反向合并到 develop

## 最佳实践

### 开发阶段
- 始终在本地运行测试
- 使用 Docker Compose 模拟生产环境
- 及时提交小改动
- 编写有意义的提交信息

### 部署阶段
- 先部署到 Staging 测试
- 在低峰时段部署到 Production
- 部署后持续监控
- 准备好回滚计划

### 安全阶段
- 不在代码中硬编码密钥
- 定期更新依赖
- 关注安全扫描报告
- 使用最小权限原则

## 获取帮助

### 文档
- [完整 CI/CD 指南](./CI_CD_GUIDE.md)
- [部署检查清单](./DEPLOYMENT_CHECKLIST.md)
- [任务总结](./SPRINT5_TASK5.2_SUMMARY.md)

### 联系方式
- DevOps Team: devops@helloagents.com
- On-call Support: oncall@helloagents.com
- Slack: #devops

---

**最后更新**: 2026-01-08
