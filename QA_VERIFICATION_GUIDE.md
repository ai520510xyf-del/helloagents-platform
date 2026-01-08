# QA 验证快速指南

**目的**: 在修复完成后快速验证 CI 和功能正常性

---

## 一、快速开始

### 1. 监控 CI 状态

```bash
# 监控 GitHub Actions 工作流
./scripts/monitor_ci.sh

# 设置环境变量（如果需要）
export GITHUB_REPO_OWNER="your-org"
export GITHUB_REPO_NAME="helloagents-platform"
export GITHUB_BRANCH="develop"
```

### 2. 执行后端冒烟测试

```bash
# 进入 backend 目录并执行
cd backend
./scripts/smoke_test.sh

# 或使用完整路径
/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/backend/scripts/smoke_test.sh
```

### 3. 执行前端冒烟测试

```bash
# 进入 frontend 目录并执行
cd frontend
./scripts/smoke_test.sh

# 启用构建测试（可选，较慢）
RUN_BUILD_TEST=1 ./scripts/smoke_test.sh
```

---

## 二、测试脚本说明

### CI 监控脚本 (`scripts/monitor_ci.sh`)

**功能**:
- 检查 GitHub Actions 工作流状态
- 显示失败 jobs 的错误日志
- 计算总体通过率

**输出示例**:
```
=========================================
  CI 监控脚本
=========================================

工作流: ci.yml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
运行 ID: 12345
状态: ✅ SUCCESS

工作流: docker-build.yml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
运行 ID: 12346
状态: ❌ FAILURE

失败的 Jobs:
  - Build Backend Image

=========================================
  总体统计
=========================================
总工作流数: 3
成功: 2
失败: 1
通过率: 66%
```

### 后端冒烟测试 (`backend/scripts/smoke_test.sh`)

**测试项**:
1. 基本导入测试
2. 环境变量检查
3. 数据库模型导入
4. API 路由导入
5. 容器池导入
6. 错误处理导入
7. API 健康检查测试
8. 容器池创建测试
9. 错误处理测试
10. 关键依赖包检查

**预期输出**:
```
=========================================
  后端冒烟测试
=========================================

[测试 1] 基本导入测试
✅ 通过

[测试 2] 环境变量检查
✅ 通过

...

=========================================
  测试结果汇总
=========================================
总测试数: 10
通过: 10
失败: 0
通过率: 100%

✅ 所有冒烟测试通过！
✅ 后端基本功能正常，可以继续进行完整测试
```

### 前端冒烟测试 (`frontend/scripts/smoke_test.sh`)

**测试项**:
1. 依赖包安装检查
2. 关键依赖包检查
3. TypeScript 配置检查
4. Vite 配置检查
5. 测试配置检查
6. 代码风格检查（ESLint）
7. 错误处理单元测试
8. TypeScript 类型检查
9. 生产构建测试（可选）
10. E2E 测试配置检查

**预期输出**:
```
=========================================
  前端冒烟测试
=========================================

[测试 1] 依赖包安装检查
✅ 通过

[测试 2] 关键依赖包检查
✅ 通过

...

=========================================
  测试结果汇总
=========================================
总测试数: 10
通过: 10
失败: 0
通过率: 100%

✅ 所有冒烟测试通过！
✅ 前端基本功能正常，可以继续进行完整测试
```

---

## 三、验证流程

### 第 1 步: 等待修复完成

监控 Slack 或团队沟通渠道，等待以下通知:
- Backend Lead: "Backend 修复完成"
- Frontend Lead: "Frontend 修复完成"

### 第 2 步: 立即执行 CI 监控

```bash
# 1. 监控 CI 状态
./scripts/monitor_ci.sh

# 2. 如果有失败，等待 5 分钟后重试
sleep 300
./scripts/monitor_ci.sh

# 3. 持续监控直到所有工作流通过
watch -n 60 './scripts/monitor_ci.sh'
```

### 第 3 步: 执行本地冒烟测试

```bash
# 1. 后端冒烟测试
cd backend
./scripts/smoke_test.sh
cd ..

# 2. 前端冒烟测试
cd frontend
./scripts/smoke_test.sh
cd ..
```

### 第 4 步: 填写验证报告

