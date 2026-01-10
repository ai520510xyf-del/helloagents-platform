#!/bin/bash

# ===================================================================
# HelloAgents Platform - 监控系统测试脚本
# ===================================================================

set -e

echo "🧪 测试 HelloAgents 监控系统..."
echo "=================================================="

# 1. 测试 Prometheus
echo ""
echo "1️⃣ 测试 Prometheus..."
PROM_STATUS=$(curl -s http://localhost:9090/-/healthy)
if [ "$PROM_STATUS" == "Prometheus Server is Healthy." ]; then
    echo "✅ Prometheus 运行正常"
else
    echo "❌ Prometheus 健康检查失败"
    exit 1
fi

# 2. 测试 Grafana
echo ""
echo "2️⃣ 测试 Grafana..."
if curl -s http://localhost:3000/api/health | grep -q 'database.*ok'; then
    echo "✅ Grafana 运行正常"
else
    echo "❌ Grafana 健康检查失败"
    exit 1
fi

# 3. 检查后端服务（如果运行）
echo ""
echo "3️⃣ 检查后端服务..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行中"

    # 测试 metrics 端点
    echo "   检查 /metrics 端点..."
    METRICS=$(curl -s http://localhost:8000/metrics)

    if echo "$METRICS" | grep -q "http_requests_total"; then
        echo "✅ 后端指标正常导出"
    else
        echo "⚠️  后端指标端点存在但数据不完整"
    fi
else
    echo "⚠️  后端服务未运行 (这是正常的，如果您还没启动后端)"
    echo "   启动后端: cd backend && uvicorn app.main:app --reload"
fi

# 4. 检查 Prometheus 目标
echo ""
echo "4️⃣ 检查 Prometheus 抓取目标..."
TARGETS=$(curl -s http://localhost:9090/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
for target in data['data']['activeTargets']:
    job = target['labels']['job']
    health = target['health']
    print(f'{job}: {health}')
" 2>/dev/null)

if [ -n "$TARGETS" ]; then
    echo "$TARGETS" | while read line; do
        JOB=$(echo "$line" | cut -d: -f1)
        STATUS=$(echo "$line" | cut -d: -f2 | xargs)

        if [ "$STATUS" == "up" ]; then
            echo "   ✅ $JOB: UP"
        else
            echo "   ⚠️  $JOB: $STATUS"
        fi
    done
else
    echo "   ⚠️  无法获取目标状态"
fi

# 5. 生成测试流量（如果后端运行）
echo ""
echo "5️⃣ 生成测试流量..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   发送 10 个测试请求..."
    for i in {1..10}; do
        curl -s http://localhost:8000/ > /dev/null
        curl -s http://localhost:8000/health > /dev/null
    done
    echo "✅ 测试流量已生成"

    # 等待指标更新
    sleep 2

    # 查询指标
    echo ""
    echo "   查询 Prometheus 指标..."
    QUERY='sum(rate(http_requests_total[1m]))'
    RESULT=$(curl -s "http://localhost:9090/api/v1/query?query=$QUERY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data['status'] == 'success' and data['data']['result']:
    value = data['data']['result'][0]['value'][1]
    print(f'请求速率: {float(value):.2f} req/s')
else:
    print('暂无数据')
" 2>/dev/null)

    echo "   $RESULT"
fi

# 6. 总结
echo ""
echo "=================================================="
echo "✅ 监控系统测试完成！"
echo "=================================================="
echo ""
echo "📊 快速访问:"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana:    http://localhost:3000"
echo "   - Backend:    http://localhost:8000/metrics"
echo ""
echo "📝 下一步:"
echo "   1. 如果后端未运行，启动: cd backend && uvicorn app.main:app --reload"
echo "   2. 登录 Grafana (admin/admin) 配置数据源"
echo "   3. 导入仪表板: monitoring/grafana/dashboards/helloagents-overview.json"
echo ""
