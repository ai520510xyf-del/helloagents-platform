# Cloudflare Pages 配置指南

## 问题原因

Cloudflare Pages 直接运行 `npm run build`，但没有先安装依赖（node_modules），导致找不到 vite 命令。

## 正确配置

登录 Cloudflare Pages 后台，设置以下配置：

### 构建设置（Build settings）

1. **Framework preset（框架预设）**: Vite

2. **Build command（构建命令）**:
   ```bash
   cd frontend && npm ci && npm run build
   ```

3. **Build output directory（构建输出目录）**:
   ```
   frontend/dist
   ```

4. **Root directory（根目录）**:
   ```
   /
   ```
   （留空或设置为 `/`，因为我们的项目是 monorepo 结构）

5. **Environment variables（环境变量）**:
   - `NODE_VERSION`: `20`
   - `VITE_API_URL`: 您的后端 API 地址（例如 `https://helloagents-platform.onrender.com`）

## 为什么之前能工作？

之前的 `package.json` 中 build 脚本是：
```json
"build": "tsc -b && vite build"
```

Cloudflare Pages 可能自动检测到这是一个 Vite 项目并自动安装了依赖。

## 当前问题

修改为 `"build": "vite build"` 后，Cloudflare Pages 可能没有正确检测到项目类型，导致跳过了依赖安装步骤。

## 解决方案选项

### 选项1：修改 Cloudflare Pages 构建命令（推荐）
在 Cloudflare Pages 后台修改构建命令为：
```bash
cd frontend && npm ci && npm run build
```

### 选项2：恢复 package.json 的 build 脚本
```json
"build": "tsc -b && vite build"
```

### 选项3：创建构建脚本
创建 `frontend/build.sh`:
```bash
#!/bin/bash
npm ci
npm run build
```

然后在 Cloudflare Pages 设置构建命令为：
```bash
cd frontend && chmod +x build.sh && ./build.sh
```

## 验证步骤

1. 修改配置后，触发重新部署
2. 查看构建日志，确认执行了 `npm ci` 或 `npm install`
3. 确认构建成功并生成了 dist 目录
4. 访问部署的网站验证功能

## 注意事项

- 使用 `npm ci` 而不是 `npm install` 可以确保一致的依赖安装
- 确保 NODE_VERSION 设置为 18 或 20（推荐 20）
- 如果使用环境变量，确保在 Cloudflare Pages 设置中配置
