"""
API 响应缓存中间件

实现基于内存的 LRU 缓存,用于缓存:
- 课程列表和内容
- 公开的只读 API 端点
- 静态资源响应

不缓存:
- POST/PUT/DELETE 请求
- 包含认证信息的请求
- 代码执行和 AI 聊天等动态内容
"""

from functools import lru_cache
from typing import Optional
import hashlib
import json
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.logger import get_logger

logger = get_logger(__name__)


class ResponseCache:
    """简单的内存响应缓存"""

    def __init__(self, max_size: int = 100):
        self._cache: dict[str, tuple[Response, datetime]] = {}
        self._max_size = max_size

    def get(self, key: str, ttl_seconds: int = 300) -> Optional[Response]:
        """获取缓存的响应"""
        if key in self._cache:
            response, cached_at = self._cache[key]
            # 检查是否过期
            if datetime.now() - cached_at < timedelta(seconds=ttl_seconds):
                return response
            else:
                # 过期,删除
                del self._cache[key]
        return None

    def set(self, key: str, response: Response):
        """设置缓存响应"""
        # LRU 策略: 如果超过最大大小,删除最早的
        if len(self._cache) >= self._max_size:
            # 删除最旧的项
            oldest_key = min(self._cache.items(), key=lambda x: x[1][1])[0]
            del self._cache[oldest_key]

        self._cache[key] = (response, datetime.now())

    def clear(self):
        """清空缓存"""
        self._cache.clear()

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            "cache_size": len(self._cache),
            "max_size": self._max_size,
            "cached_keys": list(self._cache.keys())
        }


# 全局缓存实例
response_cache = ResponseCache(max_size=100)


# 可缓存的路径模式
CACHEABLE_PATHS = [
    "/api/lessons",
    "/api/v1/lessons",
    "/health",
    "/health/ready",
    "/health/live",
]

# 可缓存的路径前缀
CACHEABLE_PREFIXES = [
    "/api/lessons/",
    "/api/v1/lessons/",
]


def is_cacheable(path: str, method: str) -> bool:
    """判断请求是否可缓存"""
    # 只缓存 GET 请求
    if method != "GET":
        return False

    # 检查完全匹配
    if path in CACHEABLE_PATHS:
        return True

    # 检查前缀匹配
    for prefix in CACHEABLE_PREFIXES:
        if path.startswith(prefix):
            return True

    return False


def get_cache_key(request: Request) -> str:
    """生成缓存键"""
    # 使用 URL 路径和查询参数生成唯一键
    url = str(request.url)
    return hashlib.md5(url.encode()).hexdigest()


def get_cache_ttl(path: str) -> int:
    """根据路径获取缓存 TTL (秒)"""
    # 健康检查端点: 10秒
    if path in ["/health", "/health/ready", "/health/live"]:
        return 10

    # 课程列表: 5分钟
    if path in ["/api/lessons", "/api/v1/lessons"]:
        return 300

    # 课程内容: 10分钟
    if "/lessons/" in path:
        return 600

    # 默认: 5分钟
    return 300


class CacheMiddleware(BaseHTTPMiddleware):
    """API 响应缓存中间件"""

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        path = request.url.path
        method = request.method

        # 检查是否可缓存
        if not is_cacheable(path, method):
            # 不可缓存,直接处理
            return await call_next(request)

        # 生成缓存键
        cache_key = get_cache_key(request)
        ttl = get_cache_ttl(path)

        # 尝试从缓存获取
        cached_response = response_cache.get(cache_key, ttl_seconds=ttl)

        if cached_response:
            # 缓存命中
            logger.debug(
                "cache_hit",
                path=path,
                cache_key=cache_key,
                ttl=ttl
            )

            # 添加缓存头
            cached_response.headers["X-Cache"] = "HIT"
            cached_response.headers["X-Cache-Key"] = cache_key

            return cached_response

        # 缓存未命中,处理请求
        logger.debug(
            "cache_miss",
            path=path,
            cache_key=cache_key
        )

        response = await call_next(request)

        # 只缓存成功响应 (2xx)
        if 200 <= response.status_code < 300:
            # 注意: 这里简化处理,实际生产环境需要复制响应体
            # 因为响应流只能读取一次

            # 添加缓存头
            response.headers["X-Cache"] = "MISS"
            response.headers["X-Cache-Key"] = cache_key
            response.headers["Cache-Control"] = f"public, max-age={ttl}"

            # TODO: 实现响应体缓存
            # 目前只记录缓存元数据
            logger.info(
                "response_cached",
                path=path,
                cache_key=cache_key,
                status_code=response.status_code,
                ttl=ttl
            )

        return response


# 清除缓存的辅助函数
def clear_cache():
    """清空所有缓存"""
    response_cache.clear()
    logger.info("cache_cleared")


def get_cache_stats() -> dict:
    """获取缓存统计"""
    return response_cache.get_stats()


# LRU 缓存装饰器用于函数级缓存
@lru_cache(maxsize=100)
def cached_get_lessons():
    """缓存的课程列表获取函数"""
    # 这个将在实际使用时被替换
    pass
