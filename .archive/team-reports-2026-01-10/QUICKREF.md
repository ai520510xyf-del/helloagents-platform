# 快速参考

## 🔗 关键链接

### 生产环境
- **前端**: https://helloagents-platform.pages.dev
- **后端**: https://helloagents-backend.onrender.com
- **API 文档**: https://helloagents-backend.onrender.com/api/v1/docs

### 监控和管理
- **Render Dashboard**: https://dashboard.render.com
- **Cloudflare Dashboard**: https://dash.cloudflare.com
- **Sentry**: https://sentry.io (需配置)
- **GitHub Actions**: https://github.com/your-org/helloagents-platform/actions

---

## 🏥 健康检查

### 快速检查
```bash
# 完整健康检查
curl https://helloagents-backend.onrender.com/health

# 就绪检查
curl https://helloagents-backend.onrender.com/health/ready

# 存活检查
curl https://helloagents-backend.onrender.com/health/live
```

### 自动化脚本
```bash
export BACKEND_URL=https://helloagents-backend.onrender.com
export FRONTEND_URL=https://helloagents-platform.pages.dev

# 健康检查
./scripts/deployment/health-check.sh

# 烟雾测试
./scripts/deployment/smoke-test.sh
```

---

## 🔧 环境变量

### 后端必需变量
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
DEEPSEEK_API_KEY=sk-xxxxx
SECRET_KEY=your-secret-key
```

### 后端可选变量
```bash
SENTRY_DSN=https://xxx@sentry.io/xxx
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
LOG_LEVEL=info
ENABLE_CONTAINER_POOL=false
```

### 前端变量
```bash
VITE_API_URL=https://helloagents-backend.onrender.com
```

---

## 📦 部署命令

### 查看日志
```bash
# Render 实时日志
render logs -s helloagents-backend --tail

# 最近 1000 条
render logs -s helloagents-backend --num 1000

# 搜索错误
render logs -s helloagents-backend --num 1000 | grep "ERROR"
```

### 手动部署
```bash
# Render CLI
render deploy -s helloagents-backend

# 或在 Render Dashboard 点击 "Manual Deploy"
```

### 环境变量管理
```bash
# 查看所有环境变量
render env list -s helloagents-backend

# 设置环境变量
render env set DEEPSEEK_API_KEY=sk-xxx -s helloagents-backend

# 获取环境变量
render env get DEEPSEEK_API_KEY -s helloagents-backend
```

---

## 🐛 故障排查

### 问题1: 部署失败
```bash
# 1. 检查构建日志
render logs -s helloagents-backend --tail

# 2. 验证依赖
pip install -r backend/requirements.txt

# 3. 测试本地构建
cd backend && docker build -t test .
```

### 问题2: 健康检查失败
```bash
# 1. 手动测试端点
curl -v https://helloagents-backend.onrender.com/health/ready

# 2. 检查数据库连接
psql $DATABASE_URL -c "SELECT 1"

# 3. 查看错误日志
render logs -s helloagents-backend | grep "ERROR\|CRITICAL"
```

### 问题3: CORS 错误
```bash
# 检查后端 CORS 配置
# 编辑 backend/app/main.py
# 添加前端域名到 allow_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://helloagents-platform.pages.dev",
        "https://your-custom-domain.com",
    ],
    ...
)
```

### 问题4: AI 助手不工作
```bash
# 1. 验证 API Key 配置
render env get DEEPSEEK_API_KEY -s helloagents-backend

# 2. 测试 API 连接
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     https://api.deepseek.com/v1/models

# 3. 检查日志
render logs -s helloagents-backend | grep "deepseek\|ai_chat"
```

---

## 🚀 部署流程

### 常规部署
```
1. 代码审查通过
2. 测试通过（CI）
3. 合并到 main 分支
4. 自动触发部署
5. 运行健康检查
6. 验证功能
```

### 紧急回滚
```
1. 登录 Render Dashboard
2. 选择服务 → Events
3. 找到上一个稳定部署
4. 点击 "Rollback"
5. 验证回滚成功
```

---

## 📊 监控指标

### 关键指标
| 指标 | 阈值 | 当前状态 |
|------|------|----------|
| Error Rate | < 1% | ✅ 监控中 |
| Response Time (P95) | < 500ms | ✅ 监控中 |
| Availability | > 99.9% | ✅ 监控中 |
| Health Check | 200 OK | ✅ 正常 |

### 查看指标
```bash
# Sentry Dashboard
# → Performance → Metrics

# Render Dashboard
# → Service → Metrics

# 手动测试响应时间
time curl https://helloagents-backend.onrender.com/health
```

---

## 📚 文档链接

### 项目文档
- [README.md](./README.md) - 项目概述和快速开始
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 详细部署指南
- [MONITORING.md](./MONITORING.md) - 监控配置指南
- [DEVOPS_SUMMARY.md](./DEVOPS_SUMMARY.md) - DevOps 优化总结
- [.env.example](./.env.example) - 环境变量示例

### 外部文档
- [Render 文档](https://render.com/docs)
- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages)
- [Sentry 文档](https://docs.sentry.io/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

## 🆘 紧急联系

### 团队联系
- **技术支持**: team@helloagents.com
- **DevOps 团队**: devops@helloagents.com
- **紧急联系**: on-call engineer

### Slack 频道
- `#devops` - DevOps 讨论
- `#deployments` - 部署通知
- `#alerts` - 监控告警
- `#incidents` - 事故响应

---

## ⚡ 常用命令速查

```bash
# === 开发 ===
# 启动后端
cd backend && uvicorn app.main:app --reload

# 启动前端
cd frontend && npm run dev

# 运行测试
pytest backend/tests
npm test --prefix frontend

# === 部署 ===
# 健康检查
./scripts/deployment/health-check.sh

# 烟雾测试
./scripts/deployment/smoke-test.sh

# 查看日志
render logs -s helloagents-backend --tail

# === Docker ===
# 构建后端镜像
docker build -t helloagents-backend backend/

# 构建前端镜像
docker build -t helloagents-frontend frontend/

# 运行本地容器
docker-compose up -d

# === Git ===
# 查看部署历史
git log --oneline -10

# 回滚到特定提交
git revert <commit-sha>

# === 安全扫描 ===
# 后端依赖扫描
cd backend && pip-audit

# 前端依赖扫描
cd frontend && npm audit
```

---

**最后更新**: 2024-01-09
**版本**: 1.0
