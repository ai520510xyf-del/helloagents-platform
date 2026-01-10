# Render 生产环境配置指南

## 🔴 Critical: 配置 DEEPSEEK_API_KEY

### 方法1: 通过 Render Dashboard（推荐，5分钟）

1. **登录 Render**
   - 访问: https://dashboard.render.com/
   - 使用你的账号登录

2. **选择后端服务**
   - 找到 `helloagents-platform-backend` 服务
   - 点击进入服务详情页

3. **配置环境变量**
   - 左侧菜单 → **Environment**
   - 点击 **Add Environment Variable**
   - 填写:
     ```
     Key: DEEPSEEK_API_KEY
     Value: [从开发环境获取的密钥]
     ```

4. **获取 DEEPSEEK_API_KEY**
   ```bash
   # 在本地项目运行
   cat backend/.env | grep DEEPSEEK_API_KEY
   ```

5. **保存并重启**
   - 点击 **Save Changes**
   - Render 会自动重启服务（约2分钟）

6. **验证**
   ```bash
   # 测试 AI 助手端点
   curl -X POST https://你的后端域名/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "你好", "lesson_id": "intro", "conversation_history": []}'

   # 应该返回 AI 的回复，而不是错误
   ```

---

### 方法2: 通过 Render CLI（3分钟）

```bash
# 1. 安装 Render CLI
npm install -g @render/cli

# 2. 登录
render login

# 3. 列出服务
render services list

# 4. 设置环境变量
render env:set DEEPSEEK_API_KEY="你的密钥" \
  --service=helloagents-platform-backend

# 5. 验证
render env:get DEEPSEEK_API_KEY \
  --service=helloagents-platform-backend
```

---

### 方法3: 通过 Render API（自动化，1分钟）

如果你给我 Render API Token，我可以帮你自动配置：

```bash
# 获取 API Token
# Render Dashboard → Account Settings → API Keys → Create API Key

# 然后运行：
export RENDER_API_KEY="你的token"

curl -X PATCH "https://api.render.com/v1/services/YOUR_SERVICE_ID/env-vars" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "env_vars": [
      {
        "key": "DEEPSEEK_API_KEY",
        "value": "你的密钥"
      }
    ]
  }'
```

---

## ✅ 验证配置成功

### 1. 检查服务状态
```bash
# 查看 Render 服务日志
# Dashboard → Service → Logs

# 应该看到：
# ✅ Service started successfully
# ✅ Connected to database
# ✅ AI Assistant initialized
```

### 2. 测试 AI 助手
```bash
# 测试聊天功能
curl -X POST https://你的后端域名/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "什么是智能体？",
    "lesson_id": "intro",
    "conversation_history": []
  }' | jq .

# 预期响应：
{
  "response": "智能体（Agent）是...",
  "success": true
}
```

### 3. 前端测试
1. 访问: https://你的前端域名/learn
2. 打开 AI 助手面板
3. 发送消息"你好"
4. 应该收到 AI 的回复

---

## 🔍 常见问题

### Q1: 重启后还是报错？
**A**: 检查密钥格式，确保没有多余空格或换行

### Q2: 如何查看当前配置？
**A**: Render Dashboard → Service → Environment → 查看已配置的变量

### Q3: 密钥泄露怎么办？
**A**: 立即到 DeepSeek 控制台重新生成密钥，然后更新 Render

---

## 📝 本地开发环境配置

如果本地也没配置，运行：

```bash
# backend/.env
echo "DEEPSEEK_API_KEY=sk-your-actual-key" >> backend/.env

# 重启后端服务
cd backend
uvicorn app.main:app --reload
```

---

**完成后请告诉我，我会验证配置！** ✅
