#!/bin/bash

###############################################################################
# E2E Test Execution Script
#
# 这个脚本用于执行完整的 E2E 测试套件，并生成测试报告。
#
# 使用方法:
#   ./scripts/run-e2e-tests.sh [选项]
#
# 选项:
#   --headed         在有头模式下运行（显示浏览器）
#   --debug          在调试模式下运行
#   --chromium       只运行 Chromium 测试
#   --firefox        只运行 Firefox 测试
#   --ui             在 UI 模式下运行
#   --help           显示此帮助信息
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认参数
HEADED=""
DEBUG=""
BROWSER=""
UI=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --headed)
      HEADED="--headed"
      shift
      ;;
    --debug)
      DEBUG="--debug"
      shift
      ;;
    --chromium)
      BROWSER="--project=chromium"
      shift
      ;;
    --firefox)
      BROWSER="--project=firefox"
      shift
      ;;
    --ui)
      UI="--ui"
      shift
      ;;
    --help)
      echo "E2E Test Execution Script"
      echo ""
      echo "Usage: ./scripts/run-e2e-tests.sh [options]"
      echo ""
      echo "Options:"
      echo "  --headed         Run in headed mode (show browser)"
      echo "  --debug          Run in debug mode"
      echo "  --chromium       Run only Chromium tests"
      echo "  --firefox        Run only Firefox tests"
      echo "  --ui             Run in UI mode"
      echo "  --help           Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        E2E Test Execution Script              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# 检查依赖
echo -e "${YELLOW}[1/5] Checking dependencies...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js is installed${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm is installed${NC}"

# 检查 Playwright 是否已安装
if [ ! -d "node_modules/@playwright" ]; then
    echo -e "${YELLOW}⚠ Playwright not found, installing...${NC}"
    npm install
fi
echo -e "${GREEN}✓ Playwright is installed${NC}"
echo ""

# 清理旧的测试报告
echo -e "${YELLOW}[2/5] Cleaning old test reports...${NC}"
rm -rf playwright-report test-results
echo -e "${GREEN}✓ Old reports cleaned${NC}"
echo ""

# 检查后端服务是否运行（可选）
echo -e "${YELLOW}[3/5] Checking backend service...${NC}"
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend service is running${NC}"
else
    echo -e "${YELLOW}⚠ Backend service is not running (tests will start dev server)${NC}"
fi
echo ""

# 运行 E2E 测试
echo -e "${YELLOW}[4/5] Running E2E tests...${NC}"
echo ""

TEST_CMD="npx playwright test"

if [ -n "$HEADED" ]; then
    TEST_CMD="$TEST_CMD $HEADED"
    echo -e "${BLUE}Mode: Headed${NC}"
fi

if [ -n "$DEBUG" ]; then
    TEST_CMD="$TEST_CMD $DEBUG"
    echo -e "${BLUE}Mode: Debug${NC}"
fi

if [ -n "$BROWSER" ]; then
    TEST_CMD="$TEST_CMD $BROWSER"
    echo -e "${BLUE}Browser: ${BROWSER#--project=}${NC}"
else
    echo -e "${BLUE}Browser: All (Chromium, Firefox)${NC}"
fi

if [ -n "$UI" ]; then
    TEST_CMD="$TEST_CMD $UI"
    echo -e "${BLUE}Mode: UI${NC}"
fi

echo ""
echo -e "${BLUE}Command: $TEST_CMD${NC}"
echo ""

# 执行测试
if eval $TEST_CMD; then
    echo ""
    echo -e "${GREEN}✓ All E2E tests passed!${NC}"
    TEST_RESULT=0
else
    echo ""
    echo -e "${RED}✗ Some E2E tests failed${NC}"
    TEST_RESULT=1
fi
echo ""

# 生成测试报告
echo -e "${YELLOW}[5/5] Generating test report...${NC}"

if [ -f "playwright-report/index.html" ]; then
    echo -e "${GREEN}✓ Test report generated${NC}"
    echo ""
    echo -e "${BLUE}Report location: playwright-report/index.html${NC}"
    echo ""
    echo -e "${YELLOW}To view the report, run:${NC}"
    echo -e "${BLUE}  npm run test:e2e:report${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠ Test report not found${NC}"
fi

# 显示测试统计
if [ -f "playwright-report/results.json" ]; then
    echo -e "${YELLOW}Test Statistics:${NC}"

    # 使用 node 解析 JSON（跨平台兼容）
    node -e "
    const fs = require('fs');
    const data = JSON.parse(fs.readFileSync('playwright-report/results.json', 'utf8'));
    const suites = data.suites || [];

    let total = 0;
    let passed = 0;
    let failed = 0;
    let skipped = 0;

    function countTests(suite) {
      if (suite.specs) {
        suite.specs.forEach(spec => {
          spec.tests.forEach(test => {
            total++;
            if (test.results[0].status === 'passed') passed++;
            else if (test.results[0].status === 'failed') failed++;
            else if (test.results[0].status === 'skipped') skipped++;
          });
        });
      }
      if (suite.suites) {
        suite.suites.forEach(countTests);
      }
    }

    suites.forEach(countTests);

    console.log('  Total:  ', total);
    console.log('  Passed: ', passed);
    console.log('  Failed: ', failed);
    console.log('  Skipped:', skipped);
    "
    echo ""
fi

# 显示失败的测试截图
if [ -d "playwright-report/screenshots" ] && [ "$(ls -A playwright-report/screenshots)" ]; then
    echo -e "${YELLOW}Failure screenshots saved to:${NC}"
    echo -e "${BLUE}  playwright-report/screenshots/${NC}"
    echo ""
fi

# 总结
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${BLUE}║${GREEN}         All E2E Tests Passed! ✓              ${BLUE}║${NC}"
else
    echo -e "${BLUE}║${RED}         Some E2E Tests Failed ✗              ${BLUE}║${NC}"
fi
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

exit $TEST_RESULT
