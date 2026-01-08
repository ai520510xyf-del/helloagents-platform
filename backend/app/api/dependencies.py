"""
API 共享依赖

提供跨版本共享的依赖注入函数
"""

from fastapi import Header, HTTPException
from typing import Optional


async def get_api_version(
    x_api_version: Optional[str] = Header(None)
) -> str:
    """
    从请求头获取 API 版本

    支持通过 X-API-Version 头指定版本
    默认返回 v1
    """
    if x_api_version is None:
        return "v1"

    # 验证版本格式
    if not x_api_version.startswith("v"):
        raise HTTPException(
            status_code=400,
            detail="Invalid API version format. Use 'v1', 'v2', etc."
        )

    # 验证版本是否支持
    supported_versions = ["v1"]
    if x_api_version not in supported_versions:
        raise HTTPException(
            status_code=400,
            detail=f"API version {x_api_version} is not supported. Supported versions: {', '.join(supported_versions)}"
        )

    return x_api_version
