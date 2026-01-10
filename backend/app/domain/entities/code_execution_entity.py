"""
Code Execution Domain Entity

代码执行领域实体：封装代码执行相关的业务逻辑
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(str, Enum):
    """执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class CodeExecutionEntity:
    """
    代码执行领域实体

    职责：
    - 封装代码执行的业务逻辑
    - 验证代码的安全性
    - 记录执行结果和状态
    """

    code: str
    language: str = "python"
    timeout: int = 30
    user_id: Optional[int] = None
    lesson_id: Optional[int] = None

    # 执行结果
    status: ExecutionStatus = ExecutionStatus.PENDING
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    executed_at: Optional[datetime] = None

    def __post_init__(self):
        """初始化后验证"""
        self.validate()

    def validate(self):
        """
        验证代码执行请求

        Raises:
            ValueError: 验证失败
        """
        if not self.code or not self.code.strip():
            raise ValueError("Code cannot be empty")

        if len(self.code) > 10000:
            raise ValueError(f"Code length exceeds limit (max 10KB, got {len(self.code)} bytes)")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

        if self.timeout > 300:
            raise ValueError("Timeout exceeds maximum (300 seconds)")

        if self.language not in ['python', 'javascript', 'go']:
            raise ValueError(f"Unsupported language: {self.language}")

    def check_security(self):
        """
        检查代码安全性

        Raises:
            ValueError: 代码包含不安全的操作
        """
        dangerous_patterns = [
            ('os.system', '禁止使用 os.system'),
            ('subprocess.', '禁止使用 subprocess 模块'),
            ('eval(', '禁止使用 eval'),
            ('exec(', '禁止使用 exec'),
            ('compile(', '禁止使用 compile'),
            ('__import__', '禁止使用 __import__'),
            ('open(', '禁止使用 open 函数'),
            ('file(', '禁止使用 file 函数'),
            ('input(', '禁止使用 input 函数'),
            ('raw_input(', '禁止使用 raw_input 函数'),
        ]

        for pattern, message in dangerous_patterns:
            if pattern in self.code:
                raise ValueError(f"Security check failed: {message}")

    def mark_as_running(self):
        """标记为执行中"""
        self.status = ExecutionStatus.RUNNING
        self.executed_at = datetime.utcnow()

    def mark_as_success(self, output: str, execution_time: float):
        """
        标记为执行成功

        Args:
            output: 执行输出
            execution_time: 执行时间（秒）
        """
        self.status = ExecutionStatus.SUCCESS
        self.output = output
        self.execution_time = execution_time

    def mark_as_failed(self, error: str, execution_time: float = 0.0):
        """
        标记为执行失败

        Args:
            error: 错误信息
            execution_time: 执行时间（秒）
        """
        self.status = ExecutionStatus.FAILED
        self.error = error
        self.execution_time = execution_time

    def mark_as_timeout(self):
        """标记为超时"""
        self.status = ExecutionStatus.TIMEOUT
        self.error = f"Execution timeout (>{self.timeout}s)"
        self.execution_time = float(self.timeout)

    def is_successful(self) -> bool:
        """判断是否执行成功"""
        return self.status == ExecutionStatus.SUCCESS

    def to_dict(self):
        """转换为字典"""
        return {
            'code': self.code,
            'language': self.language,
            'timeout': self.timeout,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'status': self.status.value,
            'output': self.output,
            'error': self.error,
            'execution_time': self.execution_time,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
        }