```bash
# 打开报告模板
open reports/CI_FIX_VERIFICATION_REPORT.md

# 或使用编辑器
code reports/CI_FIX_VERIFICATION_REPORT.md
```

**填写要点**:
1. 填写执行时间和测试人
2. 记录每个测试的状态（✅/❌）
3. 复制粘贴测试输出
4. 填写失败测试的错误日志
5. 记录修复措施
6. 总结评估和建议

### 第 5 步: 报告结果

通过 Slack 或团队沟通渠道报告:
- 总体状态（通过/失败）
- 关键指标（通过率）
- 遗留问题（如果有）
- 建议下一步行动

---

## 四、常见问题处理

### Q1: GitHub CLI 未认证

**症状**:
```
❌ GitHub CLI 未认证
请先运行: gh auth login
```

**解决方法**:
```bash
# 1. 安装 GitHub CLI（如果未安装）
brew install gh

# 2. 认证
gh auth login

# 3. 选择认证方式（推荐使用浏览器）
```

### Q2: 后端导入失败

**症状**:
```
[测试 1] 基本导入测试
❌ 失败
ImportError: No module named 'app.main'
```

**解决方法**:
```bash
# 1. 检查是否在正确的目录
pwd  # 应该在 backend/ 目录

# 2. 检查虚拟环境
source venv/bin/activate  # 或 .venv/bin/activate

# 3. 重新安装依赖
pip install -r requirements.txt

# 4. 重试
./scripts/smoke_test.sh
```

### Q3: 前端依赖问题

**症状**:
```
[测试 1] 依赖包安装检查
❌ 失败
node_modules does not exist
```

**解决方法**:
```bash
# 1. 安装依赖
npm install

# 2. 清理缓存（如果需要）
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# 3. 重试
./scripts/smoke_test.sh
```

### Q4: CI 工作流仍在运行

**症状**:
```
状态: ⏳ IN PROGRESS
```

**解决方法**:
```bash
# 1. 持续监控（每分钟检查一次）
watch -n 60 './scripts/monitor_ci.sh'

# 2. 或手动等待 5 分钟后重试
sleep 300
./scripts/monitor_ci.sh
```

---

## 五、验证清单

### Backend 验证清单

- [ ] 基本导入测试通过
- [ ] 环境变量配置正确
- [ ] 数据库模型导入成功
- [ ] API 路由导入成功
- [ ] 容器池导入成功
- [ ] 错误处理导入成功
- [ ] 单元测试通过率 ≥ 90%
- [ ] 冒烟测试全部通过

### Frontend 验证清单

- [ ] 依赖包安装成功
- [ ] 关键依赖可用
- [ ] TypeScript 配置正确
- [ ] Vite 配置正确
- [ ] 测试框架配置正确
- [ ] 单元测试通过率 ≥ 90%
- [ ] 生产构建成功
- [ ] 冒烟测试全部通过

### CI/CD 验证清单

- [ ] CI Tests 工作流通过
- [ ] Docker Build 工作流通过
- [ ] E2E Tests 工作流通过
- [ ] 所有 jobs 成功
- [ ] 无失败日志
- [ ] 总体通过率 = 100%

---

## 六、时间估算

| 阶段 | 预计时间 | 说明 |
|------|----------|------|
| 等待修复 | 40 分钟 | Backend + Frontend 修复时间 |
| CI 监控 | 5-10 分钟 | 检查工作流状态 |
| 后端冒烟测试 | 2-5 分钟 | 快速验证基本功能 |
| 前端冒烟测试 | 2-5 分钟 | 快速验证基本功能 |
| 填写报告 | 10-15 分钟 | 记录结果和建议 |
| **总计** | **约 60-75 分钟** | 包含等待时间 |

---

## 七、联系方式

**QA Automation Engineer**:
- Slack: #qa-automation
- Email: qa@example.com

**Backend Lead**:
- Slack: #backend

**Frontend Lead**:
- Slack: #frontend

---

## 八、相关文档

- CI 配置文档: `CI_CD_GUIDE.md`
- 测试文档: `backend/reports/TEST_SUMMARY.md`
- E2E 测试指南: `frontend/E2E_TESTING_GUIDE.md`
- 性能测试指南: `PERFORMANCE_TESTING_GUIDE.md`

---

**文档维护者**: QA Automation Engineer
**最后更新**: 2026-01-08
