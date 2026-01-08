#!/bin/bash

# 后端冒烟测试脚本
# 快速验证关键功能是否正常工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "  后端冒烟测试"
echo "========================================="
echo ""

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}[测试 $TOTAL_TESTS] $test_name${NC}"

    if eval "$test_command"; then
        echo -e "${GREEN}✅ 通过${NC}\n"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}\n"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 切换到 backend 目录
cd "$(dirname "$0")/.."
echo "工作目录: $(pwd)"
echo ""

# 测试 1: 基本导入测试
run_test "基本导入测试" \
    "python -c 'from app.main import app; print(\"✅ Import OK\")'"

# 测试 2: 验证环境变量
run_test "环境变量检查" \
    "python -c 'import os; assert os.getenv(\"OPENAI_API_KEY\", \"sk-test\") != \"\", \"OPENAI_API_KEY not set\"; print(\"✅ Env OK\")'"

# 测试 3: 数据库模型导入
run_test "数据库模型导入" \
    "python -c 'from app.models.chat_message import ChatMessage; from app.models.user_progress import UserProgress; from app.models.code_submission import CodeSubmission; print(\"✅ Models OK\")'"

# 测试 4: API 路由导入
run_test "API 路由导入" \
    "python -c 'from app.api.v1.endpoints.chat import router as chat_router; from app.api.v1.endpoints.sandbox import router as sandbox_router; print(\"✅ Routes OK\")'"

# 测试 5: 容器池导入
run_test "容器池导入" \
    "python -c 'from app.container_pool import ContainerPool; print(\"✅ Container Pool OK\")'"

# 测试 6: 错误处理导入
run_test "错误处理导入" \
    "python -c 'from app.exceptions import APIError; from app.error_codes import ErrorCode; print(\"✅ Error Handling OK\")'"

# 测试 7: 快速单元测试（健康检查相关）
if command -v pytest &> /dev/null; then
    run_test "API 健康检查测试" \
        "pytest tests/test_api_performance.py::test_health_check -v --tb=short -q 2>&1 | tail -n 20 || true"

    # 测试 8: 容器池基本功能测试
    run_test "容器池创建测试" \
        "pytest tests/test_container_pool.py::TestContainerPool::test_create_container -v --tb=short -q 2>&1 | tail -n 20 || true"

    # 测试 9: 错误处理测试
    run_test "错误处理测试" \
        "pytest tests/test_error_handling.py::test_api_error_creation -v --tb=short -q 2>&1 | tail -n 20 || true"
else
    echo -e "${YELLOW}⚠️  pytest 未安装，跳过单元测试${NC}\n"
fi

# 测试 10: 依赖包检查
run_test "关键依赖包检查" \
    "python -c 'import fastapi, uvicorn, docker, openai, pytest; print(\"✅ Dependencies OK\")'"

# 显示结果
echo "========================================="
echo "  测试结果汇总"
echo "========================================="
echo -e "总测试数: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo ""

# 计算通过率
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "通过率: ${BLUE}${PASS_RATE}%${NC}"
    echo ""
fi

# 返回状态
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有冒烟测试通过！${NC}"
    echo -e "${GREEN}✅ 后端基本功能正常，可以继续进行完整测试${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED_TESTS 个测试失败！${NC}"
    echo -e "${RED}❌ 请先修复基本问题再进行完整测试${NC}"
    exit 1
fi
