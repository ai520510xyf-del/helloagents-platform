#!/bin/bash
# HelloAgents Platform 一键部署脚本
#
# 使用方法:
#   ./scripts/deploy.sh              # 交互式部署
#   ./scripts/deploy.sh --quick      # 快速部署(跳过检查)
#   ./scripts/deploy.sh --check      # 仅检查环境
#   ./scripts/deploy.sh --backup     # 备份后部署

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
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

# 解析命令行参数
QUICK_MODE=false
CHECK_ONLY=false
BACKUP_BEFORE_DEPLOY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
        --backup)
            BACKUP_BEFORE_DEPLOY=true
            shift
            ;;
        --help)
            echo "HelloAgents Platform 部署脚本"
            echo ""
            echo "使用方法:"
            echo "  $0                    交互式部署"
            echo "  $0 --quick           快速部署(跳过环境检查)"
            echo "  $0 --check           仅检查环境,不部署"
            echo "  $0 --backup          备份后再部署"
            echo "  $0 --help            显示此帮助信息"
            exit 0
            ;;
        *)
            print_error "未知参数: $1"
            echo "使用 $0 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 欢迎信息
print_header "🚀 HelloAgents Platform 部署工具"

# 1. 检查系统环境
check_system() {
    print_info "检查系统环境..."

    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_success "操作系统: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_success "操作系统: macOS"
    else
        print_warning "未识别的操作系统: $OSTYPE"
    fi

    # 检查Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker: $DOCKER_VERSION"
    else
        print_error "Docker 未安装"
        print_info "安装 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f4 | cut -d',' -f1)
        print_success "Docker Compose: $COMPOSE_VERSION"
    else
        print_error "Docker Compose 未安装"
        print_info "安装 Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi

    # 检查Docker守护进程
    if ! docker ps &> /dev/null; then
        print_error "Docker 守护进程未运行"
        print_info "请启动 Docker Desktop 或运行: sudo systemctl start docker"
        exit 1
    fi

    # 检查磁盘空间
    AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
    print_success "可用磁盘空间: $AVAILABLE_SPACE"

    # 检查内存
    if command -v free &> /dev/null; then
        TOTAL_MEM=$(free -h | awk '/^Mem:/ {print $2}')
        AVAILABLE_MEM=$(free -h | awk '/^Mem:/ {print $7}')
        print_success "可用内存: $AVAILABLE_MEM / $TOTAL_MEM"
    fi

    echo ""
}

