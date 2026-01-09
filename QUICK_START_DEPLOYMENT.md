# 快速部署指南

**HelloAgents Platform** 5分钟快速部署 🚀

---

## 📦 准备工作

### 系统要求
- Docker 20.10+
- Docker Compose 1.29+
- 4GB+ 内存
- 10GB+ 磁盘空间

### 安装 Docker

**macOS:**
```bash
brew install --cask docker
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER  # 添加当前用户到docker组
```

**验证安装:**
```bash
docker --version
docker-compose --version
```

---

## 🚀 一键部署

### 方式一：使用部署脚本 (推荐)

```bash
# 1. 克隆仓库
git clone https://github.com/ai520510xyf-del/helloagents-platform.git
cd helloagents-platform

# 2. 运行部署脚本
./scripts/deploy.sh
```

脚本会自动:
- ✅ 检查系统环境
- ✅ 创建并配置 `.env` 文件
- ✅ 检查端口占用
- ✅ 构建 Docker 镜像
- ✅ 启动所有服务
- ✅ 运行健康检查

### 方式二：手动部署

```bash
# 1. 克隆仓库
git clone https://github.com/ai520510xyf-del/helloagents-platform.git
cd helloagents-platform

# 2. 配置环境变量
cp .env.example .env

# 编辑 .env 文件,设置以下必需变量:
#   ANTHROPIC_API_KEY=your_api_key_here
#   POSTGRES_PASSWORD=your_secure_password_here

nano .env  # 或使用其他编辑器

# 3. 启动所有服务
docker-compose up -d

# 4. 查看启动日志
docker-compose logs -f
```

---

## 🔑 配置 API Key

### 获取 Claude API Key

1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账号
3. 创建 API Key
4. 复制 Key 并添加到 `.env` 文件

```bash
# .env 文件
ANTHROPIC_API_KEY=sk-ant-xxx  # 替换为你的真实Key
```

### 配置数据库密码

```bash
# .env 文件
POSTGRES_PASSWORD=YourSecurePassword123!  # 至少12位,包含字母数字特殊字符
```

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
docker-compose ps
```

预期输出:
```
NAME                    STATUS              PORTS
helloagents-backend     Up                  0.0.0.0:8000->8000/tcp
helloagents-frontend    Up                  0.0.0.0:80->80/tcp
helloagents-postgres    Up                  0.0.0.0:5432->5432/tcp
helloagents-redis       Up                  0.0.0.0:6379->6379/tcp
```

### 2. 运行健康检查

```bash
./scripts/health-check.sh
```

### 3. 访问应用

打开浏览器,访问以下地址:

- 🌐 **前端应用**: http://localhost
- 🔧 **后端API**: http://localhost:8000
- 📚 **API文档**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc

---

## 🛠️ 常用命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近50行
docker-compose logs --tail=50
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
docker-compose restart frontend
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除所有数据 (谨慎!)
docker-compose down -v
```

### 更新代码

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose up -d --build
```

---

## 🔧 故障排查

### 问题1: 端口被占用

**错误信息:**
```
Error: port is already allocated
```

**解决方案:**
```bash
# 查看端口占用
lsof -i :80   # 前端
lsof -i :8000 # 后端

# 停止占用端口的进程
kill -9 <PID>

# 或修改端口 (编辑 docker-compose.yml)
```

### 问题2: API Key 错误

**错误信息:**
```
Authentication error: Invalid API key
```

**解决方案:**
```bash
# 1. 检查 .env 文件中的 API Key
cat .env | grep ANTHROPIC_API_KEY

# 2. 确认 Key 格式正确 (sk-ant-xxx)

# 3. 重启后端服务
docker-compose restart backend

# 4. 查看后端日志
docker-compose logs -f backend
```

### 问题3: 数据库连接失败

**错误信息:**
```
Cannot connect to database
```

**解决方案:**
```bash
# 1. 检查 PostgreSQL 容器状态
docker-compose ps postgres

# 2. 查看 PostgreSQL 日志
docker-compose logs postgres

# 3. 重启数据库
docker-compose restart postgres

# 4. 如果问题持续,删除并重新创建
docker-compose down -v
docker-compose up -d
```

### 问题4: 容器无法启动

**错误信息:**
```
Container exited with code 1
```

**解决方案:**
```bash
# 1. 查看详细日志
docker-compose logs <service-name>

# 2. 检查 .env 配置
./scripts/deploy.sh --check

# 3. 清理并重新构建
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

---

## 📊 性能优化

### 调整资源限制

编辑 `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'      # CPU核心数
          memory: 2G     # 内存限制
        reservations:
          cpus: '1'
          memory: 1G
```

### 启用生产模式

编辑 `.env`:

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
WORKERS=4  # 根据CPU核心数调整
```

---

## 🔐 安全配置

### 1. 修改默认密码

```bash
# 生成强密码
openssl rand -base64 32

# 更新 .env 文件
POSTGRES_PASSWORD=<生成的强密码>
SECRET_KEY=<生成的随机密钥>
```

### 2. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 5432/tcp  # 禁止外部访问数据库
sudo ufw enable
```

### 3. 设置 HTTPS

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d yourdomain.com
```

---

## 📚 下一步

部署完成后,你可以:

1. 📖 阅读 [完整部署指南](./GITHUB_HOSTING_GUIDE.md)
2. 🔧 配置 [自动部署](./CI_CD_GUIDE.md)
3. 📊 设置 [监控告警](./PERFORMANCE_OPTIMIZATIONS.md)
4. 🔐 加强 [安全配置](./DEPLOYMENT_CHECKLIST.md)

---

## 🆘 获取帮助

**遇到问题?**
- 📖 查看 [完整故障排查指南](./GITHUB_HOSTING_GUIDE.md#故障排查)
- 🐛 提交 [GitHub Issue](https://github.com/ai520510xyf-del/helloagents-platform/issues)
- 💬 查看 [文档](https://github.com/ai520510xyf-del/helloagents-platform/wiki)

---

**最后更新**: 2026-01-09
**版本**: 1.0.0
