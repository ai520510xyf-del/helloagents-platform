"""
API v2 - Clean Architecture Implementation

基于Clean Architecture重构的API v2版本
"""

from fastapi import APIRouter
from app.api.v2.routes import users, code_execution

# 创建 v2 路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(users.router, prefix="/users", tags=["users-v2"])
api_router.include_router(code_execution.router, prefix="/code", tags=["code-v2"])
