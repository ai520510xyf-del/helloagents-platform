"""
API 版本控制测试脚本

测试所有 v1 端点和向后兼容性
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_test_result(test_name: str, success: bool, details: str = ""):
    """打印测试结果"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")


def test_api_version_endpoint():
    """测试版本信息端点"""
    print("\n" + "=" * 60)
    print("测试 1: API 版本信息端点")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/version")
        success = response.status_code == 200

        if success:
            data = response.json()
            print(f"当前版本: {data.get('current_version')}")
            print(f"支持的版本: {data.get('supported_versions')}")
            print(f"已弃用的版本: {data.get('deprecated_versions')}")

            # 检查必要字段
            required_fields = ['current_version', 'supported_versions', 'latest_version', 'version_info']
            all_present = all(field in data for field in required_fields)

            print_test_result("版本信息端点", all_present)
            return all_present
        else:
            print_test_result("版本信息端点", False, f"状态码: {response.status_code}")
            return False

    except Exception as e:
        print_test_result("版本信息端点", False, str(e))
        return False


def test_version_headers():
    """测试版本响应头"""
    print("\n" + "=" * 60)
    print("测试 2: API 版本响应头")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/health")
        headers = response.headers

        has_version_header = "X-API-Version" in headers
        has_supported_header = "X-Supported-Versions" in headers

        if has_version_header:
            print(f"X-API-Version: {headers['X-API-Version']}")
        if has_supported_header:
            print(f"X-Supported-Versions: {headers['X-Supported-Versions']}")

        success = has_version_header and has_supported_header
        print_test_result("版本响应头", success)
        return success

    except Exception as e:
        print_test_result("版本响应头", False, str(e))
        return False


def test_v1_lessons_list():
    """测试 v1 课程列表端点"""
    print("\n" + "=" * 60)
    print("测试 3: v1 课程列表端点")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/v1/lessons")
        success = response.status_code == 200

        if success:
            data = response.json()
            print(f"成功获取: {len(data.get('lessons', []))} 个课程")

        print_test_result("v1 课程列表", success)
        return success

    except Exception as e:
        print_test_result("v1 课程列表", False, str(e))
        return False


def test_v1_sandbox_stats():
    """测试 v1 沙箱统计端点"""
    print("\n" + "=" * 60)
    print("测试 4: v1 沙箱统计端点")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/v1/sandbox/pool/stats")
        success = response.status_code == 200

        if success:
            data = response.json()
            print(f"容器池状态: {'启用' if data.get('pool_enabled') else '未启用'}")

        print_test_result("v1 沙箱统计", success)
        return success

    except Exception as e:
        print_test_result("v1 沙箱统计", False, str(e))
        return False


def test_v1_code_execution():
    """测试 v1 代码执行端点"""
    print("\n" + "=" * 60)
    print("测试 5: v1 代码执行端点")
    print("=" * 60)

    try:
        test_code = """
print("Hello, HelloAgents!")
result = 1 + 1
print(f"1 + 1 = {result}")
"""

        response = requests.post(
            f"{BASE_URL}/api/v1/code/execute",
            json={
                "code": test_code,
                "language": "python",
                "timeout": 30
            }
        )

        success = response.status_code == 200

        if success:
            data = response.json()
            print(f"执行成功: {data.get('success')}")
            if data.get('success'):
                print(f"输出: {data.get('output', '').strip()}")
            else:
                print(f"错误: {data.get('error', '').strip()}")

        print_test_result("v1 代码执行", success)
        return success

    except Exception as e:
        print_test_result("v1 代码执行", False, str(e))
        return False


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 60)
    print("测试 6: 向后兼容性")
    print("=" * 60)

    tests = [
        ("/api/lessons", "课程列表"),
        ("/api/sandbox/pool/stats", "沙箱统计"),
    ]

    all_success = True

    for endpoint, name in tests:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            success = response.status_code == 200
            all_success = all_success and success

            print_test_result(f"向后兼容: {name}", success)

        except Exception as e:
            print_test_result(f"向后兼容: {name}", False, str(e))
            all_success = False

    return all_success


def test_openapi_docs():
    """测试 OpenAPI 文档"""
    print("\n" + "=" * 60)
    print("测试 7: OpenAPI 文档")
    print("=" * 60)

    try:
        # 测试 OpenAPI JSON
        response = requests.get(f"{BASE_URL}/api/v1/openapi.json")
        success = response.status_code == 200

        if success:
            data = response.json()
            print(f"API 标题: {data.get('info', {}).get('title')}")
            print(f"API 版本: {data.get('info', {}).get('version')}")
            print(f"端点数量: {len(data.get('paths', {}))}")

        print_test_result("OpenAPI 文档", success)
        return success

    except Exception as e:
        print_test_result("OpenAPI 文档", False, str(e))
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("HelloAgents API 版本控制测试")
    print("=" * 60)
    print(f"测试目标: {BASE_URL}")

    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n❌ 错误: 服务器未运行或健康检查失败")
            print("请先启动后端服务: cd backend && uvicorn app.main:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("请先启动后端服务: cd backend && uvicorn app.main:app --reload")
        return
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return

    print("✅ 服务器运行正常\n")

    # 运行测试
    results = []
    results.append(test_api_version_endpoint())
    results.append(test_version_headers())
    results.append(test_v1_lessons_list())
    results.append(test_v1_sandbox_stats())
    results.append(test_v1_code_execution())
    results.append(test_backward_compatibility())
    results.append(test_openapi_docs())

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"总计: {total} 个测试")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")

    if passed == total:
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n⚠️  {failed} 个测试失败，请检查日志")


if __name__ == "__main__":
    main()
