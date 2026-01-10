# 贡献指南

感谢你对 HelloAgents Platform 的关注！我们欢迎所有形式的贡献，包括但不限于代码、文档、课程内容、bug 报告和功能建议。

---

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
  - [报告 Bug](#报告-bug)
  - [提出功能建议](#提出功能建议)
  - [贡献代码](#贡献代码)
  - [贡献课程内容](#贡献课程内容)
  - [改进文档](#改进文档)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [测试要求](#测试要求)
- [提交流程](#提交流程)
- [Pull Request 指南](#pull-request-指南)
- [课程编写指南](#课程编写指南)
- [社区与沟通](#社区与沟通)

---

## 行为准则

### 我们的承诺

为了营造开放和友好的环境，我们作为贡献者和维护者承诺：让参与我们项目和社区的每个人都免受骚扰，无论年龄、体型、残疾、种族、性别认同和表达、经验水平、国籍、外貌、种族、宗教或性取向如何。

### 我们的标准

**正面行为**:
- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

**不可接受的行为**:
- 使用性化的语言或图像
- 恶意评论、侮辱性/贬损性言论、人身或政治攻击
- 公开或私下骚扰
- 未经明确许可发布他人的私人信息
- 其他在职业环境中可能被认为不当的行为

---

## 如何贡献

### 报告 Bug

发现 bug？请帮助我们改进！

**提交 Bug 报告前**:
1. 检查 [Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues) 确认是否已被报告
2. 尝试在最新版本中复现问题
3. 准备详细的复现步骤

**Bug 报告应包含**:
- 清晰的标题和描述
- 复现步骤
- 预期行为 vs 实际行为
- 截图或日志（如适用）
- 环境信息（操作系统、浏览器、Python/Node.js 版本）

**示例**:

```markdown
### Bug 描述
代码执行超时但没有返回错误信息

### 复现步骤
1. 访问课程 4.1
2. 输入以下代码：`import time; time.sleep(100)`
3. 点击"运行代码"
4. 等待 30 秒

### 预期行为
应该返回超时错误："执行超时（>30秒）"

### 实际行为
页面卡住，没有任何提示

### 环境信息
- 操作系统: macOS 14.2
- 浏览器: Chrome 120
- 后端版本: v1.0.0
```

---

### 提出功能建议

有好的想法？我们很乐意听取！

**功能建议应包含**:
- 清晰的标题
- 详细描述：解决什么问题？如何使用？
- 用例场景
- 可能的实现方案（可选）
- UI/UX 设计草图（可选）

**示例**:

```markdown
### 功能标题
支持 JavaScript 代码执行

### 问题描述
当前平台仅支持 Python，但许多开发者也想学习 JavaScript Agent 开发。

### 解决方案
添加 JavaScript 运行时支持，允许用户选择语言（Python / JavaScript）。

### 用例
1. 用户在课程页面选择 "JavaScript"
2. 编辑器切换到 JavaScript 语法高亮
3. 代码在 Node.js 容器中执行

### 实现建议
- 使用 `node:18-alpine` Docker 镜像
- 扩展沙箱模块支持多语言
- 添加语言选择下拉菜单
```

---

### 贡献代码

#### 前置要求

- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 最新版本
- **Git**: 基本操作熟悉

#### 贡献流程

1. **Fork 仓库**
   ```bash
   # 在 GitHub 上点击 Fork 按钮
   # 克隆你的 fork
   git clone https://github.com/YOUR_USERNAME/helloagents-platform.git
   cd helloagents-platform
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/bug-description
   ```

3. **设置开发环境**（见下方详细步骤）

4. **编写代码**
   - 遵循代码规范
   - 添加必要的测试
   - 更新相关文档

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add JavaScript execution support"
   ```

6. **推送到你的 fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**（见 PR 指南）

---

### 贡献课程内容

课程是平台的核心！我们欢迎高质量的课程贡献。

**课程贡献流程**:
1. 阅读[课程编写指南](#课程编写指南)
2. 在 `backend/docs/` 下创建新课程
3. 更新 `_sidebar.md` 目录
4. 提交 PR

**课程要求**:
- Markdown 格式
- 清晰的结构（概念→示例→练习）
- 包含代码模板和测试用例
- 中英文双语（可选）

---

### 改进文档

文档改进永远受欢迎！

**文档类型**:
- **API 文档**: `API.md`
- **架构文档**: `ARCHITECTURE.md`
- **用户指南**: `USER_GUIDE.md`
- **FAQ**: `FAQ.md`
- **部署文档**: `CLOUDFLARE_DEPLOY.md`

**改进包括**:
- 修正错别字
- 补充缺失内容
- 改进示例代码
- 添加图表和截图
- 翻译文档

---

## 开发环境设置

### 后端设置

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加必要的配置
# DEEPSEEK_API_KEY=your_api_key_here

# 初始化数据库
python3 init_db.py

# 运行开发服务器
python3 run.py
```

后端将在 `http://localhost:8000` 运行

**验证安装**:
```bash
curl http://localhost:8000/health
# 应返回: {"status":"healthy","timestamp":"..."}
```

---

### 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 运行

**验证安装**:
- 打开浏览器访问 `http://localhost:5173`
- 应该看到课程列表页面

---

### Docker 设置

代码沙箱需要 Docker 支持。

```bash
# 检查 Docker 是否运行
docker ps

# 拉取 Python 镜像（提前下载，加快启动）
docker pull python:3.11-slim

# 测试容器创建
docker run --rm python:3.11-slim python --version
```

---

## 代码规范

### Python 代码规范

**遵循 PEP 8**:
```bash
# 安装 linter
pip install flake8 black isort

# 格式化代码
black backend/app/
isort backend/app/

# 检查代码质量
flake8 backend/app/
```

**命名规范**:
- 模块/包: `lowercase_with_underscores`
- 类名: `CapitalizedWords`
- 函数/变量: `lowercase_with_underscores`
- 常量: `UPPERCASE_WITH_UNDERSCORES`

**文档字符串**:
```python
def execute_code(code: str, timeout: int = 30) -> Tuple[bool, str, float]:
    """
    在沙箱中执行代码

    Args:
        code: 要执行的代码
        timeout: 超时时间（秒）

    Returns:
        (成功标志, 输出/错误信息, 执行时间)

    Raises:
        ValidationError: 代码安全检查失败
        SandboxExecutionError: 沙箱执行错误
    """
```

---

### TypeScript/React 代码规范

**使用 ESLint + Prettier**:
```bash
# 格式化代码
npm run format

# 检查代码质量
npm run lint
```

**命名规范**:
- 组件: `PascalCase`
- 函数/变量: `camelCase`
- 常量: `UPPER_SNAKE_CASE`
- 类型/接口: `PascalCase`

**组件规范**:
```typescript
import { FC } from 'react';

interface LessonViewProps {
  lessonId: string;
  onComplete: () => void;
}

export const LessonView: FC<LessonViewProps> = ({ lessonId, onComplete }) => {
  // 组件逻辑
  return (
    <div className="lesson-view">
      {/* JSX */}
    </div>
  );
};
```

---

### Git Commit 规范

**使用 Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链配置

**示例**:
```bash
feat(sandbox): add JavaScript execution support

- Add Node.js container support
- Extend sandbox module for multi-language
- Update API to accept language parameter

Closes #123
```

---

## 测试要求

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_sandbox.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

**测试要求**:
- 新功能必须有单元测试
- 核心模块测试覆盖率 > 80%
- API 端点必须有集成测试

**示例测试**:
```python
def test_code_execution_success():
    """测试代码执行成功"""
    code = "print('Hello, World!')"
    success, output, execution_time = sandbox.execute_python(code)

    assert success is True
    assert "Hello, World!" in output
    assert execution_time < 5.0  # 应该在 5 秒内完成
```

---

### 前端测试

```bash
cd frontend

# 运行单元测试
npm test

# 运行 E2E 测试
npm run test:e2e
```

**测试要求**:
- UI 组件需要有快照测试
- 核心功能需要有 E2E 测试

---

## 提交流程

### 1. 代码审查清单

在提交 PR 前，请确保：

**功能性**:
- [ ] 代码正常工作，没有明显 bug
- [ ] 所有测试通过
- [ ] 边界情况已处理
- [ ] 错误处理完善

**代码质量**:
- [ ] 遵循代码规范
- [ ] 没有不必要的注释代码
- [ ] 变量命名清晰
- [ ] 函数职责单一
- [ ] 没有硬编码的魔法值

**测试**:
- [ ] 添加了相关测试
- [ ] 测试覆盖率 > 80%
- [ ] 测试全部通过

**文档**:
- [ ] 更新了相关文档
- [ ] 添加了必要的注释
- [ ] 更新了 API 文档（如适用）
- [ ] 更新了 CHANGELOG（如适用）

**性能**:
- [ ] 没有性能退化
- [ ] 资源使用合理
- [ ] 没有内存泄漏

---

### 2. 提交代码

```bash
# 确保代码格式化
black backend/app/
npm run format  # 前端

# 运行测试
pytest
npm test

# 提交
git add .
git commit -m "feat(sandbox): add JavaScript execution support"

# 推送
git push origin feature/javascript-support
```

---

## Pull Request 指南

### PR 标题

使用清晰、描述性的标题，遵循 Conventional Commits：

```
feat(sandbox): add JavaScript execution support
fix(api): resolve CORS issue with Cloudflare Pages
docs(readme): update installation instructions
```

---

### PR 描述模板

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 代码重构
- [ ] 其他

## 变更描述
简要描述这个 PR 做了什么

## 相关 Issue
Closes #123

## 变更详情
- 添加了 JavaScript 执行支持
- 扩展了沙箱模块
- 更新了 API 文档

## 测试
- [x] 单元测试通过
- [x] 集成测试通过
- [x] 手动测试通过

## 截图（如适用）
![screenshot](url)

## 检查清单
- [x] 代码遵循项目规范
- [x] 添加了必要的测试
- [x] 更新了相关文档
- [x] 所有测试通过
- [x] 没有引入新的警告
```

---

### PR 审查流程

1. **自动检查**:
   - CI 测试通过
   - 代码覆盖率满足要求
   - Lint 检查通过

2. **人工审查**:
   - 至少 1 位维护者审查
   - 代码质量符合标准
   - 没有明显问题

3. **反馈与修改**:
   - 根据审查意见修改
   - 重新推送更新
   - 标记为 "Ready for review"

4. **合并**:
   - 审查通过后合并到 `main` 分支
   - 自动部署到生产环境

---

## 课程编写指南

### 课程结构

```markdown
# 课程标题

**学习目标**: 明确学习目标（1-3 条）

---

## 1. 概念讲解

详细讲解核心概念，使用简洁的语言和图表。

## 2. 代码示例

提供清晰的代码示例，带有注释。

\`\`\`python
class ReActAgent:
    def __init__(self, llm_client, tool_executor):
        """
        初始化 ReAct Agent

        Args:
            llm_client: LLM 客户端
            tool_executor: 工具执行器
        """
        self.llm_client = llm_client
        self.tool_executor = tool_executor
\`\`\`

## 3. 动手练习

引导学习者实现功能。

**任务**: 实现 ReActAgent 的 run() 方法

**提示**:
- 使用 for 循环控制最大步数
- 记录每一步的 Thought-Action-Observation

## 4. 测试验证

提供测试代码或预期输出。

## 5. 总结

总结关键要点（3-5 条）。

---

**下一步**: 链接到下一课程
```

---

### 课程命名规范

```
backend/docs/
├── chapter{N}/
│   ├── 第{N}章 {标题}.md           # 中文版本
│   ├── Chapter{N}-{Title}.md      # 英文版本
│   ├── {N}.{M}-{Lesson-Name}.md   # 子课程
│   └── templates/                  # 代码模板
│       └── {N}.{M}-template.py
```

**示例**:
```
backend/docs/
├── chapter4/
│   ├── 第四章 智能体经典范式构建.md
│   ├── Chapter4-Building-Classic-Agent-Paradigms.md
│   ├── 4.1-ReAct-Agent.md
│   ├── 4.2-Plan-and-Solve-Agent.md
│   └── templates/
│       ├── 4.1-react-template.py
│       └── 4.2-plan-and-solve-template.py
```

---

### 课程质量标准

**内容**:
- [ ] 概念清晰，易于理解
- [ ] 示例代码可运行
- [ ] 练习难度适中
- [ ] 包含测试验证

**格式**:
- [ ] Markdown 格式正确
- [ ] 代码块指定语言
- [ ] 无拼写错误
- [ ] 排版美观

**教学**:
- [ ] 循序渐进
- [ ] 理论与实践结合
- [ ] 鼓励动手实践
- [ ] 提供充分提示

---

## 社区与沟通

### 沟通渠道

- **GitHub Issues**: 报告 bug、功能建议
- **GitHub Discussions**: 技术讨论、问答
- **Pull Requests**: 代码审查、反馈

### 响应时间

- **Bug 报告**: 通常在 2-3 个工作日内响应
- **功能建议**: 通常在 1 周内评估
- **Pull Request**: 通常在 3-5 个工作日内审查

### 获取帮助

遇到问题？
1. 查看 [FAQ.md](./FAQ.md)
2. 搜索 [Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues)
3. 查看 [API 文档](./API.md)
4. 查看 [架构文档](./ARCHITECTURE.md)
5. 在 Discussions 提问

---

## 感谢贡献者

感谢所有为 HelloAgents Platform 做出贡献的开发者！

**贡献者名单**: [CONTRIBUTORS.md](./CONTRIBUTORS.md)（计划中）

---

## 许可证

通过贡献代码，你同意你的贡献将在 [MIT License](./LICENSE) 下发布。

---

**最后更新**: 2026-01-09
**文档版本**: v1.0.0

有任何问题或建议？欢迎在 [GitHub Issues](https://github.com/ai520510xyf-del/helloagents-platform/issues) 提出！
