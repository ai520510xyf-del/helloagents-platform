# 🚀 Cloudflare Pages 部署指南

## 方式 1：通过 Cloudflare 控制台部署（推荐）⭐

这是最简单的方式，只需在网页上点几下。

### 步骤 1：登录 Cloudflare

1. 访问 https://dash.cloudflare.com/
2. 使用 GitHub 账号登录（或创建账号）

### 步骤 2：创建 Pages 项目

1. 在左侧菜单找到 **"Workers & Pages"**
2. 点击 **"Create application"** 或 **"Create"** 按钮
3. 选择 **"Pages"** 标签
4. 点击 **"Connect to Git"**

### 步骤 3：连接 GitHub 仓库

1. 选择 **"Connect GitHub"**
2. 授权 Cloudflare 访问您的 GitHub
3. 选择仓库 `helloagents-platform`
4. 点击 **"Begin setup"**

### 步骤 4：配置构建设置

在配置页面填写：

| 设置项 | 值 |
|--------|-----|
| **Project name** | `helloagents-platform` |
| **Production branch** | `main` |
| **Framework preset** | 选择 `Vite` 或 `None` |
| **Build command** | `cd frontend && npm run build` |
| **Build output directory** | `frontend/dist` |
| **Root directory** | 留空 |

### 步骤 5：配置环境变量

点击 **"Environment variables"** 添加：

| 变量名 | 值 |
|--------|-----|
| `VITE_API_URL` | 您的后端 API 地址（Railway URL）|
| `NODE_VERSION` | `18` |

**重要**：请将后端 Railway URL 填入 `VITE_API_URL`

### 步骤 6：部署

1. 点击 **"Save and Deploy"**
2. 等待 2-5 分钟，Cloudflare 会：
   - 克隆代码
   - 安装依赖
   - 构建项目
   - 部署到全球 CDN

### 步骤 7：获取访问地址

部署完成后，您会看到：
- 生产环境 URL：`helloagents-platform.pages.dev`
- 每次部署的预览 URL

---

## 方式 2：使用 Wrangler CLI 部署

如果您喜欢命令行，可以使用这个方式。

### 步骤 1：安装 Wrangler

```bash
npm install -g wrangler
```

### 步骤 2：登录

```bash
wrangler login
```

浏览器会打开，授权后返回终端。

### 步骤 3：构建项目

```bash
cd frontend
npm run build
```

### 步骤 4：部署

```bash
wrangler pages deploy dist --project-name=helloagents-platform
```

首次部署会提示创建项目，选择 `y` 确认。

---

## ✅ 部署后的操作

### 1. 更新后端 CORS 配置

后端需要允许 Cloudflare Pages 域名访问。

在后端的 `.env` 文件中更新 `CORS_ORIGINS`：

```bash
CORS_ORIGINS=http://localhost:5173,https://helloagents-platform.pages.dev
```

然后重新部署后端到 Railway。

### 2. 测试访问

访问您的 Cloudflare Pages URL：
```
https://helloagents-platform.pages.dev
```

### 3. 自动部署

以后每次推送代码到 GitHub：
- `main` 分支 → 自动部署到生产环境
- 其他分支 → 自动生成预览 URL

---

## 🎯 Cloudflare Pages vs Vercel

| 功能 | Cloudflare Pages | Vercel |
|------|------------------|--------|
| 中国访问 | ✅ 较稳定 | ❌ 受限 |
| 免费额度 | ✅ 500 次构建/月 | ✅ 100 GB 带宽/月 |
| 构建速度 | 🟡 中等 | ✅ 快 |
| 全球 CDN | ✅ 是 | ✅ 是 |
| 自动部署 | ✅ 是 | ✅ 是 |

---

## 🔧 故障排查

### 构建失败

**问题**：构建时找不到 frontend 目录

**解决**：确保构建命令为 `cd frontend && npm run build`

---

**问题**：Node 版本不兼容

**解决**：在环境变量中添加 `NODE_VERSION=18`

---

### CORS 错误

**问题**：前端无法调用后端 API

**解决**：
1. 确认后端 CORS 配置包含 Cloudflare Pages 域名
2. 重新部署后端

---

### 页面 404

**问题**：访问子路由时出现 404

**解决**：Cloudflare Pages 自动处理 SPA 路由，无需额外配置。如果仍有问题，检查 `frontend/dist` 是否包含 `index.html`

---

## 📝 下一步

1. ✅ 部署到 Cloudflare Pages
2. ⏳ 更新后端 CORS 配置
3. ⏳ 测试完整功能
4. 🎉 开始使用！

---

需要帮助？查看 [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
