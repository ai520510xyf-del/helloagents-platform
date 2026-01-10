"""
User Management Use Case

用户管理用例：封装用户管理的业务流程
"""

from typing import Optional
from app.domain.entities.user_entity import UserEntity
from app.domain.repositories.user_repository import IUserRepository
from app.application.dto.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserResponseDTO
)
from app.logger import get_logger
from app.exceptions import ConflictError, ResourceNotFoundError

logger = get_logger(__name__)


class UserManagementUseCase:
    """
    用户管理用例

    职责：
    1. 协调用户的创建、查询、更新、删除
    2. 确保用户名的唯一性
    3. 处理用户登录记录
    """

    def __init__(self, user_repository: IUserRepository):
        """
        初始化用例

        Args:
            user_repository: 用户仓储
        """
        self.user_repository = user_repository

    def create_user(self, request: UserCreateDTO) -> UserResponseDTO:
        """
        创建用户

        Args:
            request: 用户创建请求DTO

        Returns:
            用户响应DTO

        Raises:
            ConflictError: 用户名已存在
        """
        logger.info("create_user_use_case_started", username=request.username)

        # 检查用户名是否已存在
        if self.user_repository.exists(request.username):
            raise ConflictError(
                message=f"用户名 '{request.username}' 已存在",
                resource="user"
            )

        # 创建用户实体
        user = UserEntity(
            username=request.username,
            full_name=request.full_name,
            settings=request.settings or {}
        )

        # 保存到仓储
        created_user = self.user_repository.create(user)

        logger.info(
            "create_user_use_case_completed",
            user_id=created_user.id,
            username=created_user.username
        )

        # 返回响应DTO
        return self._to_response_dto(created_user)

    def get_user_by_id(self, user_id: int) -> UserResponseDTO:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户响应DTO

        Raises:
            ResourceNotFoundError: 用户不存在
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(
                resource="User",
                resource_id=str(user_id)
            )

        return self._to_response_dto(user)

    def get_current_user(self) -> UserResponseDTO:
        """
        获取当前用户（本地模式：返回第一个用户）

        如果不存在用户，则创建默认用户

        Returns:
            用户响应DTO
        """
        user = self.user_repository.get_first()

        if not user:
            # 创建默认用户
            logger.info("creating_default_user")
            default_user = UserEntity(
                username="local_user",
                full_name="本地用户",
                settings={
                    "theme": "dark",
                    "editor": {
                        "fontSize": 14,
                        "tabSize": 4,
                        "wordWrap": True
                    }
                }
            )
            user = self.user_repository.create(default_user)

        return self._to_response_dto(user)

    def update_user(self, user_id: int, request: UserUpdateDTO) -> UserResponseDTO:
        """
        更新用户

        Args:
            user_id: 用户ID
            request: 用户更新请求DTO

        Returns:
            用户响应DTO

        Raises:
            ResourceNotFoundError: 用户不存在
        """
        logger.info("update_user_use_case_started", user_id=user_id)

        # 获取用户
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(
                resource="User",
                resource_id=str(user_id)
            )

        # 更新用户配置
        user.update_profile(
            full_name=request.full_name,
            settings=request.settings
        )

        # 保存更新
        updated_user = self.user_repository.update(user)

        logger.info("update_user_use_case_completed", user_id=user_id)

        return self._to_response_dto(updated_user)

    def record_login(self, user_id: int) -> UserResponseDTO:
        """
        记录用户登录

        Args:
            user_id: 用户ID

        Returns:
            用户响应DTO

        Raises:
            ResourceNotFoundError: 用户不存在
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(
                resource="User",
                resource_id=str(user_id)
            )

        # 记录登录时间
        user.record_login()

        # 保存更新
        updated_user = self.user_repository.update(user)

        logger.info("user_login_recorded", user_id=user_id)

        return self._to_response_dto(updated_user)

    def _to_response_dto(self, user: UserEntity) -> UserResponseDTO:
        """
        将用户实体转换为响应DTO

        Args:
            user: 用户实体

        Returns:
            用户响应DTO
        """
        user_dict = user.to_dict()
        return UserResponseDTO(**user_dict)
