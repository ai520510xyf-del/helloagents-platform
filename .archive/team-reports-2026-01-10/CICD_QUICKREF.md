# CI/CD 快速参考指南

## HelloAgents Platform - DevOps 速查表

---

## 🚀 快速命令

### GitHub Actions

```bash
# 查看 workflow 列表
gh workflow list

# 查看最近的运行
gh run list --limit 10

# 查看特定运行的详情
gh run view <run-id>

# 查看运行日志
gh run view <run-id> --log

# 手动触发 workflow
gh workflow run cicd-pipeline.yml

# 手动触发部署（指定环境）
gh workflow run cicd-pipeline.yml -f environment=staging

# 重新运行失败的 job
gh run rerun <run-id>

# 取消运行
gh run cancel <run-id>
```

### Docker

```bash
# 构建镜像
docker build -t helloagents-backend:latest ./backend
docker build -t helloagents-frontend:latest ./frontend

# 使用优化的 Dockerfile
docker build -f backend/Dockerfile.optimized -t helloagents-backend:optimized ./backend

# 运行容器
docker run -p 8000:8000 helloagents-backend:latest
docker run -p 8080:80 helloagents-frontend:latest

# 查看镜像大小
docker images | grep helloagents

# 清理未使用的镜像
docker image prune -a
```

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 停止并删除容器
docker-compose down

# 完全清理（包括卷）
docker-compose down -v
```

### 部署脚本

```bash
# 健康检查
./scripts/deployment/health-check.sh -e production

# 烟雾测试
export BACKEND_URL=https://api.helloagents.com
export FRONTEND_URL=https://helloagents.com
./scripts/deployment/smoke-test.sh

# 回滚部署
./scripts/deployment/rollback.sh -e production -v previous
```

---

## 📋 环境变量配置

### 必需的环境变量

```bash
# AI 服务
DEEPSEEK_API_KEY=sk-xxxxx

# 数据库
DATABASE_URL=postgresql://user:pass@host:port/db

# 安全
SECRET_KEY=your-secret-key-at-least-32-chars
JWT_SECRET_KEY=your-jwt-secret-key

# CORS
CORS_ORIGINS=https://helloagents-platform.pages.dev
```

### GitHub Secrets

在 GitHub Repository Settings → Secrets 中配置:

```
CODECOV_TOKEN              # Codecov 上传
CLOUDFLARE_API_TOKEN       # Cloudflare Pages 部署
CLOUDFLARE_ACCOUNT_ID      # Cloudflare 账户 ID
RENDER_DEPLOY_HOOK_STAGING # Render Staging 部署
RENDER_DEPLOY_HOOK_PRODUCTION # Render Production 部署
SENTRY_DSN                 # Sentry 错误追踪
VITE_API_URL               # 前端 API URL
```

---

## 🔄 工作流程

### 开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/your-feature

# 2. 开发和提交
git add .
git commit -m "feat: add new feature"

# 3. 推送到远程
git push origin feature/your-feature

# 4. 创建 Pull Request
gh pr create --title "Add new feature" --body "Description"

# 5. CI 自动运行测试

# 6. 合并到 develop
gh pr merge --merge

# 7. 自动部署到 Staging
```

### 发布流程

```bash
# 1. 从 develop 创建 release 分支
git checkout develop
git pull
git checkout -b release/v1.0.0

# 2. 更新版本号和 CHANGELOG
echo "v1.0.0" > VERSION
# 编辑 CHANGELOG.md

# 3. 提交 release 准备
git add .
git commit -m "chore: prepare release v1.0.0"

# 4. 合并到 main
git checkout main
git merge release/v1.0.0

# 5. 创建 tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main --tags

# 6. 自动部署到 Production

# 7. 合并回 develop
git checkout develop
git merge main
git push origin develop
```

---

## 🧪 测试命令

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html

# 只运行快速测试
pytest -m "not slow"

# 详细输出
pytest -v

# 并行测试
pytest -n auto
```

### 前端测试

```bash
cd frontend

# 运行单元测试
npm test

