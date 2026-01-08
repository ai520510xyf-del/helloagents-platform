# 🚨 紧急修复指南

**创建时间**: 2026-01-08
**优先级**: P0 - 阻塞性问题
**预计修复时间**: 1小时

---

## 问题概述

CI/CD 流水线完全失败,3个关键问题需要立即修复:

1. ❌ Backend Tests - API 密钥缺失
2. ❌ Frontend Lint/Tests - 依赖未找到
3. ❌ Frontend Tests - Jest/Vitest API 不兼容

---

## 修复步骤

### 步骤 1: 修复后端 API 密钥问题 (15分钟)

**问题**: `app/main.py` 在模块导入时初始化 OpenAI 客户端,但 CI 环境缺少 API 密钥

**方案 A: 延迟初始化 (推荐)**

编辑 `/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/backend/app/main.py`:

```python
# 找到这些行 (大约在 80-85 行):
# deepseek_client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
#     base_url="https://api.deepseek.com"
# )

# 替换为:
_deepseek_client = None

def get_deepseek_client():
    """获取 DeepSeek 客户端,如果未配置则返回 None"""
    global _deepseek_client
    if _deepseek_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            _deepseek_client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            logger.info("deepseek_client_initialized")
        else:
            logger.warning("openai_api_key_not_set", message="AI features will be disabled")
    return _deepseek_client

# 然后在所有使用 deepseek_client 的地方替换为 get_deepseek_client()
# 例如:
# client = get_deepseek_client()
# if client:
#     response = client.chat.completions.create(...)
```

**方案 B: 添加环境变量到 GitHub Secrets (临时方案)**

1. 访问: https://github.com/ai520510xyf-del/helloagents-platform/settings/secrets/actions
2. 点击 "New repository secret"
3. 添加:
   - Name: `OPENAI_API_KEY`
   - Value: `sk-test-dummy-key-for-ci` (测试用假密钥)

4. 编辑 `.github/workflows/ci.yml`,在 Backend Tests job 中添加:

```yaml
- name: Run backend tests with coverage
  working-directory: ./backend
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    pytest tests/ --cov=app --cov-report=xml --cov-report=term --cov-report=html -v
```

### 步骤 2: 修复前端依赖问题 (10分钟)

**问题**: `npm ci --prefer-offline` 可能导致某些依赖的 bin 链接未创建

编辑 `/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/.github/workflows/ci.yml`:

```yaml
# 找到所有的 "Install frontend dependencies" 步骤

# 原代码:
- name: Install frontend dependencies
  working-directory: ./frontend
  run: npm ci --prefer-offline

# 替换为:
- name: Install frontend dependencies
  working-directory: ./frontend
  run: |
    npm ci
    # 验证关键依赖
    npx eslint --version
    npx vitest --version
```

这样修改 3 处:
1. Frontend Lint job (约 110-112 行)
2. Frontend Tests job (约 143-145 行)
3. Frontend Build job (约 194-196 行)

### 步骤 3: 修复前端测试 API 不兼容 (15分钟)

**问题**: 测试文件使用了 Jest API 但项目使用 Vitest

编辑 `/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/frontend/src/utils/__tests__/errorHandler.test.ts`:

```typescript
// 第 1-2 行,修改 import
// 原代码:
// import { describe, it, expect, beforeEach } from 'vitest';

// 修改为:
import { describe, it, expect, beforeEach, vi } from 'vitest';

// 第 11 行及其他所有使用 jest 的地方
// 原代码:
// jest.clearAllTimers();

// 修改为:
vi.clearAllTimers();

// 全局搜索替换所有 jest.* 调用
```

**快速批量修复** (使用命令行):

```bash
cd /Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/frontend

# 备份文件
cp src/utils/__tests__/errorHandler.test.ts src/utils/__tests__/errorHandler.test.ts.bak

# 添加 vi 导入
sed -i '' 's/import { describe, it, expect, beforeEach }/import { describe, it, expect, beforeEach, vi }/' src/utils/__tests__/errorHandler.test.ts

# 替换所有 jest 调用为 vi
sed -i '' 's/jest\./vi./g' src/utils/__tests__/errorHandler.test.ts

# 验证修改
git diff src/utils/__tests__/errorHandler.test.ts
```

### 步骤 4: 添加 pytest-asyncio 配置 (5分钟)

**问题**: pytest-asyncio 警告未来版本行为变化

创建或编辑 `/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/backend/pytest.ini`:

