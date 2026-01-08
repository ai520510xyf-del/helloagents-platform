#!/bin/bash

# 一键验证脚本 - 执行所有验证测试
# 用于在修复完成后快速验证系统状态

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "========================================="
echo "  CI 修复一键验证"
echo "========================================="
echo "项目根目录: $PROJECT_ROOT"
echo ""

# 总体状态
OVERALL_STATUS="✅ SUCCESS"
FAILED_STAGES=()

# 函数：运行验证阶段
run_stage() {
    local stage_name="$1"
    local stage_command="$2"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}第 $3 阶段: $stage_name${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if eval "$stage_command"; then
        echo ""
        echo -e "${GREEN}✅ $stage_name 通过${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ $stage_name 失败${NC}"
        OVERALL_STATUS="❌ FAILURE"
        FAILED_STAGES+=("$stage_name")
        return 1
    fi
}

# 第 1 阶段: CI 监控
run_stage "CI 工作流监控" \
    "$SCRIPT_DIR/monitor_ci.sh" \
    "1" || true

# 第 2 阶段: 后端冒烟测试
run_stage "后端冒烟测试" \
    "cd $PROJECT_ROOT/backend && ./scripts/smoke_test.sh" \
    "2" || true

# 第 3 阶段: 前端冒烟测试
run_stage "前端冒烟测试" \
    "cd $PROJECT_ROOT/frontend && ./scripts/smoke_test.sh" \
    "3" || true

# 第 4 阶段: 后端完整测试（可选）
if [ "${RUN_FULL_TESTS:-0}" == "1" ]; then
    run_stage "后端完整测试" \
        "cd $PROJECT_ROOT/backend && pytest tests/ -v --tb=short" \
        "4" || true

    # 第 5 阶段: 前端完整测试（可选）
    run_stage "前端完整测试" \
        "cd $PROJECT_ROOT/frontend && npm test -- --run" \
        "5" || true
else
    echo ""
    echo -e "${YELLOW}ℹ️  跳过完整测试（设置 RUN_FULL_TESTS=1 启用）${NC}"
fi

# 显示总体结果
echo ""
echo "========================================="
echo "  验证结果汇总"
echo "========================================="
echo ""

if [ "$OVERALL_STATUS" == "✅ SUCCESS" ]; then
    echo -e "${GREEN}${OVERALL_STATUS}${NC}"
    echo ""
    echo -e "${GREEN}✅ 所有验证通过！${NC}"
    echo -e "${GREEN}✅ 系统状态正常，可以继续开发或部署${NC}"
    echo ""
else
    echo -e "${RED}${OVERALL_STATUS}${NC}"
    echo ""
    echo -e "${RED}❌ 有 ${#FAILED_STAGES[@]} 个阶段失败：${NC}"
    for stage in "${FAILED_STAGES[@]}"; do
        echo -e "${RED}  - $stage${NC}"
    done
    echo ""
    echo -e "${YELLOW}请查看上述错误日志并修复问题${NC}"
    echo ""
fi

# 生成报告提示
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}下一步操作${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 查看详细报告模板："
echo -e "   ${CYAN}$PROJECT_ROOT/reports/CI_FIX_VERIFICATION_REPORT.md${NC}"
echo ""
echo "2. 填写验证报告并提交"
echo ""
echo "3. 通知团队验证结果"
echo ""

# 返回状态
if [ "$OVERALL_STATUS" == "✅ SUCCESS" ]; then
    exit 0
else
    exit 1
fi