# 运行带覆盖率的测试
npm run test:coverage

# 运行 E2E 测试
npm run test:e2e

# 运行特定浏览器的 E2E
npm run test:e2e:chromium

# 调试 E2E 测试
npm run test:e2e:debug

# 查看测试报告
npm run test:e2e:report
```

---

## 📊 监控和日志

### Render 平台

```bash
# 查看日志
# 访问: https://dashboard.render.com/
# 选择服务 → Logs 标签

# 重启服务
# Dashboard → 选择服务 → Manual Deploy → Deploy latest commit

# 查看指标
# Dashboard → 选择服务 → Metrics 标签
```

### Cloudflare Pages

```bash
# 查看部署历史
# 访问: https://dash.cloudflare.com/
# 选择项目 → Deployments

# 回滚部署
# Deployments → 选择之前的部署 → Rollback

# 查看分析
# 选择项目 → Analytics
```

### 健康检查端点

```bash
# Backend
curl https://api.helloagents.com/health
curl https://api.helloagents.com/health/live
curl https://api.helloagents.com/health/ready

# Frontend
curl https://helloagents.com/
```

---

## 🐛 故障排查

### CI 失败排查

```bash
# 1. 查看失败的 job
gh run view <run-id>

# 2. 查看详细日志
gh run view <run-id> --log

# 3. 本地复现问题
# 使用相同的命令在本地运行

# 4. 修复并重新推送
git commit --amend
git push --force-with-lease

# 5. 或重新运行 CI
gh run rerun <run-id>
```

### Docker 构建问题

```bash
# 清理构建缓存
docker builder prune -a

# 不使用缓存构建
docker build --no-cache -t image:tag .

# 查看构建历史
docker history image:tag

# 进入容器调试
docker run -it --entrypoint /bin/bash image:tag
```

### 部署问题

```bash
# 1. 检查环境变量
# Render: Dashboard → Service → Environment

# 2. 查看部署日志
# Render: Dashboard → Service → Logs

# 3. 运行健康检查
./scripts/deployment/health-check.sh -e production

# 4. 如果需要，执行回滚
./scripts/deployment/rollback.sh -e production -v previous
```

---

## 📝 常见问题

### Q: 如何跳过 CI 测试？

A: 在 commit 消息中添加 `[skip ci]`:
```bash
git commit -m "docs: update README [skip ci]"
```

### Q: 如何只运行特定的测试？

A: 使用 workflow_dispatch 触发时指定参数:
```bash
gh workflow run cicd-pipeline.yml -f skip_tests=true
```

### Q: 如何查看 Docker 镜像标签？

A: 访问 GitHub Container Registry:
```
https://github.com/ai520510xyf-del/helloagents-platform/pkgs/container/helloagents-platform-backend
```

### Q: 部署失败如何快速回滚？

A: 使用回滚脚本:
```bash
./scripts/deployment/rollback.sh -e production -v previous -y
```

---

## 🔗 快速链接

| 资源 | URL |
|------|-----|
| GitHub Repo | https://github.com/ai520510xyf-del/helloagents-platform |
| GitHub Actions | https://github.com/ai520510xyf-del/helloagents-platform/actions |
| Render Dashboard | https://dashboard.render.com/ |
| Cloudflare Dashboard | https://dash.cloudflare.com/ |
| Codecov | https://codecov.io/gh/ai520510xyf-del/helloagents-platform |
| Production Frontend | https://helloagents-platform.pages.dev |
| Production Backend | https://helloagents-platform.onrender.com |
| Staging Frontend | https://helloagents-platform-staging.pages.dev |
| Staging Backend | (配置中) |

---

## 📞 获取帮助

- **文档**: 查看 [CICD_OPTIMIZATION_REPORT.md](./CICD_OPTIMIZATION_REPORT.md)
- **Issues**: https://github.com/ai520510xyf-del/helloagents-platform/issues
- **讨论**: https://github.com/ai520510xyf-del/helloagents-platform/discussions

---

**最后更新**: 2026-01-09
