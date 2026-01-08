"""
API 版本控制中间件

为所有响应添加 API 版本信息
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logger import get_logger

logger = get_logger(__name__)


class APIVersionMiddleware(BaseHTTPMiddleware):
    """
    API 版本中间件

    为所有 API 响应添加版本信息头
    """

    def __init__(self, app, default_version: str = "v1"):
        super().__init__(app)
        self.default_version = default_version

    async def dispatch(self, request: Request, call_next):
        """
        处理请求并添加版本头

        1. 检测请求路径中的版本信息
        2. 执行请求
        3. 在响应头中添加 X-API-Version
        """
        # 检测请求的 API 版本
        api_version = self.default_version
        path = request.url.path

        # 从路径中提取版本 (如 /api/v1/...)
        if path.startswith("/api/v"):
            parts = path.split("/")
            if len(parts) >= 3 and parts[2].startswith("v"):
                api_version = parts[2]

        # 检查请求头中的版本指定
        header_version = request.headers.get("X-API-Version")
        if header_version:
            api_version = header_version

        # 将版本信息添加到请求状态（供路由使用）
        request.state.api_version = api_version

        # 执行请求
        response = await call_next(request)

        # 添加版本信息到响应头
        response.headers["X-API-Version"] = api_version

        # 添加支持的版本列表
        response.headers["X-Supported-Versions"] = "v1"

        return response
