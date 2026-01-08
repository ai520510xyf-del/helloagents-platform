"""
沙箱管理 API (v1)

提供容器池状态监控和管理功能
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from app.sandbox import sandbox
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sandbox", tags=["sandbox"])


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

@router.get("/pool/stats", response_model=PoolStatsResponse)
async def get_pool_stats():
    """
    获取容器池统计信息

    返回容器池的当前状态、性能指标和容器详情

    **响应:**
    - pool_enabled: 容器池是否启用
    - available_containers: 可用容器数量
    - in_use_containers: 使用中的容器数量
    - total_executions: 总执行次数
    - timestamp: 统计时间戳（ISO 8601 格式）
    - message: 附加信息（如果容器池未启用）
    """
    if sandbox.pool is None:
        logger.info(
            "pool_stats_requested_disabled",
            pool_enabled=False
        )
        return {
            "pool_enabled": False,
            "message": "Container pool is not enabled",
            "timestamp": datetime.now().isoformat()
        }

    stats = sandbox.pool.get_stats()
    stats["pool_enabled"] = True
    stats["timestamp"] = datetime.now().isoformat()

    logger.info(
        "pool_stats_requested",
        available_containers=stats.get('available_containers', 0),
        in_use_containers=stats.get('in_use_containers', 0),
        total_executions=stats.get('total_executions', 0)
    )

    return stats
