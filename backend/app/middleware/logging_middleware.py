"""
日志记录中间件

自动记录所有 API 请求和响应，包括:
- 请求方法、路径、参数
- 响应状态码
- 执行时间
- 错误堆栈（如果有）
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP 请求/响应日志中间件
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("http")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理 HTTP 请求并记录日志
        """
        # 记录请求开始
        start_time = time.time()
        request_id = self._generate_request_id()

        # 获取请求信息
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # 记录请求日志
        self.logger.info(
            "http_request_started",
            request_id=request_id,
            method=method,
            path=path,
            query_params=query_params,
            client_host=client_host,
            user_agent=user_agent
        )

        # 处理请求
        try:
            response = await call_next(request)
            execution_time = time.time() - start_time

            # 记录成功响应
            self.logger.info(
                "http_request_completed",
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                execution_time_ms=round(execution_time * 1000, 2),
                success=True
            )

            # 添加自定义响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Execution-Time"] = str(round(execution_time * 1000, 2))

            return response

        except Exception as e:
            execution_time = time.time() - start_time

            # 记录错误响应
            self.logger.error(
                "http_request_failed",
                request_id=request_id,
                method=method,
                path=path,
                execution_time_ms=round(execution_time * 1000, 2),
                error=str(e),
                error_type=type(e).__name__,
                success=False,
                exc_info=True
            )

            # 重新抛出异常，让 FastAPI 的异常处理器处理
            raise

    def _generate_request_id(self) -> str:
        """
        生成唯一的请求 ID
        """
        import uuid
        return str(uuid.uuid4())[:8]


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    性能监控中间件

    监控慢请求并记录警告
    """

    def __init__(self, app: ASGIApp, slow_request_threshold_ms: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold_ms = slow_request_threshold_ms
        self.logger = get_logger("performance")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        监控请求性能
        """
        start_time = time.time()

        response = await call_next(request)

        execution_time_ms = (time.time() - start_time) * 1000

        # 如果请求执行时间超过阈值，记录警告
        if execution_time_ms > self.slow_request_threshold_ms:
            self.logger.warning(
                "slow_request_detected",
                method=request.method,
                path=request.url.path,
                execution_time_ms=round(execution_time_ms, 2),
                threshold_ms=self.slow_request_threshold_ms,
                status_code=response.status_code
            )

        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    错误日志中间件

    捕获并记录所有未处理的异常
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("error")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        捕获异常并记录
        """
        try:
            return await call_next(request)
        except Exception as e:
            # 记录详细错误信息
            self.logger.error(
                "unhandled_exception",
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )

            # 重新抛出异常
            raise


class RequestBodyLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求体日志中间件（仅在开发环境使用）

    记录 POST/PUT/PATCH 请求的请求体内容（谨慎使用，避免记录敏感信息）
    """

    def __init__(self, app: ASGIApp, max_body_size: int = 1000):
        super().__init__(app)
        self.max_body_size = max_body_size
        self.logger = get_logger("request_body")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        记录请求体内容
        """
        # 只记录 POST/PUT/PATCH 请求
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 读取请求体
                body = await request.body()

                # 尝试解析为 JSON
                try:
                    body_json = json.loads(body)
                    # 过滤敏感字段
                    body_json = self._filter_sensitive_fields(body_json)
                    body_str = json.dumps(body_json)
                except:
                    body_str = body.decode("utf-8", errors="ignore")

                # 截断过长的内容
                if len(body_str) > self.max_body_size:
                    body_str = body_str[:self.max_body_size] + "... (truncated)"

                self.logger.debug(
                    "request_body",
                    method=request.method,
                    path=request.url.path,
                    body=body_str
                )

            except Exception as e:
                self.logger.error(
                    "failed_to_log_request_body",
                    error=str(e)
                )

        return await call_next(request)

    def _filter_sensitive_fields(self, data: dict) -> dict:
        """
        过滤敏感字段
        """
        sensitive_keys = ["password", "token", "api_key", "secret"]

        filtered = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered[key] = "***REDACTED***"
            elif isinstance(value, dict):
                filtered[key] = self._filter_sensitive_fields(value)
            else:
                filtered[key] = value

        return filtered
