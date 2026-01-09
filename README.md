# HelloAgents Platform

**通过实践学习 AI Agent 开发的互动学习平台**

[![CI Tests](https://github.com/ai520510xyf-del/helloagents-platform/workflows/CI%20-%20Test%20Suite/badge.svg)](https://github.com/ai520510xyf-del/helloagents-platform/actions)

---

## 🎯 这是什么？

HelloAgents 是一个帮助开发者学习 AI Agent 开发的互动式学习平台。通过结构化的课程、在线编码环境和 AI 助手，让你从零开始掌握 Agent 开发。

**核心功能：**
- 📚 **结构化课程** - 从基础到进阶的完整学习路径
- 💻 **在线编码** - 内置 Python 代码编辑器，无需本地配置
- 🤖 **AI 助手** - 实时代码辅导和问题解答
- 📊 **学习跟踪** - 记录学习进度和代码提交
- 🔒 **安全沙箱** - Docker 隔离的安全代码执行环境

---

## 🚀 快速开始

### 方式 1：在线访问（推荐）

直接访问：[HelloAgents 学习平台](#)（部署中，即将上线）

无需安装，立即开始学习！

> 💡 **想要部署自己的实例？** 查看 [部署指南](./DEPLOY.md)

### 方式 2：本地运行

#### 前置要求
- Python 3.11+
- Node.js 18+
- Docker（用于代码沙箱）

#### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/ai520510xyf-del/helloagents-platform.git
cd helloagents-platform
```

2. **启动后端**
```bash
cd backend
pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，添加 DEEPSEEK_API_KEY（AI 助手功能需要）

python3 init_db.py  # 初始化数据库
python3 run.py      # 启动后端服务器
```

后端将在 `http://localhost:8000` 运行

3. **启动前端**
```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:5173` 运行

4. **开始学习**

打开浏览器访问 `http://localhost:5173`，开始你的 Agent 学习之旅！

---

## 📖 如何学习？

1. **选择课程** - 从课程列表中选择适合你水平的课程
2. **观看讲解** - 阅读课程内容和示例代码
3. **动手实践** - 在代码编辑器中完成练习
4. **运行测试** - 执行代码查看结果
5. **获取帮助** - 遇到问题时向 AI 助手求助
6. **继续前进** - 完成当前课程，解锁下一关

---

## 🛠️ 技术栈

### 后端
- FastAPI - 高性能 Web 框架
- SQLite - 轻量级数据库
- Docker - 代码沙箱容器

### 前端
- React 18 - UI 框架
- TypeScript - 类型安全
- Vite - 快速构建工具
- Tailwind CSS - 样式框架

---

## 📝 常见问题

### 为什么需要 Docker？
Docker 用于创建安全隔离的代码执行环境，确保你的代码不会影响系统安全。

### 可以离线学习吗？
部分课程内容可以离线学习，但 AI 助手功能需要网络连接。

### 学习需要付费吗？
完全免费！所有课程内容和功能都是开源免费的。

### 遇到 bug 怎么办？
欢迎在 [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues) 提交问题。

---

## 🤝 贡献

欢迎贡献代码、课程内容或提出改进建议！

1. Fork 本仓库
2. 创建功能分支
3. 提交你的修改
4. 创建 Pull Request

---

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

## 🔗 相关链接

- **项目主页**: https://github.com/ai520510xyf-del/helloagents-platform
- **问题反馈**: https://github.com/ai520510xyf-del/helloagents-platform/issues
- **在线文档**: https://github.com/ai520510xyf-del/helloagents-platform/wiki

---

**开始你的 Agent 学习之旅吧！** 🚀
