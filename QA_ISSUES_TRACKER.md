# QA 问题跟踪清单

**创建时间**: 2026-01-08
**最后更新**: 2026-01-08 17:03
**负责团队**: HelloAgents Development Team

---

## 🔴 P0 - 阻塞性问题 (必须立即修复)

### Issue #1: Backend Tests - OpenAI API 密钥缺失

- **ID**: QA-001
- **优先级**: P0
- **状态**: 🔴 待修复
- **发现时间**: 2026-01-08 09:00
- **影响**: 阻塞所有后端测试
- **严重程度**: 阻塞 CI/CD

**详细描述**:
```
openai.OpenAIError: The api_key client option must be set either by passing
api_key to the client or by setting the OPENAI_API_KEY environment variable
```

**位置**:
- 文件: `backend/app/main.py`
- 行号: 80-85

**根本原因**:
- OpenAI 客户端在模块导入时立即初始化
- CI 环境未配置 OPENAI_API_KEY
- 导致 pytest 无法加载 conftest.py

**修复方案**:
```python
# 方案 A: 延迟初始化 (推荐)
def get_deepseek_client():
    global _deepseek_client
    if _deepseek_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            _deepseek_client = OpenAI(api_key=api_key, base_url="...")
    return _deepseek_client

# 方案 B: 添加默认值
api_key = os.getenv("OPENAI_API_KEY", "sk-dummy-for-testing")
```

**验证步骤**:
```bash
cd backend
python -c "from app.main import app; print('Success')"
pytest tests/ -v
```

**预计修复时间**: 15分钟
**负责人**: Backend Developer
**截止时间**: 2026-01-08 EOD

---

### Issue #2: Frontend - 依赖可执行文件未找到

- **ID**: QA-002
- **优先级**: P0
- **状态**: 🔴 待修复
- **发现时间**: 2026-01-08 09:00
- **影响**: 阻塞前端 Lint、Tests、Build
- **严重程度**: 阻塞 CI/CD

**详细描述**:
```bash
sh: 1: eslint: not found
sh: 1: vitest: not found
```

**位置**:
- 文件: `.github/workflows/ci.yml`
- 行号: 112, 145, 196

**根本原因**:
- `npm ci --prefer-offline` 可能导致某些包的 bin 链接未创建
- 依赖缓存不完整或损坏

**修复方案**:
```yaml
# 原代码:
- name: Install frontend dependencies
  working-directory: ./frontend
  run: npm ci --prefer-offline

# 修改为:
- name: Install frontend dependencies
  working-directory: ./frontend
  run: |
    npm ci
    npx eslint --version
    npx vitest --version
```

**验证步骤**:
```bash
cd frontend
rm -rf node_modules
npm ci
npx eslint --version
npx vitest --version
```

**预计修复时间**: 10分钟
**负责人**: DevOps / Frontend Developer
**截止时间**: 2026-01-08 EOD

---

## 🟡 P1 - 高优先级问题

### Issue #3: Frontend - Jest/Vitest API 不兼容

- **ID**: QA-003
- **优先级**: P1
- **状态**: 🟡 待修复
- **发现时间**: 2026-01-08 09:02
- **影响**: 12 个测试失败 (12%)
- **严重程度**: 影响测试质量

**详细描述**:
```
ReferenceError: jest is not defined
❯ src/utils/__tests__/errorHandler.test.ts:11:5
```

**位置**:
- 文件: `frontend/src/utils/__tests__/errorHandler.test.ts`
- 行号: 11, 以及其他使用 jest.* 的地方

**根本原因**:
- 测试文件使用 Jest API (`jest.clearAllTimers()`)
- 项目使用 Vitest 作为测试运行器
- Vitest 使用不同的 API (`vi.clearAllTimers()`)

**修复方案**:
```typescript
// 1. 添加导入
import { describe, it, expect, beforeEach, vi } from 'vitest';

// 2. 替换所有 jest.* 为 vi.*
jest.clearAllTimers() → vi.clearAllTimers()
jest.useFakeTimers() → vi.useFakeTimers()
jest.advanceTimersByTime() → vi.advanceTimersByTime()
```

**快速修复命令**:
```bash
cd frontend
sed -i '' 's/import { describe, it, expect, beforeEach }/import { describe, it, expect, beforeEach, vi }/' src/utils/__tests__/errorHandler.test.ts
sed -i '' 's/jest\./vi./g' src/utils/__tests__/errorHandler.test.ts
```

**验证步骤**:
```bash
npm test src/utils/__tests__/errorHandler.test.ts
# 预期: 13/13 tests passed
```

**预计修复时间**: 15分钟
**负责人**: Frontend Developer
**截止时间**: 2026-01-09 EOD

**受影响的测试**:
1. Toast 去重功能 - 应该对相同消息去重
2. Toast 去重功能 - 应该对不同类型的消息分别处理
3. Toast 去重功能 - 应该在去重窗口外创建新 Toast
4. 批处理功能 - 应该正确批处理多个相同错误
5. 批处理功能 - 应该处理大量相同错误
6. 性能测试 - 显示 Toast 应该很快 (< 10ms)
7. 性能测试 - 去重应该提升性能
8. 队列管理 - clear() 应该清空所有待处理 Toast
9. 队列管理 - getStats() 应该返回正确的统计信息
10. 边界情况 - 应该处理空消息
11. 边界情况 - 应该处理长消息
12. 边界情况 - 应该处理特殊字符

