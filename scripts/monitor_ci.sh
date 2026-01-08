#!/bin/bash

# CI 监控脚本 - GitHub Actions 状态检查
# 用于监控多个工作流的运行状态

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
REPO_OWNER=${GITHUB_REPO_OWNER:-"your-org"}
REPO_NAME=${GITHUB_REPO_NAME:-"helloagents-platform"}
BRANCH=${GITHUB_BRANCH:-"develop"}

# 工作流列表
WORKFLOWS=("ci.yml" "docker-build.yml" "e2e-tests.yml")

echo "========================================="
echo "  CI 监控脚本"
echo "  Repository: $REPO_OWNER/$REPO_NAME"
echo "  Branch: $BRANCH"
echo "========================================="
echo ""

# 检查 GitHub CLI 是否安装
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) 未安装${NC}"
    echo "安装方法: brew install gh"
    exit 1
fi

# 检查认证状态
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI 未认证${NC}"
    echo "请先运行: gh auth login"
    exit 1
fi

echo -e "${BLUE}📊 正在检查工作流状态...${NC}\n"

# 总体统计
TOTAL_WORKFLOWS=0
SUCCESS_WORKFLOWS=0
FAILED_WORKFLOWS=0
PENDING_WORKFLOWS=0

# 遍历每个工作流
for workflow in "${WORKFLOWS[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}工作流: $workflow${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    TOTAL_WORKFLOWS=$((TOTAL_WORKFLOWS + 1))

    # 获取最新运行状态
    RUN_INFO=$(gh run list --workflow="$workflow" --branch="$BRANCH" --limit=1 --json status,conclusion,databaseId,createdAt,displayTitle 2>/dev/null || echo "[]")

    if [ "$RUN_INFO" == "[]" ]; then
        echo -e "${YELLOW}⚠️  未找到运行记录${NC}\n"
        continue
    fi

    # 解析状态
    STATUS=$(echo "$RUN_INFO" | jq -r '.[0].status')
    CONCLUSION=$(echo "$RUN_INFO" | jq -r '.[0].conclusion')
    RUN_ID=$(echo "$RUN_INFO" | jq -r '.[0].databaseId')
    CREATED_AT=$(echo "$RUN_INFO" | jq -r '.[0].createdAt')
    TITLE=$(echo "$RUN_INFO" | jq -r '.[0].displayTitle')

    echo "运行 ID: $RUN_ID"
    echo "标题: $TITLE"
    echo "创建时间: $CREATED_AT"

    # 显示状态
    if [ "$STATUS" == "completed" ]; then
        if [ "$CONCLUSION" == "success" ]; then
            echo -e "状态: ${GREEN}✅ SUCCESS${NC}"
            SUCCESS_WORKFLOWS=$((SUCCESS_WORKFLOWS + 1))
        elif [ "$CONCLUSION" == "failure" ]; then
            echo -e "状态: ${RED}❌ FAILURE${NC}"
            FAILED_WORKFLOWS=$((FAILED_WORKFLOWS + 1))

            # 获取失败的 jobs
            echo -e "\n${RED}失败的 Jobs:${NC}"
            FAILED_JOBS=$(gh run view "$RUN_ID" --json jobs --jq '.jobs[] | select(.conclusion == "failure") | {name: .name, conclusion: .conclusion}')

            if [ -n "$FAILED_JOBS" ]; then
                echo "$FAILED_JOBS" | jq -r '"  - " + .name'

                # 获取错误日志（简化版）
                echo -e "\n${RED}错误日志预览:${NC}"
                gh run view "$RUN_ID" --log-failed | head -n 20
            fi
        else
            echo -e "状态: ${YELLOW}⚠️  $CONCLUSION${NC}"
        fi
    elif [ "$STATUS" == "in_progress" ]; then
        echo -e "状态: ${YELLOW}⏳ IN PROGRESS${NC}"
        PENDING_WORKFLOWS=$((PENDING_WORKFLOWS + 1))
    else
        echo -e "状态: ${YELLOW}⏸  $STATUS${NC}"
        PENDING_WORKFLOWS=$((PENDING_WORKFLOWS + 1))
    fi

    echo ""
done

# 显示总体统计
echo "========================================="
echo "  总体统计"
echo "========================================="
echo -e "总工作流数: ${BLUE}$TOTAL_WORKFLOWS${NC}"
echo -e "成功: ${GREEN}$SUCCESS_WORKFLOWS${NC}"
echo -e "失败: ${RED}$FAILED_WORKFLOWS${NC}"
echo -e "进行中/待处理: ${YELLOW}$PENDING_WORKFLOWS${NC}"
echo ""

# 计算通过率
if [ $TOTAL_WORKFLOWS -gt 0 ]; then
    PASS_RATE=$((SUCCESS_WORKFLOWS * 100 / TOTAL_WORKFLOWS))
    echo -e "通过率: ${BLUE}${PASS_RATE}%${NC}"
    echo ""
fi

# 返回状态码
if [ $FAILED_WORKFLOWS -gt 0 ]; then
    echo -e "${RED}❌ 有工作流失败，需要修复！${NC}"
    exit 1
elif [ $PENDING_WORKFLOWS -gt 0 ]; then
    echo -e "${YELLOW}⏳ 有工作流仍在运行中...${NC}"
    exit 0
else
    echo -e "${GREEN}✅ 所有工作流运行成功！${NC}"
    exit 0
fi
