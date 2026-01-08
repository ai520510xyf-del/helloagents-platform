# HelloAgents 贡献指南

感谢你考虑为 HelloAgents Platform 贡献代码！本文档将帮助你了解如何参与项目开发。

---

## 目录

1. [行为准则](#行为准则)
2. [如何贡献](#如何贡献)
3. [开发流程](#开发流程)
4. [代码规范](#代码规范)
5. [提交规范](#提交规范)
6. [Pull Request 流程](#pull-request-流程)
7. [测试要求](#测试要求)

---

## 行为准则

参与本项目即表示你同意遵守以下准则:

- 尊重所有贡献者
- 建设性地提供反馈
- 关注项目目标
- 对新人友好

---

## 如何贡献

### 报告 Bug

如果你发现 Bug，请[创建 Issue](https://github.com/helloagents/platform/issues/new) 并包含:

1. **Bug 描述**: 简洁描述问题
2. **重现步骤**: 详细的复现步骤
3. **期望行为**: 你期望的正确行为
4. **实际行为**: 实际发生的情况
5. **环境信息**:
   - OS (macOS/Windows/Linux)
   - Python 版本
   - Node.js 版本
   - Docker 版本
6. **截图**: 如果适用
7. **日志**: 相关错误日志

### 提出新功能

如果你有新功能建议:

1. 先检查是否已有相关 Issue
2. 创建 Feature Request Issue
3. 描述功能目标和使用场景
4. 讨论实现方案
5. 等待维护者反馈

### 贡献代码

1. Fork 本仓库
2. 创建功能分支
3. 实现功能并编写测试
4. 提交 Pull Request

---

## 开发流程

### 1. Fork 和克隆

```bash
# Fork 仓库 (在 GitHub 上点击 Fork 按钮)

# 克隆你的 Fork
git clone https://github.com/YOUR_USERNAME/helloagents-platform.git
cd helloagents-platform

# 添加上游仓库
git remote add upstream https://github.com/helloagents/platform.git

# 验证远程仓库
git remote -v
```

### 2. 创建功能分支

```bash
# 更新本地 develop 分支
git checkout develop
git pull upstream develop

# 创建功能分支 (使用描述性名称)
git checkout -b feature/my-feature

# 或修复 Bug
git checkout -b fix/bug-description
```

### 3. 开发

```bash
# 后端开发
cd backend
pip install -r requirements.txt
python3 run.py

# 前端开发
cd frontend
npm install
npm run dev

# 运行测试
cd backend && pytest
cd frontend && npm test
```

### 4. 提交修改

```bash
# 查看修改
git status

# 暂存修改
git add .

# 提交 (遵循提交规范)
git commit -m "feat: add new feature"

# 推送到你的 Fork
git push origin feature/my-feature
```

### 5. 创建 Pull Request

1. 访问你的 Fork 页面
2. 点击 "New Pull Request"
3. 选择 `base: develop` ← `compare: feature/my-feature`
4. 填写 PR 描述 (参考模板)
5. 提交 PR

---

## 代码规范

### Python (后端)

**代码风格**
- 遵循 PEP 8
- 使用 Black 格式化 (行长度 88)
- 使用类型提示 (Type Hints)

```python
# ✅ 推荐
def get_user(user_id: int) -> User | None:
    """获取用户信息

    Args:
        user_id: 用户 ID

    Returns:
        用户对象，如果不存在返回 None
    """
    return db.query(User).filter(User.id == user_id).first()

# ❌ 避免
def get_user(user_id):  # 缺少类型提示和文档字符串
    return db.query(User).filter(User.id == user_id).first()
```

**命名规范**
- 类名: PascalCase (`User`, `UserProgress`)
- 函数/变量: snake_case (`get_user`, `user_id`)
- 常量: UPPER_SNAKE_CASE (`API_VERSION`, `MAX_RETRIES`)
- 私有成员: 以下划线开头 (`_internal_method`)

### TypeScript (前端)

**代码风格**
- ESLint + Prettier
- React Hooks 规范
- 避免 any 类型

```typescript
// ✅ 推荐
interface User {
  id: number;
  username: string;
  email: string;
}

const fetchUser = async (userId: number): Promise<User> => {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
};

// ❌ 避免
const fetchUser = async (userId: any): Promise<any> => {  // 使用 any
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
};
```

**命名规范**
- 组件: PascalCase (`Button`, `LearnPage`)
- 文件: PascalCase for components (`Button.tsx`)
- Hooks: camelCase with "use" prefix (`useLesson`, `useChatMessages`)
- 常量: UPPER_SNAKE_CASE (`API_BASE_URL`)

---

## 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(backend): add chat API` |
| `fix` | Bug 修复 | `fix(frontend): fix button style` |
| `docs` | 文档更新 | `docs: update README` |
| `style` | 代码格式化 (不影响功能) | `style: format code with black` |
| `refactor` | 代码重构 | `refactor(backend): simplify error handling` |
| `perf` | 性能优化 | `perf(sandbox): optimize container pool` |
| `test` | 测试相关 | `test(backend): add chat API tests` |
| `chore` | 构建/工具相关 | `chore: update dependencies` |
| `ci` | CI 配置 | `ci: add codecov integration` |

### Scope (可选)

- `backend` - 后端相关
- `frontend` - 前端相关
- `sandbox` - 沙箱相关
- `database` - 数据库相关
- `ci` - CI/CD 相关
- `docs` - 文档相关

### 示例

```bash
# 简单提交
git commit -m "feat(backend): add user authentication"

# 详细提交
git commit -m "fix(frontend): fix memory leak in code editor

The code editor component was not properly cleaning up
event listeners, causing memory leaks.

- Add cleanup function in useEffect
- Remove event listeners on unmount
- Add tests for cleanup behavior

Closes #123"
```

---

## Pull Request 流程

### PR 描述模板

```markdown
## 变更描述

简要描述此 PR 的目的和内容。

## 变更类型

- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 文档更新 (docs)
- [ ] 代码重构 (refactor)
- [ ] 性能优化 (perf)
- [ ] 测试相关 (test)
- [ ] 其他 (chore, style, ci)

## 相关 Issue

Closes #123

## 测试

- [ ] 后端测试通过 (`pytest`)
- [ ] 前端测试通过 (`npm test`)
- [ ] 新增测试用例
- [ ] 手动测试通过

## 检查清单

- [ ] 代码遵循项目规范
- [ ] 已添加必要的文档
- [ ] 已添加必要的测试
- [ ] 所有测试通过
- [ ] CI 构建通过
- [ ] 已自我审查代码

## 截图 (如适用)

添加截图或 GIF 演示功能。

## 其他说明

其他需要审查者注意的内容。
```

### 审查流程

1. **提交 PR**: 填写完整的 PR 描述
2. **CI 检查**: 等待自动化测试通过
3. **代码审查**: 至少 1 人审查
4. **修改反馈**: 根据审查意见修改
5. **合并**: 审查通过后合并到 develop

### 审查标准

**功能正确性**
- [ ] 功能符合需求
- [ ] 边界情况已处理
- [ ] 错误处理完善

**代码质量**
- [ ] 代码可读性良好
- [ ] 变量命名清晰
- [ ] 无重复代码
- [ ] 遵循项目风格

**性能**
- [ ] 无明显性能问题
- [ ] 数据库查询优化
- [ ] 避免不必要的计算

**安全性**
- [ ] 输入验证完善
- [ ] 无安全漏洞
- [ ] 敏感信息已加密

**测试**
- [ ] 单元测试覆盖
- [ ] 测试用例充分
- [ ] 测试全部通过

---

## 测试要求

### 后端测试

**单元测试**
- 所有新功能必须有单元测试
- 测试覆盖率 >= 80%
- 测试命名清晰

```python
# tests/test_user_api.py
def test_create_user_success():
    """测试成功创建用户"""
    response = client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_create_user_duplicate():
    """测试创建重复用户"""
    # 首先创建用户
    client.post("/api/users", json={"username": "testuser"})

    # 尝试创建重复用户
    response = client.post("/api/users", json={"username": "testuser"})
    assert response.status_code == 400
```

### 前端测试

**组件测试**
- 所有新组件必须有测试
- 测试用户交互
- 测试边界情况

```typescript
// Button.spec.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('应该渲染按钮文本', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('应该在点击时调用 onClick', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

### 运行测试

```bash
# 后端测试
cd backend
pytest --cov=app --cov-report=term

# 前端测试
cd frontend
npm test

# 前端覆盖率
npm run test:coverage
```

---

## 常见问题

### Q: 我应该从哪个分支创建功能分支?
A: 始终从 `develop` 分支创建功能分支。

### Q: PR 应该合并到哪个分支?
A: 合并到 `develop` 分支。只有维护者会将 `develop` 合并到 `main`。

### Q: 我的 PR 需要多久才能被审查?
A: 我们努力在 24-48 小时内审查所有 PR。

### Q: 测试失败怎么办?
A: 检查 CI 日志，在本地修复问题，然后推送新的提交。

### Q: 如何更新我的功能分支?
```bash
# 更新本地 develop
git checkout develop
git pull upstream develop

# 合并到功能分支
git checkout feature/my-feature
git merge develop

# 或使用 rebase (推荐)
git rebase develop
```

### Q: 如何撤销提交?
```bash
# 撤销最后一次提交 (保留修改)
git reset --soft HEAD~1

# 撤销最后一次提交 (丢弃修改)
git reset --hard HEAD~1
```

---

## 获取帮助

- **Slack**: `#helloagents-dev`
- **GitHub Issues**: 技术问题
- **GitHub Discussions**: 一般讨论
- **Email**: team@helloagents.com

---

## 致谢

感谢你的贡献！每一个 PR、Issue 和反馈都让项目变得更好。

---

**Last Updated**: 2026-01-08
