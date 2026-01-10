# 开发者指南

**HelloAgents 学习平台开发指南**

本指南帮助开发者快速搭建本地开发环境，了解项目结构和开发流程。

---

## 📋 目录

- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [开发环境配置](#开发环境配置)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [常见问题](#常见问题)

---

## 前置要求

### 必需工具

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| **Python** | 3.11+ | 后端开发语言 |
| **Node.js** | 18+ | 前端开发环境 |
| **npm** | 9+ | 包管理工具 |
| **Docker** | 20+ | 代码沙箱容器 |
| **Git** | 2.30+ | 版本控制 |

### 可选工具

- **Docker Compose**: 简化多容器管理
- **VS Code**: 推荐的代码编辑器
- **Postman/Insomnia**: API 测试工具
- **DBeaver/TablePlus**: 数据库管理工具

### 验证环境

运行以下命令验证工具安装：

```bash
# Python
python3 --version  # 应显示 3.11 或更高

# Node.js
node --version     # 应显示 v18 或更高
npm --version      # 应显示 9 或更高

# Docker
docker --version   # 应显示 20 或更高
docker ps          # 验证 Docker 守护进程运行正常

# Git
git --version      # 应显示 2.30 或更高
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/ai520510xyf-del/helloagents-platform.git
cd helloagents-platform
```

### 2. 启动后端服务

```bash
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加必要的配置

# 初始化数据库
python3 init_db.py

# 启动开发服务器
python3 run.py
```

后端服务将在 `http://localhost:8000` 运行。

访问 `http://localhost:8000/api/v1/docs` 查看 API 文档。

### 3. 启动前端服务

打开新的终端窗口：

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 运行。

### 4. 验证安装

1. 打开浏览器访问 `http://localhost:5173`
2. 点击课程列表，应能正常加载
3. 在代码编辑器中输入 `print("Hello")` 并运行
4. 与 AI 助手聊天（需要配置 `DEEPSEEK_API_KEY`）

---

## 项目结构

```
helloagents-platform/
├── backend/                 # 后端服务（FastAPI）
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   └── v1/         # v1 版本 API
│   │   │       ├── routes/
│   │   │       │   ├── code.py      # 代码执行
│   │   │       │   ├── lessons.py   # 课程管理
│   │   │       │   ├── chat.py      # AI 聊天
│   │   │       │   └── sandbox.py   # 沙箱管理
│   │   │       └── __init__.py
│   │   ├── models/         # 数据库模型
│   │   │   ├── user.py
│   │   │   ├── lesson.py
│   │   │   ├── code_submission.py
│   │   │   └── chat_message.py
│   │   ├── middleware/     # 中间件
│   │   │   ├── logging_middleware.py
│   │   │   ├── error_handler.py
│   │   │   └── version_middleware.py
│   │   ├── routers/        # 向后兼容路由
│   │   ├── database.py     # 数据库配置
│   │   ├── sandbox.py      # 代码沙箱
│   │   ├── courses.py      # 课程管理器
│   │   ├── logger.py       # 日志配置
│   │   ├── exceptions.py   # 自定义异常
│   │   └── main.py         # 应用入口
│   ├── tests/              # 测试文件
│   │   ├── test_api.py
│   │   ├── test_sandbox.py
│   │   └── conftest.py
│   ├── docs/               # 后端文档
│   ├── scripts/            # 部署和工具脚本
│   ├── requirements.txt    # Python 依赖
│   ├── run.py             # 启动脚本
│   └── init_db.py         # 数据库初始化
│
├── frontend/               # 前端应用（React + Vite）
│   ├── src/
│   │   ├── components/    # React 组件
│   │   │   ├── CodeEditor/       # 代码编辑器
│   │   │   ├── ChatPanel/        # AI 聊天面板
│   │   │   ├── LessonView/       # 课程视图
│   │   │   └── ui/               # UI 组件库
│   │   ├── services/      # API 服务
│   │   │   ├── api.ts            # API 客户端
│   │   │   ├── codeService.ts    # 代码执行
│   │   │   ├── lessonService.ts  # 课程服务
│   │   │   └── chatService.ts    # 聊天服务
│   │   ├── store/         # 状态管理（Zustand）
│   │   │   ├── useCodeStore.ts
│   │   │   ├── useLessonStore.ts
│   │   │   └── useChatStore.ts
│   │   ├── types/         # TypeScript 类型定义
│   │   ├── utils/         # 工具函数
│   │   ├── App.tsx        # 应用入口
│   │   └── main.tsx       # React 挂载点
│   ├── tests/             # 前端测试
│   │   ├── unit/          # 单元测试
│   │   └── e2e/           # E2E 测试（Playwright）
│   ├── public/            # 静态资源
│   ├── package.json       # Node.js 依赖
│   ├── vite.config.ts     # Vite 配置
│   ├── tsconfig.json      # TypeScript 配置
│   └── tailwind.config.js # Tailwind CSS 配置
│
├── docs/                  # 项目文档
│   ├── API.md            # API 参考文档
│   ├── DEVELOPER_GUIDE.md # 开发者指南（本文档）
│   ├── ARCHITECTURE.md    # 架构设计文档
│   ├── DEPLOYMENT.md      # 部署指南
│   └── USER_GUIDE.md      # 用户手册
│
├── scripts/              # 自动化脚本
│   └── deployment/       # 部署相关
│       ├── health-check.sh
│       └── smoke-test.sh
│
├── .github/              # GitHub 配置
│   └── workflows/        # CI/CD 工作流
│       ├── ci-tests.yml
│       └── deploy.yml
│
├── README.md             # 项目说明
├── CONTRIBUTING.md       # 贡献指南
├── LICENSE               # 许可证
└── .gitignore           # Git 忽略文件
```

---

## 开发环境配置

### 后端环境变量

创建 `backend/.env` 文件：

```bash
# 应用配置
ENVIRONMENT=development
DEBUG=true

# 数据库配置
DATABASE_URL=sqlite:///./helloagents.db
# 生产环境使用 PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/helloagents

# AI 服务配置（必需）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# CORS 配置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174

# 沙箱配置
DOCKER_IMAGE=python:3.11-slim
SANDBOX_TIMEOUT=30
CONTAINER_POOL_SIZE=5

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json

# 监控配置（可选）
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### 前端环境变量

创建 `frontend/.env` 文件：

```bash
# API 配置
VITE_API_BASE_URL=http://localhost:8000

# 功能开关
VITE_ENABLE_AI_CHAT=true
VITE_ENABLE_CODE_HINTS=false

# 监控配置（可选）
VITE_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

### VS Code 配置

创建 `.vscode/settings.json`：

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "typescript.tsdk": "node_modules/typescript/lib",
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ]
}
```

创建 `.vscode/extensions.json`（推荐插件）：

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "charliermarsh.ruff"
  ]
}
```

