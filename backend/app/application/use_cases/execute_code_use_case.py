"""
Execute Code Use Case

代码执行用例：协调代码执行的完整业务流程
"""

from typing import Optional
from app.domain.entities.code_execution_entity import CodeExecutionEntity, ExecutionStatus
from app.domain.services.code_execution_service import ICodeExecutionService
from app.application.dto.code_execution_dto import (
    CodeExecutionRequestDTO,
    CodeExecutionResponseDTO
)
from app.logger import get_logger
from app.exceptions import ValidationError, SandboxExecutionError

logger = get_logger(__name__)


class ExecuteCodeUseCase:
    """
    代码执行用例

    职责：
    1. 验证代码安全性
    2. 调用领域服务执行代码
    3. 记录执行结果
    4. 返回标准化响应
    """

    def __init__(self, execution_service: ICodeExecutionService):
        """
        初始化用例

        Args:
            execution_service: 代码执行服务
        """
        self.execution_service = execution_service

    def execute(self, request: CodeExecutionRequestDTO) -> CodeExecutionResponseDTO:
        """
        执行代码

        Args:
            request: 代码执行请求DTO

        Returns:
            代码执行响应DTO

        Raises:
            ValidationError: 代码验证失败
            SandboxExecutionError: 执行错误
        """
        logger.info(
            "execute_code_use_case_started",
            code_length=len(request.code),
            language=request.language,
            timeout=request.timeout,
            user_id=request.user_id,
            lesson_id=request.lesson_id
        )

        try:
            # 创建执行实体
            execution = CodeExecutionEntity(
                code=request.code,
                language=request.language,
                timeout=request.timeout,
                user_id=request.user_id,
                lesson_id=request.lesson_id
            )

            # 验证代码安全性（会抛出 ValidationError）
            execution.check_security()

            # 标记为执行中
            execution.mark_as_running()

            # 执行代码（委托给领域服务）
            success, output, execution_time = self.execution_service.execute(execution)

            # 更新执行状态
            if success:
                execution.mark_as_success(output, execution_time)
            else:
                execution.mark_as_failed(output, execution_time)

            # 记录执行完成
            logger.info(
                "execute_code_use_case_completed",
                success=success,
                execution_time_ms=round(execution_time * 1000, 2),
                output_length=len(output),
                status=execution.status.value
            )

            # 返回响应DTO
            return CodeExecutionResponseDTO(
                success=success,
                output=output if success else "",
                error=output if not success else None,
                execution_time=execution_time,
                status=execution.status.value
            )

        except ValidationError as e:
            # 验证错误 - 直接抛出让上层处理
            logger.warning(
                "execute_code_validation_failed",
                error=str(e),
                code_length=len(request.code)
            )
            raise

        except SandboxExecutionError as e:
            # 沙箱执行错误 - 直接抛出让上层处理
            logger.error(
                "execute_code_sandbox_error",
                error=str(e),
                code_length=len(request.code),
                exc_info=True
            )
            raise

        except Exception as e:
            # 未预期错误 - 包装为 SandboxExecutionError
            logger.error(
                "execute_code_unexpected_error",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise SandboxExecutionError(
                message=f"代码执行失败: {str(e)}",
                code_snippet=request.code[:500]
            )
