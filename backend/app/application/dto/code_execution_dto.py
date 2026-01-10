"""
Code Execution DTOs

代码执行数据传输对象
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional


class CodeExecutionRequestDTO(BaseModel):
    """代码执行请求DTO"""
    code: str = Field(..., min_length=1, max_length=10000, description="要执行的代码")
    language: str = Field(default="python", description="编程语言")
    timeout: int = Field(default=30, ge=1, le=300, description="超时时间（秒）")
    user_id: Optional[int] = Field(None, description="用户ID")
    lesson_id: Optional[int] = Field(None, description="课程ID")

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """验证编程语言"""
        allowed = ['python', 'javascript', 'go']
        if v not in allowed:
            raise ValueError(f"Language must be one of {allowed}")
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "code": "print('Hello, World!')",
            "language": "python",
            "timeout": 30
        }
    })


class CodeExecutionResponseDTO(BaseModel):
    """代码执行响应DTO"""
    success: bool = Field(..., description="执行是否成功")
    output: str = Field(default="", description="执行输出")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., ge=0, description="执行时间（秒）")
    status: str = Field(..., description="执行状态")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "output": "Hello, World!\n",
            "error": None,
            "execution_time": 0.05,
            "status": "success"
        }
    })
