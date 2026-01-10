"""
Prometheus 指标收集中间件

为 FastAPI 应用添加 Prometheus 指标导出功能,监控关键业务指标。
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# ===========================
# 创建 Prometheus 指标
# ===========================

# HTTP 请求指标
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

http_request_size_bytes = Summary(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

http_response_size_bytes = Summary(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

# 代码沙箱指标
sandbox_executions_total = Counter(
    'sandbox_executions_total',
    'Total code executions in sandbox',
    ['language', 'status']
)

sandbox_execution_duration_seconds = Histogram(
    'sandbox_execution_duration_seconds',
    'Code execution time in sandbox',
    ['language'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

sandbox_pool_available = Gauge(
    'sandbox_pool_available',
    'Number of available containers in the pool'
)

sandbox_pool_in_use = Gauge(
    'sandbox_pool_in_use',
    'Number of containers currently in use'
)

# AI 助手指标
ai_chat_requests_total = Counter(
    'ai_chat_requests_total',
    'Total AI chat requests',
    ['status']
)

ai_chat_duration_seconds = Histogram(
    'ai_chat_duration_seconds',
    'AI chat response time in seconds',
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0)
)

ai_chat_tokens_total = Counter(
    'ai_chat_tokens_total',
    'Total tokens consumed by AI chat',
    ['model']
)

ai_chat_errors_total = Counter(
    'ai_chat_errors_total',
    'Total AI chat errors',
    ['error_type']
)

# 数据库指标
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_query_errors_total = Counter(
    'db_query_errors_total',
    'Total database query errors',
    ['operation', 'error_type']
)

# 应用健康指标
app_health_status = Gauge(
    'app_health_status',
    'Application health status (1=healthy, 0=unhealthy)',
    ['component']
)

# ===========================
# Prometheus 中间件
# ===========================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Prometheus 指标收集中间件

    自动收集所有 HTTP 请求的指标数据
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并收集指标
        """
        # 跳过 /metrics 端点本身
        if request.url.path == "/metrics":
            return await call_next(request)

        # 标准化端点路径 (移除路径参数)
        endpoint = self._normalize_path(request.url.path)
        method = request.method

        # 增加进行中的请求计数
        http_requests_in_progress.labels(
            method=method,
            endpoint=endpoint
        ).inc()

        # 记录请求大小
        request_size = int(request.headers.get("content-length", 0))
        if request_size > 0:
            http_request_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)

        # 记录请求开始时间
        start_time = time.time()

        try:
            # 处理请求
            response = await call_next(request)

            # 计算响应时间
            duration = time.time() - start_time

            # 记录响应大小
            response_size = int(response.headers.get("content-length", 0))
            if response_size > 0:
                http_response_size_bytes.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(response_size)

            # 记录请求指标
            status_code = response.status_code
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            return response

        except Exception as e:
            # 记录错误请求
            duration = time.time() - start_time

            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            raise

        finally:
            # 减少进行中的请求计数
            http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint
            ).dec()

    def _normalize_path(self, path: str) -> str:
        """
        标准化路径,将路径参数替换为占位符

        例如: /api/lessons/1 -> /api/lessons/{id}
        """
        # 移除查询参数
        path = path.split('?')[0]

        # 简单的路径标准化
        parts = path.split('/')
        normalized_parts = []

        for part in parts:
            # 如果是数字,替换为 {id}
            if part.isdigit():
                normalized_parts.append('{id}')
            else:
                normalized_parts.append(part)

        return '/'.join(normalized_parts)


# ===========================
# 辅助函数 - 业务指标记录
# ===========================

def record_sandbox_execution(
    language: str,
    duration: float,
    success: bool
):
    """
    记录沙箱代码执行指标

    Args:
        language: 编程语言
        duration: 执行时间(秒)
        success: 是否成功
    """
    status = 'success' if success else 'error'

    sandbox_executions_total.labels(
        language=language,
        status=status
    ).inc()

    sandbox_execution_duration_seconds.labels(
        language=language
    ).observe(duration)


def record_sandbox_pool_stats(available: int, in_use: int):
    """
    记录容器池状态

    Args:
        available: 可用容器数
        in_use: 使用中容器数
    """
    sandbox_pool_available.set(available)
    sandbox_pool_in_use.set(in_use)


def record_ai_chat_request(
    duration: float,
    success: bool,
    tokens: int = 0,
    model: str = "deepseek-chat",
    error_type: str = None
):
    """
    记录 AI 聊天请求指标

    Args:
        duration: 响应时间(秒)
        success: 是否成功
        tokens: 消耗 token 数
        model: 使用的模型
        error_type: 错误类型(如果失败)
    """
    status = 'success' if success else 'error'

    ai_chat_requests_total.labels(status=status).inc()
    ai_chat_duration_seconds.observe(duration)

    if success and tokens > 0:
        ai_chat_tokens_total.labels(model=model).inc(tokens)

    if not success and error_type:
        ai_chat_errors_total.labels(error_type=error_type).inc()


def record_db_query(
    operation: str,
    duration: float,
    success: bool = True,
    error_type: str = None
):
    """
    记录数据库查询指标

    Args:
        operation: 操作类型 (SELECT, INSERT, UPDATE, DELETE)
        duration: 查询时间(秒)
        success: 是否成功
        error_type: 错误类型(如果失败)
    """
    db_query_duration_seconds.labels(operation=operation).observe(duration)

    if not success and error_type:
        db_query_errors_total.labels(
            operation=operation,
            error_type=error_type
        ).inc()


def update_health_status(component: str, is_healthy: bool):
    """
    更新组件健康状态

    Args:
        component: 组件名称 (api, database, sandbox, ai_service)
        is_healthy: 是否健康
    """
    status = 1 if is_healthy else 0
    app_health_status.labels(component=component).set(status)


# ===========================
# 指标导出
# ===========================

def get_metrics() -> bytes:
    """
    获取 Prometheus 格式的指标数据

    Returns:
        Prometheus 文本格式的指标
    """
    return generate_latest()
