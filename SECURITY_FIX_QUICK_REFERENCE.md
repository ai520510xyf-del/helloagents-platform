# P0 安全修复 - 快速参考

## 开发者快速开始

### 1. 创建环境配置（首次使用）
```bash
# 复制模板
cp .env.example .env

# 编辑配置（使用你喜欢的编辑器）
nano .env
```

### 2. 配置必需变量
在 `.env` 文件中设置:
```bash
# 必需: Anthropic API 密钥
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# 必需: 数据库密码（最少 12 字符）
POSTGRES_PASSWORD=xK9$mP2@nQ7&vR4!wL8
```

### 3. 验证配置
```bash
./scripts/check-env.sh
```

### 4. 启动服务
```bash
docker-compose up -d
```

---

## 已修复的 P0 问题

### P0-1: 硬编码数据库密码
- **修复前**: `POSTGRES_PASSWORD=helloagents_secret`
- **修复后**: `POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?Error}`
- **影响**: 必须在 `.env` 中配置，不会被提交到 Git

### P0-2: 环境变量验证缺失
- **修复前**: 无验证，运行时才发现错误
- **修复后**: 启动前强制验证 + 自动化验证脚本
- **影响**: 提前发现配置错误，提升用户体验

---

## 生成强密码

### macOS/Linux
```bash
# 方法 1: OpenSSL
openssl rand -base64 24

# 方法 2: Python
python3 -c "import secrets; print(secrets.token_urlsafe(24))"

# 方法 3: 在线工具
# https://passwordsgenerator.net/
```

### Windows PowerShell
```powershell
# 生成随机密码
-join ((65..90) + (97..122) + (48..57) + (33..47) | Get-Random -Count 16 | ForEach-Object {[char]$_})
```

---

## 验证脚本输出

### 成功配置
```
✅ Environment validation PASSED
All required environment variables are properly configured.
```

### 配置错误
```
❌ Environment validation FAILED
  ❌ ANTHROPIC_API_KEY is not set (REQUIRED)
  ❌ POSTGRES_PASSWORD is too weak
```

---

## 常见错误

### 错误 1: docker-compose 启动失败
```
Error: POSTGRES_PASSWORD not set
```
**解决**: 创建 `.env` 文件并设置 `POSTGRES_PASSWORD`

### 错误 2: API 密钥无效
```
401 Unauthorized: Invalid API key
```
**解决**: 检查 `ANTHROPIC_API_KEY` 是否正确

### 错误 3: 密码太弱
```
❌ POSTGRES_PASSWORD is too weak
```
**解决**: 使用至少 12 字符的强密码

---

## 安全检查清单

开发者自检:
- [ ] `.env` 文件已创建
- [ ] `ANTHROPIC_API_KEY` 已设置（真实密钥）
- [ ] `POSTGRES_PASSWORD` 已设置（强密码，≥12 字符）
- [ ] 运行 `./scripts/check-env.sh` 通过
- [ ] 确认 `.env` 未被添加到 Git（`git status` 不显示）

Code Review 检查:
- [ ] 没有硬编码密钥
- [ ] docker-compose.yml 使用 `${VAR:?Error}` 语法
- [ ] .gitignore 包含 `.env`

---

## 文档链接

- **完整修复说明**: [P0_SECURITY_FIX_SUMMARY.md](./P0_SECURITY_FIX_SUMMARY.md)
- **环境配置指南**: [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md)
- **部署检查清单**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

---

## 紧急联系

如有问题:
1. 运行 `./scripts/check-env.sh` 获取诊断信息
2. 查看 [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md) 故障排查部分
3. 在 GitHub Issues 提交问题（不要包含真实密钥！）
