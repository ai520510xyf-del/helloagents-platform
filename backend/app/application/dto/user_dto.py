"""
User DTOs

用户数据传输对象
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any


class UserCreateDTO(BaseModel):
    """用户创建DTO"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="用户设置")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "username": "alice",
            "full_name": "Alice Wang",
            "settings": {"theme": "dark"}
        }
    })


class UserUpdateDTO(BaseModel):
    """用户更新DTO"""
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    settings: Optional[Dict[str, Any]] = Field(None, description="用户设置")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "full_name": "Alice Wang",
            "settings": {"theme": "light"}
        }
    })


class UserResponseDTO(BaseModel):
    """用户响应DTO"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    full_name: Optional[str] = Field(None, description="全名")
    settings: Dict[str, Any] = Field(default_factory=dict, description="用户设置")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    last_login: Optional[str] = Field(None, description="最后登录时间")

    model_config = ConfigDict(from_attributes=True)