---

### Issue #4: 本地开发环境 - Docker 未安装

- **ID**: QA-004
- **优先级**: P1
- **状态**: 🟡 环境问题
- **发现时间**: 2026-01-08 09:01
- **影响**: 无法运行容器相关测试
- **严重程度**: 影响本地测试

**详细描述**:
```
docker.errors.DockerException: Error while fetching server API version:
('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))
```

**位置**:
- 本地开发环境

**根本原因**:
- 本地未安装 Docker Desktop
- 或 Docker 服务未启动

**修复方案**:
```bash
# macOS
brew install --cask docker
open -a Docker

# Linux
sudo apt-get install docker.io
sudo systemctl start docker
```

**临时方案** (如果无法安装 Docker):
- 在测试中添加 Docker 可用性检查
- 如不可用则跳过相关测试
```python
import pytest
import docker

@pytest.fixture(scope="session")
def docker_available():
    try:
        client = docker.from_env()
        client.ping()
        return True
    except:
        return False

@pytest.mark.skipif(not docker_available(), reason="Docker not available")
def test_container_pool():
    ...
```

**预计修复时间**: N/A (环境问题)
**负责人**: 开发者自行安装
**截止时间**: N/A

---

## 🟢 P2 - 中等优先级

### Issue #5: pytest-asyncio 配置警告

- **ID**: QA-005
- **优先级**: P2
- **状态**: 🟢 建议修复
- **发现时间**: 2026-01-08 09:01
- **影响**: 警告信息,未来可能导致问题
- **严重程度**: 低

**详细描述**:
```
PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
```

**修复方案**:
创建或编辑 `backend/pytest.ini`:
```ini
[pytest]
asyncio_default_fixture_loop_scope = function
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short
```

**预计修复时间**: 5分钟
**负责人**: Backend Developer
**截止时间**: 2026-01-10

---

### Issue #6: 性能测试未验证

- **ID**: QA-006
- **优先级**: P2
- **状态**: 🟢 待验证
- **发现时间**: 2026-01-08 09:01
- **影响**: 无法确认性能优化效果
- **严重程度**: 中

**详细描述**:
由于 Docker 环境问题,以下性能目标未验证:
- 快速健康检查: < 100ms (目标 4-10x 提升)
- 容器重置: < 300ms (目标 2x 提升)
- 容器获取: < 150ms
- Toast 去重: 减少重复创建 (目标 10x 提升)

**观察到的数据** (从 CI 日志):
- 容器创建时间: 198-206ms ✅ 符合预期
- 容器池初始化: 成功
- 后台线程: 正常启动

**修复方案**:
在有 Docker 环境中重新运行性能测试:
```bash
cd backend
pytest tests/test_performance.py -v -s
pytest tests/test_container_pool.py -v
pytest tests/test_performance_benchmarks.py --benchmark-only
```

**预计修复时间**: 30分钟 (在 Docker 环境中)
**负责人**: QA Engineer
**截止时间**: 2026-01-09

---

## 📊 问题统计

| 优先级 | 总数 | 待修复 | 进行中 | 已完成 |
|--------|------|--------|--------|--------|
| P0 | 2 | 2 | 0 | 0 |
| P1 | 2 | 2 | 0 | 0 |
| P2 | 2 | 2 | 0 | 0 |
| **总计** | **6** | **6** | **0** | **0** |

---

## ✅ 修复验证清单

### P0 问题验证 (必须全部通过)

- [ ] **QA-001**: Backend Tests 成功运行
  ```bash
  cd backend && pytest tests/ -v
  ```

- [ ] **QA-002**: Frontend Lint/Tests/Build 成功
  ```bash
  cd frontend
  npm run lint
  npm test
  npm run build
  ```

- [ ] **CI 全绿**: 所有 GitHub Actions 工作流通过
  - [ ] CI workflow ✅
  - [ ] E2E Tests ✅

### P1 问题验证

- [ ] **QA-003**: 所有前端测试通过 (101/101)
  ```bash
  cd frontend && npm test
  ```

- [ ] **QA-004**: 本地 Docker 测试可运行
  ```bash
  docker ps && cd backend && pytest tests/test_performance.py -v
  ```

### P2 问题验证

- [ ] **QA-005**: pytest 无警告信息
- [ ] **QA-006**: 性能基准达标

---

## 📈 进度跟踪

### 2026-01-08 17:03
- ✅ 完成 CI/CD 监控
- ✅ 识别所有阻塞问题
- ✅ 创建修复指南
- 📋 等待开发团队修复

### 待更新
- [ ] P0 问题修复完成
- [ ] CI 恢复正常
- [ ] 性能测试验证完成

---

## 📞 联系方式

**QA 负责人**: QA Automation Engineer (Claude)
**Slack 频道**: #qa, #development
**紧急联系**: 查看 URGENT_FIX_GUIDE.md

---

## 📚 相关文档

- [QA 测试报告](./QA_TEST_REPORT.md)
- [紧急修复指南](./URGENT_FIX_GUIDE.md)
- [执行摘要](./QA_EXECUTIVE_SUMMARY.md)
- [CI/CD 指南](./QUICK_START_CICD.md)

---

**文档版本**: 1.0
**最后更新**: 2026-01-08 17:03
**下次审查**: P0 问题修复后
