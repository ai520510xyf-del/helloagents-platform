"""
统一 API 响应格式

定义标准化的响应模型，确保所有 API 端点返回一致的格式
"""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

# 泛型类型
T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """
    成功响应的统一格式

    示例:
    ```json
    {
        "success": true,
        "data": {...},
        "message": "操作成功",
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
    """
    success: bool = Field(default=True, description="请求是否成功")
    data: T = Field(..., description="响应数据")
    message: Optional[str] = Field(None, description="附加消息")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="响应时间戳"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "示例"},
                "message": "操作成功",
                "timestamp": "2024-01-08T10:00:00Z"
            }
        }


class ErrorDetail(BaseModel):
    """错误详情"""
    field: Optional[str] = Field(None, description="错误字段")
    message: str = Field(..., description="错误描述")
    code: Optional[str] = Field(None, description="错误代码")


class ErrorResponse(BaseModel):
    """
    错误响应的统一格式

    示例:
    ```json
    {
        "success": false,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "验证失败",
            "details": [...]
        },
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
    """
    success: bool = Field(default=False, description="请求是否成功")
    error: dict = Field(..., description="错误信息")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="响应时间戳"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "验证失败",
                    "details": [
                        {"field": "email", "message": "无效的邮箱格式"}
                    ]
                },
                "timestamp": "2024-01-08T10:00:00Z"
            }
        }


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(..., ge=1, description="当前页码")
    limit: int = Field(..., ge=1, le=100, description="每页数量")
    total: int = Field(..., ge=0, description="总记录数")
    total_pages: int = Field(..., ge=0, description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应的统一格式

    示例:
    ```json
    {
        "success": true,
        "data": [...],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 100,
            "total_pages": 5,
            "has_next": true,
            "has_prev": false
        },
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
    """
    success: bool = Field(default=True, description="请求是否成功")
    data: list[T] = Field(..., description="数据列表")
    pagination: PaginationMeta = Field(..., description="分页信息")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="响应时间戳"
    )


# 辅助函数，方便创建响应
def success_response(data: Any, message: Optional[str] = None) -> dict:
    """
    创建成功响应

    Args:
        data: 响应数据
        message: 可选的附加消息

    Returns:
        符合 SuccessResponse 格式的字典
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def error_response(
    code: str,
    message: str,
    details: Optional[Any] = None,
    status_code: int = 400
) -> dict:
    """
    创建错误响应

    Args:
        code: 错误代码
        message: 错误消息
        details: 错误详情
        status_code: HTTP 状态码

    Returns:
        符合 ErrorResponse 格式的字典
    """
    error_dict = {
        "code": code,
        "message": message
    }
    if details:
        error_dict["details"] = details

    return {
        "success": False,
        "error": error_dict,
        "timestamp": datetime.utcnow().isoformat()
    }


def paginated_response(
    data: list,
    page: int,
    limit: int,
    total: int
) -> dict:
    """
    创建分页响应

    Args:
        data: 数据列表
        page: 当前页码
        limit: 每页数量
        total: 总记录数

    Returns:
        符合 PaginatedResponse 格式的字典
    """
    total_pages = (total + limit - 1) // limit  # 向上取整

    return {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "timestamp": datetime.utcnow().isoformat()
    }
