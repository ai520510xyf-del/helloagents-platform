"""
Docker Code Execution Service

基于Docker的代码执行服务实现
"""

from typing import Tuple
from app.domain.entities.code_execution_entity import CodeExecutionEntity
from app.domain.services.code_execution_service import ICodeExecutionService
from app.sandbox import sandbox
from app.logger import get_logger
from app.exceptions import ValidationError, SandboxExecutionError

logger = get_logger(__name__)


class DockerCodeExecutionService(ICodeExecutionService):
    """
    Docker代码执行服务

    使用Docker容器池实现安全的代码执行
    """

    def __init__(self):
        """初始化服务"""
        self.sandbox = sandbox

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
        """
        logger.info(
            "docker_code_execution_started",
            code_length=len(execution.code),
            language=execution.language,
            timeout=execution.timeout
        )

        try:
            # 验证代码（会抛出 ValidationError）
            self.validate_code(execution.code)

            # 使用沙箱执行代码
            success, output, exec_time = self.sandbox.execute_python(execution.code)

            logger.info(
                "docker_code_execution_completed",
                success=success,
                execution_time_ms=round(exec_time * 1000, 2),
                output_length=len(output)
            )

            return success, output, exec_time

        except ValidationError:
            # 验证错误 - 直接向上抛出
            raise

        except Exception as e:
            # 沙箱执行错误 - 包装为 SandboxExecutionError
            logger.error(
                "docker_code_execution_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise SandboxExecutionError(
                message=f"Docker执行错误: {str(e)}",
                code_snippet=execution.code[:500]
            )

    def validate_code(self, code: str) -> None:
        """
        验证代码安全性

        Args:
            code: 要验证的代码

        Raises:
            ValidationError: 代码不安全
        """
        # 使用沙箱的安全检查
        self.sandbox._check_code_safety(code)

    def get_execution_stats(self) -> dict:
        """
        获取执行统计信息

        Returns:
            统计信息字典
        """
        if self.sandbox.pool:
            return self.sandbox.pool.get_stats()

        return {
            "pool_enabled": False,
            "message": "Container pool is not enabled"
        }
