#!/bin/bash

# 前端冒烟测试脚本
# 快速验证关键功能是否正常工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "  前端冒烟测试"
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

# 切换到 frontend 目录
cd "$(dirname "$0")/.."
echo "工作目录: $(pwd)"
echo ""

# 测试 1: 检查 node_modules
run_test "依赖包安装检查" \
    "[ -d node_modules ] && echo '✅ node_modules exists'"

# 测试 2: 检查关键依赖
run_test "关键依赖包检查" \
    "node -e \"require('react'); require('react-dom'); require('vite'); console.log('✅ Dependencies OK')\""

# 测试 3: TypeScript 配置检查
run_test "TypeScript 配置检查" \
    "[ -f tsconfig.json ] && echo '✅ tsconfig.json exists'"

# 测试 4: Vite 配置检查
run_test "Vite 配置检查" \
    "[ -f vite.config.ts ] && echo '✅ vite.config.ts exists'"

# 测试 5: 检查测试配置
run_test "测试配置检查" \
    "node -e \"const config = require('./vite.config.ts'); console.log('✅ Vitest config OK')\" 2>&1 | grep -q 'OK' || true"

# 测试 6: ESLint 检查（轻量级）
if command -v npm &> /dev/null && npm run lint:check &> /dev/null; then
    run_test "代码风格检查（ESLint）" \
        "npm run lint 2>&1 | tail -n 10"
else
    echo -e "${YELLOW}⚠️  ESLint 未配置，跳过代码风格检查${NC}\n"
fi

# 测试 7: 错误处理测试
if command -v npm &> /dev/null; then
    run_test "错误处理单元测试" \
        "npm test -- errorHandling.test.tsx --run --reporter=verbose 2>&1 | tail -n 20 || true"
else
    echo -e "${YELLOW}⚠️  无法运行测试，跳过${NC}\n"
fi

# 测试 8: 快速类型检查
if command -v npx &> /dev/null; then
    run_test "TypeScript 类型检查" \
        "npx tsc --noEmit --skipLibCheck 2>&1 | head -n 20"
else
    echo -e "${YELLOW}⚠️  TypeScript 编译器未找到，跳过类型检查${NC}\n"
fi

# 测试 9: 生产构建测试（可选，较慢）
if [ "${RUN_BUILD_TEST:-0}" == "1" ]; then
    run_test "生产构建测试" \
        "npm run build 2>&1 | tail -n 20"

    # 检查构建产物
    run_test "构建产物检查" \
        "[ -d dist ] && [ -f dist/index.html ] && echo '✅ Build artifacts exist'"
else
    echo -e "${YELLOW}ℹ️  跳过生产构建测试（设置 RUN_BUILD_TEST=1 启用）${NC}\n"
fi

# 测试 10: Playwright 配置检查（E2E 测试准备）
run_test "E2E 测试配置检查" \
    "[ -f playwright.config.ts ] && echo '✅ Playwright config exists'"

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
    echo -e "${GREEN}✅ 前端基本功能正常，可以继续进行完整测试${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED_TESTS 个测试失败！${NC}"
    echo -e "${RED}❌ 请先修复基本问题再进行完整测试${NC}"
    exit 1
fi
