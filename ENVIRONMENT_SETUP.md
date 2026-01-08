# HelloAgents Platform - 环境变量配置指南

## 快速开始

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

### 2. 配置必需的环境变量

编辑 `.env` 文件，设置以下必需变量:

```bash
# 必需: Anthropic API 密钥
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# 必需: PostgreSQL 数据库密码（生产环境必须使用强密码）
POSTGRES_PASSWORD=your_secure_password_minimum_12_chars
```

### 3. 验证配置

运行验证脚本:

```bash
./scripts/check-env.sh
```

### 4. 启动服务

```bash
docker-compose up -d
```

---

## 必需的环境变量

### ANTHROPIC_API_KEY (必需)
- **用途**: 用于 Claude AI 功能
- **获取**: https://console.anthropic.com/
- **格式**: `sk-ant-xxxxxxxxxxxxx`

### POSTGRES_PASSWORD (必需)
- **用途**: PostgreSQL 数据库密码
- **要求**:
  - 最少 12 个字符
  - 不要使用常见词汇 (password, secret, 123456 等)
  - 建议使用密码生成器
- **示例**: `xK9$mP2@nQ7&vR4!wL8`

---

## 可选的环境变量

### OPENAI_API_KEY (可选)
- **用途**: 用于 OpenAI GPT 功能
- **获取**: https://platform.openai.com/api-keys

### DEEPSEEK_API_KEY (可选)
- **用途**: 用于 DeepSeek AI 功能
- **获取**: https://platform.deepseek.com/api_keys

### SENTRY_DSN (可选)
- **用途**: 生产环境错误追踪
- **获取**: https://sentry.io/

---

## Docker Compose 环境变量

### 环境变量语法说明

```yaml
# ✅ 必需变量（未设置会报错）
- POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?Error: POSTGRES_PASSWORD not set}

# ✅ 可选变量（未设置使用默认值）
- POSTGRES_USER=${POSTGRES_USER:-helloagents}

# ✅ 可选变量（未设置为空）
- OPENAI_API_KEY=${OPENAI_API_KEY:-}
```

---

## 安全最佳实践

### ✅ 推荐做法

1. **永远不要提交 .env 文件**
   - `.env` 已在 `.gitignore` 中
   - 只提交 `.env.example` 模板

2. **使用强密码**
   ```bash
   # 生成随机密码 (macOS/Linux)
   openssl rand -base64 24
   ```

3. **定期轮换密钥**
   - API 密钥每 90 天轮换
   - 数据库密码每季度更新

4. **使用密钥管理服务**
   - 生产环境使用 AWS Secrets Manager
   - 或 HashiCorp Vault
   - 或 Azure Key Vault

### ❌ 避免做法

1. **不要硬编码密钥**
   ```yaml
   # ❌ 错误
   - POSTGRES_PASSWORD=mysecret123

   # ✅ 正确
   - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?Error: POSTGRES_PASSWORD not set}
   ```

2. **不要使用弱密码**
   - ❌ `password123`
   - ❌ `admin`
   - ❌ `secret`
   - ✅ `xK9$mP2@nQ7&vR4!wL8`

3. **不要在日志中打印密钥**
   ```python
   # ❌ 错误
   logger.info(f"API Key: {api_key}")

   # ✅ 正确
   logger.info("API Key configured successfully")
   ```

---

## 环境变量验证

### 自动验证

在启动服务前，自动运行验证:

```bash
# 在 docker-compose up 之前运行
./scripts/check-env.sh && docker-compose up -d
```

### 验证脚本功能

- ✅ 检查必需变量是否设置
- ✅ 检查是否使用占位符值
- ✅ 验证密码强度
- ✅ 确认 .env 在 .gitignore 中
- ✅ 提供详细的错误和警告信息

### 验证输出示例

```
🔍 Checking required environment variables...

📋 Required Variables:
  ✅ ANTHROPIC_API_KEY is set
  ✅ POSTGRES_PASSWORD is set

📋 Optional Variables:
  ⚠️  OPENAI_API_KEY is not set (optional)
  ✅ DEEPSEEK_API_KEY is set

📄 Configuration Files:
  ✅ .env file exists
  ✅ .env.example file exists

🔒 Security Checks:
  ✅ POSTGRES_PASSWORD length is acceptable
  ✅ POSTGRES_PASSWORD doesn't contain common weak patterns

📝 Git Configuration:
  ✅ .env is properly ignored in .gitignore

================================
✅ Environment validation PASSED

All required environment variables are properly configured.
You can now start the application safely.
```

---

## 不同环境的配置

### 开发环境 (development)

```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
POSTGRES_PASSWORD=dev_password_change_in_production
```

### 测试环境 (staging)

```bash
ENVIRONMENT=staging
LOG_LEVEL=INFO
POSTGRES_PASSWORD=staging_secure_password_123
SENTRY_DSN=https://xxx@sentry.io/staging
```

### 生产环境 (production)

```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
POSTGRES_PASSWORD=production_very_secure_password_456
SENTRY_DSN=https://xxx@sentry.io/production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

## 故障排查

### 问题: Docker Compose 启动失败

```
Error: POSTGRES_PASSWORD not set
```

**解决方案**:
1. 确认 `.env` 文件存在
2. 确认 `POSTGRES_PASSWORD` 已设置
3. 运行 `./scripts/check-env.sh` 验证

### 问题: API 密钥无效

```
401 Unauthorized: Invalid API key
```

**解决方案**:
1. 检查 API 密钥格式是否正确
2. 确认密钥未过期
3. 验证密钥权限

### 问题: 环境变量未生效

**解决方案**:
```bash
# 重新加载 .env
docker-compose down
docker-compose up -d
```

---

## 更多资源

- [Docker Compose 环境变量文档](https://docs.docker.com/compose/environment-variables/)
- [12-Factor App: 配置](https://12factor.net/config)
- [OWASP 密钥管理备忘单](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)

---

## 联系支持

如有问题，请:
1. 查看 [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
2. 运行 `./scripts/check-env.sh` 获取诊断信息
3. 在 GitHub Issues 中报告问题
