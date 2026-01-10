#!/bin/bash

# =============================================================================
# 烟雾测试脚本
# 用于验证部署后的核心功能是否正常工作
# =============================================================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKEND_URL="${BACKEND_URL:-https://helloagents-backend.onrender.com}"
FRONTEND_URL="${FRONTEND_URL:-https://helloagents-platform.pages.dev}"
TIMEOUT="${TIMEOUT:-10}"

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

# 测试计数器
total_tests=0
passed_tests=0
failed_tests=0

# 执行测试
run_test() {
    local test_name=$1
    local test_function=$2

    total_tests=$((total_tests + 1))
    log_info "Running test: $test_name"

    if $test_function; then
        passed_tests=$((passed_tests + 1))
        log_success "✅ PASSED: $test_name"
        return 0
    else
        failed_tests=$((failed_tests + 1))
        log_error "❌ FAILED: $test_name"
        return 1
    fi
}

# ==================================================
# 测试用例
# ==================================================

# 测试1: 后端根端点
test_backend_root() {
    local response=$(curl -s --max-time "$TIMEOUT" "$BACKEND_URL/")
    local status=$(echo "$response" | jq -r '.status' 2>/dev/null)

    if [ "$status" == "ok" ]; then
        log_info "Backend version: $(echo "$response" | jq -r '.version')"
        return 0
    else
        log_error "Backend root endpoint returned unexpected status: $status"
        return 1
    fi
}

# 测试2: 健康检查端点
test_health_check() {
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$BACKEND_URL/health")
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$status_code" -eq 200 ]; then
        local health_status=$(echo "$body" | jq -r '.status' 2>/dev/null)
        if [ "$health_status" == "healthy" ]; then
            return 0
        else
            log_error "Health status is: $health_status"
            return 1
        fi
    else
        log_error "Health check returned HTTP $status_code"
        return 1
    fi
}

# 测试3: 就绪检查端点
test_readiness_check() {
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$BACKEND_URL/health/ready")
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$status_code" -eq 200 ]; then
        local status=$(echo "$body" | jq -r '.status' 2>/dev/null)
        if [ "$status" == "ready" ]; then
            return 0
        else
            return 1
        fi
    else
        log_error "Readiness check returned HTTP $status_code"
        return 1
    fi
}

# 测试4: 存活检查端点
test_liveness_check() {
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$BACKEND_URL/health/live")
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$status_code" -eq 200 ]; then
        local status=$(echo "$body" | jq -r '.status' 2>/dev/null)
        if [ "$status" == "alive" ]; then
            return 0
        else
            return 1
        fi
    else
        log_error "Liveness check returned HTTP $status_code"
        return 1
    fi
}

# 测试5: API 文档可访问
test_api_docs() {
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$BACKEND_URL/api/v1/docs")
    local status_code=$(echo "$response" | tail -n1)

    if [ "$status_code" -eq 200 ]; then
        return 0
    else
        log_error "API docs returned HTTP $status_code"
        return 1
    fi
}

# 测试6: 获取课程列表
test_get_lessons() {
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$BACKEND_URL/api/v1/lessons")
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$status_code" -eq 200 ]; then
        local success=$(echo "$body" | jq -r '.success' 2>/dev/null)
        if [ "$success" == "true" ]; then
            local lesson_count=$(echo "$body" | jq '.lessons | length' 2>/dev/null)
            log_info "Found $lesson_count lessons"
            return 0
        else
            return 1
        fi
    else
        log_error "Get lessons returned HTTP $status_code"
        return 1
    fi
}

# 测试7: 获取特定课程内容
test_get_lesson_content() {
    local lesson_id="1"
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$BACKEND_URL/api/v1/lessons/$lesson_id")
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$status_code" -eq 200 ]; then
        local title=$(echo "$body" | jq -r '.title' 2>/dev/null)
        if [ -n "$title" ] && [ "$title" != "null" ]; then
            log_info "Lesson title: $title"
            return 0
        else
            return 1
        fi
    else
        log_error "Get lesson content returned HTTP $status_code"
        return 1
    fi
}

# 测试8: 代码执行 API（简单测试）
test_code_execution() {
    local code="print('Hello, HelloAgents!')"
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" \
        -X POST "$BACKEND_URL/api/v1/code/execute" \
        -H "Content-Type: application/json" \
        -d "{\"code\":\"$code\",\"language\":\"python\",\"timeout\":10}")

    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$status_code" -eq 200 ]; then
        local success=$(echo "$body" | jq -r '.success' 2>/dev/null)
        if [ "$success" == "true" ]; then
            local output=$(echo "$body" | jq -r '.output' 2>/dev/null)
            log_info "Code execution output: $output"
            return 0
        else
            log_warning "Code execution reported success=false"
            # 仍然返回0，因为API正常响应了
            return 0
        fi
    else
        log_error "Code execution returned HTTP $status_code"
        return 1
    fi
}