---

## 开发流程

### 分支管理

采用 **Git Flow** 工作流：

```
main          (生产环境，受保护)
  ↑
develop       (开发主分支)
  ↑
feature/*     (功能开发分支)
bugfix/*      (Bug 修复分支)
hotfix/*      (紧急修复分支)
```

**创建功能分支：**

```bash
# 从 develop 创建新分支
git checkout develop
git pull origin develop
git checkout -b feature/add-new-lesson

# 开发完成后
git add .
git commit -m "feat: 添加新课程模块"
git push origin feature/add-new-lesson

# 在 GitHub 上创建 Pull Request
```

### Commit 规范

使用 **Conventional Commits** 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）：**

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 添加或修改测试
- `chore`: 构建或工具变更
- `ci`: CI/CD 配置

**示例：**

```bash
# 好的提交
git commit -m "feat(chat): 添加 Markdown 渲染支持"
git commit -m "fix(sandbox): 修复容器内存泄漏问题"
git commit -m "docs(api): 更新 API 文档示例"

# 避免的提交
git commit -m "修改了一些东西"
git commit -m "bug fix"
git commit -m "更新"
```

### Pull Request 流程

1. **创建 PR**
   - 标题遵循 Commit 规范
   - 描述清楚变更内容和原因
   - 关联相关 Issue

2. **自动检查**
   - CI 测试通过
   - 代码覆盖率 > 80%
   - Lint 检查通过

3. **代码审查**
   - 至少 1 位团队成员审查
   - 解决所有评论

4. **合并**
   - 使用 **Squash and Merge**
   - 删除功能分支

### 本地开发循环

```bash
# 1. 拉取最新代码
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/my-feature

# 3. 开发和测试
npm run dev           # 前端开发
python3 run.py        # 后端开发
npm run test          # 运行测试

# 4. 代码格式化
npm run lint          # 前端 Lint
ruff check backend/   # 后端 Lint
black backend/        # 后端格式化

# 5. 提交代码
git add .
git commit -m "feat: 添加新功能"

# 6. 推送并创建 PR
git push origin feature/my-feature
```

---

## 代码规范

### Python 规范（后端）

使用 **Ruff** 和 **Black** 进行代码检查和格式化。

**安装工具：**

```bash
pip install ruff black
```

**运行检查：**

```bash
# Lint 检查
ruff check backend/

# 自动修复
ruff check backend/ --fix

# 代码格式化
black backend/
```

**代码风格：**

