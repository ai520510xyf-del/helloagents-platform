"""
Dependency Injection Container

依赖注入容器：管理应用的所有依赖关系，实现控制反转(IoC)
"""

from typing import Dict, Any, Callable
from sqlalchemy.orm import Session

from app.domain.repositories.user_repository import IUserRepository
from app.domain.services.code_execution_service import ICodeExecutionService

from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.external_services.docker_code_execution_service import DockerCodeExecutionService

from app.application.use_cases.user_management_use_case import UserManagementUseCase
from app.application.use_cases.execute_code_use_case import ExecuteCodeUseCase

from app.database import SessionLocal
from app.logger import get_logger

logger = get_logger(__name__)


class Container:
    """
    依赖注入容器

    职责：
    1. 管理服务的生命周期
    2. 解析和注入依赖
    3. 提供服务定位功能

    模式：Service Locator + Dependency Injection
    """

    def __init__(self):
        """初始化容器"""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}

        # 注册服务
        self._register_services()

        logger.info("dependency_injection_container_initialized")

    def _register_services(self):
        """注册所有服务"""

        # ============================================
        # Infrastructure Layer - Repositories
        # ============================================

        self._factories['user_repository'] = lambda: UserRepositoryImpl(
            session=self.get('db_session')
        )

        # ============================================
        # Infrastructure Layer - External Services
        # ============================================

        # 代码执行服务 (单例)
        self._singletons['code_execution_service'] = DockerCodeExecutionService()

        # ============================================
        # Application Layer - Use Cases
        # ============================================

        self._factories['user_management_use_case'] = lambda: UserManagementUseCase(
            user_repository=self.get('user_repository')
        )

        self._factories['execute_code_use_case'] = lambda: ExecuteCodeUseCase(
            execution_service=self.get('code_execution_service')
        )

        logger.debug("services_registered", count=len(self._factories) + len(self._singletons))

    def get(self, service_name: str) -> Any:
        """
        获取服务实例

        Args:
            service_name: 服务名称

        Returns:
            服务实例

        Raises:
            KeyError: 服务未注册
        """
        # 1. 检查单例缓存
        if service_name in self._singletons:
            return self._singletons[service_name]

        # 2. 检查服务工厂
        if service_name in self._factories:
            return self._factories[service_name]()

        # 3. 检查已注册服务
        if service_name in self._services:
            return self._services[service_name]

        # 4. 特殊处理：数据库会话（每次请求创建新会话）
        if service_name == 'db_session':
            return SessionLocal()

        # 5. 服务未找到
        raise KeyError(f"Service '{service_name}' not registered in container")

    def register(self, service_name: str, service: Any):
        """
        注册服务实例

        Args:
            service_name: 服务名称
            service: 服务实例
        """
        self._services[service_name] = service
        logger.debug("service_registered", service_name=service_name)

    def register_factory(self, service_name: str, factory: Callable):
        """
        注册服务工厂

        Args:
            service_name: 服务名称
            factory: 服务工厂函数
        """
        self._factories[service_name] = factory
        logger.debug("service_factory_registered", service_name=service_name)

    def register_singleton(self, service_name: str, service: Any):
        """
        注册单例服务

        Args:
            service_name: 服务名称
            service: 服务实例
        """
        self._singletons[service_name] = service
        logger.debug("singleton_registered", service_name=service_name)


# 创建全局容器实例
container = Container()


# ============================================
# FastAPI 依赖注入辅助函数
# ============================================

def get_container() -> Container:
    """
    获取容器实例（用于FastAPI依赖注入）

    Returns:
        容器实例
    """
    return container


def get_db_session() -> Session:
    """
    获取数据库会话（用于FastAPI依赖注入）

    每次请求创建新会话，请求结束后自动关闭

    Yields:
        数据库会话
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_user_management_use_case(session: Session) -> UserManagementUseCase:
    """
    获取用户管理用例（用于FastAPI依赖注入）

    Args:
        session: 数据库会话

    Returns:
        用户管理用例实例
    """
    user_repository = UserRepositoryImpl(session)
    return UserManagementUseCase(user_repository)


def get_execute_code_use_case() -> ExecuteCodeUseCase:
    """
    获取代码执行用例（用于FastAPI依赖注入）

    Returns:
        代码执行用例实例
    """
    code_execution_service = container.get('code_execution_service')
    return ExecuteCodeUseCase(code_execution_service)
