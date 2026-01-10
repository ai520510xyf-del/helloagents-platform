"""
沙箱管理 API (v1)

提供容器池状态监控和管理功能
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.sandbox import sandbox
from app.logger import get_logger
from app.api.response_models import success_response

logger = get_logger(__name__)

router = APIRouter(prefix="/sandbox", tags=["sandbox"])
limiter = Limiter(key_func=get_remote_address)


# ============================================
# 数据模型
# ============================================

class PoolStatsResponse(BaseModel):
    """容器池统计响应"""
    pool_enabled: bool = Field(..., description="容器池是否启用")
    available_containers: Optional[int] = Field(None, description="可用容器数量")
    in_use_containers: Optional[int] = Field(None, description="使用中的容器数量")
    total_executions: Optional[int] = Field(None, description="总执行次数")
    timestamp: str = Field(..., description="统计时间戳")
    message: Optional[str] = Field(None, description="附加信息")


# ============================================
# API 端点
# ============================================

@router.get("/pool/stats")
@limiter.limit("30/minute")
async def get_pool_stats(request: Request):
    """
    获取容器池统计信息

    返回容器池的当前状态、性能指标和容器详情

    **速率限制:** 30次/分钟

    **响应格式:**
    ```json
    {
        "success": true,
        "data": {
            "pool_enabled": true,
            "available_containers": 3,
            "in_use_containers": 2,
            "total_executions": 1234
        },
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
    """
    if sandbox.pool is None:
        logger.info(
            "pool_stats_requested_disabled",
            pool_enabled=False
        )
        return success_response(
            data={
                "pool_enabled": False,
                "available_containers": 0,
                "in_use_containers": 0,
                "total_executions": 0
            },
            message="容器池未启用"
        )

    stats = sandbox.pool.get_stats()
    stats["pool_enabled"] = True

    logger.info(
        "pool_stats_requested",
        available_containers=stats.get('available_containers', 0),
        in_use_containers=stats.get('in_use_containers', 0),
        total_executions=stats.get('total_executions', 0)
    )

    return success_response(
        data=stats,
        message="容器池统计信息获取成功"
    )
