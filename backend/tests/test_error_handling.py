"""
错误处理测试模块

测试统一错误处理机制，包括自定义异常、错误中间件和错误响应格式
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 导入应用
from app.main import app

# 导入异常类
from app.exceptions import (
    HelloAgentsException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    RateLimitError,
    SandboxExecutionError,
    ContainerPoolError,
    DatabaseError,
    ExternalServiceError,
    TimeoutError,
)

# 导入错误代码
from app import error_codes


# ============================================
# 测试夹具
# ============================================

@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


# ============================================
# 异常类测试
# ============================================

def test_helloagents_exception():
    """测试基础异常类"""
    exc = HelloAgentsException(
        message="Test error",
        code="TEST_ERROR",
        status_code=500,
        details={"key": "value"}
    )

    assert exc.message == "Test error"
    assert exc.code == "TEST_ERROR"
    assert exc.status_code == 500
    assert exc.details == {"key": "value"}

    # 测试 to_dict 方法
    exc_dict = exc.to_dict()
    assert exc_dict["code"] == "TEST_ERROR"
    assert exc_dict["message"] == "Test error"
    assert exc_dict["details"]["key"] == "value"


def test_validation_error():
    """测试验证错误"""
    exc = ValidationError(
        message="Invalid input",
        field="username"
    )

    assert exc.message == "Invalid input"
    assert exc.code == "VALIDATION_ERROR"
    assert exc.status_code == 400
    assert exc.details["field"] == "username"


def test_authentication_error():
    """测试认证错误"""
    exc = AuthenticationError(message="Invalid credentials")

    assert exc.message == "Invalid credentials"
    assert exc.code == "AUTHENTICATION_ERROR"
    assert exc.status_code == 401


def test_authorization_error():
    """测试授权错误"""
    exc = AuthorizationError(
        message="Access denied",
        resource="lesson"
    )

    assert exc.message == "Access denied"
    assert exc.code == "AUTHORIZATION_ERROR"
    assert exc.status_code == 403
    assert exc.details["resource"] == "lesson"


def test_resource_not_found_error():
    """测试资源未找到错误"""
    exc = ResourceNotFoundError(
        resource="User",
        resource_id="123"
    )

    assert "User not found: 123" in exc.message
    assert exc.code == "RESOURCE_NOT_FOUND"
    assert exc.status_code == 404
    assert exc.details["resource"] == "User"
    assert exc.details["resource_id"] == "123"


def test_rate_limit_error():
    """测试速率限制错误"""
    exc = RateLimitError(retry_after=60)

    assert exc.code == "RATE_LIMIT_EXCEEDED"
    assert exc.status_code == 429
    assert exc.details["retry_after"] == 60


def test_sandbox_execution_error():
    """测试沙箱执行错误"""
    exc = SandboxExecutionError(
        message="Code execution failed",
        code_snippet="print('hello')",
        execution_output="Error: timeout"
    )

    assert exc.message == "Code execution failed"
    assert exc.code == "SANDBOX_EXECUTION_ERROR"
    assert exc.status_code == 500
    assert "code_snippet" in exc.details
    assert "execution_output" in exc.details


def test_container_pool_error():
    """测试容器池错误"""
    pool_status = {
        "available_containers": 0,
        "in_use_containers": 10
    }

    exc = ContainerPoolError(
        message="Container pool exhausted",
        pool_status=pool_status
    )

    assert exc.code == "CONTAINER_POOL_ERROR"
    assert exc.status_code == 503
    assert exc.details["pool_status"] == pool_status


def test_database_error():
    """测试数据库错误"""
    exc = DatabaseError(
        message="Query failed",
        operation="SELECT"
    )

    assert exc.code == "DATABASE_ERROR"
    assert exc.status_code == 500
    assert exc.details["operation"] == "SELECT"


def test_external_service_error():
    """测试外部服务错误"""
    exc = ExternalServiceError(
        message="API call failed",
        service_name="DeepSeek",
        status_code=502
    )

    assert exc.code == "EXTERNAL_SERVICE_ERROR"
    assert exc.status_code == 502
    assert exc.details["service_name"] == "DeepSeek"
    assert exc.details["external_status_code"] == 502


def test_timeout_error():
    """测试超时错误"""
    exc = TimeoutError(
        message="Operation timeout",
        timeout_seconds=30.0,
        operation="code_execution"
    )

    assert exc.code == "TIMEOUT_ERROR"
    assert exc.status_code == 504
    assert exc.details["timeout_seconds"] == 30.0
    assert exc.details["operation"] == "code_execution"


# ============================================
# 错误代码测试
# ============================================

def test_error_code_constants():
    """测试错误代码常量定义"""
    assert error_codes.VALIDATION_ERROR == "VALIDATION_ERROR"
    assert error_codes.AUTHENTICATION_ERROR == "AUTHENTICATION_ERROR"
    assert error_codes.RESOURCE_NOT_FOUND == "RESOURCE_NOT_FOUND"
    assert error_codes.SANDBOX_EXECUTION_ERROR == "SANDBOX_EXECUTION_ERROR"
    assert error_codes.CONTAINER_POOL_ERROR == "CONTAINER_POOL_ERROR"


def test_error_code_groups():
    """测试错误代码分组"""
    # 客户端错误
    assert error_codes.VALIDATION_ERROR in error_codes.CLIENT_ERRORS
    assert error_codes.AUTHENTICATION_ERROR in error_codes.CLIENT_ERRORS
    assert error_codes.RESOURCE_NOT_FOUND in error_codes.CLIENT_ERRORS

    # 服务端错误
    assert error_codes.SANDBOX_EXECUTION_ERROR in error_codes.SERVER_ERRORS
    assert error_codes.CONTAINER_POOL_ERROR in error_codes.SERVER_ERRORS
    assert error_codes.DATABASE_ERROR in error_codes.SERVER_ERRORS

    # 可重试错误
    assert error_codes.RATE_LIMIT_EXCEEDED in error_codes.RETRYABLE_ERRORS
    assert error_codes.CONTAINER_UNAVAILABLE in error_codes.RETRYABLE_ERRORS
    assert error_codes.SERVICE_UNAVAILABLE in error_codes.RETRYABLE_ERRORS


def test_error_code_helper_functions():
    """测试错误代码辅助函数"""
    # 客户端错误检查
    assert error_codes.is_client_error("VALIDATION_ERROR") is True
    assert error_codes.is_client_error("SANDBOX_EXECUTION_ERROR") is False

    # 服务端错误检查
    assert error_codes.is_server_error("SANDBOX_EXECUTION_ERROR") is True
    assert error_codes.is_server_error("VALIDATION_ERROR") is False

    # 可重试错误检查
    assert error_codes.is_retryable_error("RATE_LIMIT_EXCEEDED") is True
    assert error_codes.is_retryable_error("VALIDATION_ERROR") is False


# ============================================
# API 错误响应测试
# ============================================

def test_api_validation_error_response(client):
    """测试 API 验证错误响应"""
    # 发送无效请求 (缺少必需字段)
    response = client.post(
        "/api/execute",
        json={}  # 缺少 code 字段
    )

    assert response.status_code == 422
    data = response.json()

    # 检查错误响应格式
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "message" in data["error"]
    assert "path" in data["error"]
    assert "timestamp" in data["error"]
    assert "details" in data["error"]
    assert "validation_errors" in data["error"]["details"]


def test_api_resource_not_found_response(client):
    """测试 API 资源未找到响应"""
    # 请求不存在的课程
    response = client.get("/api/lessons/999999")

    assert response.status_code == 404
    data = response.json()

    # 检查错误响应格式
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
    assert "message" in data["error"]
    assert "path" in data["error"]
    assert "timestamp" in data["error"]


def test_api_code_safety_check_error(client):
    """测试代码安全检查错误响应"""
    # 提交不安全的代码
    response = client.post(
        "/api/execute",
        json={
            "code": "import os; os.system('ls')",
            "language": "python"
        }
    )

    # 应该被安全检查拦截
    assert response.status_code == 400
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "安全检查失败" in data["error"]["message"] or "禁止使用" in data["error"]["message"]


# ============================================
# 错误中间件测试
# ============================================

@patch('app.main.sandbox.execute_python')
def test_middleware_catches_helloagents_exception(mock_execute, client):
    """测试中间件捕获 HelloAgents 异常"""
    # 模拟沙箱抛出异常
    mock_execute.side_effect = SandboxExecutionError(
        message="Container execution failed",
        code_snippet="print('test')"
    )

    response = client.post(
        "/api/execute",
        json={
            "code": "print('hello')",
            "language": "python"
        }
    )

    assert response.status_code == 500
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "SANDBOX_EXECUTION_ERROR"
    assert "Container execution failed" in data["error"]["message"]


@patch('app.main.sandbox.execute_python')
def test_middleware_catches_unexpected_exception(mock_execute, client):
    """测试中间件捕获未预期异常"""
    # 模拟未预期的异常
    mock_execute.side_effect = RuntimeError("Unexpected error")

    response = client.post(
        "/api/execute",
        json={
            "code": "print('hello')",
            "language": "python"
        }
    )

    assert response.status_code == 500
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    # 不应该暴露内部错误详情
    assert "Unexpected error" not in data["error"]["message"]
    assert "unexpected error occurred" in data["error"]["message"].lower()


# ============================================
# 错误响应格式测试
# ============================================

def test_error_response_format_consistency(client):
    """测试错误响应格式一致性"""
    # 测试多种错误场景，确保格式一致
    test_cases = [
        {
            "endpoint": "/api/execute",
            "method": "post",
            "json": {},  # 验证错误
            "expected_status": 422
        },
        {
            "endpoint": "/api/lessons/999999",
            "method": "get",
            "expected_status": 404
        }
    ]

    for test_case in test_cases:
        if test_case["method"] == "post":
            response = client.post(
                test_case["endpoint"],
                json=test_case.get("json", {})
            )
        else:
            response = client.get(test_case["endpoint"])

        assert response.status_code == test_case["expected_status"]
        data = response.json()

        # 检查必需字段
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "path" in data["error"]
        assert "timestamp" in data["error"]

        # 检查字段类型
        assert isinstance(data["error"]["code"], str)
        assert isinstance(data["error"]["message"], str)
        assert isinstance(data["error"]["path"], str)
        assert isinstance(data["error"]["timestamp"], (int, float))


# ============================================
# 运行测试
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