```python
# ✅ 好的实践
from typing import Optional, List
from pydantic import BaseModel, Field

class CodeExecutionRequest(BaseModel):
    """代码执行请求"""
    code: str = Field(..., min_length=1, description="要执行的代码")
    language: str = Field(default="python", description="编程语言")
    timeout: int = Field(default=30, ge=1, le=60, description="超时时间（秒）")

def execute_code(request: CodeExecutionRequest) -> CodeExecutionResponse:
    """
    执行用户代码

    Args:
        request: 代码执行请求

    Returns:
        代码执行响应

    Raises:
        ValidationError: 参数验证失败
    """
    # 实现逻辑
    pass


# ❌ 避免的实践
def exec_code(code, lang="python", timeout=30):  # 缺少类型注解
    # 没有文档字符串
    pass
```

### TypeScript 规范（前端）

使用 **ESLint** 和 **Prettier** 进行代码检查和格式化。

**运行检查：**

```bash
# Lint 检查
npm run lint

# 代码格式化
npm run format
```

**代码风格：**

```typescript
// ✅ 好的实践
interface CodeExecutionRequest {
  code: string;
  language: string;
  timeout: number;
}

interface CodeExecutionResponse {
  success: boolean;
  output: string;
  error: string | null;
  execution_time: number;
}

/**
 * 执行代码
 * @param request - 代码执行请求
 * @returns 代码执行响应
 */
export async function executeCode(
  request: CodeExecutionRequest
): Promise<CodeExecutionResponse> {
  const response = await fetch('/api/v1/code/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`执行失败: ${response.statusText}`);
  }

  return response.json();
}


// ❌ 避免的实践
async function execCode(req: any): Promise<any> {  // 使用 any 类型
  // 缺少错误处理
  const res = await fetch('/api/v1/code/execute', {
    method: 'POST',
    body: JSON.stringify(req),
  });
  return res.json();
}
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| **变量** | 驼峰命名 | `userName`, `isActive` |
| **常量** | 大写下划线 | `API_BASE_URL`, `MAX_TIMEOUT` |
| **函数** | 驼峰命名（动词开头） | `getUserInfo()`, `validateInput()` |
| **类** | 帕斯卡命名 | `UserModel`, `CodeExecutor` |
| **组件** | 帕斯卡命名 | `CodeEditor`, `ChatPanel` |
| **文件** | 驼峰命名 | `userService.ts`, `codeEditor.tsx` |
| **接口/类型** | 帕斯卡命名 | `IUser`, `CodeRequest` |

---

## 测试指南

### 后端测试

使用 **pytest** 进行测试。

**运行测试：**

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 运行特定测试函数
pytest tests/test_api.py::test_execute_code

# 生成覆盖率报告
pytest --cov=app --cov-report=html
# 打开 htmlcov/index.html 查看报告
```

**编写测试：**

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_execute_code_success():
    """测试代码执行成功"""
    response = client.post(
        "/api/v1/code/execute",
        json={
            "code": "print('Hello, World!')",
            "language": "python",
            "timeout": 30
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Hello, World!" in data["output"]


def test_execute_code_syntax_error():
    """测试代码语法错误"""
    response = client.post(
        "/api/v1/code/execute",
        json={
            "code": "print('Hello'",  # 缺少括号
            "language": "python"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "SyntaxError" in data["error"]


@pytest.mark.asyncio
async def test_chat_with_ai():
    """测试 AI 聊天"""
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "什么是 Agent？",
            "lesson_id": "1"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["message"]) > 0
```

### 前端测试

使用 **Vitest** 进行单元测试，**Playwright** 进行 E2E 测试。

**运行单元测试：**

```bash
cd frontend

# 运行所有测试
npm run test

# 监听模式
npm run test:watch

# UI 模式
npm run test:ui

# 生成覆盖率报告
npm run test:coverage
```

**运行 E2E 测试：**

```bash
# 运行所有 E2E 测试
npm run test:e2e

# UI 模式
npm run test:e2e:ui

# 调试模式
npm run test:e2e:debug

# 生成报告
npm run test:e2e:report
```

**编写单元测试：**

```typescript
// tests/unit/codeService.test.ts
import { describe, it, expect, vi } from 'vitest';
import { executeCode } from '@/services/codeService';

describe('codeService', () => {
  it('should execute code successfully', async () => {
    // Mock fetch
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          output: 'Hello, World!\n',
          execution_time: 0.123,
        }),
      })
    ) as any;

    const result = await executeCode({
      code: 'print("Hello, World!")',
      language: 'python',
      timeout: 30,
    });

    expect(result.success).toBe(true);
    expect(result.output).toContain('Hello, World!');
  });

  it('should handle execution errors', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        statusText: 'Internal Server Error',
      })
    ) as any;

    await expect(
      executeCode({
        code: 'invalid code',
        language: 'python',
        timeout: 30,
      })
    ).rejects.toThrow('执行失败');
  });
});
```

**编写 E2E 测试：**

```typescript
// tests/e2e/code-execution.spec.ts
import { test, expect } from '@playwright/test';

