# 部署指南

## 目录

- [环境变量配置](#环境变量配置)
- [部署流程](#部署流程)
- [安全检查清单](#安全检查清单)
- [故障排查](#故障排查)
- [回滚流程](#回滚流程)

---

## 环境变量配置

### 后端环境变量

#### 必需环境变量

| 变量名 | 说明 | 示例 | 设置位置 |
|--------|------|------|----------|
| `DATABASE_URL` | PostgreSQL 数据库连接字符串 | `postgresql://user:pass@host:5432/db` | Render Dashboard |
| `DEEPSEEK_API_KEY` | DeepSeek AI API 密钥 | `sk-xxxxx` | Render Dashboard |
| `SECRET_KEY` | 应用密钥（用于会话加密） | 随机生成的长字符串 | Render Dashboard |

#### 可选环境变量

| 变量名 | 说明 | 默认值 | 推荐值 |
|--------|------|--------|--------|
| `SENTRY_DSN` | Sentry 错误追踪 DSN | None | 生产环境必填 |
| `SENTRY_ENVIRONMENT` | Sentry 环境名称 | `development` | `production` |
| `SENTRY_TRACES_SAMPLE_RATE` | 性能追踪采样率 | `0.1` | `0.1` (10%) |
| `LOG_LEVEL` | 日志级别 | `info` | `info` |
| `ENABLE_CONTAINER_POOL` | 启用容器池 | `false` | `false` (Render不支持) |
| `CORS_ORIGINS` | 允许的 CORS 源 | 默认配置 | 前端URL |

#### 环境变量设置步骤

##### 方法1: Render Dashboard（推荐）

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 选择你的服务 (helloagents-backend)
3. 进入 **Environment** 标签页
4. 点击 **Add Environment Variable**
5. 输入变量名和值
6. 点击 **Save Changes**

##### 方法2: render.yaml（基础配置）

```yaml
services:
  - type: web
    name: helloagents-backend
    envVars:
      - key: LOG_LEVEL
        value: info
      - key: SENTRY_ENVIRONMENT
        value: production
      - key: DEEPSEEK_API_KEY
        sync: false  # 敏感信息，手动设置
```

##### 方法3: Render CLI

```bash
# 安装 Render CLI
npm install -g @render/cli

# 登录
render login

# 设置环境变量
render env set DEEPSEEK_API_KEY=sk-xxxxx -s helloagents-backend
render env set SENTRY_DSN=https://xxx@sentry.io/xxx -s helloagents-backend
```

### 前端环境变量

#### 构建时环境变量

| 变量名 | 说明 | 示例 | 设置位置 |
|--------|------|------|----------|
| `VITE_API_URL` | 后端 API 地址 | `https://helloagents-backend.onrender.com` | Cloudflare Pages 设置 |

#### Cloudflare Pages 设置步骤

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 选择你的项目 (helloagents-platform)
3. 进入 **Settings** → **Environment Variables**
4. 添加 `VITE_API_URL` 变量
5. 设置为生产环境的后端 URL
6. 保存并重新部署

### 本地开发环境变量

创建 `.env` 文件（不要提交到 Git）：

```bash
# 后端 .env
DATABASE_URL=postgresql://localhost:5432/helloagents_dev
DEEPSEEK_API_KEY=sk-xxxxx
SECRET_KEY=your-secret-key-for-development
LOG_LEVEL=debug
ENABLE_CONTAINER_POOL=false

# 可选
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
```

```bash
# 前端 .env
VITE_API_URL=http://localhost:8000
```

参考 `.env.example` 文件获取完整配置模板。

---

## 部署流程

### 自动部署

#### Render（后端）

Render 配置了自动部署，当代码推送到 `main` 分支时自动触发：

1. GitHub 推送触发 webhook
2. Render 自动构建 Docker 镜像
3. 运行健康检查
4. 滚动更新部署
5. 验证部署成功

#### Cloudflare Pages（前端）

Cloudflare Pages 同样配置了自动部署：

1. GitHub 推送触发构建
2. 构建前端静态资源
3. 部署到 CDN 边缘节点
4. 自动分配预览 URL（PR 预览）

### 手动部署

#### 使用 Render Dashboard

1. 登录 Render Dashboard
2. 选择服务
3. 点击 **Manual Deploy** → **Deploy latest commit**
4. 等待部署完成

#### 使用 GitHub Actions

手动触发部署工作流：

```bash
# 在 GitHub 仓库页面
# 1. 进入 Actions 标签
# 2. 选择 "Deploy" workflow
# 3. 点击 "Run workflow"
# 4. 选择分支和环境（staging/production）
# 5. 点击 "Run workflow"
```

### 部署验证

部署完成后，运行健康检查和烟雾测试：

```bash
# 设置环境变量
export BACKEND_URL=https://helloagents-backend.onrender.com
export FRONTEND_URL=https://helloagents-platform.pages.dev

# 运行健康检查
./scripts/deployment/health-check.sh

# 运行烟雾测试
./scripts/deployment/smoke-test.sh
```

#### 成功标准

- [ ] 所有健康检查通过（/health, /health/ready, /health/live）
- [ ] 烟雾测试成功率 >= 95%
- [ ] 响应时间 < 2000ms
- [ ] 无错误日志
- [ ] Sentry 未报告严重错误

---

## 安全检查清单

### 部署前检查

#### 代码安全

- [ ] 所有依赖项已更新到最新稳定版本
- [ ] 运行安全扫描（`npm audit`, `pip-audit`）
- [ ] 代码审查已通过
- [ ] 单元测试和集成测试全部通过
- [ ] 没有硬编码的密钥或密码

```bash
# 后端安全扫描
cd backend
pip install pip-audit
pip-audit

# 前端安全扫描
cd frontend
npm audit
npm audit fix  # 自动修复
```

#### 环境变量安全

- [ ] 敏感环境变量已在 Render Dashboard 设置（不在代码中）
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 生产环境使用强密码和随机密钥
- [ ] API 密钥定期轮换（建议每 90 天）

```bash
# 生成安全的 SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 或者使用 openssl
openssl rand -base64 32
```

#### 数据库安全

- [ ] 数据库连接使用 SSL
- [ ] 数据库密码强度足够（>= 16 字符，包含大小写字母、数字、特殊字符）
- [ ] 数据库备份已配置（自动每日备份）
- [ ] 数据库访问限制（仅允许 Render 服务访问）

#### 网络安全

- [ ] HTTPS 已启用（Render 和 Cloudflare 自动配置）
- [ ] CORS 配置正确（仅允许授权的前端域名）
- [ ] Rate limiting 已配置（防止 DDoS 攻击）
- [ ] 安全响应头已配置（CSP, X-Frame-Options 等）

```python
# 后端 CORS 配置示例
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://helloagents-platform.pages.dev",
        "https://helloagents.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 日志和监控安全

- [ ] 日志不包含敏感信息（密码、API 密钥、个人数据）
- [ ] Sentry 配置了 `send_default_pii=False`
- [ ] 错误消息不暴露内部实现细节
- [ ] 监控告警已配置

### 部署后验证

#### 功能验证

- [ ] 运行完整的烟雾测试套件
- [ ] 验证关键用户流程（注册、登录、代码执行、聊天）
- [ ] 检查前后端集成是否正常
- [ ] 验证数据库连接和迁移

#### 性能验证

- [ ] API 响应时间 < 500ms (P95)
- [ ] 页面加载时间 < 3秒
- [ ] 无内存泄漏
- [ ] CPU 使用率正常（< 80%）

#### 监控验证

- [ ] Sentry 正常接收事件
- [ ] 日志系统正常工作
- [ ] 告警规则触发正常
- [ ] 仪表板显示最新数据

### 安全审计清单

定期（每季度）进行安全审计：

```bash
# 1. 检查过期的依赖项
cd backend && pip list --outdated
cd frontend && npm outdated

# 2. 扫描已知漏洞
cd backend && pip-audit
cd frontend && npm audit

# 3. 检查 Docker 镜像漏洞
docker scan helloagents-backend:latest
docker scan helloagents-frontend:latest

# 4. 审查环境变量
render env list -s helloagents-backend

# 5. 检查数据库权限
psql $DATABASE_URL -c "\du"

# 6. 审查访问日志
render logs -s helloagents-backend --num 1000 | grep "ERROR\|CRITICAL"
```

---

## 故障排查

### 常见问题

#### 1. 部署失败：构建错误

**症状**：
- Render 构建失败
- 错误信息："Failed to build"

**排查步骤**：

```bash
# 1. 检查 requirements.txt 是否正确
cat backend/requirements.txt

# 2. 本地构建测试
cd backend
docker build -t test-backend .

# 3. 检查 Python 版本
python --version  # 应该是 3.11

# 4. 检查依赖冲突
pip install pip-tools
pip-compile requirements.txt
```

**解决方案**：
- 确保 `requirements.txt` 包含所有依赖
- 固定依赖版本（避免使用 `>=`）
- 移除不必要的依赖

#### 2. 部署失败：健康检查超时

**症状**：
- 部署过程卡住
- 错误信息："Health check failed"

**排查步骤**：

```bash
# 1. 手动测试健康检查端点
curl https://helloagents-backend.onrender.com/health/ready

# 2. 检查服务日志
render logs -s helloagents-backend --tail

# 3. 检查数据库连接
psql $DATABASE_URL -c "SELECT 1"
```

**解决方案**：
- 增加健康检查超时时间（Render Settings）
- 确保数据库可访问
- 检查环境变量配置

#### 3. 运行时错误：数据库连接失败

**症状**：
- 服务启动后立即崩溃
- 日志显示："Database connection failed"

**排查步骤**：

```bash
# 1. 验证 DATABASE_URL 格式
echo $DATABASE_URL

# 2. 测试数据库连接
psql $DATABASE_URL -c "SELECT version();"

# 3. 检查数据库服务状态
render services list | grep database
```

**解决方案**：
- 验证 `DATABASE_URL` 环境变量正确
- 确保数据库服务运行中
- 检查数据库防火墙规则

#### 4. 前端无法连接后端

**症状**：
- 前端加载成功但无法调用 API
- 浏览器控制台显示 CORS 错误

**排查步骤**：

```bash
# 1. 检查 VITE_API_URL 配置
# 在 Cloudflare Pages Settings → Environment Variables

# 2. 测试 CORS 配置
curl -H "Origin: https://helloagents-platform.pages.dev" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://helloagents-backend.onrender.com/api/v1/lessons

# 3. 检查后端 CORS 配置
# 在 backend/app/main.py 中查看 CORSMiddleware 配置
```

**解决方案**：
- 在后端 CORS 配置中添加前端 URL
- 确保 `allow_credentials=True`
- 重新部署后端服务

#### 5. Sentry 未接收到事件

**症状**：
- Sentry Dashboard 没有新事件
- 错误未被追踪

**排查步骤**：

```bash
# 1. 检查 SENTRY_DSN 配置
render env get SENTRY_DSN -s helloagents-backend

# 2. 测试 Sentry 连接
python3 -c "import sentry_sdk; sentry_sdk.init('YOUR_DSN'); sentry_sdk.capture_message('Test')"

# 3. 检查 Sentry 项目状态
# 访问 Sentry Dashboard → Project Settings
```

**解决方案**：
- 验证 `SENTRY_DSN` 正确
- 确保 Sentry 项目未暂停
- 检查防火墙是否阻止连接到 sentry.io

### 日志查看命令

```bash
# 实时查看日志
render logs -s helloagents-backend --tail

# 查看最近 1000 条日志
render logs -s helloagents-backend --num 1000

# 搜索错误日志
render logs -s helloagents-backend --num 1000 | grep "ERROR"

# 按时间过滤
render logs -s helloagents-backend --from "2024-01-09T00:00:00Z"

# 保存日志到文件
render logs -s helloagents-backend --num 10000 > logs.txt
```

---

## 回滚流程

### 自动回滚

Render 支持自动回滚失败的部署：

1. 部署失败时自动回滚到上一个稳定版本
2. 健康检查失败时自动回滚
3. 错误率超过阈值时手动触发回滚

### 手动回滚

#### 方法1: Render Dashboard

1. 登录 Render Dashboard
2. 选择服务 (helloagents-backend)
3. 进入 **Events** 标签页
4. 找到上一个成功的部署
5. 点击 **Rollback** 按钮
6. 确认回滚操作

#### 方法2: 重新部署特定提交

```bash
# 1. 查看 Git 历史
git log --oneline -10

# 2. 找到稳定的提交 SHA
STABLE_COMMIT=abc123

# 3. 创建回滚分支
git checkout -b rollback-$STABLE_COMMIT $STABLE_COMMIT

# 4. 推送到 main 分支（触发部署）
git push origin rollback-$STABLE_COMMIT:main -f

# 5. 或者使用 GitHub PR 进行回滚
```

#### 方法3: Git Revert

```bash
# 1. 回退最近的提交
git revert HEAD

# 2. 推送回退提交
git push origin main

# 3. 触发自动部署
```

### 回滚验证

回滚后立即运行验证：

```bash
# 1. 健康检查
./scripts/deployment/health-check.sh

# 2. 烟雾测试
./scripts/deployment/smoke-test.sh

# 3. 检查 Sentry 错误率
# 访问 Sentry Dashboard 查看错误率是否降低

# 4. 监控日志
render logs -s helloagents-backend --tail
```

### 回滚后操作

- [ ] 通知团队回滚已完成
- [ ] 更新事故报告
- [ ] 调查失败原因
- [ ] 修复问题并重新测试
- [ ] 准备新的部署

---

## 部署检查清单

### 部署前

- [ ] 代码审查通过
- [ ] 所有测试通过（单元测试、集成测试、E2E 测试）
- [ ] 安全扫描通过
- [ ] 性能测试通过
- [ ] 数据库迁移脚本准备好
- [ ] 环境变量已更新
- [ ] 通知团队即将部署

### 部署中

- [ ] 监控构建日志
- [ ] 确认健康检查通过
- [ ] 观察错误率
- [ ] 监控响应时间
- [ ] 验证数据库连接

### 部署后

- [ ] 运行健康检查脚本
- [ ] 运行烟雾测试脚本
- [ ] 手动测试关键功能
- [ ] 检查 Sentry Dashboard
- [ ] 查看应用日志
- [ ] 验证性能指标
- [ ] 更新部署记录
- [ ] 通知团队部署完成

---

## 相关文档

- [监控配置指南](./MONITORING.md)
- [环境变量示例](./.env.example)
- [Render 文档](https://render.com/docs)
- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages)

---

## 支持

如有问题，请联系：

- 技术支持：team@helloagents.com
- DevOps 团队：devops@helloagents.com
- Slack 频道：#devops #deployments
