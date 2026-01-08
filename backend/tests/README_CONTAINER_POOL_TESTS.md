# 容器池测试文档

## 概述

本目录包含容器池 (`app/container_pool.py`) 的完整测试套件，包括单元测试和集成测试。

---

## 测试文件结构

```
tests/
├── test_container_pool.py              # 单元测试 (44 个用例)
├── test_container_pool_integration.py  # 集成测试 (20 个用例)
├── conftest.py                         # Fixtures (包含 Mock fixtures)
└── README_CONTAINER_POOL_TESTS.md      # 本文件
```

---

## 测试类型

### 1. 单元测试 (`test_container_pool.py`)
- **Mock 方式**: 使用 `unittest.mock` 模拟 Docker 客户端和容器
- **优点**: 快速、无需 Docker 环境、隔离测试
- **用例数**: 44 个

### 2. 集成测试 (`test_container_pool_integration.py`)
- **真实环境**: 需要 Docker 守护进程运行
- **优点**: 验证真实场景、端到端测试
- **用例数**: 20 个
- **标记**: `@pytest.mark.integration`

---

## 运行测试

### 快速开始

```bash
# 进入后端目录
cd backend

# 运行所有单元测试
pytest tests/test_container_pool.py -v

# 运行核心测试
pytest tests/test_container_pool.py -k "init or get_container or return" -v

# 运行集成测试 (需要 Docker)
pytest tests/test_container_pool_integration.py -m integration -v
```

### 详细命令

#### 运行特定测试
```bash
# 运行池初始化测试
pytest tests/test_container_pool.py::test_pool_initialization -v

# 运行健康检查相关测试
pytest tests/test_container_pool.py -k "health_check" -v

# 运行并发测试
pytest tests/test_container_pool.py -k "concurrent" -v
```

#### 排除特定测试
```bash
# 排除慢速测试
pytest tests/test_container_pool.py -k "not slow" -v

# 排除并发测试
pytest tests/test_container_pool.py -k "not concurrent" -v
```

#### 生成覆盖率报告
```bash
# HTML 报告
pytest tests/test_container_pool.py --cov=app.container_pool --cov-report=html

# 终端报告（显示未覆盖行）
pytest tests/test_container_pool.py --cov=app.container_pool --cov-report=term-missing
```

#### 运行性能测试
```bash
# 单元测试性能
pytest tests/test_container_pool.py -m slow -v

# 集成测试性能对比
pytest tests/test_container_pool_integration.py::test_pool_vs_temp_container_performance -v -s
```

---

## Mock Fixtures

### `mock_docker_client` (conftest.py)
Mock Docker 客户端，模拟 `docker.from_env()` 返回

**功能**:
- 创建容器: `containers.run()`
- 管理镜像: `images`
- 关闭客户端: `close()`

### `mock_docker_container` (conftest.py)
Mock 容器对象，模拟真实容器行为

**属性**:
- `id`: 容器 ID
- `short_id`: 短 ID
- `status`: 运行状态

**方法**:
- `exec_run(cmd)`: 模拟命令执行（智能返回结果）
- `reload()`: 刷新状态
- `stats()`: 资源统计
- `stop()` / `remove()`: 停止/删除

### `container_pool_factory` (test_container_pool.py)
容器池工厂 fixture，用于创建不同配置的池

**用法**:
```python
def test_example(container_pool_factory):
    pool = container_pool_factory(initial_size=3, max_size=10)
    # ... 测试代码
    pool.shutdown()
```

---

## 测试用例清单

### 单元测试 (44 个)

#### 1. 池初始化 (3 个)
- `test_pool_initialization`
- `test_pool_initialization_with_custom_config`
- `test_pool_has_unique_id`

#### 2. 获取容器 (6 个)
- `test_get_container_from_available_queue`
- `test_get_container_creates_new_when_queue_empty`
- `test_get_container_blocks_when_pool_exhausted`
- `test_get_container_timeout`
- `test_get_container_marks_in_use`

#### 3. 归还容器 (4 个)
- `test_return_container_success`
- `test_return_container_resets_state`
- `test_return_container_health_check`
- `test_return_container_reset_failure`

#### 4. 容器重置 (5 个)
- `test_container_reset_success`
- `test_container_reset_kills_processes`
- `test_container_reset_cleans_tmp`
- `test_container_reset_validates`
- `test_container_reset_checks_process_count`

#### 5. 健康检查 (8 个)
- `test_health_check_running_container`
- `test_health_check_stopped_container`
- `test_health_check_unresponsive_container`
- `test_health_check_high_memory`
- `test_health_check_too_many_processes`
- `test_health_check_readonly_filesystem`
- `test_health_check_writable_filesystem`

#### 6. 并发获取 (2 个)
- `test_concurrent_get_container`
- `test_concurrent_get_no_race_condition`

#### 7. 池耗尽 (2 个)
- `test_pool_exhaustion`
- `test_pool_exhaustion_blocking`

#### 8. 容器故障 (2 个)
- `test_container_failure_recovery`
- `test_destroy_and_replace_container`

#### 9. 空闲清理 (2 个)
- `test_idle_container_cleanup`
- `test_idle_cleanup_respects_min_size`

#### 10. 优雅关闭 (3 个)
- `test_graceful_shutdown`
- `test_shutdown_waits_for_in_use_containers`
- `test_shutdown_cleans_up_resources`