test.describe('代码执行功能', () => {
  test('应该成功执行 Python 代码', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // 选择课程
    await page.click('text=Agent 是什么？');

    // 在编辑器中输入代码
    await page.locator('.monaco-editor').click();
    await page.keyboard.type('print("Hello from E2E test")');

    // 点击运行按钮
    await page.click('button:has-text("运行代码")');

    // 等待执行结果
    await page.waitForSelector('.output-panel');

    // 验证输出
    const output = await page.textContent('.output-panel');
    expect(output).toContain('Hello from E2E test');
  });

  test('应该显示语法错误', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('text=Agent 是什么？');

    await page.locator('.monaco-editor').click();
    await page.keyboard.type('print("unclosed string');

    await page.click('button:has-text("运行代码")');

    await page.waitForSelector('.error-message');
    const error = await page.textContent('.error-message');
    expect(error).toContain('SyntaxError');
  });
});
```

---

## 调试技巧

### 后端调试

**使用 VS Code 调试器：**

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

**使用 pdb 调试：**

```python
# 在代码中插入断点
import pdb; pdb.set_trace()

# 调试命令
# n - 下一行
# s - 进入函数
# c - 继续执行
# p variable - 打印变量
# l - 查看当前代码
# q - 退出调试
```

**查看日志：**

```bash
# 实时查看日志
tail -f backend/logs/app.log

# 搜索错误日志
grep "ERROR" backend/logs/app.log

# 查看结构化日志（JSON 格式）
cat backend/logs/app.log | jq '.'
```

### 前端调试

**使用 React Developer Tools：**

1. 安装 Chrome 扩展：[React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
2. 打开开发者工具 → Components 标签
3. 查看组件树和 Props/State

**使用 VS Code 调试器：**

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome against localhost",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/frontend/src",
      "sourceMaps": true
    }
  ]
}
```

**使用浏览器开发工具：**

```typescript
// 在代码中添加断点
debugger;

// 打印调试信息
console.log('变量值:', variable);
console.table(array);  // 以表格形式显示数组
console.time('操作');
// ... 代码 ...
console.timeEnd('操作');  // 显示耗时
```

---

## 常见问题

### 后端问题

#### Q: Docker 容器无法启动？

```bash
# 检查 Docker 服务状态
docker ps

# 查看 Docker 日志
docker logs <container_id>

# 清理未使用的容器和镜像
docker system prune -a
```

#### Q: 数据库连接失败？

```bash
# 检查数据库文件
ls -la backend/helloagents.db

# 重新初始化数据库
rm backend/helloagents.db
python3 backend/init_db.py
```

#### Q: AI 助手不工作？

```bash
# 检查环境变量
echo $DEEPSEEK_API_KEY

# 测试 API 连接
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

### 前端问题

#### Q: 前端无法连接后端？

1. 检查后端是否运行：`curl http://localhost:8000/health`
2. 检查 CORS 配置：`backend/app/main.py` 中的 `allow_origins`
3. 检查前端环境变量：`frontend/.env` 中的 `VITE_API_BASE_URL`

#### Q: Monaco Editor 不显示？

```bash
# 清理缓存
rm -rf frontend/node_modules
rm frontend/package-lock.json
npm install

# 重新启动开发服务器
npm run dev
```

#### Q: 构建失败？

```bash
# 检查 TypeScript 错误
npm run build

# 查看详细错误信息
npx tsc --noEmit
```

### 常用命令

```bash
# 后端
cd backend
python3 -m pytest                # 运行测试
python3 -m pytest --cov         # 测试覆盖率
ruff check .                     # Lint 检查
black .                          # 代码格式化
uvicorn app.main:app --reload   # 启动服务

# 前端
cd frontend
npm run dev                     # 开发服务器
npm run build                   # 生产构建
npm run preview                 # 预览构建结果
npm run test                    # 单元测试
npm run test:e2e               # E2E 测试
npm run lint                    # Lint 检查

# Docker
docker ps                       # 查看运行中的容器
docker images                   # 查看镜像
docker logs <container>         # 查看容器日志
docker exec -it <container> sh  # 进入容器

# Git
git status                      # 查看状态
git log --oneline --graph       # 查看提交历史
git diff                        # 查看变更
git stash                       # 暂存变更
git stash pop                   # 恢复暂存
```

---

## 下一步

- 查看 [API 文档](./API.md) 了解接口详情
- 查看 [架构文档](./ARCHITECTURE.md) 了解系统设计
- 查看 [贡献指南](../CONTRIBUTING.md) 了解贡献流程
- 加入 [GitHub Discussions](https://github.com/ai520510xyf-del/helloagents-platform/discussions) 参与讨论

---

**最后更新**: 2024-01-09 | **欢迎贡献！**
