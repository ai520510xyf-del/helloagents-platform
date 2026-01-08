"""
API 版本信息端点

提供 API 版本查询和管理功能
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

router = APIRouter(tags=["version"])


# ============================================
# 数据模型
# ============================================

class VersionInfo(BaseModel):
    """版本详细信息"""
    status: str = Field(..., description="版本状态：stable, beta, deprecated")
    release_date: str = Field(..., description="发布日期（ISO 8601 格式）")
    deprecation_date: Optional[str] = Field(None, description="弃用日期（ISO 8601 格式）")
    end_of_life_date: Optional[str] = Field(None, description="终止支持日期（ISO 8601 格式）")
    description: Optional[str] = Field(None, description="版本描述")


class APIVersionResponse(BaseModel):
    """API 版本信息响应"""
    current_version: str = Field(..., description="当前推荐版本")
    supported_versions: List[str] = Field(..., description="支持的版本列表")
    deprecated_versions: List[str] = Field(..., description="已弃用的版本列表")
    latest_version: str = Field(..., description="最新版本")
    version_info: Dict[str, VersionInfo] = Field(..., description="各版本详细信息")


# ============================================
# 版本配置
# ============================================

VERSION_CONFIG = {
    "current": "v1",
    "latest": "v1",
    "supported": ["v1"],
    "deprecated": [],
    "info": {
        "v1": {
            "status": "stable",
            "release_date": "2026-01-08",
            "deprecation_date": None,
            "end_of_life_date": None,
            "description": "Initial stable release with code execution, lessons, sandbox monitoring, and AI chat features."
        }
    }
}


# ============================================
# API 端点
# ============================================

@router.get("/api/version", response_model=APIVersionResponse)
@router.get("/version", response_model=APIVersionResponse, include_in_schema=False)
async def get_api_version():
    """
    获取 API 版本信息

    返回当前支持的所有 API 版本及其状态

    **响应:**
    - current_version: 当前推荐使用的版本
    - supported_versions: 所有支持的版本列表
    - deprecated_versions: 已弃用但仍可用的版本列表
    - latest_version: 最新版本
    - version_info: 各版本的详细信息
    """
    return {
        "current_version": VERSION_CONFIG["current"],
        "supported_versions": VERSION_CONFIG["supported"],
        "deprecated_versions": VERSION_CONFIG["deprecated"],
        "latest_version": VERSION_CONFIG["latest"],
        "version_info": VERSION_CONFIG["info"]
    }
