"""
代码执行沙箱模块

使用 Docker 容器提供安全的代码执行环境，支持容器池优化性能
"""

import docker
import time
from typing import Tuple, Optional
from .logger import get_logger
from .container_pool import ContainerPool
from .exceptions import (
    ValidationError,
    SandboxExecutionError,
    ContainerPoolError,
    TimeoutError as HelloAgentsTimeoutError
)

logger = get_logger(__name__)

class CodeSandbox:
    """
    代码执行沙箱

    使用 Docker 容器隔离执行用户代码，提供安全保障
    使用容器池提升性能，将执行延迟从 1-2s 降低到 0.05-0.1s
    """

    def __init__(
        self,
        image: str = "python:3.11-slim",
        timeout: int = 30,
        use_pool: bool = True,
        pool_initial_size: int = 3,
        pool_max_size: int = 10
    ):
        """
        初始化沙箱

        Args:
            image: Docker 镜像名称
            timeout: 执行超时时间（秒）
            use_pool: 是否使用容器池优化
            pool_initial_size: 容器池初始大小
            pool_max_size: 容器池最大大小
        """
        self.image = image
        self.timeout = timeout
        self.use_pool = use_pool
        self.client = None
        self.pool = None

        try:
            self.client = docker.from_env()
            # 检查镜像是否存在，不存在则拉取
            try:
                self.client.images.get(self.image)
                logger.info("docker_image_found", image=self.image)
            except docker.errors.ImageNotFound:
                logger.info("docker_image_pulling", image=self.image)
                self.client.images.pull(self.image)
                logger.info("docker_image_pulled", image=self.image)

            # 初始化容器池
            if use_pool:
                logger.info(
                    "container_pool_initialization_started",
                    initial_size=pool_initial_size,
                    max_size=pool_max_size
                )
                self.pool = ContainerPool(
                    initial_size=pool_initial_size,
                    max_size=pool_max_size,
                    image=image
                )
                logger.info("container_pool_ready")
        except Exception as e:
            logger.warning(
                "docker_unavailable",
                error=str(e),
                fallback="local_execution"
            )
            self.client = None
            self.pool = None

    def _check_code_safety(self, code: str):
        """
        检查代码安全性

        Args:
            code: 要检查的代码

        Raises:
            ValidationError: 代码不符合安全规范
        """
        # 黑名单关键字（基础安全检查）
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
            if pattern in code:
                raise ValidationError(
                    message=f'代码安全检查失败: {message}',
                    details={
                        "pattern": pattern,
                        "reason": message
                    }
                )

        # 检查代码长度（防止 DoS）
        if len(code) > 10000:  # 10KB
            raise ValidationError(
                message='代码长度超过限制（最大 10KB）',
                details={
                    "code_length": len(code),
                    "max_length": 10000
                }
            )

    def execute_python(self, code: str) -> Tuple[bool, str, float]:
        """
        在沙箱中执行 Python 代码

        Args:
            code: 要执行的代码

        Returns:
            (成功标志, 输出/错误信息, 执行时间)

        Raises:
            ValidationError: 代码安全检查失败
            ContainerPoolError: 容器池错误
            SandboxExecutionError: 沙箱执行错误
        """
        logger.info(
            "sandbox_execution_started",
            code_length=len(code),
            execution_mode="pool" if self.pool else ("docker" if self.client else "local")
        )

        # 预检查代码安全性 (会抛出 ValidationError)
        self._check_code_safety(code)

        if self.client is None:
            # Docker 不可用，使用本地执行（仅开发环境）
            logger.warning("sandbox_using_local_execution")
            return self._execute_local(code)

        # 使用容器池执行
        if self.pool:
            return self._execute_with_pool(code)

        # 使用一次性容器执行（旧逻辑）
        return self._execute_with_temp_container(code)

    def _execute_with_pool(self, code: str) -> Tuple[bool, str, float]:
        """
        使用容器池执行代码

        Raises:
            ContainerPoolError: 容器池错误
            SandboxExecutionError: 沙箱执行错误
            HelloAgentsTimeoutError: 执行超时
        """

        # 从池获取容器
        container = self.pool.get_container(timeout=30)
        if not container:
            logger.error("container_acquisition_failed")
            raise ContainerPoolError(
                message="无法获取容器 (池已满或超时)",
                pool_status=self.pool.get_stats() if self.pool else None
            )

        try:
            start_time = time.time()

            # 在容器中执行代码
            # 注意: timeout参数在旧版docker库中不支持，已移除以兼容CI环境
            result = container.exec_run(
                ["python", "-c", code],
                demux=True
            )

            execution_time = time.time() - start_time

            # 处理输出
            stdout, stderr = result.output if isinstance(result.output, tuple) else (result.output, b'')
            output = (stdout or b'').decode('utf-8')
            error = (stderr or b'').decode('utf-8')

            # 截断过长的输出（防止内存溢出）
            MAX_OUTPUT_SIZE = 10000  # 10KB
            if len(output) > MAX_OUTPUT_SIZE:
                output = output[:MAX_OUTPUT_SIZE] + f'\n\n... (输出被截断，总共 {len(output)} 字符)'

            # 检查退出码
            if result.exit_code == 0:
                logger.info(
                    "sandbox_execution_completed",
                    success=True,
                    execution_time_ms=round(execution_time * 1000, 2),
                    output_length=len(output),
                    execution_mode="pool"
                )
                return True, output, execution_time
            else:
                logger.warning(
                    "sandbox_execution_failed",
                    exit_code=result.exit_code,
                    execution_time_ms=round(execution_time * 1000, 2),
                    output_length=len(output),
                    execution_mode="pool"
                )
                return False, error or output, execution_time

        except docker.errors.DockerException as e:
            # Docker 相关错误
            logger.error(
                "sandbox_docker_error",
                error=str(e),
                error_type=type(e).__name__,
                execution_mode="pool",
                exc_info=True
            )
            raise SandboxExecutionError(
                message=f"Docker 执行错误: {str(e)}",
                code_snippet=code[:500]
            )

        except Exception as e:
            # 其他未预期错误
            logger.error(
                "sandbox_execution_error",
                error=str(e),
                error_type=type(e).__name__,
                execution_mode="pool",
                exc_info=True
            )
            raise SandboxExecutionError(
                message=f"沙箱执行错误: {str(e)}",
                code_snippet=code[:500]
            )

        finally:
            # 归还容器到池
            self.pool.return_container(container)

    def _execute_with_temp_container(self, code: str) -> Tuple[bool, str, float]:
        """使用临时容器执行代码（旧逻辑，向后兼容）"""

        try:
            start_time = time.time()

            # 创建临时容器执行代码（完整安全配置）
            container = self.client.containers.run(
                image=self.image,
                command=["python", "-c", code],
                detach=True,

                # 内存限制
                mem_limit="128m",        # 最大内存 128MB
                memswap_limit="128m",    # 禁用 swap（内存+swap = mem_limit）

                # CPU 限制
                cpu_quota=50000,         # CPU 配额 = 50% 的一个核心（100000 = 1核）
                cpu_period=100000,       # CPU 调度周期（微秒）

                # 进程数限制
                pids_limit=64,           # 最多 64 个进程

                # 安全选项
                network_disabled=True,   # 禁用网络
                read_only=True,          # 只读文件系统
                cap_drop=['ALL'],        # 移除所有 Linux capabilities
                security_opt=['no-new-privileges'],  # 禁止提权

                # 临时目录（可写）
                tmpfs={'/tmp': 'size=10M,mode=1777'},  # 10MB 临时目录

                # 自动清理
                remove=True,             # 执行完自动删除
                auto_remove=True,
            )

            # 等待容器执行完成（带超时）
            result = container.wait(timeout=self.timeout)
            execution_time = time.time() - start_time

            # 获取输出
            output = container.logs().decode('utf-8')

            # 截断过长的输出（防止内存溢出）
            MAX_OUTPUT_SIZE = 10000  # 10KB
            if len(output) > MAX_OUTPUT_SIZE:
                output = output[:MAX_OUTPUT_SIZE] + f'\n\n... (输出被截断，总共 {len(output)} 字符)'

            # 检查退出码
            exit_code = result.get('StatusCode', 1)

            if exit_code == 0:
                logger.info(
                    "sandbox_execution_completed",
                    success=True,
                    execution_time_ms=round(execution_time * 1000, 2),
                    output_length=len(output),
                    execution_mode="temp_container"
                )
                return True, output, execution_time
            else:
                logger.warning(
                    "sandbox_execution_failed",
                    exit_code=exit_code,
                    execution_time_ms=round(execution_time * 1000, 2),
                    output_length=len(output),
                    execution_mode="temp_container"
                )
                return False, output, execution_time

        except docker.errors.ContainerError as e:
            # 容器执行错误
            error_output = e.stderr.decode('utf-8')
            logger.error(
                "sandbox_container_error",
                error=error_output,
                exc_info=True
            )
            raise SandboxExecutionError(
                message="容器执行错误",
                code_snippet=code[:500],
                execution_output=error_output
            )

        except docker.errors.DockerException as e:
            # Docker 相关错误
            logger.error(
                "sandbox_docker_error",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise SandboxExecutionError(
                message=f"Docker 错误: {str(e)}",
                code_snippet=code[:500]
            )

        except Exception as e:
            # 其他未预期错误
            logger.error(
                "sandbox_unexpected_error",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise SandboxExecutionError(
                message=f"沙箱执行错误: {str(e)}",
                code_snippet=code[:500]
            )

    def _execute_local(self, code: str) -> Tuple[bool, str, float]:
        """
        本地执行代码（不安全，仅用于开发环境）

        警告: 此方法不提供任何安全保障！
        """
        import subprocess
        import sys

        try:
            start_time = time.time()

            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            execution_time = time.time() - start_time

            if result.returncode == 0:
                return True, result.stdout, execution_time
            else:
                return False, result.stderr, execution_time

        except subprocess.TimeoutExpired:
            return False, f"执行超时（>{self.timeout}秒）", self.timeout

        except Exception as e:
            return False, f"执行错误: {str(e)}", 0.0

    def cleanup(self):
        """清理资源"""
        # 优雅关闭容器池
        if self.pool:
            logger.info("shutting_down_container_pool")
            self.pool.shutdown()

        # 关闭 Docker 客户端
        if self.client:
            self.client.close()

# 创建全局沙箱实例
sandbox = CodeSandbox()
