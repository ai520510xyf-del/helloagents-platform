# HelloAgents 性能测试指南

完整的后端性能测试体系，包含基准测试、负载测试、压力测试、性能监控。

---

## 目录

- [概述](#概述)
- [测试工具](#测试工具)
- [快速开始](#快速开始)
- [性能基准测试](#性能基准测试)
- [API 性能测试](#api-性能测试)
- [负载测试](#负载测试)
- [报告生成](#报告生成)
- [性能目标](#性能目标)
- [CI/CD 集成](#cicd-集成)
- [故障排查](#故障排查)

---

## 概述

HelloAgents 性能测试体系涵盖:

1. **基准测试** (Pytest-Benchmark): 容器池、代码执行、API 端点的精确性能基准
2. **负载测试** (Locust): 模拟真实用户负载，测试系统吞吐量和响应时间
3. **压力测试** (K6): 多场景压力测试，评估系统极限和稳定性
4. **性能监控**: 实时监控和报告生成

---

## 测试工具

### 1. Pytest-Benchmark
- **用途**: 微基准测试，精确测量函数/方法性能
- **优势**: 统计准确、易于集成、自动热身
- **适用场景**: 容器池性能、代码执行延迟、数据库查询

### 2. Locust
- **用途**: 分布式负载测试，模拟用户行为
- **优势**: Python 编写、Web UI、分布式支持
- **适用场景**: API 负载测试、真实用户流量模拟

### 3. K6
- **用途**: 现代化负载测试，支持多种测试场景
- **优势**: JavaScript 编写、性能优异、场景丰富
- **适用场景**: 压力测试、峰值测试、浸泡测试

---

## 快速开始

### 安装依赖

```bash
# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 K6 (可选)
# macOS
brew install k6

# Linux
sudo apt-get install k6

# Windows
choco install k6
```

### 运行完整测试套件

```bash
# 1. 运行性能基准测试
pytest tests/test_performance_benchmarks.py --benchmark-only

# 2. 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. 运行 Locust 负载测试 (新终端)
locust -f locustfile.py --host=http://localhost:8000 --headless -u 50 -r 10 -t 2m

# 4. 运行 K6 压力测试 (新终端)
k6 run load-test-k6.js

# 5. 生成性能报告
python scripts/generate_performance_report.py
```

---

## 性能基准测试

### 容器池性能测试

```bash
# 运行所有容器池基准测试
pytest tests/test_performance_benchmarks.py::test_container_acquisition_performance --benchmark-only

pytest tests/test_performance_benchmarks.py::test_container_reset_performance --benchmark-only

pytest tests/test_performance_benchmarks.py::test_concurrent_container_acquisition --benchmark-only
```

**性能目标:**
- 容器获取: < 100ms (平均)
- 容器重置: < 250ms
- 并发获取: < 500ms (10 并发)

### 代码执行性能测试

```bash
# 对比容器池 vs 无容器池
pytest tests/test_performance_benchmarks.py -k "sandbox_execution" --benchmark-only

# 查看详细统计
pytest tests/test_performance_benchmarks.py --benchmark-only --benchmark-verbose
```

**性能目标:**
- 使用容器池: < 200ms
- 不使用容器池: > 1000ms
- 性能提升: 5-10x

### 健康检查性能测试

```bash
pytest tests/test_performance_benchmarks.py -k "health_check" --benchmark-only
```

**性能目标:**
- 快速健康检查: < 50ms
- 深度健康检查: < 500ms

### 生成基准报告

```bash
# 生成 JSON 报告
pytest tests/test_performance_benchmarks.py --benchmark-only --benchmark-json=benchmark_results.json

# 生成 HTML 报告
pytest tests/test_performance_benchmarks.py --benchmark-only --benchmark-autosave

# 对比历史基准
pytest tests/test_performance_benchmarks.py --benchmark-compare --benchmark-compare-fail=mean:5%
```

---

## API 性能测试

### 运行 API 端点测试

```bash
# 运行所有 API 性能测试
pytest tests/test_api_performance.py --benchmark-only

# 按组运行
pytest tests/test_api_performance.py -m api_code --benchmark-only
pytest tests/test_api_performance.py -m api_lessons --benchmark-only
pytest tests/test_api_performance.py -m api_progress --benchmark-only

# 并发测试
pytest tests/test_api_performance.py -m concurrent --benchmark-only
```

**性能目标:**

| 端点 | P95 目标 | P99 目标 |
|------|----------|----------|
| POST /api/v1/code/execute | < 300ms | < 500ms |
| GET /api/v1/lessons | < 100ms | < 200ms |
| GET /api/v1/lessons/{id} | < 50ms | < 100ms |
| POST /api/v1/progress | < 100ms | < 200ms |
| GET /api/v1/progress | < 50ms | < 100ms |

### 响应时间分布测试

```bash
# 测试 P50/P95/P99 分布
pytest tests/test_api_performance.py::test_api_response_time_distribution -v
```

---

## 负载测试

### Locust 负载测试

#### Web UI 模式 (推荐)

```bash
# 启动 Locust Web UI
locust -f locustfile.py --host=http://localhost:8000

# 访问 http://localhost:8089
# 设置用户数和增长率，点击 Start swarming
```

#### 无头模式 (命令行)

```bash
# 基准负载测试 (10 用户, 2 分钟)
locust -f locustfile.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 2m

# 负载测试 (100 用户, 5 分钟)
locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 5m

# 压力测试 (500 用户, 10 分钟)
locust -f locustfile.py --host=http://localhost:8000 --headless -u 500 -r 50 -t 10m

# 生成报告
locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 5m --html=locust_report.html --csv=locust_stats
```

#### 用户类型说明

- **CodeExecutionUser** (70% 流量): 频繁执行代码的用户
- **BrowsingUser** (30% 流量): 主要浏览课程的用户
- **LearningUser**: 按完整学习流程操作的用户
- **StressTestUser**: 高频压力测试用户

### K6 负载测试

#### 运行所有场景

```bash
# 运行完整测试套件 (包含所有场景)
k6 run load-test-k6.js
```

#### 运行特定场景

```bash
# 基准测试 (10 VUs, 2 分钟)
k6 run --env SCENARIO=baseline load-test-k6.js

# 负载测试 (逐步增加到 100 VUs)
k6 run --env SCENARIO=load load-test-k6.js

# 压力测试 (300 VUs)
k6 run --env SCENARIO=stress load-test-k6.js

# 峰值测试 (500 VUs 突发)
k6 run --env SCENARIO=spike load-test-k6.js

# 浸泡测试 (30 VUs, 30 分钟)
k6 run --env SCENARIO=soak load-test-k6.js
```

#### 生成报告

```bash
# 生成 JSON 报告
k6 run load-test-k6.js --out json=k6_results.json

# 导出总结
k6 run load-test-k6.js --summary-export=summary.json

# K6 Cloud (需要账号)
k6 cloud load-test-k6.js
```

#### K6 场景说明

| 场景 | VUs | 持续时间 | 目的 |
|------|-----|----------|------|
| baseline | 10 | 2m | 建立性能基线 |
| load | 0→100 | 14m | 测试正常负载 |
| stress | 0→300 | 10m | 测试系统极限 |
| spike | 0→500→0 | 1.5m | 测试突发流量 |
| soak | 30 | 30m | 测试长期稳定性 |

---

## 报告生成

### 使用报告生成器

```bash
# 生成完整报告 (HTML + Markdown)
python scripts/generate_performance_report.py

# 仅生成 HTML
python scripts/generate_performance_report.py --format html

# 仅生成 Markdown
python scripts/generate_performance_report.py --format markdown

# 指定文件路径
python scripts/generate_performance_report.py \
  --pytest-benchmark .benchmarks/*/0001_*.json \
  --locust locust_stats.json \
  --k6 summary.json
```

### 报告内容

报告包含:
- ✅ 测试概览和执行时间
- ⚠️ 性能警告
- 🎯 性能目标检查 (Pass/Fail)
- 🧪 Pytest Benchmark 详细结果
- 🦗 Locust 负载测试统计
- 📈 K6 压力测试指标

### 查看报告

```bash
# 自动在浏览器中打开
open performance_reports/performance_report_*.html

# 或查看 Markdown 版本
cat performance_reports/performance_report_*.md
```

---

## 性能目标

### 容器池性能

| 指标 | 目标 |
|------|------|
| 容器获取 (平均) | < 100ms |
| 容器获取 (P95) | < 200ms |
| 容器重置 | < 250ms |
| 健康检查 (快速) | < 50ms |
| 健康检查 (深度) | < 500ms |
| 并发获取 (10 并发) | < 500ms |

### API 响应时间

| 端点 | P95 | P99 |
|------|-----|-----|
| POST /api/v1/code/execute | < 300ms | < 500ms |
| GET /api/v1/lessons | < 100ms | < 200ms |
| GET /api/v1/lessons/{id} | < 50ms | < 100ms |
| POST /api/v1/progress | < 100ms | < 200ms |

### 系统吞吐量

| 指标 | 目标 |
|------|------|
| 吞吐量 (RPS) | > 100 |
| 并发代码执行 | > 50 |
| 错误率 | < 1% |

### 资源使用

| 资源 | 限制 |
|------|------|
| 容器内存 | 128MB |
| 容器 CPU | 50% (半核) |
| 池大小 | 10 (最大) |

---

## CI/CD 集成

### GitHub Actions 配置

```yaml
name: Performance Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨 2 点

jobs:
  performance:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run benchmark tests
        run: |
          cd backend
          pytest tests/test_performance_benchmarks.py --benchmark-only --benchmark-json=benchmark.json

      - name: Check performance regression
        run: |
          cd backend
          pytest tests/test_performance_benchmarks.py --benchmark-compare --benchmark-compare-fail=mean:10%

      - name: Upload benchmark results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: backend/benchmark.json

      - name: Generate performance report
        run: |
          cd backend
          python scripts/generate_performance_report.py --format markdown

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('backend/performance_reports/performance_report_*.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

### 性能退化检测

```bash
# 设置基准
pytest tests/test_performance_benchmarks.py --benchmark-only --benchmark-save=baseline

# 检测退化 (容忍 5% 性能下降)
pytest tests/test_performance_benchmarks.py --benchmark-compare=baseline --benchmark-compare-fail=mean:5%
```

---

## 故障排查

### 常见问题

#### 1. 容器池性能未达预期

**症状:** 容器获取时间 > 200ms

**排查步骤:**
```bash
# 检查 Docker 状态
docker ps
docker stats

# 查看容器池日志
tail -f backend/logs/app.log | grep "container_pool"

# 测试容器创建时间
python backend/test_pool_performance.py
```

**解决方案:**
- 增加容器池预热大小
- 检查 Docker 资源限制
- 优化容器镜像大小

#### 2. API 响应时间过慢

**症状:** P95 > 500ms

**排查步骤:**
```bash
# 查看慢查询
pytest tests/test_api_performance.py::test_api_response_time_distribution -v

# 检查数据库性能
pytest tests/test_api_performance.py -m database --benchmark-only
```

**解决方案:**
- 添加数据库索引
- 启用查询缓存
- 优化 SQL 查询

#### 3. 高并发下错误率高

**症状:** 并发 > 100 时错误率 > 5%

**排查步骤:**
```bash
# 压力测试
pytest tests/test_performance_benchmarks.py::test_pool_under_stress -m stress

# Locust 压力测试
locust -f locustfile.py --host=http://localhost:8000 --headless -u 200 -r 20 -t 5m
```

**解决方案:**
- 增加容器池最大大小
- 优化容器获取超时时间
- 添加请求队列和限流

#### 4. 内存泄漏

**症状:** 长时间运行后内存持续增长

**排查步骤:**
```bash
# 浸泡测试
k6 run --env SCENARIO=soak load-test-k6.js

# 监控内存
docker stats
```

**解决方案:**
- 检查容器是否正确清理
- 优化容器池空闲回收
- 添加定期重启机制

### 性能分析工具

```bash
# 使用 py-spy 进行性能分析
pip install py-spy
py-spy record -o profile.svg -- python -m pytest tests/test_performance_benchmarks.py

# 使用 memory_profiler
pip install memory_profiler
python -m memory_profiler backend/app/container_pool.py
```

---

## 最佳实践

### 1. 定期运行性能测试

- ✅ 每次 PR 运行基准测试
- ✅ 每日运行完整负载测试
- ✅ 每周运行浸泡测试
- ✅ 发布前运行压力测试

### 2. 建立性能基线

```bash
# 保存性能基线
pytest tests/test_performance_benchmarks.py --benchmark-only --benchmark-save=v1.0.0

# 对比新版本
pytest tests/test_performance_benchmarks.py --benchmark-compare=v1.0.0
```

### 3. 监控关键指标

- 响应时间 (P50/P95/P99)
- 吞吐量 (RPS)
- 错误率
- 资源使用 (CPU/内存)
- 容器池状态

### 4. 性能优化优先级

1. **高优先级**: P95 > 目标 2x
2. **中优先级**: P95 > 目标 1.5x
3. **低优先级**: P95 > 目标 1.2x

---

## 参考资源

- [Pytest-Benchmark 文档](https://pytest-benchmark.readthedocs.io/)
- [Locust 文档](https://docs.locust.io/)
- [K6 文档](https://k6.io/docs/)
- [Docker 性能最佳实践](https://docs.docker.com/config/containers/resource_constraints/)

---

**维护者:** HelloAgents Performance Team
**最后更新:** 2026-01-08
