"""
User Repository Interface

用户仓储接口：定义用户数据访问的抽象方法
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user_entity import UserEntity


class IUserRepository(ABC):
    """
    用户仓储接口

    定义用户数据访问的所有操作，具体实现由 Infrastructure 层提供
    """

    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        """
        创建用户

        Args:
            user: 用户实体

        Returns:
            创建后的用户实体（包含ID）

        Raises:
            ConflictError: 用户已存在
        """
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户实体，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserEntity]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户实体，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def get_first(self) -> Optional[UserEntity]:
        """
        获取第一个用户

        Returns:
            用户实体，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def update(self, user: UserEntity) -> UserEntity:
        """
        更新用户

        Args:
            user: 用户实体

        Returns:
            更新后的用户实体

        Raises:
            ResourceNotFoundError: 用户不存在
        """
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """
        删除用户

        Args:
            user_id: 用户ID

        Returns:
            删除成功返回 True，用户不存在返回 False
        """
        pass

    @abstractmethod
    def list_all(self, limit: int = 100, offset: int = 0) -> List[UserEntity]:
        """
        列出所有用户

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            用户实体列表
        """
        pass

    @abstractmethod
    def exists(self, username: str) -> bool:
        """
        检查用户是否存在

        Args:
            username: 用户名

        Returns:
            存在返回 True，否则返回 False
        """
        pass
