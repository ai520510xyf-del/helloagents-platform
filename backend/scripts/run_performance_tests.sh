#!/bin/bash

# HelloAgents 性能测试执行脚本
#
# 自动运行所有性能测试并生成报告
#
# 使用方法:
#   ./scripts/run_performance_tests.sh          # 运行所有测试
#   ./scripts/run_performance_tests.sh quick    # 快速测试
#   ./scripts/run_performance_tests.sh full     # 完整测试

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    # 检查 Python
    if ! command -v python &> /dev/null; then
        log_error "Python 未安装"
        exit 1
    fi

    # 检查 pytest
    if ! python -c "import pytest" &> /dev/null; then
        log_error "pytest 未安装，请运行: pip install -r requirements.txt"
        exit 1
    fi

    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_warning "Docker 未安装，部分测试将被跳过"
    fi

    # 检查 Locust (可选)
    if ! python -c "import locust" &> /dev/null; then
        log_warning "Locust 未安装，负载测试将被跳过"
    fi

    # 检查 K6 (可选)
    if ! command -v k6 &> /dev/null; then
        log_warning "K6 未安装，K6 测试将被跳过。安装: brew install k6"
    fi

    log_success "依赖检查完成"
}

# 运行 pytest-benchmark 测试
run_benchmark_tests() {
    log_info "运行 Pytest Benchmark 测试..."

    pytest tests/test_performance_benchmarks.py \
        --benchmark-only \
        --benchmark-autosave \
        --benchmark-json=benchmark_results.json \
        -v

    if [ $? -eq 0 ]; then
        log_success "Benchmark 测试完成"
    else
        log_error "Benchmark 测试失败"
        return 1
    fi
}

# 运行 API 性能测试
run_api_tests() {
    log_info "运行 API 性能测试..."

    pytest tests/test_api_performance.py \
        --benchmark-only \
        --benchmark-json=api_benchmark.json \
        -v

    if [ $? -eq 0 ]; then
        log_success "API 性能测试完成"
    else
        log_error "API 性能测试失败"
        return 1
    fi
}

# 运行 Locust 负载测试
run_locust_tests() {
    log_info "运行 Locust 负载测试..."

    if ! python -c "import locust" &> /dev/null; then
        log_warning "Locust 未安装，跳过负载测试"
        return 0
    fi

    # 检查后端是否运行
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_warning "后端服务未运行，跳过 Locust 测试"
        log_info "请先启动后端: uvicorn app.main:app --host 0.0.0.0 --port 8000"
        return 0
    fi

    # 运行快速负载测试 (10 用户, 1 分钟)
    locust -f locustfile.py \
        --host=http://localhost:8000 \
        --headless \
        -u 10 \
        -r 2 \
        -t 1m \
        --html=locust_report.html \
        --csv=locust_stats

    if [ $? -eq 0 ]; then
        log_success "Locust 负载测试完成"
    else
        log_error "Locust 负载测试失败"
        return 1
    fi
}

# 运行 K6 测试
run_k6_tests() {
    log_info "运行 K6 负载测试..."

    if ! command -v k6 &> /dev/null; then
        log_warning "K6 未安装，跳过 K6 测试"
        return 0
    fi

    # 检查后端是否运行
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_warning "后端服务未运行，跳过 K6 测试"
        log_info "请先启动后端: uvicorn app.main:app --host 0.0.0.0 --port 8000"
        return 0
    fi

    # 运行基准测试场景
    k6 run --env SCENARIO=baseline load-test-k6.js --summary-export=summary.json

    if [ $? -eq 0 ]; then
        log_success "K6 测试完成"
    else
        log_error "K6 测试失败"
        return 1
    fi
}

# 生成性能报告
generate_report() {
    log_info "生成性能报告..."

    python scripts/generate_performance_report.py --format both

    if [ $? -eq 0 ]; then
        log_success "性能报告已生成"

        # 查找最新的报告
        LATEST_HTML=$(ls -t performance_reports/performance_report_*.html | head -1)
        LATEST_MD=$(ls -t performance_reports/performance_report_*.md | head -1)

        log_info "HTML 报告: $LATEST_HTML"
        log_info "Markdown 报告: $LATEST_MD"

        # 在 macOS 上自动打开报告
        if [[ "$OSTYPE" == "darwin"* ]]; then
            log_info "在浏览器中打开报告..."
            open "$LATEST_HTML"
        fi
    else
        log_error "报告生成失败"
        return 1
    fi
}

# 快速测试 (仅 benchmark)
quick_test() {
    echo ""
    echo "=================================="
    echo "  HelloAgents 快速性能测试"
    echo "=================================="
    echo ""

    check_dependencies
    run_benchmark_tests
    generate_report

    log_success "快速测试完成"
}

# 完整测试 (所有测试)
full_test() {
    echo ""
    echo "=================================="
    echo "  HelloAgents 完整性能测试"
    echo "=================================="
    echo ""

    check_dependencies
    run_benchmark_tests
    run_api_tests
    run_locust_tests
    run_k6_tests
    generate_report

    log_success "完整测试完成"
}

# 主函数
main() {
    case "${1:-quick}" in
        quick)
            quick_test
            ;;
        full)
            full_test
            ;;
        benchmark)
            check_dependencies
            run_benchmark_tests
            ;;
        api)
            check_dependencies
            run_api_tests
            ;;
        locust)
            check_dependencies
            run_locust_tests
            ;;
        k6)
            check_dependencies
            run_k6_tests
            ;;
        report)
            generate_report
            ;;
        *)
            echo "用法: $0 {quick|full|benchmark|api|locust|k6|report}"
            echo ""
            echo "命令说明:"
            echo "  quick      - 快速测试 (仅 benchmark)"
            echo "  full       - 完整测试 (所有测试)"
            echo "  benchmark  - 仅运行 benchmark 测试"
            echo "  api        - 仅运行 API 性能测试"
            echo "  locust     - 仅运行 Locust 负载测试"
            echo "  k6         - 仅运行 K6 测试"
            echo "  report     - 仅生成报告"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
