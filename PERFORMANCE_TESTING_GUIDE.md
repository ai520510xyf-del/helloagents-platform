# 性能测试指南

## 概述

本指南介绍如何运行性能测试,验证优化效果。

---

## 后端性能测试

### 测试文件位置
```
backend/tests/test_performance.py
```

### 测试覆盖
- ✅ 快速健康检查性能 (目标: < 100ms)
- ✅ 深度健康检查性能 (目标: < 600ms)
- ✅ 容器重置性能 (目标: < 300ms)
- ✅ 容器获取性能 (目标: < 150ms)
- ✅ 容器归还性能 (目标: < 400ms)
- ✅ 并发容器操作性能

### 运行测试

#### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-cov
```

#### 2. 运行完整性能测试
```bash
# 运行所有性能测试 (详细输出)
pytest tests/test_performance.py -v -s

# 运行特定测试
pytest tests/test_performance.py::TestContainerPoolPerformance::test_quick_health_check_performance -v -s
```

#### 3. 运行带覆盖率的测试
```bash
pytest tests/test_performance.py --cov=app.container_pool --cov-report=html
```

### 性能基准

| 测试项 | 目标 | 优化前 |
|--------|------|--------|
| 快速健康检查 | < 100ms | 200-500ms |
| 深度健康检查 | < 600ms | 200-500ms |
| 容器重置 | < 300ms | 300-500ms |
| 容器获取 | < 150ms | - |
| 容器归还 | < 400ms | - |

### 示例输出
```
backend/tests/test_performance.py::TestContainerPoolPerformance::test_quick_health_check_performance
快速健康检查平均耗时: 45.32ms
PASSED

backend/tests/test_performance.py::TestContainerPoolPerformance::test_container_reset_performance
容器重置平均耗时: 185.67ms
PASSED
```

---

## 前端性能测试

### 测试文件位置
```
frontend/src/utils/__tests__/errorHandler.test.ts
```

### 测试覆盖
- ✅ Toast 去重功能
- ✅ Toast 批处理功能
- ✅ Toast 显示性能 (目标: < 10ms/次)
- ✅ 队列管理
- ✅ 边界情况处理

### 运行测试

#### 1. 安装依赖
```bash
cd frontend
npm install
```

#### 2. 运行性能测试
```bash
# 运行所有测试
npm test

# 运行特定测试文件
npm test errorHandler.test.ts

# 运行性能基准测试
npm test errorHandler.test.ts -- --verbose
```

#### 3. 运行带覆盖率的测试
```bash
npm test -- --coverage
```

### 性能基准

| 测试项 | 目标 | 说明 |
|--------|------|------|
| 单次 Toast | < 1ms | 显示单个 Toast |
| 10 个相同 Toast | < 50ms | 去重批处理 |
| 100 个相同 Toast | < 100ms | 去重批处理 |
| 1000 个相同 Toast | < 500ms | 去重批处理 |

### 示例输出
```
 PASS  src/utils/__tests__/errorHandler.test.ts
  ToastManager
    性能测试
      ✓ 显示 Toast 应该很快 (< 10ms) (12 ms)
        显示 100 个 Toast 耗时: 8.23ms
      ✓ 去重应该提升性能 (15 ms)
        不同消息: 10.45ms, 相同消息: 3.21ms

  性能基准测试
    ✓ 批量 Toast 性能基准 (25 ms)
      ============================================================
      Toast 性能基准测试
      ============================================================

      10 个相同 Toast: 2.15ms (目标: < 50ms)
      100 个相同 Toast: 8.67ms (目标: < 100ms)
      1000 个相同 Toast: 35.42ms (目标: < 500ms)

      优化效果:
      - 单次 Toast 平均耗时: 0.0354ms
      - 去重带来的性能提升: 显著 (避免了 999 次 DOM 操作)
```

---

## 集成测试

### 端到端性能测试

#### 1. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload
```

#### 2. 运行性能测试脚本
```bash
# 测试代码执行性能
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello\")"}' \
  -w "\nTotal time: %{time_total}s\n"

# 批量测试
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/code/execute \
    -H "Content-Type: application/json" \
    -d "{\"code\": \"print($i)\"}" \
    -w "\nTime: %{time_total}s\n"
done
```

#### 3. 查看日志
```bash
# 查看容器池性能日志
tail -f backend/logs/app.log | grep -E "quick_health_check|container_reset|acquisition_time"
```

---

## 性能监控

### 后端日志分析

#### 关键性能指标
```python
# 快速健康检查
"quick_health_check_completed" check_time_ms=35.2

# 深度健康检查
"deep_health_check_completed" check_time_ms=245.6

# 容器重置
"container_reset_success" reset_time_ms=185.3

# 容器获取
"container_acquired" acquisition_time_ms=42.1
```

