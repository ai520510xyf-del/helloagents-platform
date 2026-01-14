# Cloudflare Workers AI 配置指南

HelloAgents 平台使用 Cloudflare Workers AI 提供图片分析功能。本文档说明如何配置所需的环境变量。

## 为什么需要 Cloudflare Workers AI？

- **图片分析功能**：当用户在聊天中上传图片时，需要使用支持视觉的 AI 模型来分析图片内容
- **Llama 3.2 Vision 模型**：我们使用 Cloudflare 的 `@cf/meta/llama-3.2-11b-vision-instruct` 模型
- **成本效益**：Cloudflare Workers AI 提供免费额度，非常适合初期使用

## 获取 Cloudflare 配置

### 1. 注册 Cloudflare 账号

访问 [Cloudflare Dashboard](https://dash.cloudflare.com/) 并注册账号（如果还没有）。

### 2. 获取 Account ID

1. 登录 Cloudflare Dashboard
2. 在右侧边栏或账号设置中找到 **Account ID**
3. 复制这个 ID

### 3. 创建 API Token

1. 访问 [API Tokens 页面](https://dash.cloudflare.com/profile/api-tokens)
2. 点击 "Create Token"
3. 选择 "Custom Token" 或使用 "Workers AI" 模板
4. 设置权限：
   - **Account** > **Workers AI** > **Edit**
5. 点击 "Continue to summary"
6. 点击 "Create Token"
7. **重要**：立即复制生成的 Token（关闭页面后将无法再查看）

## 在 Render 中配置

### 方法 1：通过 Render Dashboard（推荐）

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 选择你的 `helloagents-backend` 服务
3. 点击 "Environment" 标签
4. 添加以下环境变量：

```
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
```

5. 点击 "Save Changes"
6. Render 会自动重新部署服务

### 方法 2：通过 render.yaml（已配置）

`render.yaml` 文件中已经包含了这些环境变量的声明：

```yaml
envVars:
  - key: CLOUDFLARE_ACCOUNT_ID
    sync: false  # 需要在 Dashboard 中手动设置

  - key: CLOUDFLARE_API_TOKEN
    sync: false  # 需要在 Dashboard 中手动设置

  - key: AI_PROVIDER
    value: cloudflare-vision  # 启用 Cloudflare Workers AI
```

你仍然需要在 Render Dashboard 中设置实际的值。

## 验证配置

配置完成后，重新部署服务。检查部署日志：

- ✅ **成功**：上传图片后，AI 能够描述图片内容
- ❌ **失败**：会看到错误提示 "图片分析功能需要配置 Cloudflare Workers AI"

## 本地开发配置

在本地开发时，在 `backend/.env` 文件中添加：

```bash
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
AI_PROVIDER=cloudflare-vision
```

## 故障排除

### 错误：CLOUDFLARE_CONFIG_MISSING

**原因**：环境变量未设置或值为空

**解决方案**：
1. 确认在 Render Dashboard 中设置了两个环境变量
2. 确认变量名拼写正确（区分大小写）
3. 重新部署服务

### 错误：Cloudflare AI request failed

**原因**：API Token 权限不足或已过期

**解决方案**：
1. 确认 API Token 有 "Workers AI Edit" 权限
2. 检查 Token 是否过期
3. 重新创建 Token 并更新环境变量

### 错误：Cloudflare AI request timed out

**原因**：API 请求超时（60秒限制）

**解决方案**：
1. 检查网络连接
2. 图片文件可能过大，尝试压缩图片
3. 稍后重试

## 成本考虑

Cloudflare Workers AI 定价（截至 2024）：
- **免费额度**：每天 10,000 次 Neurons（AI 调用单位）
- **超出部分**：$0.011 per 1,000 Neurons

对于个人学习平台，免费额度通常足够使用。

## 相关资源

- [Cloudflare Workers AI 文档](https://developers.cloudflare.com/workers-ai/)
- [Llama 3.2 Vision 模型文档](https://developers.cloudflare.com/workers-ai/models/llama-3.2-vision/)
- [API Token 管理](https://dash.cloudflare.com/profile/api-tokens)

## 支持

如有问题，请在 GitHub Issues 中提问。
