"""
Code Execution Domain Service

代码执行领域服务：封装代码执行的核心业务逻辑
"""

from abc import ABC, abstractmethod
from typing import Tuple
from app.domain.entities.code_execution_entity import CodeExecutionEntity


class ICodeExecutionService(ABC):
    """
    代码执行服务接口

    定义代码执行的核心业务操作
    """

    @abstractmethod
    def execute(self, execution: CodeExecutionEntity) -> Tuple[bool, str, float]:
        """
        执行代码

        Args:
            execution: 代码执行实体

        Returns:
            (成功标志, 输出/错误信息, 执行时间)

        Raises:
            ValidationError: 代码验证失败
            SandboxExecutionError: 沙箱执行错误
            TimeoutError: 执行超时
        """
        pass

    @abstractmethod
    def validate_code(self, code: str) -> None:
        """
        验证代码安全性

        Args:
            code: 要验证的代码

        Raises:
            ValidationError: 代码不安全
        """
        pass

    @abstractmethod
    def get_execution_stats(self) -> dict:
        """
        获取执行统计信息

        Returns:
            统计信息字典
        """
        pass
