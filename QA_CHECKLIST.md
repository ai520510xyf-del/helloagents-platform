# QA 验证清单

## 准备阶段 - 完成 ✅

- [x] CI 监控脚本创建
- [x] 后端冒烟测试脚本创建
- [x] 前端冒烟测试脚本创建
- [x] 一键验证脚本创建
- [x] 验证报告模板创建
- [x] 详细文档创建
- [x] 脚本执行权限设置
- [x] 快速参考卡片创建

**状态**: 🟢 准备完成

---

## 等待阶段 - 进行中 ⏳

- [ ] Backend Lead 完成修复（预计 20-30 分钟）
  - [ ] API 密钥配置
  - [ ] 导入路径修复
  - [ ] 测试用例修复
  
- [ ] Frontend Lead 完成修复（预计 20-30 分钟）
  - [ ] package.json 修复
  - [ ] Vitest 配置修复
  - [ ] 测试设置修复

**状态**: 🟡 待命中

---

## 验证阶段 - 待执行 📋

### 步骤 1: CI 监控（5-10 分钟）

```bash
./scripts/monitor_ci.sh
```

- [ ] CI Tests 工作流通过
- [ ] Docker Build 工作流通过
- [ ] E2E Tests 工作流通过
- [ ] 总体通过率 = 100%

### 步骤 2: 后端冒烟测试（2-5 分钟）

```bash
cd backend && ./scripts/smoke_test.sh
```

- [ ] 基本导入测试通过
- [ ] 环境变量检查通过
- [ ] 数据库模型导入通过
- [ ] API 路由导入通过
- [ ] 容器池导入通过
- [ ] 错误处理导入通过
- [ ] API 健康检查通过
- [ ] 容器池创建测试通过
- [ ] 错误处理测试通过
- [ ] 依赖包检查通过

### 步骤 3: 前端冒烟测试（2-5 分钟）

```bash
cd frontend && ./scripts/smoke_test.sh
```

- [ ] 依赖包安装检查通过
- [ ] 关键依赖检查通过
- [ ] TypeScript 配置检查通过
- [ ] Vite 配置检查通过
- [ ] 测试配置检查通过
- [ ] 代码风格检查通过
- [ ] 错误处理测试通过
- [ ] TypeScript 类型检查通过
- [ ] E2E 配置检查通过

### 步骤 4: 填写报告（10-15 分钟）

```bash
open reports/CI_FIX_VERIFICATION_REPORT.md
```

- [ ] 填写执行概要
- [ ] 记录 Backend 修复验证结果
- [ ] 记录 Frontend 修复验证结果
- [ ] 记录 CI/CD 工作流状态
- [ ] 填写修复措施汇总
- [ ] 完成总体评估
- [ ] 填写遗留问题和建议

### 步骤 5: 通知团队（5 分钟）

- [ ] 在 Slack #qa-automation 发布结果
- [ ] 通知 Backend Lead
- [ ] 通知 Frontend Lead
- [ ] 提供报告链接

---

## 成功标准

### Backend ✓

- [ ] 导入测试 100% 通过
- [ ] 单元测试通过率 ≥ 90%
- [ ] 冒烟测试 100% 通过
- [ ] 无错误日志

### Frontend ✓

- [ ] 依赖安装成功
- [ ] 单元测试通过率 ≥ 90%
- [ ] 生产构建成功
- [ ] 冒烟测试 100% 通过

### CI/CD ✓

- [ ] 所有工作流通过
- [ ] 所有 jobs 成功
- [ ] 总体通过率 = 100%
- [ ] 无失败日志

---

## 快速命令

```bash
# 一键验证（推荐）
./scripts/verify_all.sh

# 或分步执行
./scripts/monitor_ci.sh
cd backend && ./scripts/smoke_test.sh
cd ../frontend && ./scripts/smoke_test.sh

# 查看报告模板
open reports/CI_FIX_VERIFICATION_REPORT.md

# 查看快速参考
cat QA_QUICK_REFERENCE.md
```

---

**当前状态**: 🟡 待命中
**预计响应**: 5 分钟内启动验证
**预计完成**: 15 分钟内完成初步报告

🚀 准备就绪，等待修复完成！
