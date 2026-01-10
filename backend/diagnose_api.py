#!/usr/bin/env python3
"""
后端API诊断工具
检测路由问题、端点可用性、响应格式等
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_routes():
    """分析所有注册的路由"""
    from app.main import app
    from fastapi.routing import APIRoute

    print("\n" + "=" * 80)
    print("1. 路由注册分析")
    print("=" * 80)

    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ','.join(sorted(route.methods))
            routes.append({
                'methods': methods,
                'path': route.path,
                'name': route.name,
                'tags': list(route.tags) if route.tags else []
            })

    # 按路径排序
    routes.sort(key=lambda x: x['path'])

    print(f"\n总计注册路由: {len(routes)}\n")

    # 按标签分组
    by_tag = {}
    for route in routes:
        tags = route['tags'] if route['tags'] else ['其他']
        for tag in tags:
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(route)

    for tag, tag_routes in sorted(by_tag.items()):
        print(f"\n[{tag}] - {len(tag_routes)} 个端点")
        print("-" * 80)
        for route in tag_routes:
            print(f"  {route['methods']:10} {route['path']}")

    return routes

def test_critical_endpoints():
    """测试关键API端点"""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    print("\n" + "=" * 80)
    print("2. 关键端点测试")
    print("=" * 80)

    test_cases = [
        # 健康检查
        ("GET", "/", "根端点"),
        ("GET", "/health", "健康检查"),
        ("GET", "/health/ready", "就绪检查"),
        ("GET", "/health/live", "存活检查"),

        # API v1 - 课程
        ("GET", "/api/v1/lessons", "获取课程列表 (v1)"),
        ("GET", "/api/v1/lessons/", "获取课程列表 (v1, 带斜杠)"),
        ("GET", "/api/v1/lessons/1", "获取课程详情 (v1)"),

        # API v1 - 代码执行
        ("POST", "/api/v1/code/execute", "代码执行 (v1)", {
            "code": "print('Hello, World!')",
            "language": "python"
        }),

        # API v1 - AI 聊天
        ("POST", "/api/v1/chat", "AI 聊天 (v1)", {
            "message": "Hello"
        }),

        # 向后兼容端点
        ("GET", "/api/lessons", "获取课程列表 (旧版)"),
        ("GET", "/api/lessons/1", "获取课程详情 (旧版)"),
        ("POST", "/api/execute", "代码执行 (旧版)", {
            "code": "print('Test')",
            "language": "python"
        }),

        # 用户端点
        ("GET", "/api/users/current", "获取当前用户"),

        # 沙箱统计
        ("GET", "/api/sandbox/pool/stats", "容器池统计"),
    ]

    results = []

    for test_case in test_cases:
        method = test_case[0]
        path = test_case[1]
        description = test_case[2]
        data = test_case[3] if len(test_case) > 3 else None

        try:
            if method == "GET":
                response = client.get(path)
            elif method == "POST":
                response = client.post(path, json=data)
            else:
                response = None

            success = response.status_code < 400
            result = {
                'method': method,
                'path': path,
                'description': description,
                'status_code': response.status_code,
                'success': success,
                'error': None if success else response.text[:200]
            }

            # 显示结果
            status_icon = "✅" if success else "❌"
            print(f"\n{status_icon} {description}")
            print(f"   {method} {path} -> {response.status_code}")

            if not success:
                print(f"   错误: {response.text[:100]}")
            elif response.status_code == 200:
                try:
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        keys = list(json_data.keys())[:5]
                        print(f"   返回字段: {', '.join(keys)}")
                except:
                    pass

        except Exception as e:
            result = {
                'method': method,
                'path': path,
                'description': description,
                'status_code': None,
                'success': False,
                'error': str(e)
            }
            print(f"\n❌ {description}")
            print(f"   {method} {path} -> 异常: {str(e)}")

        results.append(result)

    return results

def check_route_conflicts():
    """检查路由冲突"""
    from app.main import app
    from fastapi.routing import APIRoute

    print("\n" + "=" * 80)
    print("3. 路由冲突检测")
    print("=" * 80)

    routes_by_path = {}
    conflicts = []

    for route in app.routes:
        if isinstance(route, APIRoute):
            path = route.path
            methods = route.methods

            if path not in routes_by_path:
                routes_by_path[path] = []

            routes_by_path[path].append({
                'methods': methods,
                'name': route.name,
                'tags': list(route.tags) if route.tags else []
            })

    # 检查冲突
    for path, path_routes in routes_by_path.items():
        if len(path_routes) > 1:
            # 检查是否有方法冲突
            all_methods = set()
            for r in path_routes:
                for method in r['methods']:
                    if method in all_methods:
                        conflicts.append({
                            'path': path,
                            'method': method,
                            'routes': path_routes
                        })
                    all_methods.add(method)

    if conflicts:
        print(f"\n⚠️  发现 {len(conflicts)} 个路由冲突:\n")
        for conflict in conflicts:
            print(f"路径: {conflict['path']}")
            print(f"方法: {conflict['method']}")
            print("冲突的路由:")
            for r in conflict['routes']:
                print(f"  - {r['name']} ({','.join(r['methods'])}) [{','.join(r['tags'])}]")
            print()
    else:
        print("\n✅ 未发现路由冲突")

    return conflicts

def check_middleware_order():
    """检查中间件顺序"""
    from app.main import app

    print("\n" + "=" * 80)
    print("4. 中间件顺序检查")
    print("=" * 80)

    print("\n注册的中间件 (执行顺序从下往上):\n")

    middleware_stack = []
    current = app

    # 遍历中间件栈
    while hasattr(current, 'app'):
        middleware_name = type(current).__name__
        if middleware_name != 'FastAPI':
            middleware_stack.append(middleware_name)
        current = current.app
        if current == app:
            break

    for i, mw in enumerate(reversed(middleware_stack)):
        print(f"{i+1}. {mw}")

    return middleware_stack

def generate_report(routes, test_results, conflicts, middleware_stack):
    """生成诊断报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_routes': len(routes),
            'test_cases': len(test_results),
            'passed_tests': sum(1 for r in test_results if r['success']),
            'failed_tests': sum(1 for r in test_results if not r['success']),
            'route_conflicts': len(conflicts),
            'middleware_count': len(middleware_stack)
        },
        'routes': routes,
        'test_results': test_results,
        'conflicts': conflicts,
        'middleware_stack': middleware_stack
    }

    # 保存 JSON 报告
    report_path = 'api_diagnostic_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("5. 诊断摘要")
    print("=" * 80)

    print(f"\n总计路由: {report['summary']['total_routes']}")
    print(f"测试用例: {report['summary']['test_cases']}")
    print(f"  ✅ 通过: {report['summary']['passed_tests']}")
    print(f"  ❌ 失败: {report['summary']['failed_tests']}")
    print(f"路由冲突: {report['summary']['route_conflicts']}")
    print(f"中间件数: {report['summary']['middleware_count']}")

    print(f"\n详细报告已保存至: {report_path}")

    return report

def main():
    print("=" * 80)
    print("HelloAgents Platform - API 诊断工具")
    print("=" * 80)

    try:
        # 1. 分析路由
        routes = analyze_routes()

        # 2. 测试关键端点
        test_results = test_critical_endpoints()

        # 3. 检查路由冲突
        conflicts = check_route_conflicts()

        # 4. 检查中间件顺序
        middleware_stack = check_middleware_order()

        # 5. 生成报告
        report = generate_report(routes, test_results, conflicts, middleware_stack)

        # 6. 返回状态码
        if report['summary']['failed_tests'] > 0 or report['summary']['route_conflicts'] > 0:
            print("\n⚠️  发现问题，请查看报告详情")
            sys.exit(1)
        else:
            print("\n✅ 所有检查通过")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ 诊断失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
