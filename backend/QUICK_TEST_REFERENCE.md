# 快速测试参考指南

## 🚀 快速开始

### 运行所有新增测试
```bash
cd backend
pytest tests/test_sandbox_enhanced.py tests/test_db_migration.py tests/test_db_monitoring.py tests/test_db_utils.py -v
```

### 查看覆盖率
```bash
pytest tests/test_sandbox_enhanced.py --cov=app.sandbox --cov-report=term
pytest tests/test_db_migration.py --cov=app.db_migration --cov-report=term
pytest tests/test_db_monitoring.py --cov=app.db_monitoring --cov-report=term
pytest tests/test_db_utils.py --cov=app.db_utils --cov-report=term
```

## 📊 当前覆盖率

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| sandbox.py | 100% | ✅ 优秀 |
| db_migration.py | 79% | ✅ 良好 |
| db_monitoring.py | 96% | ✅ 优秀 |
| db_utils.py | 81% | ✅ 良好 |
| **总体** | **89%** | ✅ **优秀** |

## 🧪 测试文件说明

### `test_sandbox_enhanced.py` (30 tests)
测试代码执行沙箱的所有功能：
- 初始化和配置
- 代码安全检查
- 容器池执行
- 临时容器执行
- 本地执行
- 异常处理
- 资源清理

**运行**: `pytest tests/test_sandbox_enhanced.py -v`

### `test_db_migration.py` (39 tests)
测试数据库迁移工具：
- 索引创建和删除
- 数据库分析和优化
- 索引状态检查
- 性能基准测试
- 命令行接口

**运行**: `pytest tests/test_db_migration.py -v`

### `test_db_monitoring.py` (44 tests)
测试性能监控工具：
- 查询统计收集
- 慢查询检测
- 性能追踪
- 表分析
- 优化建议

**运行**: `pytest tests/test_db_monitoring.py -v`

### `test_db_utils.py` (37 tests)
测试查询优化工具：
- 用户提交查询
- 聊天历史查询
- 学习进度查询
- 仪表盘数据
- 批量操作

**运行**: `pytest tests/test_db_utils.py -v`

## 🔍 调试技巧

### 运行单个测试
```bash
pytest tests/test_sandbox_enhanced.py::test_sandbox_init_with_pool -v
```

### 查看详细输出
```bash
pytest tests/test_sandbox_enhanced.py -v -s
```

### 只运行失败的测试
```bash
pytest tests/test_sandbox_enhanced.py --lf
```

### 生成 HTML 覆盖率报告
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

## 📝 常见问题

### Q: 测试运行很慢？
A: 使用 `-n auto` 并行运行测试（需要 pytest-xdist）：
```bash
pytest tests/ -n auto
```

### Q: 如何跳过特定测试？
A: 使用 `-k` 参数：
```bash
pytest tests/ -k "not slow"
```

### Q: 如何查看测试覆盖的具体行？
A: 使用 `--cov-report=term-missing`：
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## ✅ 测试清单

在提交代码前，确保：

- [ ] 所有测试通过
- [ ] 覆盖率 > 85%
- [ ] 无新的告警
- [ ] 代码格式正确

运行完整检查：
```bash
# 运行所有测试
pytest tests/ -v

# 检查覆盖率
pytest tests/ --cov=app --cov-report=term

# 检查代码质量（如果配置了 flake8）
flake8 app/ tests/
```

## 🎯 覆盖率目标

| 类型 | 最低要求 | 推荐 |
|------|---------|------|
| 总体覆盖率 | 75% | 85%+ |
| 核心模块 | 80% | 90%+ |
| 工具模块 | 70% | 80%+ |
| API 路由 | 75% | 85%+ |

## 📚 更多资源

- 详细报告: `TEST_COVERAGE_IMPROVEMENT_SUMMARY.md`
- pytest 文档: https://docs.pytest.org/
- coverage.py 文档: https://coverage.readthedocs.io/
