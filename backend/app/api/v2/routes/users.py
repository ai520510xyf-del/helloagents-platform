"""
Users API v2 - Clean Architecture

用户管理API（基于Clean Architecture重构）
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.use_cases.user_management_use_case import UserManagementUseCase
from app.application.dto.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserResponseDTO
)
from app.container import get_db_session, get_user_management_use_case
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户，用户名必须唯一",
    responses={
        201: {
            "description": "用户创建成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "alice",
                        "full_name": "Alice Wang",
                        "settings": {"theme": "dark"},
                        "created_at": "2024-01-09T10:00:00",
                        "updated_at": "2024-01-09T10:00:00",
                        "last_login": None
                    }
                }
            }
        },
        409: {"description": "用户名已存在"},
        422: {"description": "请求参数验证失败"}
    }
)
def create_user(
    request: UserCreateDTO,
    session: Session = Depends(get_db_session),
    use_case: UserManagementUseCase = Depends(get_user_management_use_case)
):
    """
    创建用户

    - **username**: 用户名（3-50字符，必填）
    - **full_name**: 全名（可选）
    - **settings**: 用户设置（可选JSON对象）
    """
    logger.info("api_v2_create_user", username=request.username)
    return use_case.create_user(request)


@router.get(
    "/current",
    response_model=UserResponseDTO,
    summary="获取当前用户",
    description="获取当前登录用户（本地模式返回第一个用户）",
    responses={
        200: {
            "description": "成功获取当前用户",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "local_user",
                        "full_name": "本地用户",
                        "settings": {"theme": "dark"},
                        "created_at": "2024-01-09T10:00:00",
                        "updated_at": "2024-01-09T10:00:00",
                        "last_login": "2024-01-09T12:00:00"
                    }
                }
            }
        }
    }
)
def get_current_user(
    session: Session = Depends(get_db_session),
    use_case: UserManagementUseCase = Depends(get_user_management_use_case)
):
    """
    获取当前用户

    本地模式：返回第一个用户，如果不存在则自动创建默认用户
    """
    logger.info("api_v2_get_current_user")
    return use_case.get_current_user()


@router.get(
    "/{user_id}",
    response_model=UserResponseDTO,
    summary="获取指定用户",
    description="根据用户ID获取用户信息",
    responses={
        200: {"description": "成功获取用户"},
        404: {"description": "用户不存在"}
    }
)
def get_user(
    user_id: int,
    session: Session = Depends(get_db_session),
    use_case: UserManagementUseCase = Depends(get_user_management_use_case)
):
    """
    获取指定用户

    - **user_id**: 用户ID
    """
    logger.info("api_v2_get_user", user_id=user_id)
    return use_case.get_user_by_id(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponseDTO,
    summary="更新用户",
    description="更新用户信息",
    responses={
        200: {"description": "用户更新成功"},
        404: {"description": "用户不存在"},
        422: {"description": "请求参数验证失败"}
    }
)
def update_user(
    user_id: int,
    request: UserUpdateDTO,
    session: Session = Depends(get_db_session),
    use_case: UserManagementUseCase = Depends(get_user_management_use_case)
):
    """
    更新用户

    - **user_id**: 用户ID
    - **full_name**: 全名（可选）
    - **settings**: 用户设置（可选）
    """
    logger.info("api_v2_update_user", user_id=user_id)
    return use_case.update_user(user_id, request)


@router.post(
    "/{user_id}/login",
    response_model=UserResponseDTO,
    summary="记录用户登录",
    description="记录用户登录时间",
    responses={
        200: {"description": "登录记录成功"},
        404: {"description": "用户不存在"}
    }
)
def record_login(
    user_id: int,
    session: Session = Depends(get_db_session),
    use_case: UserManagementUseCase = Depends(get_user_management_use_case)
):
    """
    记录用户登录

    - **user_id**: 用户ID
    """
    logger.info("api_v2_record_login", user_id=user_id)
    return use_case.record_login(user_id)
