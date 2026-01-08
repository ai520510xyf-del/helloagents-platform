"""
错误处理中间件

提供统一的错误处理机制，捕获所有异常并返回标准化的错误响应
"""

import time
import traceback
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.exceptions import HelloAgentsException
from app.logger import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    错误处理中间件

    捕获所有异常并返回统一格式的错误响应
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并捕获异常

        Args:
            request: FastAPI 请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            响应对象
        """
        # 生成请求 ID (用于追踪)
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            # 调用下一个处理器
            response = await call_next(request)
            return response

        except HelloAgentsException as e:
            # 处理自定义异常
            return self._handle_helloagents_exception(request, e, request_id)

        except Exception as e:
            # 处理未捕获的异常
            return self._handle_unexpected_exception(request, e, request_id)

    def _handle_helloagents_exception(
        self,
        request: Request,
        exc: HelloAgentsException,
        request_id: str
    ) -> JSONResponse:
        """
        处理 HelloAgents 自定义异常

        Args:
            request: 请求对象
            exc: 异常对象
            request_id: 请求 ID

        Returns:
            JSON 错误响应
        """
        # 根据状态码决定日志级别
        if exc.status_code >= 500:
            # 服务端错误 - ERROR 级别
            logger.error(
                "application_error",
                error_code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                path=request.url.path,
                method=request.method,
                request_id=request_id,
                details=exc.details,
                exc_info=True
            )
        else:
            # 客户端错误 - WARNING 级别
            logger.warning(
                "application_error",
                error_code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                path=request.url.path,
                method=request.method,
                request_id=request_id,
                details=exc.details
            )

        # 构建错误响应
        error_response = {
            "error": {
                "code": exc.code,
                "message": exc.message,
                "path": request.url.path,
                "timestamp": time.time(),
                "request_id": request_id
            }
        }

        # 添加详情 (如果有)
        if exc.details:
            error_response["error"]["details"] = exc.details

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )

    def _handle_unexpected_exception(
        self,
        request: Request,
        exc: Exception,
        request_id: str
    ) -> JSONResponse:
        """
        处理未捕获的异常

        Args:
            request: 请求对象
            exc: 异常对象
            request_id: 请求 ID

        Returns:
            JSON 错误响应
        """
        # 记录详细的错误信息
        logger.error(
            "unexpected_error",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
            request_id=request_id,
            traceback=traceback.format_exc(),
            exc_info=True
        )

        # 返回通用错误响应 (不暴露内部错误详情)
        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "path": request.url.path,
                "timestamp": time.time(),
                "request_id": request_id
            }
        }

        return JSONResponse(
            status_code=500,
            content=error_response
        )


# ============================================
# 辅助函数
# ============================================


def get_request_id(request: Request) -> str:
    """
    从请求中获取请求 ID

    Args:
        request: FastAPI 请求对象

    Returns:
        请求 ID
    """
    return getattr(request.state, "request_id", "unknown")
