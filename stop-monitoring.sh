#!/bin/bash

# ===================================================================
# HelloAgents Platform - 监控系统停止脚本
# ===================================================================

echo "🛑 停止 HelloAgents 监控系统..."
echo "=================================================="

# 1. 停止 Prometheus
if lsof -ti:9090 > /dev/null 2>&1; then
    echo "⏹️  停止 Prometheus..."
    kill $(lsof -ti:9090)
    echo "✅ Prometheus 已停止"
else
    echo "ℹ️  Prometheus 未在运行"
fi

# 2. 停止 Grafana
if brew services list | grep grafana | grep started > /dev/null; then
    echo "⏹️  停止 Grafana..."
    brew services stop grafana
    echo "✅ Grafana 已停止"
else
    echo "ℹ️  Grafana 未在运行"
fi

echo ""
echo "=================================================="
echo "✅ 监控系统已停止"
echo "=================================================="
