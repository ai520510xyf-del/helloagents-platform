# QA 验证脚本说明

本目录包含用于 CI 修复验证的自动化脚本。

---

## 脚本列表

### 1. `verify_all.sh` - 一键验证脚本

**用途**: 执行所有验证测试，包括 CI 监控和冒烟测试。

**使用方法**:
```bash
# 基本使用（仅冒烟测试）
./scripts/verify_all.sh

# 包含完整测试
RUN_FULL_TESTS=1 ./scripts/verify_all.sh
```

**执行阶段**:
1. CI 工作流监控
2. 后端冒烟测试
3. 前端冒烟测试
4. 后端完整测试（可选）
5. 前端完整测试（可选）

---

### 2. `monitor_ci.sh` - CI 监控脚本

**用途**: 监控 GitHub Actions 工作流状态。

**使用方法**:
```bash
# 基本使用
./scripts/monitor_ci.sh

# 设置仓库信息
export GITHUB_REPO_OWNER="your-org"
export GITHUB_REPO_NAME="helloagents-platform"
export GITHUB_BRANCH="develop"
./scripts/monitor_ci.sh

# 持续监控（每分钟检查一次）
watch -n 60 './scripts/monitor_ci.sh'
```

**监控的工作流**:
- `ci.yml` - CI 测试套件
- `docker-build.yml` - Docker 构建
- `e2e-tests.yml` - E2E 测试

**输出信息**:
- 工作流运行状态
- 失败 jobs 列表
- 错误日志预览
- 总体通过率

---

## 后端脚本

### `backend/scripts/smoke_test.sh` - 后端冒烟测试

**用途**: 快速验证后端基本功能。

**使用方法**:
```bash
cd backend
./scripts/smoke_test.sh
```

**测试项**:
- 基本导入测试
- 环境变量检查
- 数据库模型导入
- API 路由导入
- 容器池导入
- 错误处理导入
- API 健康检查
- 容器池创建
- 关键依赖包

---

## 前端脚本

### `frontend/scripts/smoke_test.sh` - 前端冒烟测试

**用途**: 快速验证前端基本功能。

**使用方法**:
```bash
cd frontend
./scripts/smoke_test.sh

# 包含生产构建测试
RUN_BUILD_TEST=1 ./scripts/smoke_test.sh
```

**测试项**:
- 依赖包安装
- 关键依赖检查
- TypeScript 配置
- Vite 配置
- 测试框架配置
- 代码风格检查
- 错误处理测试
- TypeScript 类型检查
- 生产构建（可选）
- E2E 配置检查

---

## 快速开始

### 场景 1: 修复完成后验证

```bash
# 1. 执行一键验证
./scripts/verify_all.sh

# 2. 查看结果并填写报告
open reports/CI_FIX_VERIFICATION_REPORT.md
```

### 场景 2: 仅监控 CI

```bash
# 监控 CI 状态
./scripts/monitor_ci.sh

# 持续监控
watch -n 60 './scripts/monitor_ci.sh'
```

### 场景 3: 仅后端验证

```bash
cd backend
./scripts/smoke_test.sh
```

### 场景 4: 仅前端验证

```bash
cd frontend
./scripts/smoke_test.sh
```

### 场景 5: 完整测试（包含单元测试）

```bash
RUN_FULL_TESTS=1 ./scripts/verify_all.sh
```

---

## 环境要求

### CI 监控脚本

- GitHub CLI (`gh`) - [安装说明](https://cli.github.com/)
- jq - JSON 处理工具

```bash
# macOS
brew install gh jq

# 认证
gh auth login
```

### 后端脚本

- Python 3.9+
- pytest
- 虚拟环境已激活

```bash
cd backend
source venv/bin/activate  # 或 .venv/bin/activate
pip install -r requirements.txt
```

### 前端脚本

- Node.js 16+
- npm
- 依赖已安装

```bash
cd frontend
npm install
```

---

## 故障排查

### 问题 1: GitHub CLI 未认证

```bash
# 安装 GitHub CLI
brew install gh

# 认证
gh auth login
```

### 问题 2: 脚本无执行权限

```bash
# 添加执行权限
chmod +x scripts/*.sh
chmod +x backend/scripts/*.sh
chmod +x frontend/scripts/*.sh
```

### 问题 3: 后端导入失败

```bash
# 检查虚拟环境
cd backend
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题 4: 前端依赖缺失

```bash
# 清理并重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 输出示例

### 成功输出

```
=========================================
  CI 修复一键验证
=========================================

第 1 阶段: CI 工作流监控
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ CI 工作流监控 通过

第 2 阶段: 后端冒烟测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 后端冒烟测试 通过

第 3 阶段: 前端冒烟测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 前端冒烟测试 通过

=========================================
  验证结果汇总
=========================================

✅ SUCCESS

✅ 所有验证通过！
✅ 系统状态正常，可以继续开发或部署
```

### 失败输出

```
=========================================
  验证结果汇总
=========================================

❌ FAILURE

❌ 有 2 个阶段失败：
  - CI 工作流监控
  - 后端冒烟测试

请查看上述错误日志并修复问题
```

---

## 相关文档

- **验证指南**: `../QA_VERIFICATION_GUIDE.md`
- **验证报告模板**: `../reports/CI_FIX_VERIFICATION_REPORT.md`
- **CI 配置指南**: `../CI_CD_GUIDE.md`
- **测试文档**: `../backend/reports/TEST_SUMMARY.md`

---

**维护者**: QA Automation Engineer
**最后更新**: 2026-01-08
