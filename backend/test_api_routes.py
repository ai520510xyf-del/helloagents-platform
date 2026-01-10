#!/usr/bin/env python3
"""
测试后端API路由
验证所有关键端点是否正确注册
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoints():
    """测试健康检查端点"""
    print("\n=== 健康检查端点 ===")

    # 测试根端点
    response = client.get("/")
    print(f"GET /: {response.status_code}")

    # 测试健康检查
    response = client.get("/health")
    print(f"GET /health: {response.status_code}")

    # 测试就绪检查
    response = client.get("/health/ready")
    print(f"GET /health/ready: {response.status_code}")

    # 测试存活检查
    response = client.get("/health/live")
    print(f"GET /health/live: {response.status_code}")

def test_api_v1_endpoints():
    """测试 API v1 端点"""
    print("\n=== API v1 端点 ===")

    # 测试课程列表
    response = client.get("/api/v1/lessons")
    print(f"GET /api/v1/lessons: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - 返回课程数量: {len(data.get('lessons', []))}")
    else:
        print(f"  - 错误: {response.text}")

    # 测试课程列表 (带斜杠)
    response = client.get("/api/v1/lessons/")
    print(f"GET /api/v1/lessons/: {response.status_code}")

    # 测试获取特定课程
    response = client.get("/api/v1/lessons/1")
    print(f"GET /api/v1/lessons/1: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - 课程标题: {data.get('title')}")
    else:
        print(f"  - 错误: {response.text}")

    # 测试代码执行
    response = client.post("/api/v1/code/execute", json={
        "code": "print('Hello, World!')",
        "language": "python"
    })
    print(f"POST /api/v1/code/execute: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - 执行成功: {data.get('success')}")
        print(f"  - 输出: {data.get('output', '')[:50]}")
    else:
        print(f"  - 错误: {response.text}")

    # 测试 AI 聊天 (需要 API key)
    response = client.post("/api/v1/chat", json={
        "message": "Hello"
    })
    print(f"POST /api/v1/chat: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - 成功: {data.get('success')}")
    else:
        print(f"  - 错误: {response.text[:100]}")

def test_backward_compat_endpoints():
    """测试向后兼容端点"""
    print("\n=== 向后兼容端点 ===")

    # 测试旧版课程列表
    response = client.get("/api/lessons")
    print(f"GET /api/lessons: {response.status_code}")

    # 测试旧版课程详情
    response = client.get("/api/lessons/1")
    print(f"GET /api/lessons/1: {response.status_code}")

    # 测试旧版代码执行
    response = client.post("/api/execute", json={
        "code": "print('Test')",
        "language": "python"
    })
    print(f"POST /api/execute: {response.status_code}")

def list_all_routes():
    """列出所有注册的路由"""
    print("\n=== 所有注册路由 ===")
    from fastapi.routing import APIRoute

    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ','.join(sorted(route.methods))
            routes.append((methods, route.path))

    # 按路径排序
    routes.sort(key=lambda x: x[1])

    for methods, path in routes:
        print(f"{methods:10} {path}")

if __name__ == "__main__":
    print("=" * 60)
    print("HelloAgents Platform - API 路由测试")
    print("=" * 60)

    try:
        list_all_routes()
        test_health_endpoints()
        test_api_v1_endpoints()
        test_backward_compat_endpoints()

        print("\n" + "=" * 60)
        print("✅ API 路由测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
