# Cloudflare Workers AI 图片分析功能配置指南

本文档介绍如何配置 Cloudflare Workers AI 以启用 AI 助手的图片分析功能。

## 功能说明

- 使用 **Cloudflare Workers AI** 的 **Llama 3.2 Vision** 模型
- 支持图片分析、图像问答、OCR等视觉理解任务
- 每天 **10,000 次免费请求额度**
- 与现有 DeepSeek 文本模型共存，自动根据是否有图片选择合适的模型

## 配置步骤

### 1. 获取 Cloudflare Account ID

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 点击左侧菜单 **Workers & Pages**
3. 在概览页面右侧可以看到你的 **Account ID**
4. 复制该 ID

### 2. 创建 API Token

1. 访问 [API Tokens 页面](https://dash.cloudflare.com/profile/api-tokens)
2. 点击 **Create Token**
3. 选择 **Create Custom Token**
4. 配置权限：
   - **Account** → **Workers AI** → **Read** ✅
   - **Account** → **Workers AI** → **Edit** ✅
5. 设置 **Account Resources**：
   - 选择你的账户
6. 点击 **Continue to summary**，然后 **Create Token**
7. **重要**：复制生成的 Token（只显示一次）

### 3. 配置环境变量

#### 本地开发

编辑 `backend/.env` 文件，添加以下配置：

```bash
# Cloudflare Workers AI 配置
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here

# 可选：设置 AI 提供商（默认为 deepseek-chat）
# deepseek-chat: 纯文本对话（无图片时更快更便宜）
# cloudflare-vision: 始终使用 Cloudflare（适合测试）
AI_PROVIDER=deepseek-chat
```

#### 生产环境（Render）

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 选择你的 Web Service
3. 进入 **Environment** 标签
4. 添加环境变量：
   - `CLOUDFLARE_ACCOUNT_ID` = 你的 Account ID
   - `CLOUDFLARE_API_TOKEN` = 你的 API Token
   - `AI_PROVIDER` = `deepseek-chat` (可选)
5. 保存后 Render 会自动重新部署

## 工作原理

### 智能模型选择

后端会根据请求自动选择合适的 AI 模型：

```
有图片？
  ├─ 是 → 使用 Cloudflare Llama 3.2 Vision
  └─ 否 → 使用 DeepSeek Chat（更快、更便宜）
```

### 降级策略

如果 Cloudflare Workers AI 调用失败（例如配置错误、额度用尽），系统会自动降级到 DeepSeek：

```
Cloudflare 失败？
  └─ 降级到 DeepSeek（添加提示：无法处理图片）
```

## 使用方式

### 前端使用

用户在 AI 助手对话框中：

1. 点击图片上传按钮 📷
2. 选择或粘贴图片（支持 JPG, PNG, WebP）
3. 输入问题（例如："这张图片中有什么？"）
4. 点击发送

图片会自动通过 base64 编码发送到后端。

### API 调用示例

```bash
curl -X POST 'https://your-backend.onrender.com/api/chat' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "这张图片中有什么？",
    "conversation_history": [],
    "lesson_id": "1",
    "code": "",
    "images": ["data:image/jpeg;base64,/9j/4AAQSkZJRgABA..."]
  }'
```

## 限制和注意事项

### 图片限制

- **格式**：JPG, PNG, WebP
- **大小**：建议 < 5MB
- **数量**：目前仅支持发送 1 张图片（模型限制）

### 免费额度

- 每天 **10,000 次请求**
- 超出后会自动降级到 DeepSeek
- 额度在 UTC 时间每天重置

### 响应时间

- Cloudflare Vision: 约 5-15 秒
- DeepSeek Chat: 约 2-5 秒

## 故障排查

### 问题：收到"CLOUDFLARE_ACCOUNT_ID must be set"错误

**解决方案：**
- 检查 `.env` 文件是否正确配置
- 确认环境变量已加载（重启后端服务）
- 生产环境：检查 Render 环境变量配置

### 问题：图片分析失败，但文本对话正常

**可能原因：**
1. API Token 权限不足
   - 解决：重新创建 Token，确保有 Workers AI Read/Edit 权限
2. Account ID 错误
   - 解决：在 Cloudflare Dashboard 确认正确的 Account ID
3. 免费额度用尽
   - 解决：等待次日额度重置，或升级到付费计划

### 问题：所有请求都返回"无法连接到AI服务"

**可能原因：**
- DeepSeek API Key 也未配置
- 解决：至少配置 DeepSeek 或 Cloudflare 其中一个

## 测试

### 手动测试

使用图片分析功能：

1. 启动后端：`python run.py`
2. 访问前端：`http://localhost:5173`
3. 在 AI 助手中上传测试图片
4. 输入"描述这张图片"并发送

### API 测试

```bash
# 测试 Cloudflare Workers AI 健康状态
curl https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai/run/@cf/meta/llama-3.2-11b-vision-instruct \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -d '{"messages":[{"role":"user","content":[{"type":"text","text":"Hello"}]}]}'
```

## 更多资源

- [Cloudflare Workers AI 文档](https://developers.cloudflare.com/workers-ai/)
- [Llama 3.2 Vision 模型文档](https://developers.cloudflare.com/workers-ai/models/llama-3.2-11b-vision-instruct/)
- [API Tokens 管理](https://dash.cloudflare.com/profile/api-tokens)

## 支持

遇到问题？

- [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)
- [Cloudflare Community](https://community.cloudflare.com/)
