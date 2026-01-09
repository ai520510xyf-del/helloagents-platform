# GitHub 托管与部署指南

**HelloAgents Platform** 完整部署指南 - 从GitHub到生产环境

---

## 📋 目录

1. [快速部署](#快速部署) (5分钟)
2. [Docker Compose 本地部署](#docker-compose-本地部署)
3. [云服务器部署](#云服务器部署)
4. [GitHub Actions 自动部署](#github-actions-自动部署)
5. [环境变量配置](#环境变量配置)
6. [故障排查](#故障排查)

---

## 🚀 快速部署

### 方案一：Docker Compose (推荐)

最简单的一键部署方式,适合本地开发和小型部署。

```bash
# 1. 克隆仓库
git clone https://github.com/ai520510xyf-del/helloagents-platform.git
cd helloagents-platform

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件,添加必需的 API Key:
# ANTHROPIC_API_KEY=your_api_key_here
# POSTGRES_PASSWORD=your_secure_password_here

# 3. 启动所有服务
docker-compose up -d

# 4. 访问应用
# 前端: http://localhost
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

**就这么简单！** 🎉

---

## 🐳 Docker Compose 本地部署

### 完整部署步骤

#### 1. 准备工作

**系统要求：**
- Docker 20.10+
- Docker Compose 1.29+
- 4GB+ 可用内存
- 10GB+ 可用磁盘空间

**安装 Docker：**
```bash
# macOS (使用 Homebrew)
brew install --cask docker

# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh

# 验证安装
docker --version
docker-compose --version
```

#### 2. 环境变量配置

创建 `.env` 文件：

```bash
# .env 文件内容

# ==================== 必需配置 ====================

# AI API Keys (至少配置一个)
ANTHROPIC_API_KEY=sk-ant-xxx  # Claude API密钥 (推荐)
OPENAI_API_KEY=sk-xxx          # OpenAI API密钥 (可选)

# 数据库密码 (至少12位,包含字母数字特殊字符)
POSTGRES_PASSWORD=YourSecurePassword123!

# ==================== 可选配置 ====================

# 数据库配置
POSTGRES_USER=helloagents
POSTGRES_DB=helloagents

# 应用配置
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS 配置 (如果前端域名不同需要修改)
CORS_ORIGINS=http://localhost,http://localhost:80

# 前端API地址 (如果后端域名不同需要修改)
VITE_API_URL=http://localhost:8000
```

**安全提示：**
- ⚠️ 永远不要提交 `.env` 文件到Git
- ⚠️ 生产环境使用强密码
- ⚠️ 定期轮换 API Keys

#### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps

# 预期输出:
# NAME                    STATUS              PORTS
# helloagents-backend     Up                  0.0.0.0:8000->8000/tcp
# helloagents-frontend    Up                  0.0.0.0:80->80/tcp
# helloagents-postgres    Up                  0.0.0.0:5432->5432/tcp
# helloagents-redis       Up                  0.0.0.0:6379->6379/tcp
```

#### 4. 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 预期输出:
# {"status":"healthy","database":"connected"}

# 检查前端
curl http://localhost/

# 访问API文档
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux
```

#### 5. 停止和清理

```bash
# 停止所有服务
docker-compose down

# 停止并删除所有数据 (谨慎使用!)
docker-compose down -v

# 重启特定服务
docker-compose restart backend
docker-compose restart frontend
```

---

## ☁️ 云服务器部署

### 适用于：AWS EC2、阿里云ECS、腾讯云CVM等

#### 方案一：标准VPS部署

**1. 服务器要求：**
- 操作系统: Ubuntu 22.04 LTS 或更高
- CPU: 2核+
- 内存: 4GB+
- 磁盘: 20GB+
- 网络: 公网IP

**2. 服务器初始化：**

```bash
# SSH 连接到服务器
ssh root@your-server-ip

# 更新系统
apt update && apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
apt install docker-compose -y

# 配置防火墙
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

**3. 部署应用：**

```bash
# 克隆仓库
cd /opt
git clone https://github.com/ai520510xyf-del/helloagents-platform.git
cd helloagents-platform

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 启动服务
docker-compose up -d

# 设置开机自启
systemctl enable docker
```

**4. 配置域名和HTTPS：**

```bash
# 安装 Certbot
apt install certbot python3-certbot-nginx -y

# 获取SSL证书
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
certbot renew --dry-run
```

**5. Nginx 反向代理配置：**

创建 `/etc/nginx/sites-available/helloagents`：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # 前端
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket 支持
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

启用配置：

```bash
ln -s /etc/nginx/sites-available/helloagents /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 方案二：使用GitHub Container Registry

**1. 在GitHub上构建镜像**

项目已配置 `.github/workflows/docker-build.yml`,每次推送代码会自动构建镜像。

**2. 在服务器上拉取镜像**

```bash
# 登录 GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# 拉取镜像
docker pull ghcr.io/ai520510xyf-del/helloagents-platform-backend:latest
docker pull ghcr.io/ai520510xyf-del/helloagents-platform-frontend:latest

# 运行容器
docker run -d \
  --name backend \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  ghcr.io/ai520510xyf-del/helloagents-platform-backend:latest

docker run -d \
  --name frontend \
  -p 80:80 \
  ghcr.io/ai520510xyf-del/helloagents-platform-frontend:latest
```

---

## 🤖 GitHub Actions 自动部署

### 设置自动部署到VPS

#### 1. 生成SSH密钥

在本地机器上：

```bash
# 生成SSH密钥对
ssh-keygen -t ed25519 -C "deploy-key" -f ~/.ssh/deploy_key

# 查看私钥 (用于GitHub Secrets)
cat ~/.ssh/deploy_key

# 查看公钥 (用于服务器)
cat ~/.ssh/deploy_key.pub
```

#### 2. 配置服务器

在VPS上：

```bash
# 添加公钥到 authorized_keys
echo "ssh-ed25519 AAAAC3... deploy-key" >> ~/.ssh/authorized_keys

# 设置权限
chmod 600 ~/.ssh/authorized_keys
```

#### 3. 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

**Settings → Secrets and variables → Actions → New repository secret**

- `DEPLOY_SSH_KEY`: 私钥内容
- `DEPLOY_SERVER_HOST`: 服务器IP或域名
- `DEPLOY_SERVER_USER`: SSH用户名(如 `root`)
- `ANTHROPIC_API_KEY`: AI API密钥
- `POSTGRES_PASSWORD`: 数据库密码

#### 4. 创建自动部署 Workflow

已有配置文件：`.github/workflows/deploy.yml`

**简化版自动部署** (创建 `.github/workflows/deploy-vps.yml`):

```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.DEPLOY_SERVER_HOST }}
          username: ${{ secrets.DEPLOY_SERVER_USER }}
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            cd /opt/helloagents-platform
            git pull origin main
            docker-compose down
            docker-compose up -d --build
            docker-compose logs --tail=50

      - name: Health Check
        run: |
          sleep 30
          curl -f https://${{ secrets.DEPLOY_SERVER_HOST }}/health || exit 1

      - name: Notify Success
        if: success()
        run: |
          echo "✅ Deployment successful!"

      - name: Notify Failure
        if: failure()
        run: |
          echo "❌ Deployment failed!"
```

#### 5. 触发部署

**自动触发：**
- 推送代码到 `main` 分支自动部署

**手动触发：**
- 在 GitHub Actions 页面点击 "Run workflow"

---

## ⚙️ 环境变量配置

### 完整环境变量列表

创建 `.env` 文件：

```bash
# ==================== 核心配置 ====================

# 运行环境 (development/staging/production)
ENVIRONMENT=production

# AI API Keys
ANTHROPIC_API_KEY=sk-ant-xxx              # Claude API (推荐)
OPENAI_API_KEY=sk-xxx                     # OpenAI API (可选)
DEEPSEEK_API_KEY=sk-xxx                   # DeepSeek API (可选)

# ==================== 数据库配置 ====================

# PostgreSQL (生产环境推荐)
POSTGRES_USER=helloagents
POSTGRES_PASSWORD=YourSecurePassword123!   # 必须设置
POSTGRES_DB=helloagents
POSTGRES_HOST=postgres                     # Docker内部主机名
POSTGRES_PORT=5432

# SQLite (开发环境)
DATABASE_URL=sqlite:///./helloagents.db

# ==================== 应用配置 ====================

# 后端配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
LOG_LEVEL=INFO                             # DEBUG/INFO/WARNING/ERROR

# 前端配置
VITE_API_URL=http://localhost:8000        # 后端API地址

# CORS 配置
CORS_ORIGINS=http://localhost,http://localhost:5173,http://localhost:80,https://yourdomain.com

# ==================== Redis配置 ====================

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# ==================== 安全配置 ====================

# JWT密钥 (生产环境必须设置)
SECRET_KEY=your-secret-key-here

# 会话配置
SESSION_TIMEOUT=3600                       # 1小时

# ==================== 监控配置 ====================

# Sentry (可选)
SENTRY_DSN=https://xxx@sentry.io/xxx

# ==================== Docker配置 ====================

# Docker沙箱配置
DOCKER_TIMEOUT=30
MAX_CONTAINER_POOL_SIZE=10

# ==================== 其他配置 ====================

# 调试模式 (生产环境设为false)
DEBUG=false

# 日志格式
LOG_FORMAT=json                            # json/text
```

### 环境变量验证脚本

创建 `scripts/check-env.sh`:

```bash
#!/bin/bash
# 环境变量检查脚本

set -e

echo "🔍 检查环境变量配置..."

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "❌ .env 文件不存在!"
    echo "💡 请运行: cp .env.example .env"
    exit 1
fi

# 检查必需的环境变量
REQUIRED_VARS=(
    "ANTHROPIC_API_KEY"
    "POSTGRES_PASSWORD"
)

MISSING_VARS=()

for VAR in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^$VAR=" .env || grep -q "^$VAR=$" .env || grep -q "^$VAR=your" .env; then
        MISSING_VARS+=("$VAR")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ 缺少以下必需的环境变量:"
    for VAR in "${MISSING_VARS[@]}"; do
        echo "   - $VAR"
    done
    echo ""
    echo "💡 请编辑 .env 文件并设置这些变量"
    exit 1
fi

# 检查密码强度
PASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2)
if [ ${#PASSWORD} -lt 12 ]; then
    echo "⚠️  警告: POSTGRES_PASSWORD 太短 (至少12位)"
fi

echo "✅ 环境变量配置正确!"
```

使用方法：

```bash
chmod +x scripts/check-env.sh
./scripts/check-env.sh
```

---

## 🛠️ 故障排查

### 常见问题

#### 1. 容器启动失败

**问题：** `docker-compose up` 失败

**解决方案：**

```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 检查端口占用
lsof -i :8000  # 后端端口
lsof -i :80    # 前端端口

# 清理并重新构建
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### 2. 数据库连接失败

**问题：** Backend日志显示 `Cannot connect to database`

**解决方案：**

```bash
# 检查PostgreSQL容器状态
docker-compose ps postgres

# 查看PostgreSQL日志
docker-compose logs postgres

# 进入PostgreSQL容器
docker exec -it helloagents-postgres psql -U helloagents

# 检查数据库是否存在
\l

# 手动创建数据库
CREATE DATABASE helloagents;
```

#### 3. API Key 错误

**问题：** AI聊天功能不工作

**解决方案：**

```bash
# 检查 .env 文件中的 API Key
cat .env | grep ANTHROPIC_API_KEY

# 验证 API Key (使用curl)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# 重启后端以加载新的环境变量
docker-compose restart backend
```

#### 4. 前端无法访问后端

**问题：** 前端显示 `Network Error`

**解决方案：**

```bash
# 检查CORS配置
# 编辑 .env 文件
CORS_ORIGINS=http://localhost,http://localhost:5173,https://yourdomain.com

# 检查前端API地址配置
grep VITE_API_URL .env

# 确保前端构建时使用了正确的API地址
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

#### 5. 性能问题

**问题：** 应用响应缓慢

**解决方案：**

```bash
# 检查容器资源使用
docker stats

# 查看后端性能日志
docker-compose logs backend | grep "slow query"

# 优化数据库
docker exec -it helloagents-postgres psql -U helloagents -d helloagents
VACUUM ANALYZE;

# 增加容器资源限制 (修改 docker-compose.yml)
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

#### 6. SSL证书问题

**问题：** HTTPS无法访问

**解决方案：**

```bash
# 检查证书状态
certbot certificates

# 手动续期证书
certbot renew

# 强制续期
certbot renew --force-renewal

# 重启Nginx
systemctl restart nginx
```

### 日志查看

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近50行日志
docker-compose logs --tail=50

# 保存日志到文件
docker-compose logs > deployment.log
```

### 健康检查

```bash
# 创建健康检查脚本 scripts/health-check.sh
#!/bin/bash

echo "🏥 运行健康检查..."

# 检查后端
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端: 健康"
else
    echo "❌ 后端: 不健康"
    exit 1
fi

# 检查前端
if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ 前端: 健康"
else
    echo "❌ 前端: 不健康"
    exit 1
fi

# 检查数据库
if docker exec helloagents-postgres pg_isready -U helloagents > /dev/null 2>&1; then
    echo "✅ 数据库: 健康"
else
    echo "❌ 数据库: 不健康"
    exit 1
fi

echo "✅ 所有服务健康!"
```

---

## 📊 监控和维护

### 日常维护

**每日检查：**
```bash
# 查看容器状态
docker-compose ps

# 查看资源使用
docker stats --no-stream

# 查看最近的错误日志
docker-compose logs --tail=100 | grep -i error
```

**每周维护：**
```bash
# 备份数据库
docker exec helloagents-postgres pg_dump -U helloagents helloagents > backup_$(date +%Y%m%d).sql

# 清理无用的Docker资源
docker system prune -a

# 更新镜像
docker-compose pull
docker-compose up -d
```

### 性能优化

**数据库优化：**
```bash
# 进入PostgreSQL容器
docker exec -it helloagents-postgres psql -U helloagents -d helloagents

# 运行分析
ANALYZE;

# 运行VACUUM
VACUUM ANALYZE;

# 重建索引
REINDEX DATABASE helloagents;
```

**应用优化：**
```bash
# 启用Redis缓存
# 确保docker-compose.yml中redis服务已启动

# 配置后端使用Redis
# 在 .env 文件中:
REDIS_HOST=redis
REDIS_PORT=6379
```

---

## 🔐 安全最佳实践

### 1. 环境变量安全

```bash
# ❌ 错误做法
ANTHROPIC_API_KEY=sk-ant-123456  # 直接暴露在代码中

# ✅ 正确做法
# 使用 .env 文件,并添加到 .gitignore
echo ".env" >> .gitignore

# 使用 GitHub Secrets 存储敏感信息
# Settings → Secrets → New repository secret
```

### 2. 容器安全

```bash
# 使用非root用户运行容器 (已在Dockerfile中配置)
USER appuser

# 定期更新基础镜像
docker-compose build --pull --no-cache

# 扫描镜像安全漏洞
docker scan helloagents-backend:latest
```

### 3. 网络安全

```bash
# 配置防火墙 (UFW)
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw deny 5432/tcp  # 禁止外部访问数据库
ufw enable

# 使用 fail2ban 防止暴力破解
apt install fail2ban -y
systemctl enable fail2ban
```

### 4. 数据备份

```bash
# 创建自动备份脚本 scripts/backup.sh
#!/bin/bash

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
docker exec helloagents-postgres pg_dump -U helloagents helloagents > \
  $BACKUP_DIR/db_backup_$DATE.sql

# 压缩备份
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 删除30天前的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "✅ 备份完成: db_backup_$DATE.sql.gz"
```

```bash
# 设置定时任务
crontab -e

# 每天凌晨2点备份
0 2 * * * /opt/helloagents-platform/scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

## 📚 相关文档

- [部署清单](./DEPLOYMENT_CHECKLIST.md) - 完整的部署检查清单
- [CI/CD 指南](./CI_CD_GUIDE.md) - GitHub Actions配置指南
- [环境配置](./ENVIRONMENT_SETUP.md) - 详细的环境变量说明
- [性能优化](./PERFORMANCE_OPTIMIZATIONS.md) - 性能优化指南

---

## 🆘 获取帮助

**遇到问题？**
- 📖 查看 [故障排查](#故障排查) 章节
- 🐛 提交 [GitHub Issue](https://github.com/ai520510xyf-del/helloagents-platform/issues)
- 💬 加入讨论区提问

**需要支持？**
- 📧 邮件: support@helloagents.com
- 📚 文档: [Wiki](https://github.com/ai520510xyf-del/helloagents-platform/wiki)

---

**最后更新**: 2026-01-09
**版本**: 1.0.0
**维护者**: HelloAgents Platform Team
