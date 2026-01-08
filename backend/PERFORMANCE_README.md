# 后端性能测试快速开始

欢迎使用 HelloAgents 后端性能测试套件! 这个 README 将帮助你快速开始性能测试。

---

## 🚀 5 分钟快速开始

### 步骤 1: 验证环境

```bash
cd backend
python3 scripts/verify_performance_setup.py
```

### 步骤 2: 安装依赖

```bash
pip install -r requirements.txt
```

**新增的测试依赖:**
- `pytest-benchmark` - 性能基准测试
- `pytest-asyncio` - 异步测试支持
- `locust` - 负载测试
- `faker` - 测试数据生成

### 步骤 3: 运行快速测试

```bash
./scripts/run_performance_tests.sh quick
```

这将运行所有性能基准测试并生成报告 (约 2-5 分钟)。

---

## 📊 查看测试结果

测试完成后,报告会自动生成在 `performance_reports/` 目录:

```bash
# 在浏览器中打开 HTML 报告
open performance_reports/performance_report_*.html

# 或查看 Markdown 报告
cat performance_reports/performance_report_*.md
```

---

## 🧪 运行特定测试

### 性能基准测试

```bash
# 容器池性能测试
pytest tests/test_performance_benchmarks.py::test_container_acquisition_performance --benchmark-only

# API 性能测试
pytest tests/test_api_performance.py::test_code_execute_endpoint_performance --benchmark-only

# 查看所有测试
pytest tests/test_performance_benchmarks.py --collect-only
```

### 负载测试

```bash
# 1. 启动后端服务 (新终端)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. 运行 Locust 负载测试
locust -f locustfile.py --host=http://localhost:8000 --headless -u 50 -r 10 -t 2m

# 3. 运行 K6 负载测试 (需要安装 K6)
k6 run load-test-k6.js
```

---

## 🎯 性能目标

| 指标 | 目标 | 如何测试 |
|------|------|----------|
| 容器获取 | < 100ms | `test_container_acquisition_performance` |
| API 响应 (P95) | < 300ms | `test_code_execute_endpoint_performance` |
| 吞吐量 | > 100 RPS | Locust 或 K6 |
| 错误率 | < 1% | 所有负载测试 |

---

## 📝 主要文件

| 文件 | 说明 |
|------|------|
| `tests/test_performance_benchmarks.py` | 容器池性能基准测试 (15+ 个测试) |
| `tests/test_api_performance.py` | API 端点性能测试 (10+ 个测试) |
| `locustfile.py` | Locust 负载测试脚本 |
| `load-test-k6.js` | K6 负载测试脚本 |
| `scripts/run_performance_tests.sh` | 自动化测试脚本 |
| `scripts/generate_performance_report.py` | 报告生成器 |
| `PERFORMANCE_TESTING.md` | 完整使用指南 |

---

## 💡 常用命令

```bash
# 快速测试 (仅 benchmark)
./scripts/run_performance_tests.sh quick

# 完整测试 (需要后端服务运行)
./scripts/run_performance_tests.sh full

# 仅运行 benchmark
./scripts/run_performance_tests.sh benchmark

# 仅运行 API 测试
./scripts/run_performance_tests.sh api

# 仅生成报告
./scripts/run_performance_tests.sh report

# 验证环境
python3 scripts/verify_performance_setup.py
```

---

## 🔧 故障排查

### 问题: Docker 未运行

**解决方案:**
```bash
# 启动 Docker Desktop
# 或在 Linux 上: sudo systemctl start docker
```

### 问题: 依赖未安装

**解决方案:**
```bash
pip install -r requirements.txt
```

### 问题: K6 未安装

**解决方案:**
```bash
# macOS
brew install k6

# Linux
sudo apt-get install k6

# Windows
choco install k6
```

---

## 📖 更多信息

- **完整文档**: 查看 `PERFORMANCE_TESTING.md`
- **任务总结**: 查看 `PERFORMANCE_TEST_SUMMARY.md`
- **交付清单**: 查看 `DELIVERY_CHECKLIST.md`

---

## 🤝 贡献

性能测试框架已完整实现,包括:
- ✅ 30+ 个性能测试
- ✅ 3 种测试工具 (Pytest-Benchmark, Locust, K6)
- ✅ 自动化报告生成
- ✅ 完整文档

如需添加新的性能测试,请参考现有测试文件的结构。

---

**Performance Engineer:** Claude
**完成日期:** 2026-01-08
**版本:** 1.0.0