#### 日志过滤示例
```bash
# 查看快速健康检查耗时
grep "quick_health_check_completed" backend/logs/app.log | awk '{print $NF}'

# 查看容器重置耗时
grep "container_reset_success" backend/logs/app.log | awk '{print $(NF-2)}'

# 统计平均耗时
grep "quick_health_check_completed" backend/logs/app.log | \
  awk '{print $NF}' | \
  awk '{s+=$1; c++} END {print "Average:", s/c, "ms"}'
```

### 前端性能监控

#### 浏览器控制台
```javascript
// 查看 Toast 队列统计
ToastManager.getStats()
// { queueSize: 2, totalPending: 5 }

// 测试 Toast 去重
for (let i = 0; i < 100; i++) {
  ToastManager.showToast("测试错误", "error");
}

// 应该只显示 1 个 Toast: "测试错误 (100 个相同错误)"
```

---

## 性能回归检测

### 持续集成 (CI)

#### GitHub Actions 配置示例
```yaml
name: Performance Tests

on: [push, pull_request]

jobs:
  backend-performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest
      - name: Run performance tests
        run: |
          cd backend
          pytest tests/test_performance.py -v

  frontend-performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run performance tests
        run: |
          cd frontend
          npm test errorHandler.test.ts
```

---

## 性能分析工具

### 后端分析

#### 1. cProfile (Python 性能分析)
```bash
cd backend
python -m cProfile -o performance.prof -m pytest tests/test_performance.py

# 查看分析结果
python -c "import pstats; p = pstats.Stats('performance.prof'); p.sort_stats('cumulative').print_stats(20)"
```

#### 2. py-spy (实时性能分析)
```bash
pip install py-spy

# 启动后端服务
uvicorn app.main:app &

# 性能分析
py-spy top --pid $(pgrep -f uvicorn)
py-spy record --pid $(pgrep -f uvicorn) --output profile.svg
```

### 前端分析

#### 1. Chrome DevTools
1. 打开 Chrome DevTools (F12)
2. 切换到 "Performance" 标签
3. 点击录制按钮
4. 触发批量错误场景
5. 停止录制,查看性能分析

#### 2. React DevTools Profiler
1. 安装 React DevTools 扩展
2. 切换到 "Profiler" 标签
3. 录制组件渲染性能
4. 分析 Toast 组件的渲染耗时

---

## 性能优化验证清单

### 后端优化验证 ✅
- [ ] 快速健康检查 < 100ms
- [ ] 深度健康检查 < 600ms
- [ ] 容器重置 < 300ms
- [ ] 容器获取 < 150ms
- [ ] 容器归还 < 400ms
- [ ] 并发操作无错误
- [ ] 日志显示性能改进

### 前端优化验证 ✅
- [ ] Toast 去重工作正常
- [ ] 批量 Toast 正确合并
- [ ] 100 个 Toast < 100ms
- [ ] UI 不再阻塞
- [ ] 无 JavaScript 错误

### 集成测试验证 ✅
- [ ] 端到端代码执行性能改善
- [ ] 批量操作无 Toast 堆积
- [ ] 系统稳定性保持
- [ ] 无性能回归

---

## 故障排查

### 后端性能问题

#### 问题: 容器获取耗时超过 150ms
**排查步骤**:
1. 检查 Docker 服务状态
2. 查看容器池日志
3. 确认快速健康检查是否生效
4. 检查系统资源 (CPU、内存)

#### 问题: 容器重置失败
**排查步骤**:
1. 检查容器状态
2. 查看重置脚本输出
3. 验证容器权限配置
4. 检查 Docker API 响应时间

### 前端性能问题

#### 问题: Toast 仍然堆积
**排查步骤**:
1. 确认 ToastManager 是否正确导入
2. 检查浏览器控制台错误
3. 验证去重窗口设置
4. 查看 Toast 队列统计

#### 问题: TypeScript 编译错误
**排查步骤**:
1. 检查 tsconfig.json 配置
2. 更新 TypeScript 版本
3. 安装缺失的类型定义
4. 重新编译项目

---

## 性能报告

### 生成性能报告
```bash
# 后端性能报告
cd backend
pytest tests/test_performance.py -v -s --html=performance-report.html

# 前端性能报告
cd frontend
npm test errorHandler.test.ts -- --coverage --coverageReporters=html
```

### 报告内容
- 各测试项的执行时间
- 性能基准对比
- 优化前后差异
- 建议和改进方向

---

## 总结

通过以上测试,可以验证性能优化的效果:

### 预期性能提升
- **后端**: 容器获取 4-10x 提升,容器重置 2x 提升
- **前端**: Toast 显示 10x 提升 (批量场景)
- **整体**: 用户体验显著改善

### 持续监控
- 定期运行性能测试
- 监控生产环境性能指标
- 及时发现性能回归
- 不断优化系统性能

---

## 相关文档
- [性能优化实施总结](./PERFORMANCE_OPTIMIZATIONS.md)
- [容器池架构设计](./reports/容器池架构设计_2026-01-08.md)
- [后端性能测试](./backend/tests/test_performance.py)
- [前端性能测试](./frontend/src/utils/__tests__/errorHandler.test.ts)
