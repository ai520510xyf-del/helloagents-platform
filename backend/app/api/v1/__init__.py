"""
API v1 版本模块

聚合所有 v1 版本的路由
"""

from fastapi import APIRouter

from .routes import code, lessons, sandbox, chat

# 创建 v1 API 路由
api_router = APIRouter()

# 注册各模块路由
api_router.include_router(code.router)
api_router.include_router(lessons.router)
api_router.include_router(sandbox.router)
api_router.include_router(chat.router)

__all__ = ["api_router"]