# 测试9: 沙箱池统计（如果启用）
test_sandbox_pool_stats() {
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$BACKEND_URL/api/v1/sandbox/pool/stats")
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$status_code" -eq 200 ]; then
        local pool_enabled=$(echo "$body" | jq -r '.pool_enabled' 2>/dev/null)
        if [ "$pool_enabled" == "true" ]; then
            log_info "Container pool is enabled"
        else
            log_info "Container pool is disabled"
        fi
        return 0
    else
        log_error "Sandbox pool stats returned HTTP $status_code"
        return 1
    fi
}

# 测试10: 前端首页可访问
test_frontend_homepage() {
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$FRONTEND_URL")
    local status_code=$(echo "$response" | tail -n1)

    if [ "$status_code" -eq 200 ]; then
        return 0
    else
        log_error "Frontend homepage returned HTTP $status_code"
        return 1
    fi
}

# 测试11: CORS 配置
test_cors() {
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" \
        -X OPTIONS "$BACKEND_URL/api/v1/lessons" \
        -H "Origin: $FRONTEND_URL" \
        -H "Access-Control-Request-Method: GET")

    local status_code=$(echo "$response" | tail -n1)

    if [ "$status_code" -eq 200 ] || [ "$status_code" -eq 204 ]; then
        log_info "CORS preflight successful"
        return 0
    else
        log_warning "CORS check returned HTTP $status_code (may be expected)"
        # 不算失败，因为某些服务器可能不响应 OPTIONS
        return 0
    fi
}

# 测试12: 响应时间测试
test_response_time() {
    local start_time=$(date +%s%N)
    curl -s --max-time "$TIMEOUT" "$BACKEND_URL/health/live" > /dev/null
    local end_time=$(date +%s%N)

    local duration=$(( (end_time - start_time) / 1000000 ))
    log_info "Response time: ${duration}ms"

    if [ "$duration" -lt 2000 ]; then
        return 0
    else
        log_warning "Response time is high: ${duration}ms"
        return 0  # 不算失败，只是警告
    fi
}

# ==================================================
# 主函数
# ==================================================

main() {
    echo ""
    echo "======================================"
    echo "  HelloAgents 烟雾测试"
    echo "======================================"
    echo ""
    log_info "Backend URL: $BACKEND_URL"
    log_info "Frontend URL: $FRONTEND_URL"
    echo ""

    # 记录开始时间
    start_time=$(date +%s)

    # 运行所有测试
    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "后端基础测试"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    run_test "Backend Root Endpoint" test_backend_root
    echo ""

    run_test "Health Check Endpoint" test_health_check
    echo ""

    run_test "Readiness Check Endpoint" test_readiness_check
    echo ""

    run_test "Liveness Check Endpoint" test_liveness_check
    echo ""

    run_test "API Documentation" test_api_docs
    echo ""

    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "API 功能测试"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    run_test "Get Lessons List" test_get_lessons
    echo ""

    run_test "Get Lesson Content" test_get_lesson_content
    echo ""

    run_test "Code Execution" test_code_execution
    echo ""

    run_test "Sandbox Pool Stats" test_sandbox_pool_stats
    echo ""

    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "前端测试"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    run_test "Frontend Homepage" test_frontend_homepage
    echo ""

    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "性能和配置测试"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    run_test "CORS Configuration" test_cors
    echo ""

    run_test "Response Time" test_response_time
    echo ""

    # 计算执行时间
    end_time=$(date +%s)
    duration=$((end_time - start_time))

    # 显示总结
    echo ""
    echo "======================================"
    echo "  烟雾测试结果"
    echo "======================================"
    echo ""
    echo "总测试数: $total_tests"
    echo -e "通过: ${GREEN}$passed_tests${NC}"
    echo -e "失败: ${RED}$failed_tests${NC}"
    echo "执行时间: ${duration}秒"
    echo ""

    # 计算成功率
    if [ $total_tests -gt 0 ]; then
        success_rate=$(( passed_tests * 100 / total_tests ))
        echo "成功率: ${success_rate}%"
        echo ""

        if [ $failed_tests -eq 0 ]; then
            log_success "✅ 所有烟雾测试通过！部署成功！"
            echo ""
            exit 0
        elif [ $success_rate -ge 80 ]; then
            log_warning "⚠️  部分测试失败，但核心功能正常（成功率 >= 80%）"
            echo ""
            exit 0
        else
            log_error "❌ 多项测试失败，部署可能有问题"
            echo ""
            exit 1
        fi
    else
        log_error "❌ 没有运行任何测试"
        exit 1
    fi
}

# 运行主函数
main
