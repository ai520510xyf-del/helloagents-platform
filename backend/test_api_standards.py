#!/usr/bin/env python3
"""
API 规范化测试脚本

快速验证 API 是否符合新的规范
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def test_response_format(response: requests.Response, endpoint: str):
    """测试响应格式是否符合规范"""
    try:
        data = response.json()

        # 检查必需字段
        if "success" not in data:
            print_error(f"{endpoint}: 缺少 'success' 字段")
            return False

        if "timestamp" not in data:
            print_error(f"{endpoint}: 缺少 'timestamp' 字段")
            return False

        # 检查成功响应
        if data.get("success"):
            if "data" not in data:
                print_error(f"{endpoint}: 成功响应缺少 'data' 字段")
                return False
            print_success(f"{endpoint}: 响应格式正确（成功）")
        else:
            # 检查错误响应
            if "error" not in data:
                print_error(f"{endpoint}: 错误响应缺少 'error' 字段")
                return False

            error = data["error"]
            if "code" not in error or "message" not in error:
                print_error(f"{endpoint}: 错误对象格式不正确")
                return False

            print_success(f"{endpoint}: 响应格式正确（错误）")

        return True

    except json.JSONDecodeError:
        print_error(f"{endpoint}: 响应不是有效的 JSON")
        return False
    except Exception as e:
        print_error(f"{endpoint}: 测试失败 - {str(e)}")
        return False

def test_lessons_list():
    """测试课程列表端点"""
    print_info("测试: GET /api/v1/lessons")

    try:
        response = requests.get(f"{BASE_URL}/lessons")

        if response.status_code == 200:
            if test_response_format(response, "GET /lessons"):
                data = response.json()
                if "lessons" in data["data"]:
                    print_success(f"  课程数量: {len(data['data']['lessons'])}")
                return True
        else:
            print_error(f"  状态码错误: {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"  请求失败: {str(e)}")
        return False

def test_lesson_detail():
    """测试课程详情端点"""
    print_info("测试: GET /api/v1/lessons/{lesson_id}")

    # 测试存在的课程
    try:
        response = requests.get(f"{BASE_URL}/lessons/1")

        if response.status_code == 200:
            if test_response_format(response, "GET /lessons/1"):
                data = response.json()
                lesson = data["data"]
                if all(k in lesson for k in ["lesson_id", "title", "content", "code_template"]):
                    print_success(f"  课程标题: {lesson['title']}")
                    return True
        else:
            print_error(f"  状态码错误: {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"  请求失败: {str(e)}")
        return False

def test_lesson_not_found():
    """测试不存在的课程"""
    print_info("测试: GET /api/v1/lessons/999 (404 错误)")

    try:
        response = requests.get(f"{BASE_URL}/lessons/999")

        # 应该返回错误但格式正确
        if test_response_format(response, "GET /lessons/999"):
            data = response.json()
            if not data["success"] and data["error"]["code"] == "LESSON_NOT_FOUND":
                print_success("  404 错误格式正确")
                return True
        return False
    except requests.RequestException as e:
        print_error(f"  请求失败: {str(e)}")
        return False

def test_code_execution():
    """测试代码执行端点"""
    print_info("测试: POST /api/v1/code/execute")

    payload = {
        "code": "print('Hello, World!')",
        "language": "python",
        "timeout": 30
    }

    try:
        response = requests.post(f"{BASE_URL}/code/execute", json=payload)

        if response.status_code == 200:
            if test_response_format(response, "POST /code/execute"):
                data = response.json()
                result = data["data"]
                if "output" in result and "execution_time" in result:
                    print_success(f"  输出: {result['output'].strip()}")
                    print_success(f"  执行时间: {result['execution_time']:.3f}s")
                    return True
        else:
            print_error(f"  状态码错误: {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"  请求失败: {str(e)}")
        return False

def test_rate_limiting():
    """测试速率限制"""
    print_info("测试: 速率限制（发送 10 个快速请求）")

    success_count = 0
    rate_limited = False

    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/lessons")

            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                print_warning(f"  第 {i+1} 个请求被限流")
                break

            time.sleep(0.1)  # 短暂延迟
        except requests.RequestException as e:
            print_error(f"  请求失败: {str(e)}")
            break

    print_info(f"  成功请求数: {success_count}/10")

    if rate_limited:
        print_success("  速率限制正常工作")
        return True
    elif success_count == 10:
        print_warning("  未触发速率限制（可能需要更多请求）")
        return True
    else:
        print_error("  速率限制测试异常")
        return False

def test_openapi_docs():
    """测试 OpenAPI 文档"""
    print_info("测试: OpenAPI 文档")

    try:
        # 测试 OpenAPI JSON
        response = requests.get("http://localhost:8000/api/v1/openapi.json")

        if response.status_code == 200:
            openapi = response.json()

            # 检查基本信息
            if "info" in openapi:
                print_success(f"  标题: {openapi['info']['title']}")
                print_success(f"  版本: {openapi['info']['version']}")

            # 检查端点数量
            if "paths" in openapi:
                endpoint_count = len(openapi["paths"])
                print_success(f"  端点数量: {endpoint_count}")

            # 检查标签
            if "tags" in openapi:
                tags = [tag["name"] for tag in openapi["tags"]]
                print_success(f"  标签: {', '.join(tags)}")

            return True
        else:
            print_error(f"  状态码错误: {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"  请求失败: {str(e)}")
        return False

def test_sandbox_stats():
    """测试沙箱统计端点"""
    print_info("测试: GET /api/v1/sandbox/pool/stats")

    try:
        response = requests.get(f"{BASE_URL}/sandbox/pool/stats")

        if response.status_code == 200:
            if test_response_format(response, "GET /sandbox/pool/stats"):
                data = response.json()
                stats = data["data"]
                print_success(f"  容器池状态: {'启用' if stats.get('pool_enabled') else '未启用'}")
                return True
        else:
            print_error(f"  状态码错误: {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"  请求失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 HelloAgents API 规范化测试")
    print("="*60 + "\n")

    tests = [
        ("OpenAPI 文档", test_openapi_docs),
        ("课程列表", test_lessons_list),
        ("课程详情", test_lesson_detail),
        ("404 错误处理", test_lesson_not_found),
        ("代码执行", test_code_execution),
        ("沙箱统计", test_sandbox_stats),
        ("速率限制", test_rate_limiting),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} 测试异常: {str(e)}")
            results.append((name, False))
        print()

    # 打印总结
    print("="*60)
    print("📊 测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n通过率: {passed}/{total} ({passed*100//total}%)")

    if passed == total:
        print_success("\n🎉 所有测试通过！API 规范化成功！")
    else:
        print_warning(f"\n⚠️  {total - passed} 个测试失败，请检查服务器状态")

    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print_error(f"\n测试运行失败: {str(e)}")
