"""
User Repository Implementation

用户仓储实现：使用SQLAlchemy实现用户数据访问
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json

from app.domain.entities.user_entity import UserEntity
from app.domain.repositories.user_repository import IUserRepository
from app.models.user import User
from app.exceptions import ConflictError, DatabaseError
from app.logger import get_logger

logger = get_logger(__name__)


class UserRepositoryImpl(IUserRepository):
    """
    用户仓储实现

    使用SQLAlchemy ORM进行数据持久化
    """

    def __init__(self, session: Session):
        """
        初始化仓储

        Args:
            session: SQLAlchemy数据库会话
        """
        self.session = session

    def create(self, user: UserEntity) -> UserEntity:
        """创建用户"""
        try:
            # 转换为ORM模型
            db_user = User(
                username=user.username,
                full_name=user.full_name,
                settings=json.dumps(user.settings)
            )

            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)

            logger.info("user_created", user_id=db_user.id, username=db_user.username)

            # 转换回实体
            return self._to_entity(db_user)

        except IntegrityError as e:
            self.session.rollback()
            logger.warning("user_creation_failed_duplicate", username=user.username)
            raise ConflictError(
                message=f"用户名 '{user.username}' 已存在",
                resource="user"
            )

        except Exception as e:
            self.session.rollback()
            logger.error("user_creation_failed", error=str(e), exc_info=True)
            raise DatabaseError(
                message="创建用户失败",
                operation="create_user"
            )

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """根据ID获取用户"""
        try:
            db_user = self.session.query(User).filter(User.id == user_id).first()

            if db_user:
                return self._to_entity(db_user)

            return None

        except Exception as e:
            logger.error("user_query_failed", user_id=user_id, error=str(e), exc_info=True)
            raise DatabaseError(
                message="查询用户失败",
                operation="get_user_by_id"
            )

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        """根据用户名获取用户"""
        try:
            db_user = self.session.query(User).filter(User.username == username).first()

            if db_user:
                return self._to_entity(db_user)

            return None

        except Exception as e:
            logger.error("user_query_failed", username=username, error=str(e), exc_info=True)
            raise DatabaseError(
                message="查询用户失败",
                operation="get_user_by_username"
            )

    def get_first(self) -> Optional[UserEntity]:
        """获取第一个用户"""
        try:
            db_user = self.session.query(User).first()

            if db_user:
                return self._to_entity(db_user)

            return None

        except Exception as e:
            logger.error("user_query_failed", error=str(e), exc_info=True)
            raise DatabaseError(
                message="查询用户失败",
                operation="get_first_user"
            )

    def update(self, user: UserEntity) -> UserEntity:
        """更新用户"""
        try:
            db_user = self.session.query(User).filter(User.id == user.id).first()

            if not db_user:
                raise DatabaseError(
                    message=f"用户不存在: {user.id}",
                    operation="update_user"
                )

            # 更新字段
            db_user.full_name = user.full_name
            db_user.settings = json.dumps(user.settings)
            db_user.updated_at = user.updated_at.isoformat() if user.updated_at else None
            db_user.last_login = user.last_login.isoformat() if user.last_login else None

            self.session.commit()
            self.session.refresh(db_user)

            logger.info("user_updated", user_id=db_user.id)

            return self._to_entity(db_user)

        except Exception as e:
            self.session.rollback()
            logger.error("user_update_failed", user_id=user.id, error=str(e), exc_info=True)
            raise DatabaseError(
                message="更新用户失败",
                operation="update_user"
            )

    def delete(self, user_id: int) -> bool:
        """删除用户"""
        try:
            db_user = self.session.query(User).filter(User.id == user_id).first()

            if not db_user:
                return False

            self.session.delete(db_user)
            self.session.commit()

            logger.info("user_deleted", user_id=user_id)

            return True

        except Exception as e:
            self.session.rollback()
            logger.error("user_deletion_failed", user_id=user_id, error=str(e), exc_info=True)
            raise DatabaseError(
                message="删除用户失败",
                operation="delete_user"
            )

    def list_all(self, limit: int = 100, offset: int = 0) -> List[UserEntity]:
        """列出所有用户"""
        try:
            db_users = self.session.query(User).limit(limit).offset(offset).all()
            return [self._to_entity(db_user) for db_user in db_users]

        except Exception as e:
            logger.error("user_list_failed", error=str(e), exc_info=True)
            raise DatabaseError(
                message="列出用户失败",
                operation="list_users"
            )

    def exists(self, username: str) -> bool:
        """检查用户是否存在"""
        try:
            count = self.session.query(User).filter(User.username == username).count()
            return count > 0

        except Exception as e:
            logger.error("user_exists_check_failed", username=username, error=str(e), exc_info=True)
            raise DatabaseError(
                message="检查用户是否存在失败",
                operation="user_exists"
            )

    def _to_entity(self, db_user: User) -> UserEntity:
        """
        将ORM模型转换为领域实体

        Args:
            db_user: SQLAlchemy ORM模型

        Returns:
            用户领域实体
        """
        return UserEntity.from_dict(db_user.to_dict())