# 2. 检查环境变量配置
check_env() {
    print_info "检查环境变量配置..."

    # 检查 .env 文件是否存在
    if [ ! -f .env ]; then
        print_error ".env 文件不存在"
        print_info "正在创建 .env 文件..."

        if [ -f .env.example ]; then
            cp .env.example .env
            print_success ".env 文件已创建"
            print_warning "请编辑 .env 文件,设置必需的环境变量:"
            print_warning "  - ANTHROPIC_API_KEY"
            print_warning "  - POSTGRES_PASSWORD"
            echo ""
            read -p "是否现在编辑 .env 文件? (y/n) " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ${EDITOR:-nano} .env
            else
                print_error "请先配置 .env 文件,然后重新运行部署脚本"
                exit 1
            fi
        else
            print_error ".env.example 文件也不存在"
            exit 1
        fi
    fi

    # 检查必需的环境变量
    source .env

    MISSING_VARS=()

    # 检查 API Key
    if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
        MISSING_VARS+=("ANTHROPIC_API_KEY")
    fi

    # 检查数据库密码
    if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "your_secure_password_here" ]; then
        MISSING_VARS+=("POSTGRES_PASSWORD")
    fi

    if [ ${#MISSING_VARS[@]} -ne 0 ]; then
        print_error "以下必需的环境变量未设置:"
        for VAR in "${MISSING_VARS[@]}"; do
            echo "   - $VAR"
        done
        echo ""
        print_info "请编辑 .env 文件并设置这些变量"
        exit 1
    fi

    # 检查密码强度
    if [ ${#POSTGRES_PASSWORD} -lt 12 ]; then
        print_warning "POSTGRES_PASSWORD 太短 (建议至少12位)"
    fi

    print_success "环境变量配置正确"
    echo ""
}

# 3. 检查端口占用
check_ports() {
    print_info "检查端口占用..."

    PORTS=(80 8000 5432 6379)
    PORT_NAMES=("前端" "后端" "PostgreSQL" "Redis")
    OCCUPIED_PORTS=()

    for i in "${!PORTS[@]}"; do
        PORT=${PORTS[$i]}
        NAME=${PORT_NAMES[$i]}

        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "端口 $PORT ($NAME) 已被占用"
            OCCUPIED_PORTS+=("$PORT")
        else
            print_success "端口 $PORT ($NAME) 可用"
        fi
    done

    if [ ${#OCCUPIED_PORTS[@]} -ne 0 ]; then
        echo ""
        read -p "端口已占用,是否停止现有服务并继续? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "部署已取消"
            exit 1
        fi
    fi

    echo ""
}

# 4. 备份数据
backup_data() {
    print_info "备份现有数据..."

    BACKUP_DIR="backups"
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"

    mkdir -p $BACKUP_DIR

    # 备份数据库
    if docker ps | grep -q helloagents-postgres; then
        print_info "备份PostgreSQL数据库..."
        docker exec helloagents-postgres pg_dump -U helloagents helloagents > "$BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sql"
        gzip "$BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sql"
        print_success "数据库备份完成"
    else
        print_info "没有运行中的数据库容器,跳过备份"
    fi

    echo ""
}

# 5. 停止现有服务
stop_services() {
    print_info "停止现有服务..."

    if [ -f docker-compose.yml ]; then
        docker-compose down 2>/dev/null || true
        print_success "服务已停止"
    else
        print_warning "docker-compose.yml 文件不存在"
    fi

    echo ""
}

# 6. 拉取最新代码
pull_code() {
    print_info "检查Git仓库..."

    if [ -d .git ]; then
        CURRENT_BRANCH=$(git branch --show-current)
        print_info "当前分支: $CURRENT_BRANCH"

        # 检查是否有未提交的更改
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            print_warning "检测到未提交的更改"
            read -p "是否暂存并拉取最新代码? (y/n) " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git stash
                git pull origin $CURRENT_BRANCH
                print_success "代码已更新"
            fi
        else
            git pull origin $CURRENT_BRANCH 2>/dev/null || print_info "无法拉取代码(可能没有远程仓库)"
        fi
    else
        print_info "不是Git仓库,跳过代码更新"
    fi

    echo ""
}

# 7. 构建和启动服务
deploy_services() {
    print_info "构建Docker镜像..."
    docker-compose build --no-cache
    print_success "镜像构建完成"

    echo ""
    print_info "启动服务..."
    docker-compose up -d

    echo ""
    print_info "等待服务启动..."
    sleep 10

    # 显示服务状态
    docker-compose ps

    echo ""
}

# 8. 健康检查
health_check() {
    print_info "运行健康检查..."

    MAX_RETRIES=30
    RETRY_COUNT=0

    # 检查后端
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "后端服务: 健康"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
                print_error "后端服务: 启动失败"
                docker-compose logs backend
                exit 1
            fi
            sleep 2
        fi
    done

    # 检查前端
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f http://localhost/ > /dev/null 2>&1; then
            print_success "前端服务: 健康"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
                print_error "前端服务: 启动失败"
                docker-compose logs frontend
                exit 1
            fi
            sleep 2
        fi
    done

    # 检查数据库
    if docker exec helloagents-postgres pg_isready -U helloagents > /dev/null 2>&1; then
        print_success "数据库服务: 健康"
    else
        print_error "数据库服务: 不健康"
    fi

    # 检查Redis
    if docker exec helloagents-redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis服务: 健康"
    else
        print_warning "Redis服务: 不健康"
    fi

    echo ""
}

# 9. 显示部署信息
show_deployment_info() {
    print_header "🎉 部署完成!"

    echo "访问地址:"
    echo "  前端应用:    http://localhost"
    echo "  后端API:     http://localhost:8000"
    echo "  API文档:     http://localhost:8000/docs"
    echo "  ReDoc文档:   http://localhost:8000/redoc"
    echo ""

    echo "常用命令:"
    echo "  查看日志:    docker-compose logs -f"
    echo "  重启服务:    docker-compose restart"
    echo "  停止服务:    docker-compose down"
    echo "  查看状态:    docker-compose ps"
    echo ""

    echo "健康检查:"
    echo "  ./scripts/health-check.sh"
    echo ""

    print_success "部署成功完成! 🚀"
    echo ""
}

# 主流程
main() {
    # 检查系统环境
    if [ "$QUICK_MODE" = false ]; then
        check_system
        check_env
        check_ports
    fi

    # 如果只是检查模式,到这里就结束
    if [ "$CHECK_ONLY" = true ]; then
        print_success "环境检查完成,一切正常!"
        exit 0
    fi

    # 备份
    if [ "$BACKUP_BEFORE_DEPLOY" = true ]; then
        backup_data
    fi

    # 停止现有服务
    stop_services

    # 拉取最新代码
    if [ "$QUICK_MODE" = false ]; then
        pull_code
    fi

    # 部署服务
    deploy_services

    # 健康检查
    health_check

    # 显示部署信息
    show_deployment_info
}

# 运行主流程
main
