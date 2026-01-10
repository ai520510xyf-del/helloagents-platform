"""
Code Execution API v2 - Clean Architecture

代码执行API（基于Clean Architecture重构）
"""

from fastapi import APIRouter, Depends, status

from app.application.use_cases.execute_code_use_case import ExecuteCodeUseCase
from app.application.dto.code_execution_dto import (
    CodeExecutionRequestDTO,
    CodeExecutionResponseDTO
)
from app.container import get_execute_code_use_case
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/execute",
    response_model=CodeExecutionResponseDTO,
    summary="执行代码",
    description="在安全沙箱环境中执行代码",
    responses={
        200: {
            "description": "代码执行完成（成功或失败）",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "执行成功",
                            "value": {
                                "success": True,
                                "output": "Hello, World!\n",
                                "error": None,
                                "execution_time": 0.05,
                                "status": "success"
                            }
                        },
                        "failure": {
                            "summary": "执行失败",
                            "value": {
                                "success": False,
                                "output": "",
                                "error": "NameError: name 'x' is not defined",
                                "execution_time": 0.02,
                                "status": "failed"
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "代码验证失败（不安全的代码）"},
        422: {"description": "请求参数验证失败"},
        500: {"description": "沙箱执行错误"}
    }
)
def execute_code(
    request: CodeExecutionRequestDTO,
    use_case: ExecuteCodeUseCase = Depends(get_execute_code_use_case)
):
    """
    执行代码

    在Docker容器沙箱中安全执行用户代码

    **安全限制:**
    - 禁止使用 os.system, subprocess, eval, exec 等危险函数
    - 代码长度限制：10KB
    - 执行超时：默认30秒，最大300秒
    - 内存限制：128MB
    - CPU限制：50%核心
    - 禁用网络访问

    **参数:**
    - **code**: 要执行的代码（必填）
    - **language**: 编程语言（默认：python）
    - **timeout**: 超时时间秒数（默认：30，范围：1-300）
    - **user_id**: 用户ID（可选）
    - **lesson_id**: 课程ID（可选）

    **返回:**
    - **success**: 执行是否成功
    - **output**: 执行输出（成功时）
    - **error**: 错误信息（失败时）
    - **execution_time**: 执行时间（秒）
    - **status**: 执行状态（success/failed/timeout）
    """
    logger.info(
        "api_v2_execute_code",
        code_length=len(request.code),
        language=request.language,
        timeout=request.timeout
    )

    return use_case.execute(request)


@router.get(
    "/stats",
    summary="获取执行统计",
    description="获取代码执行服务的统计信息",
    responses={
        200: {
            "description": "统计信息",
            "content": {
                "application/json": {
                    "example": {
                        "pool_enabled": True,
                        "available_containers": 3,
                        "in_use_containers": 0,
                        "total_executions": 1234,
                        "total_created": 10,
                        "total_destroyed": 2
                    }
                }
            }
        }
    }
)
def get_execution_stats(
    use_case: ExecuteCodeUseCase = Depends(get_execute_code_use_case)
):
    """
    获取执行统计

    返回容器池和代码执行的统计信息
    """
    logger.info("api_v2_get_execution_stats")

    # 获取统计信息
    stats = use_case.execution_service.get_execution_stats()

    return {
        "success": True,
        "data": stats
    }
