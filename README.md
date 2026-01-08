# HelloAgents Platform

**Interactive Agent Learning Platform** - 通过实践学习 AI Agent 开发

[![CI Tests](https://github.com/ai520510xyf-del/helloagents-platform/workflows/CI%20-%20Test%20Suite/badge.svg)](https://github.com/ai520510xyf-del/helloagents-platform/actions)
[![Backend Coverage](https://img.shields.io/badge/backend%20coverage-82%25-brightgreen)](./backend/htmlcov/index.html)
[![Frontend Coverage](https://img.shields.io/badge/frontend%20coverage-84.63%25-brightgreen)](./frontend/coverage/)
[![Tests](https://img.shields.io/badge/tests-216%20passing-brightgreen)](#测试)

---

## 项目简介

HelloAgents 是一个互动式学习平台，帮助开发者通过实践学习 AI Agent 开发。平台提供：

- 🎯 **结构化课程** - 从基础到进阶的完整学习路径
- 💻 **在线编码** - 内置 Python 代码编辑器和沙箱环境
- 🤖 **AI 助手** - 实时代码辅导和问题解答
- 📊 **进度跟踪** - 记录学习进度和代码提交历史
- 🔒 **安全沙箱** - Docker 容器隔离的代码执行环境

---

## 技术栈

### 后端
- **框架**: FastAPI 0.109.0
- **数据库**: SQLite + SQLAlchemy ORM
- **沙箱**: Docker (Python 3.11-slim)
- **测试**: pytest (82% coverage, 151/151 tests passing)

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite 5.4.13
- **UI 库**: Tailwind CSS 3.4.17
- **测试**: Vitest + React Testing Library (84.63% coverage, 65/65 tests passing)

---

## 快速开始

### 前置要求
- Python 3.11+
- Node.js 18+
- Docker 20.10+ (用于代码沙箱)
- Git

### 1. 克隆仓库
```bash
git clone https://github.com/ai520510xyf-del/helloagents-platform.git
cd helloagents-platform
```

### 2. 后端设置
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 DEEPSEEK_API_KEY

# 初始化数据库
python3 init_db.py

# 运行测试
pytest

# 启动后端服务器
python3 run.py
# 后端将在 http://localhost:8000 运行
```

### 3. 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 运行测试
npm test

# 启动开发服务器
npm run dev
# 前端将在 http://localhost:5173 运行
```

---

## Git 工作流

### 分支策略 (Git Flow)

```
main (生产分支)
  ↑
develop (开发分支)
  ↑
feature/xxx (功能分支)
```

### 提交规范 (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型:**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例:**
```bash
git commit -m "feat(backend): add chat API test cases

- Add test for successful chat flow
- Add test for API key error handling
- Add test for streaming response

Closes #123"
```

### 开发流程

1. **从 develop 创建功能分支**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
```

2. **开发并提交**
```bash
# 进行代码修改
git add .
git commit -m "feat: add new feature"
```

3. **推送到远程**
```bash
git push origin feature/my-feature
```

4. **创建 Pull Request**
- 从 `feature/my-feature` 到 `develop`
- 等待代码审查
- CI 测试通过后合并

5. **删除功能分支**
```bash
git checkout develop
git pull origin develop
git branch -d feature/my-feature
```

### 常用命令

```bash
# 查看状态
git status

# 查看提交历史
git log --oneline --graph --all

# 查看分支
git branch -a

# 切换分支
git checkout develop

# 更新本地代码
git pull origin develop

# 暂存修改
git stash
git stash pop
```

---

## 测试

### 后端测试
```bash
cd backend

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term

# 运行特定测试文件
pytest tests/test_api_basic.py

# 运行特定测试用例
pytest tests/test_api_basic.py::test_root_endpoint
```

### 前端测试
```bash
cd frontend

# 运行所有测试
npm test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行测试 (watch 模式)
npm run test:watch

# 运行测试 (UI 模式)
npm run test:ui
```

### CI/CD

项目使用 GitHub Actions 进行持续集成:
- ✅ 每次 Push/PR 自动运行测试
- ✅ 自动生成覆盖率报告
- ✅ 构建检查
- ✅ 代码质量检查 (ESLint)

查看 CI 配置: `.github/workflows/test.yml`

---

## 项目结构

```
helloagents-platform/
├── .github/
│   └── workflows/
│       └── test.yml              # CI 配置
├── backend/
│   ├── app/
│   │   ├── models/               # 数据库模型
│   │   ├── routers/              # API 路由
│   │   ├── database.py           # 数据库连接
│   │   ├── main.py               # FastAPI 应用
│   │   └── sandbox.py            # 代码沙箱
│   ├── tests/                    # 后端测试
│   ├── requirements.txt          # Python 依赖
│   └── pytest.ini                # pytest 配置
├── frontend/
│   ├── src/
│   │   ├── components/           # React 组件
│   │   ├── hooks/                # 自定义 Hooks
│   │   ├── pages/                # 页面组件
│   │   ├── services/             # API 服务
│   │   └── test/                 # 前端测试
│   ├── package.json              # Node.js 依赖
│   └── vitest.config.ts          # Vitest 配置
├── reports/                      # 项目报告
├── .gitignore                    # Git 忽略文件
├── README.md                     # 项目说明
└── SPRINT_PLAN.md               # Sprint 计划

```

---

## API 文档

### 后端 API

启动后端后访问:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端点

**课程管理**
- `GET /api/lessons` - 获取所有课程
- `GET /api/lessons/{lesson_id}` - 获取课程详情

**代码执行**
- `POST /api/sandbox/execute` - 执行 Python 代码

**用户进度**
- `GET /api/progress/{user_id}` - 获取用户进度
- `POST /api/progress/{user_id}` - 更新用户进度

**AI 聊天**
- `POST /api/chat` - 发送聊天消息 (SSE 流式响应)

**数据迁移**
- `POST /api/migrate` - 从 localStorage 迁移数据

---

## 开发指南

### 代码风格

**Python**
- 遵循 PEP 8
- 使用 Black 格式化 (行长度 88)
- 类型提示 (Type Hints)

**TypeScript**
- ESLint + Prettier
- React Hooks 规范
- 组件文件使用 PascalCase

### 代码审查清单

**功能正确性**
- [ ] 功能符合需求
- [ ] 边界情况已处理
- [ ] 错误处理完善

**代码质量**
- [ ] 代码可读性良好
- [ ] 变量命名清晰
- [ ] 无重复代码
- [ ] 遵循项目风格

**测试**
- [ ] 单元测试覆盖
- [ ] 测试用例充分
- [ ] 测试全部通过

**安全性**
- [ ] 输入验证完善
- [ ] 无安全漏洞

---

## 故障排查

### 后端问题

**测试失败**
1. 检查数据库是否初始化: `python3 init_db.py`
2. 检查依赖是否安装: `pip install -r requirements.txt`
3. 检查 Docker 是否运行: `docker ps`

**Docker 问题**
```bash
# 检查 Docker 版本
docker --version

# 清理容器
docker system prune -a
```

### 前端问题

**依赖安装失败**
```bash
# 清理并重新安装
rm -rf node_modules package-lock.json
npm install
```

**测试失败**
```bash
# 清理缓存
npm run test:clear

# 重新运行测试
npm test
```

---

## 当前状态

### Phase 1 完成度: 95%

**Sprint 1 已完成** ✅
- ✅ 数据库架构设计 (SQLite + SQLAlchemy)
- ✅ ORM 模型实现 (5 张表)
- ✅ 数据库 API 集成 (151/151 测试通过)
- ✅ 沙箱安全加固 (80/80 测试通过)
- ✅ 后端测试框架 (pytest, 82% 覆盖率, 151 测试)
- ✅ 前端测试框架 (Vitest, 84.63% 覆盖率, 65 测试)
- ✅ LearnPage 重构 (705 行 → 213 行)
- ✅ Git 仓库初始化并推送到 GitHub
- ✅ 测试框架增强 (MSW 2.x, 测试工厂)
- ✅ CI/CD 配置优化 (GitHub Actions)

**进行中 (Sprint 2)**
- 🔄 日志监控系统 (structlog + Sentry)
- 🔄 容器池架构设计

**计划中 (Sprint 3-4)**
- 📋 容器池实现 (性能优化)
- 📋 错误处理统一 (前后端)
- 📋 API 版本控制
- 📋 数据迁移工具

---

## 贡献指南

欢迎贡献！请遵循以下步骤:

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交修改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

详细指南请参考 `CONTRIBUTING.md` (即将添加)

---

## 许可证

MIT License - 详见 `LICENSE` 文件

---

## 联系方式

- **项目主页**: [https://github.com/ai520510xyf-del/helloagents-platform](https://github.com/ai520510xyf-del/helloagents-platform)
- **问题反馈**: [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)
- **文档**: [Wiki](https://github.com/ai520510xyf-del/helloagents-platform/wiki)

---

## 致谢

感谢所有贡献者的努力和支持！

**核心团队**
- Technical Architect
- Senior Backend Developer
- Senior Frontend Developer
- DevOps Engineer
- Technical Project Manager

**顾问团队**
- QA Automation Engineer
- Security Auditor
- UI/UX Engineer

---

**Last Updated**: 2026-01-08 | **Version**: Phase 1 (Sprint 1)
