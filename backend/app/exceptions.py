"""
自定义异常类模块

定义 HelloAgents 应用的所有自定义异常类型，提供统一的错误处理机制
"""

from typing import Optional, Dict, Any


class HelloAgentsException(Exception):
    """
    HelloAgents 基础异常类

    所有自定义异常的基类，提供统一的错误信息和状态码接口
    """

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常

        Args:
            message: 人类可读的错误消息
            code: 错误代码 (用于程序化处理)
            status_code: HTTP 状态码
            details: 额外的错误详情 (可选)
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


# ============================================
# 客户端错误 (4xx)
# ============================================


class ValidationError(HelloAgentsException):
    """
    输入验证错误 (400)

    用于请求参数验证失败的场景
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化验证错误

        Args:
            message: 错误消息
            field: 验证失败的字段名 (可选)
            details: 额外的验证详情 (可选)
        """
        error_details = details or {}
        if field:
            error_details["field"] = field

        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=error_details
        )


class AuthenticationError(HelloAgentsException):
    """
    认证错误 (401)

    用于用户身份验证失败的场景
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(HelloAgentsException):
    """
    授权错误 (403)

    用于用户无权访问资源的场景
    """

    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if resource:
            error_details["resource"] = resource

        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
            details=error_details
        )


class ResourceNotFoundError(HelloAgentsException):
    """
    资源未找到 (404)

    用于请求的资源不存在的场景
    """

    def __init__(
        self,
        resource: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details.update({
            "resource": resource,
            "resource_id": resource_id
        })

        super().__init__(
            message=f"{resource} not found: {resource_id}",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=error_details
        )


class ConflictError(HelloAgentsException):
    """
    资源冲突 (409)

    用于资源已存在或状态冲突的场景
    """

    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if resource:
            error_details["resource"] = resource

        super().__init__(
            message=message,
            code="CONFLICT_ERROR",
            status_code=409,
            details=error_details
        )


class RateLimitError(HelloAgentsException):
    """
    速率限制 (429)

    用于请求频率超过限制的场景
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after

        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=error_details
        )


# ============================================
# 服务端错误 (5xx)
# ============================================


class SandboxExecutionError(HelloAgentsException):
    """
    沙箱执行错误 (500)

    用于代码沙箱执行失败的场景
    """

    def __init__(
        self,
        message: str,
        code_snippet: Optional[str] = None,
        execution_output: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if code_snippet:
            # 截断过长的代码片段
            error_details["code_snippet"] = code_snippet[:500] + "..." if len(code_snippet) > 500 else code_snippet
        if execution_output:
            error_details["execution_output"] = execution_output[:1000] + "..." if len(execution_output) > 1000 else execution_output

        super().__init__(
            message=message,
            code="SANDBOX_EXECUTION_ERROR",
            status_code=500,
            details=error_details
        )


class ContainerPoolError(HelloAgentsException):
    """
    容器池错误 (503)

    用于容器池不可用或获取容器失败的场景
    """

    def __init__(
        self,
        message: str,
        pool_status: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if pool_status:
            error_details["pool_status"] = pool_status

        super().__init__(
            message=message,
            code="CONTAINER_POOL_ERROR",
            status_code=503,
            details=error_details
        )


class DatabaseError(HelloAgentsException):
    """
    数据库错误 (500)

    用于数据库操作失败的场景
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if operation:
            error_details["operation"] = operation

        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=error_details
        )


class ExternalServiceError(HelloAgentsException):
    """
    外部服务错误 (502)

    用于调用外部服务失败的场景 (如 DeepSeek API)
    """

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if service_name:
            error_details["service_name"] = service_name
        if status_code:
            error_details["external_status_code"] = status_code

        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=error_details
        )


class ConfigurationError(HelloAgentsException):
    """
    配置错误 (500)

    用于应用配置缺失或无效的场景
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key

        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=error_details
        )


class TimeoutError(HelloAgentsException):
    """
    超时错误 (504)

    用于操作超时的场景
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if timeout_seconds:
            error_details["timeout_seconds"] = timeout_seconds
        if operation:
            error_details["operation"] = operation

        super().__init__(
            message=message,
            code="TIMEOUT_ERROR",
            status_code=504,
            details=error_details
        )


class ServiceUnavailableError(HelloAgentsException):
    """
    服务不可用 (503)

    用于服务暂时不可用的场景
    """

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after

        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=error_details
        )
