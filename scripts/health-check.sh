#!/bin/bash
# HelloAgents Platform 健康检查脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 健康检查结果
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

check_service() {
    local SERVICE_NAME=$1
    local CHECK_COMMAND=$2
    local CHECK_DESCRIPTION=$3

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if eval "$CHECK_COMMAND" > /dev/null 2>&1; then
        print_success "$SERVICE_NAME: $CHECK_DESCRIPTION"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        print_error "$SERVICE_NAME: $CHECK_DESCRIPTION"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

print_header "🏥 HelloAgents Platform 健康检查"

# 1. Docker 容器状态检查
print_info "检查 Docker 容器状态..."
echo ""

CONTAINERS=("helloagents-backend" "helloagents-frontend" "helloagents-postgres" "helloagents-redis")

for CONTAINER in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER)
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER 2>/dev/null || echo "no health check")

        if [ "$STATUS" = "running" ]; then
            if [ "$HEALTH" = "healthy" ] || [ "$HEALTH" = "no health check" ]; then
                print_success "$CONTAINER: 运行中"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
            else
                print_error "$CONTAINER: 运行中但健康检查失败 ($HEALTH)"
                FAILED_CHECKS=$((FAILED_CHECKS + 1))
            fi
        else
            print_error "$CONTAINER: 状态异常 ($STATUS)"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    else
        print_error "$CONTAINER: 容器不存在或未运行"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi
done

echo ""

# 2. 服务端点检查
print_info "检查服务端点..."
echo ""

# 后端健康检查
check_service "后端" "curl -f http://localhost:8000/health" "健康检查端点响应正常"

# 后端API文档
check_service "后端" "curl -f http://localhost:8000/docs" "API文档可访问"

# 前端
check_service "前端" "curl -f http://localhost/" "前端页面可访问"

echo ""

# 3. 数据库检查
print_info "检查数据库连接..."
echo ""

check_service "PostgreSQL" "docker exec helloagents-postgres pg_isready -U helloagents" "数据库连接正常"

# 检查数据库表
if docker exec helloagents-postgres psql -U helloagents -d helloagents -c '\dt' > /dev/null 2>&1; then
    TABLE_COUNT=$(docker exec helloagents-postgres psql -U helloagents -d helloagents -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    print_success "数据库表: $TABLE_COUNT 个表已创建"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    print_error "数据库表: 无法查询表信息"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

echo ""

# 4. Redis 检查
print_info "检查 Redis 连接..."
echo ""

check_service "Redis" "docker exec helloagents-redis redis-cli ping | grep -q PONG" "Redis连接正常"

echo ""

# 5. 资源使用检查
print_info "检查资源使用..."
echo ""

# CPU使用率
for CONTAINER in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        CPU_USAGE=$(docker stats --no-stream --format "{{.CPUPerc}}" $CONTAINER | sed 's/%//')
        MEM_USAGE=$(docker stats --no-stream --format "{{.MemUsage}}" $CONTAINER)

        # CPU使用率检查 (超过80%警告)
        if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
            print_error "$CONTAINER: CPU使用率过高 ($CPU_USAGE%)"
        else
            print_success "$CONTAINER: CPU $CPU_USAGE% | 内存 $MEM_USAGE"
        fi
    fi
done

echo ""

# 6. 日志检查 (检查最近的错误)
print_info "检查最近的错误日志..."
echo ""

ERROR_COUNT=$(docker-compose logs --tail=100 2>/dev/null | grep -i "error" | grep -v "ERROR_HANDLER" | wc -l | tr -d ' ')

if [ "$ERROR_COUNT" -eq 0 ]; then
    print_success "日志: 最近100行日志中没有错误"
else
    print_error "日志: 最近100行日志中发现 $ERROR_COUNT 个错误"
    echo ""
    echo "最近的错误:"
    docker-compose logs --tail=100 2>/dev/null | grep -i "error" | grep -v "ERROR_HANDLER" | tail -5
fi

echo ""

# 7. 总结
print_header "📊 健康检查总结"

echo "总检查项: $TOTAL_CHECKS"
echo "通过: $PASSED_CHECKS"
echo "失败: $FAILED_CHECKS"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    print_success "所有检查通过! 系统运行正常 ✨"
    echo ""
    exit 0
else
    print_error "发现 $FAILED_CHECKS 个问题,请检查!"
    echo ""
    echo "查看详细日志:"
    echo "  docker-compose logs -f"
    echo ""
    echo "重启服务:"
    echo "  docker-compose restart"
    echo ""
    exit 1
fi
