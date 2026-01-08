# QA 验证快速参考卡片

**状态**: 🟢 准备就绪
**用途**: 修复完成后快速执行验证

---

## 一键验证（推荐）

```bash
# 在项目根目录执行
./scripts/verify_all.sh
```

**预计时间**: 10-15 分钟
**包含**: CI 监控 + 后端冒烟测试 + 前端冒烟测试

---

## 分步执行

### 1. 监控 CI

```bash
./scripts/monitor_ci.sh
```

或持续监控（每分钟检查）：
```bash
watch -n 60 './scripts/monitor_ci.sh'
```

### 2. 后端冒烟测试

```bash
cd backend
./scripts/smoke_test.sh
```

### 3. 前端冒烟测试

```bash
cd frontend
./scripts/smoke_test.sh
```

---

## 完整测试模式

```bash
# 包含单元测试（较慢，20-30分钟）
RUN_FULL_TESTS=1 ./scripts/verify_all.sh
```

---

## 填写报告

```bash
# 打开报告模板
open reports/CI_FIX_VERIFICATION_REPORT.md
```

---

## 环境检查

```bash
# 检查必需工具
gh --version  # GitHub CLI
jq --version  # JSON 处理
python --version  # Python
node --version  # Node.js

# GitHub 认证
gh auth status
```

---

## 故障排查

### GitHub CLI 未认证

```bash
brew install gh
gh auth login
```

### 后端导入失败

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 前端依赖缺失

```bash
cd frontend
npm install
```

---

## 成功标准

- ✅ CI 工作流全部通过
- ✅ 后端冒烟测试通过率 100%
- ✅ 前端冒烟测试通过率 100%
- ✅ 无错误日志

---

## 通知团队

**Slack 频道**: #qa-automation

**消息模板**:
```
✅ CI 修复验证完成

Backend: [通过/失败] (通过率: X%)
Frontend: [通过/失败] (通过率: X%)
CI/CD: [通过/失败] (通过率: X%)

详细报告: reports/CI_FIX_VERIFICATION_REPORT.md
```

---

## 详细文档

- **完整指南**: `QA_VERIFICATION_GUIDE.md`
- **脚本说明**: `scripts/README.md`
- **待命状态**: `QA_STANDBY_STATUS.md`
- **准备报告**: `QA_PREPARATION_COMPLETE.md`

---

**保存此卡片**: 修复完成后立即使用！
