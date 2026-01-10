#!/bin/bash

# ===================================================================
# HelloAgents Platform - 监控系统启动脚本
# ===================================================================

set -e

PROJECT_DIR="/Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform"
PROMETHEUS_CONFIG="$PROJECT_DIR/prometheus-local.yml"
PROMETHEUS_DATA="/tmp/prometheus-data"
PROMETHEUS_LOG="/tmp/prometheus.log"

echo "🚀 启动 HelloAgents 监控系统..."
echo "=================================================="

# 1. 检查 Prometheus 配置文件
if [ ! -f "$PROMETHEUS_CONFIG" ]; then
    echo "❌ 配置文件不存在: $PROMETHEUS_CONFIG"
    exit 1
fi
echo "✅ Prometheus 配置文件: $PROMETHEUS_CONFIG"

# 2. 创建数据目录
mkdir -p "$PROMETHEUS_DATA"
echo "✅ 数据目录: $PROMETHEUS_DATA"

# 3. 停止已运行的 Prometheus (如果存在)
if lsof -ti:9090 > /dev/null 2>&1; then
    echo "⚠️  停止已运行的 Prometheus..."
    kill $(lsof -ti:9090) 2>/dev/null || true
    sleep 2
fi

# 4. 启动 Prometheus
echo "🚀 启动 Prometheus..."
nohup prometheus \
    --config.file="$PROMETHEUS_CONFIG" \
    --storage.tsdb.path="$PROMETHEUS_DATA" \
    --web.listen-address=:9090 \
    > "$PROMETHEUS_LOG" 2>&1 &

PROMETHEUS_PID=$!
sleep 3

# 验证 Prometheus 启动
if lsof -ti:9090 > /dev/null 2>&1; then
    echo "✅ Prometheus 已启动 (PID: $PROMETHEUS_PID)"
    echo "   访问地址: http://localhost:9090"
    echo "   日志文件: $PROMETHEUS_LOG"
else
    echo "❌ Prometheus 启动失败，查看日志: $PROMETHEUS_LOG"
    tail -20 "$PROMETHEUS_LOG"
    exit 1
fi

# 5. 启动 Grafana
echo ""
echo "🚀 启动 Grafana..."
if brew services list | grep grafana | grep started > /dev/null; then
    echo "✅ Grafana 已在运行"
else
    brew services start grafana
    echo "✅ Grafana 已启动"
fi
echo "   访问地址: http://localhost:3000"
echo "   默认账号: admin / admin"

# 6. 总结
echo ""
echo "=================================================="
echo "🎉 监控系统启动完成！"
echo "=================================================="
echo ""
echo "📊 监控服务访问地址:"
echo "   - Prometheus:  http://localhost:9090"
echo "   - Grafana:     http://localhost:3000 (admin/admin)"
echo ""
echo "📝 后续步骤:"
echo "   1. 启动后端服务: cd backend && uvicorn app.main:app --reload"
echo "   2. 访问 Prometheus 查看目标: http://localhost:9090/targets"
echo "   3. 访问后端指标端点: http://localhost:8000/metrics"
echo "   4. 登录 Grafana 配置数据源和仪表板"
echo ""
echo "🛑 停止监控系统:"
echo "   ./stop-monitoring.sh"
echo ""
