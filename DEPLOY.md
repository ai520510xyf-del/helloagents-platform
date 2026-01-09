# 🚀 HelloAgents 部署指南

## 前端部署（Vercel）

### 方式 1：通过 Vercel 网站部署（推荐）

1. **访问 Vercel**
   - 打开 https://vercel.com
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 "Add New" → "Project"
   - 选择你的 GitHub 仓库 `helloagents-platform`
   - 点击 "Import"

3. **配置项目**
   - **Root Directory**: 选择 `frontend`
   - **Framework Preset**: Vite（自动检测）
   - **Build Command**: `npm run build`（自动填写）
   - **Output Directory**: `dist`（自动填写）

4. **配置环境变量**

   点击 "Environment Variables"，添加：

   | Name | Value |
   |------|-------|
   | `VITE_API_URL` | 你的后端 API 地址（暂时可以填 `http://localhost:8000`） |

5. **部署**
   - 点击 "Deploy"
   - 等待几分钟，部署完成！
   - Vercel 会自动生成一个域名，例如：`helloagents-xxx.vercel.app`

6. **后续更新**
   - 每次推送代码到 GitHub，Vercel 会自动重新部署
   - 无需手动操作！

---

### 方式 2：使用 Vercel CLI

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 进入前端目录
cd frontend

# 3. 登录 Vercel
vercel login

# 4. 部署
vercel

# 5. 生产环境部署
vercel --prod
```

---

## 后端部署（待配置）

后端需要部署到支持 Python 和 Docker 的平台，推荐：

### 选项 A：Railway（推荐）
- ✅ 支持 Docker
- ✅ 免费额度：500 小时/月
- ✅ 自动部署
- ✅ 内置 PostgreSQL（可替换 SQLite）

### 选项 B：Fly.io
- ✅ 支持 Docker
- ✅ 免费额度：3个共享 CPU
- ✅ 全球部署

### 选项 C：Render
- ✅ 支持 Docker
- ✅ 免费层级
- ✅ 自动部署

---

## 数据库（Supabase）

### 1. 创建 Supabase 项目

1. 访问 https://supabase.com
2. 创建新项目
3. 获取连接信息：
   - Database URL
   - API URL
   - API Key

### 2. 配置后端

将 SQLite 迁移到 Supabase PostgreSQL：

```python
# backend/.env
DATABASE_URL=postgresql://user:password@db.xxx.supabase.co:5432/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_api_key
```

---

## 完整部署流程

### Step 1: 前端部署到 Vercel
- ✅ 按照上面的步骤操作
- ✅ 记录 Vercel 部署的域名

### Step 2: 后端部署（选择一个平台）
- 📋 待配置

### Step 3: 配置数据库
- 📋 创建 Supabase 项目
- 📋 迁移数据库结构
- 📋 配置环境变量

### Step 4: 连接前后端
- 📋 在 Vercel 环境变量中更新 `VITE_API_URL` 为后端地址
- 📋 重新部署前端

---

## 环境变量清单

### 前端（Vercel）

| 变量 | 说明 | 示例 |
|------|------|------|
| `VITE_API_URL` | 后端 API 地址 | `https://api.example.com` |

### 后端（待配置）

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | 数据库连接 | `postgresql://...` |
| `DEEPSEEK_API_KEY` | AI 助手 API Key | `sk-...` |
| `SUPABASE_URL` | Supabase URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase API Key | `eyJ...` |

---

## 故障排查

### 前端部署失败

**问题：构建失败**
- 检查 `package.json` 中的依赖是否正确
- 确保 Node.js 版本兼容（需要 18+）

**问题：页面 404**
- 检查 `vercel.json` 的 rewrites 配置
- 确保路由配置正确

### 后端连接失败

**问题：CORS 错误**
- 后端需要配置 CORS 允许前端域名
- 添加 Vercel 域名到 CORS 白名单

**问题：API 超时**
- 检查后端是否正常运行
- 检查网络连接

---

## 下一步

1. ✅ 前端已配置完成，可以部署到 Vercel
2. ⏳ 后端部署需要选择平台并配置
3. ⏳ 数据库需要迁移到 Supabase

**需要帮助？** 查看 [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)