#### 11. 统计信息 (2 个)
- `test_get_stats`
- `test_stats_update_on_operations`

#### 12. 边界情况 (5 个)
- `test_zero_initial_size`
- `test_max_size_equals_initial_size`
- `test_get_container_with_zero_timeout`
- `test_return_nonexistent_container`
- `test_container_metadata_structure`

#### 13. 性能测试 (2 个) - @pytest.mark.slow
- `test_pool_performance_get_container`
- `test_pool_performance_concurrent`

---

### 集成测试 (20 个)

#### 1. 基础功能 (4 个)
- `test_execute_simple_code`
- `test_execute_error_code`
- `test_execute_timeout`
- `test_execute_with_imports`

#### 2. 并发执行 (3 个)
- `test_concurrent_executions`
- `test_concurrent_mixed_operations`
- `test_high_load` - @pytest.mark.slow

#### 3. 容器复用 (3 个)
- `test_container_reuse`
- `test_container_reset_effectiveness`
- `test_container_isolation`

#### 4. 资源限制 (3 个)
- `test_memory_limit_enforcement`
- `test_network_disabled`
- `test_filesystem_readonly`

#### 5. 健康检查 (2 个)
- `test_background_health_check` - @pytest.mark.slow
- `test_unhealthy_container_replacement`

#### 6. 性能基准 (2 个)
- `test_pool_vs_temp_container_performance` - @pytest.mark.slow
- `test_execution_latency`

#### 7. 压力测试 (2 个)
- `test_pool_under_sustained_load` - @pytest.mark.slow
- `test_pool_recovery_after_errors`

#### 8. 统计监控 (2 个)
- `test_pool_statistics`
- `test_container_metadata_accuracy`

---

## 测试标记

### `@pytest.mark.slow`
标记耗时较长的测试（> 30秒），可以选择性跳过：
```bash
# 跳过慢速测试
pytest tests/test_container_pool.py -k "not slow" -v

# 只运行慢速测试
pytest tests/test_container_pool.py -m slow -v
```

### `@pytest.mark.integration`
标记集成测试，需要 Docker 环境：
```bash
# 只运行集成测试
pytest tests/ -m integration -v

# 跳过集成测试
pytest tests/ -m "not integration" -v
```

---

## 调试技巧

### 1. 查看详细输出
```bash
pytest tests/test_container_pool.py::test_name -v -s
# -v: verbose (详细)
# -s: 显示 print 输出
```

### 2. 在失败时停止
```bash
pytest tests/test_container_pool.py -x
# -x: 第一个失败时停止
```

### 3. 运行最后失败的测试
```bash
pytest tests/test_container_pool.py --lf
# --lf: last-failed
```

### 4. 查看完整错误信息
```bash
pytest tests/test_container_pool.py --tb=long
# --tb=short: 短错误信息
# --tb=long: 长错误信息
# --tb=no: 不显示错误信息
```

### 5. 并行运行（需要 pytest-xdist）
```bash
pytest tests/test_container_pool.py -n 4
# -n 4: 使用 4 个进程并行运行
```

---

## 常见问题

### Q1: 测试运行很慢
**原因**: 包含了慢速测试和并发测试
**解决**: 
```bash
# 排除慢速测试
pytest tests/test_container_pool.py -k "not slow" -v
```

### Q2: 集成测试失败（Docker 相关）
**原因**: Docker 守护进程未运行
**解决**: 
```bash
# 检查 Docker 状态
docker ps

# 跳过集成测试
pytest tests/ -m "not integration" -v
```

### Q3: Mock 测试失败
**原因**: Mock 配置可能需要更新
**解决**: 检查 `conftest.py` 中的 Mock fixtures

### Q4: 并发测试偶尔失败
**原因**: 时间依赖的断言
**解决**: 增加时间容差或重试机制

---

## 性能基准

### 单元测试性能
- 平均每个测试: ~2-3 秒
- 快速测试: < 1 秒
- 慢速测试: 10-30 秒

### 集成测试性能
- 基础测试: 5-10 秒
- 并发测试: 10-20 秒
- 压力测试: 30-60 秒

---

## 贡献指南

### 添加新测试

1. **单元测试** (test_container_pool.py)
```python
def test_new_feature(container_pool_factory):
    """测试新功能描述"""
    pool = container_pool_factory(initial_size=2)
    
    # 测试代码
    assert pool.some_feature() == expected_value
    
    pool.shutdown()
```

2. **集成测试** (test_container_pool_integration.py)
```python
@pytest.mark.integration
def test_new_feature_integration(real_container_pool):
    """测试新功能集成场景"""
    # 使用真实 Docker 容器测试
    result = real_container_pool.some_feature()
    assert result is not None
```

### 测试命名规范
- 测试函数以 `test_` 开头
- 使用描述性名称说明测试内容
- 使用 snake_case 命名

### 断言指南
- 使用清晰的断言消息
- 一个测试验证一个行为
- 避免过度依赖时间的断言

---

## 相关文档

- [容器池实现](../app/container_pool.py)
- [详细测试报告](../reports/CONTAINER_POOL_TEST_REPORT.md)
- [测试总结](../reports/TEST_SUMMARY.md)

---

**维护者**: Backend Team
**最后更新**: 2026-01-08