```ini
[pytest]
asyncio_default_fixture_loop_scope = function
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
markers =
    asyncio: mark test as async
    slow: mark test as slow
```

---

## 验证修复

### 本地验证 (推荐)

```bash
# 1. 前端测试
cd frontend
npm test
# 预期: 101 tests passed

# 2. 后端测试 (需要 Docker)
cd backend
source venv/bin/activate
export OPENAI_API_KEY="sk-test-dummy"
pytest tests/ -v
# 如果没有 Docker,至少验证导入不报错:
python -c "from app.main import app; print('✅ Import successful')"
```

### CI 验证

```bash
# 提交修复
git add .
git commit -m "fix(ci): 修复 CI 测试失败的关键问题

- fix: 延迟初始化 OpenAI 客户端以避免模块导入时缺少 API 密钥
- fix: 移除 npm ci 的 --prefer-offline 选项确保依赖完整安装
- fix: 将 errorHandler 测试中的 jest API 替换为 vitest API
- fix: 添加 pytest-asyncio 配置消除警告

Closes #XX"

git push origin develop
```

然后访问: https://github.com/ai520510xyf-del/helloagents-platform/actions

预期结果:
- ✅ Backend Tests 通过
- ✅ Frontend Lint 通过
- ✅ Frontend Tests 通过
- ✅ Frontend Build 成功

---

## 快速命令汇总

一次性执行所有修复的命令:

```bash
cd /Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform

# 1. 备份关键文件
cp backend/app/main.py backend/app/main.py.bak
cp frontend/src/utils/__tests__/errorHandler.test.ts frontend/src/utils/__tests__/errorHandler.test.ts.bak
cp .github/workflows/ci.yml .github/workflows/ci.yml.bak

# 2. 修复前端测试
cd frontend
sed -i '' 's/import { describe, it, expect, beforeEach }/import { describe, it, expect, beforeEach, vi }/' src/utils/__tests__/errorHandler.test.ts
sed -i '' 's/jest\./vi./g' src/utils/__tests__/errorHandler.test.ts

# 3. 修复 CI 配置
cd ..
sed -i '' 's/npm ci --prefer-offline/npm ci/' .github/workflows/ci.yml

# 4. 添加 pytest 配置
cat > backend/pytest.ini << 'EOF'
[pytest]
asyncio_default_fixture_loop_scope = function
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short
markers =
    asyncio: mark test as async
    slow: mark test as slow
EOF

# 5. 验证前端测试
cd frontend
npm test

# 6. 查看修改
cd ..
git status
git diff

# 7. 提交并推送
git add .
git commit -m "fix(ci): 修复 CI 测试失败的关键问题"
git push origin develop
```

**注意**: 步骤 1 的后端修复需要手动编辑代码,因为涉及逻辑改动。

---

## 预期结果

修复后:
- ✅ CI 通过率: 0% → 100%
- ✅ 前端测试通过率: 88% → 100%
- ✅ 后端测试: 可以运行 (虽然部分需要 Docker)
- ✅ 构建成功: 前端可正常构建

---

## 如果修复失败

### 后端测试仍失败

**可能原因**: 其他模块也在导入时初始化 AI 客户端

**排查**:
```bash
cd backend
grep -r "OpenAI(" app/
grep -r "Anthropic(" app/
```

找到所有初始化位置并应用相同的延迟初始化模式。

### 前端测试仍失败

**可能原因**: sed 替换不完整或有语法错误

**手动修复**:
1. 打开 `frontend/src/utils/__tests__/errorHandler.test.ts`
2. 搜索所有 `jest.` 并替换为 `vi.`
3. 确保导入了 `vi`: `import { ..., vi } from 'vitest'`

### CI 仍报依赖未找到

**可能原因**: npm cache 问题

**临时方案**:
在 CI 配置中添加清理步骤:
```yaml
- name: Install frontend dependencies
  working-directory: ./frontend
  run: |
    rm -rf node_modules package-lock.json
    npm install
```

---

## 联系支持

如果按照此指南修复后问题仍存在:

1. 查看 GitHub Actions 日志获取详细错误
2. 检查 `/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/QA_TEST_REPORT.md` 获取完整分析
3. 参考相关文档:
   - [CI/CD 快速指南](./QUICK_START_CICD.md)
   - [性能测试指南](./PERFORMANCE_TESTING_GUIDE.md)

---

**最后更新**: 2026-01-08 17:03
**版本**: 1.0
**创建者**: QA Automation Engineer (Claude)
