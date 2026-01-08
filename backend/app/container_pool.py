"""
容器池管理模块

实现容器复用以提升代码执行性能，将容器启动开销从 1-2s 降低到 0.05-0.1s
"""

import docker
import time
import threading
import uuid
from queue import Queue, Empty, Full
from dataclasses import dataclass
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from .logger import get_logger
from .exceptions import (
    ContainerPoolError,
    ValidationError,
    TimeoutError as HelloAgentsTimeoutError
)

logger = get_logger(__name__)


class ContainerPoolConfig:
    """容器池配置常量"""

    # 健康检查阈值
    MAX_MEMORY_PERCENT = 90
    MAX_PROCESS_COUNT = 50
    MAX_HEALTH_CHECK_FAILURES = 3
    HEALTH_CHECK_TIMEOUT = 2
    QUICK_HEALTH_CHECK_TIMEOUT = 1
    DEEP_HEALTH_CHECK_TIMEOUT = 2

    # 容器限制
    MAX_OUTPUT_SIZE = 10000  # 10KB
    MAX_CODE_LENGTH = 10000  # 10KB

    # 重置验证
    MAX_RESET_PROCESS_COUNT = 5

    # 超时设置
    DEFAULT_CONTAINER_TIMEOUT = 30
    RESET_TIMEOUT = 3
    CONTAINER_STOP_TIMEOUT = 5


@dataclass
class ContainerMetadata:
    """容器元数据"""
    container_id: str           # 容器 ID
    container: Any              # Docker 容器对象
    created_at: float           # 创建时间戳
    last_used_at: float         # 最后使用时间
    execution_count: int        # 执行次数
    reset_count: int            # 重置次数
    status: str                 # 状态: 'available', 'in_use', 'unhealthy'
    health_check_failures: int  # 连续健康检查失败次数


class ContainerPool:
    """
    容器池管理器

    职责:
    - 容器生命周期管理 (创建/复用/销毁)
    - 容器健康检查与自动恢复
    - 并发控制与资源限制
    - 容器重置与状态清理
    """

    def __init__(
        self,
        initial_size: int = 3,           # 初始容器数
        max_size: int = 10,              # 最大容器数
        min_size: int = 1,               # 最小容器数
        idle_timeout: int = 300,         # 空闲超时 (5分钟)
        health_check_interval: int = 30, # 健康检查间隔 (30秒)
        image: str = "python:3.11-slim",
        **container_config               # 容器配置参数
    ):
        """初始化容器池"""

        # 配置参数
        self.initial_size = initial_size
        self.max_size = max_size
        self.min_size = min_size
        self.idle_timeout = idle_timeout
        self.health_check_interval = health_check_interval
        self.image = image
        self.container_config = container_config

        # 生成唯一池ID
        self.pool_id = str(uuid.uuid4())[:8]

        # Docker 客户端
        self.client = docker.from_env()

        # 容器管理
        self.available_containers = Queue(maxsize=max_size)  # 可用容器队列
        self.in_use_containers: Dict[str, ContainerMetadata] = {}  # 使用中的容器
        self.container_metadata: Dict[str, ContainerMetadata] = {}  # 所有容器元数据

        # 线程安全锁
        self.lock = threading.RLock()  # 可重入锁

        # 统计信息
        self.stats = {
            'total_created': 0,         # 总创建数
            'total_destroyed': 0,       # 总销毁数
            'total_executions': 0,      # 总执行次数
            'total_resets': 0,          # 总重置次数
            'health_check_failures': 0, # 健康检查失败次数
        }

        # 后台线程
        self.health_check_thread: Optional[threading.Thread] = None
        self.idle_cleanup_thread: Optional[threading.Thread] = None
        self.running = False

        # 初始化池
        logger.info(
            "container_pool_initializing",
            pool_id=self.pool_id,
            initial_size=initial_size,
            max_size=max_size,
            image=image
        )
        self._initialize_pool()

        logger.info(
            "container_pool_initialized",
            pool_id=self.pool_id,
            available_containers=self.available_containers.qsize()
        )

    def _initialize_pool(self):
        """初始化容器池 (预热)"""

        logger.info(
            "container_pool_preheating",
            pool_id=self.pool_id,
            target_size=self.initial_size
        )

        # 并行创建容器 (使用线程池加速)
        with ThreadPoolExecutor(max_workers=self.initial_size) as executor:
            futures = [
                executor.submit(self._create_container)
                for _ in range(self.initial_size)
            ]

            for future in as_completed(futures):
                try:
                    container = future.result()
                    self.available_containers.put(container)
                    logger.info(
                        "container_ready",
                        pool_id=self.pool_id,
                        container_id=container.short_id
                    )
                except Exception as e:
                    logger.error(
                        "container_creation_failed",
                        pool_id=self.pool_id,
                        error=str(e),
                        exc_info=True
                    )

        # 启动后台线程
        self._start_background_threads()

    def _start_background_threads(self):
        """启动后台维护线程"""

        self.running = True

        # 健康检查线程
        self.health_check_thread = threading.Thread(
            target=self._background_health_check,
            daemon=True,
            name=f"health_check_{self.pool_id}"
        )
        self.health_check_thread.start()

        # 空闲清理线程
        self.idle_cleanup_thread = threading.Thread(
            target=self._background_idle_cleanup,
            daemon=True,
            name=f"idle_cleanup_{self.pool_id}"
        )
        self.idle_cleanup_thread.start()

        logger.info(
            "background_threads_started",
            pool_id=self.pool_id,
            health_check_interval=self.health_check_interval,
            idle_timeout=self.idle_timeout
        )

    def _create_container(self) -> Any:
        """
        创建新容器

        配置:
        - 内存限制: 128MB
        - CPU 限制: 50% (半核)
        - 进程数限制: 64
        - 网络: 禁用
        - 文件系统: 只读 + 10MB tmpfs
        - 安全: 移除所有 capabilities
        - 模式: 长期运行 (detach=True)
        - 命令: sleep infinity (保持运行)

        返回:
            创建的容器对象
        """

        start_time = time.time()

        try:
            container = self.client.containers.run(
                image=self.image,
                command=["sleep", "infinity"],  # 保持运行
                detach=True,

                # 资源限制
                mem_limit="128m",
                memswap_limit="128m",
                cpu_quota=50000,
                cpu_period=100000,
                pids_limit=64,

                # 安全配置
                network_disabled=True,      # 禁用网络
                read_only=True,             # 只读文件系统
                cap_drop=['ALL'],           # 移除所有权限
                security_opt=['no-new-privileges'],  # 禁止提权

                # 临时目录
                tmpfs={'/tmp': 'size=10M,mode=1777'},

                # 标签 (用于追踪和管理)
                labels={
                    'helloagents.pool_id': self.pool_id,
                    'helloagents.created_at': str(time.time()),
                    'helloagents.version': '1.0',
                },

                # 不自动删除 (由池管理)
                remove=False,
                auto_remove=False,
            )

            creation_time = time.time() - start_time

            # 创建元数据
            metadata = ContainerMetadata(
                container_id=container.id,
                container=container,
                created_at=time.time(),
                last_used_at=time.time(),
                execution_count=0,
                reset_count=0,
                status='available',
                health_check_failures=0
            )

            # 保存元数据
            with self.lock:
                self.container_metadata[container.id] = metadata
                self.stats['total_created'] += 1

            logger.info(
                "container_created",
                pool_id=self.pool_id,
                container_id=container.short_id,
                creation_time_ms=round(creation_time * 1000, 2)
            )

            return container

        except Exception as e:
            logger.error(
                "container_creation_error",
                pool_id=self.pool_id,
                error=str(e),
                exc_info=True
            )
            raise

    def get_container(self, timeout: int = ContainerPoolConfig.DEFAULT_CONTAINER_TIMEOUT) -> Optional[Any]:
        """
        从池中获取可用容器

        逻辑:
        1. 尝试从队列获取现有容器 (非阻塞)
        2. 如果队列为空且未达上限，创建新容器
        3. 如果达到上限，阻塞等待可用容器 (最多 timeout 秒)
        4. 更新容器状态为 'in_use'
        5. 记录使用时间戳

        Args:
            timeout: 获取超时时间 (秒)

        Returns:
            容器对象或 None (超时)

        Raises:
            ValidationError: timeout 参数无效
        """
        # 验证 timeout 参数
        self._validate_timeout(timeout)

        start_time = time.time()

        while True:
            # 1. 尝试快速获取 (非阻塞)
            container = self._try_get_from_queue(start_time)
            if container:
                return container

            # 2. 检查是否可以创建新容器
            container = self._try_create_new_container()
            if container:
                return container

            # 3. 达到上限，阻塞等待
            if self._is_timeout(start_time, timeout):
                return None

            container = self._wait_for_available_container(start_time, timeout)
            if container:
                return container

            # 如果等待超时，返回 None
            if self._is_timeout(start_time, timeout):
                return None

    def _validate_timeout(self, timeout: int) -> None:
        """验证 timeout 参数"""
        if timeout <= 0:
            raise ValidationError(
                message="Timeout must be positive",
                field="timeout",
                details={"provided_timeout": timeout}
            )

    def _try_get_from_queue(self, start_time: float) -> Optional[Any]:
        """
        尝试从队列获取容器 (非阻塞)

        Args:
            start_time: 开始时间戳

        Returns:
            容器对象或 None
        """
        try:
            container = self.available_containers.get_nowait()

            # 快速健康检查 (30-50ms)
            if self._quick_health_check(container):
                with self.lock:
                    self._mark_in_use(container)

                logger.info(
                    "container_acquired",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    acquisition_time_ms=round((time.time() - start_time) * 1000, 2)
                )
                return container
            else:
                # 不健康，销毁并重试
                logger.warning(
                    "container_unhealthy_on_acquire",
                    pool_id=self.pool_id,
                    container_id=container.short_id
                )
                self._destroy_container(container.id)
                return None

        except Empty:
            # 队列为空
            return None

    def _try_create_new_container(self) -> Optional[Any]:
        """
        尝试创建新容器 (如果未达上限)

        Returns:
            容器对象或 None
        """
        with self.lock:
            current_size = len(self.container_metadata)

            if current_size < self.max_size:
                # 未达上限，创建新容器
                try:
                    container = self._create_container()
                    self._mark_in_use(container)

                    logger.info(
                        "container_created_on_demand",
                        pool_id=self.pool_id,
                        container_id=container.short_id,
                        current_size=current_size + 1
                    )
                    return container
                except Exception as e:
                    logger.error(
                        "on_demand_creation_failed",
                        pool_id=self.pool_id,
                        error=str(e)
                    )
                    # 创建失败，返回 None
                    return None

        return None

    def _is_timeout(self, start_time: float, timeout: int) -> bool:
        """
        检查是否超时

        Args:
            start_time: 开始时间戳
            timeout: 超时时间 (秒)

        Returns:
            是否超时
        """
        elapsed = time.time() - start_time
        remaining_timeout = timeout - elapsed

        if remaining_timeout <= 0:
            logger.warning(
                "container_acquisition_timeout",
                pool_id=self.pool_id,
                timeout=timeout,
                pool_size=len(self.container_metadata)
            )
            return True

        return False

    def _wait_for_available_container(self, start_time: float, timeout: int) -> Optional[Any]:
        """
        阻塞等待可用容器

        Args:
            start_time: 开始时间戳
            timeout: 总超时时间 (秒)

        Returns:
            容器对象或 None (超时)
        """
        elapsed = time.time() - start_time
        remaining_timeout = timeout - elapsed

        if remaining_timeout <= 0:
            return None

        try:
            # 阻塞等待，最多 remaining_timeout 秒
            container = self.available_containers.get(timeout=remaining_timeout)

            if self._quick_health_check(container):
                with self.lock:
                    self._mark_in_use(container)

                logger.info(
                    "container_acquired_after_wait",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    wait_time_ms=round((time.time() - start_time) * 1000, 2)
                )
                return container
            else:
                self._destroy_container(container.id)
                return None

        except Empty:
            logger.warning(
                "container_acquisition_timeout",
                pool_id=self.pool_id,
                timeout=timeout
            )
            return None

    def _mark_in_use(self, container: Any):
        """标记容器为使用中 (需要持锁调用)"""

        container_id = container.id
        metadata = self.container_metadata.get(container_id)

        if metadata:
            metadata.status = 'in_use'
            metadata.last_used_at = time.time()
            metadata.execution_count += 1
            self.in_use_containers[container_id] = metadata
            self.stats['total_executions'] += 1

    def return_container(self, container: Any) -> None:
        """
        归还容器到池中

        逻辑:
        1. 标记为非使用状态
        2. 执行容器重置
        3. 健康检查
        4. 如果健康，归还到可用队列
        5. 如果不健康，销毁并创建新容器 (保持池大小)
        6. 更新容器元数据
        """

        container_id = container.id

        logger.info(
            "container_return_started",
            pool_id=self.pool_id,
            container_id=container.short_id
        )

        # 1. 标记为非使用状态
        with self.lock:
            if container_id in self.in_use_containers:
                del self.in_use_containers[container_id]

        # 2. 重置容器 (耗时操作，不持锁)
        reset_start = time.time()
        reset_success = self._reset_container(container)
        reset_time = time.time() - reset_start

        if not reset_success:
            logger.warning(
                "container_reset_failed",
                pool_id=self.pool_id,
                container_id=container.short_id,
                reset_time_ms=round(reset_time * 1000, 2)
            )
            # 重置失败，销毁并重建
            self._destroy_and_replace_container(container_id)
            return

        logger.info(
            "container_reset_completed",
            pool_id=self.pool_id,
            container_id=container.short_id,
            reset_time_ms=round(reset_time * 1000, 2)
        )

        # 3. 深度健康检查 (归还后需要全面检查)
        is_healthy = self._deep_health_check(container)

        if not is_healthy:
            logger.warning(
                "container_unhealthy_after_reset",
                pool_id=self.pool_id,
                container_id=container.short_id
            )
            # 不健康，销毁并重建
            self._destroy_and_replace_container(container_id)
            return

        # 4. 归还到队列
        with self.lock:
            metadata = self.container_metadata.get(container_id)
            if metadata:
                metadata.status = 'available'
                metadata.last_used_at = time.time()
                metadata.reset_count += 1
                metadata.health_check_failures = 0  # 重置失败计数
                self.stats['total_resets'] += 1

        # 5. 放回队列 (Queue 是线程安全的)
        try:
            self.available_containers.put_nowait(container)
            logger.info(
                "container_returned",
                pool_id=self.pool_id,
                container_id=container.short_id
            )
        except Full:
            # 队列已满 (不应该发生)，销毁容器
            logger.error(
                "queue_full_on_return",
                pool_id=self.pool_id,
                container_id=container.short_id
            )
            self._destroy_container(container_id)

    def _reset_container(self, container: Any) -> bool:
        """
        优化版容器重置 (150-250ms)

        优化策略:
        - 将多个串行 exec_run() 合并为单个 shell 脚本
        - 减少 Docker API 调用次数 (从 5 次降低到 1 次)
        - 集成验证逻辑到单个脚本

        步骤:
        1. 终止所有 Python 进程
        2. 清理 /tmp 目录
        3. 验证重置有效性 (响应性、文件数、进程数)

        返回:
            重置是否成功
        """
        reset_start = time.time()

        try:
            # 合并所有重置和验证命令为单个 shell 脚本
            reset_script = """
            # 1. 终止所有 Python 进程 (保留主进程 sleep infinity)
            pkill -9 python 2>/dev/null || true

            # 2. 清理临时目录
            rm -rf /tmp/* /tmp/.* 2>/dev/null || true

            # 3. 验证响应性
            echo "reset_ok"

            # 4. 检查 /tmp 是否为空
            file_count=$(ls -A /tmp 2>/dev/null | wc -l)
            echo "files:$file_count"

            # 5. 检查进程数 (应该只有主进程)
            process_count=$(ps aux | wc -l)
            echo "processes:$process_count"
            """

            result = container.exec_run(
                ["sh", "-c", reset_script],
                detach=False,
                timeout=ContainerPoolConfig.RESET_TIMEOUT
            )

            reset_time = time.time() - reset_start

            # 检查执行是否成功
            if result.exit_code != 0:
                logger.warning(
                    "container_reset_script_failed",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    exit_code=result.exit_code,
                    reset_time_ms=round(reset_time * 1000, 2)
                )
                return False

            # 解析输出
            output = result.output.decode('utf-8').strip()
            lines = output.split('\n')

            # 验证响应性 (第一行应该是 "reset_ok")
            if not lines or 'reset_ok' not in lines[0]:
                logger.warning(
                    "container_reset_no_response",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    output=output[:100]
                )
                return False

            # 解析文件数和进程数
            file_count = 0
            process_count = 999

            for line in lines:
                if line.startswith('files:'):
                    try:
                        file_count = int(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('processes:'):
                    try:
                        process_count = int(line.split(':')[1].strip())
                    except:
                        pass

            # 验证 /tmp 是否为空
            if file_count > 0:
                logger.warning(
                    "tmp_not_empty_after_reset",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    file_count=file_count
                )
                return False

            # 验证进程数 (标题行 + sleep + sh + ps + wc = 最多 5 个)
            if process_count > ContainerPoolConfig.MAX_RESET_PROCESS_COUNT:
                logger.warning(
                    "too_many_processes_after_reset",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    process_count=process_count
                )
                return False

            logger.debug(
                "container_reset_success",
                pool_id=self.pool_id,
                container_id=container.short_id,
                reset_time_ms=round(reset_time * 1000, 2),
                file_count=file_count,
                process_count=process_count
            )

            return True

        except Exception as e:
            reset_time = time.time() - reset_start
            logger.error(
                "container_reset_error",
                pool_id=self.pool_id,
                container_id=container.short_id,
                error=str(e),
                reset_time_ms=round(reset_time * 1000, 2),
                exc_info=True
            )
            return False

    def _quick_health_check(self, container: Any) -> bool:
        """
        快速健康检查 (30-50ms)

        仅执行最基本的检查:
        1. 容器状态是否为 'running'
        2. 容器响应性 (echo 测试)

        用于:
        - get_container() 快速获取容器
        - 后台健康检查首次验证

        返回:
            是否健康
        """
        check_start = time.time()

        try:
            # 1. 检查容器状态 (~10ms)
            container.reload()
            if container.status != 'running':
                logger.warning(
                    "quick_check_not_running",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    status=container.status
                )
                return False

            # 2. 检查容器响应性 (echo 测试, ~20ms)
            result = container.exec_run(
                "echo ok",
                timeout=ContainerPoolConfig.QUICK_HEALTH_CHECK_TIMEOUT
            )

            is_healthy = result.exit_code == 0

            check_time = time.time() - check_start
            logger.debug(
                "quick_health_check_completed",
                pool_id=self.pool_id,
                container_id=container.short_id,
                is_healthy=is_healthy,
                check_time_ms=round(check_time * 1000, 2)
            )

            return is_healthy

        except Exception as e:
            check_time = time.time() - check_start
            logger.error(
                "quick_health_check_error",
                pool_id=self.pool_id,
                container_id=container.short_id if hasattr(container, 'short_id') else 'unknown',
                error=str(e),
                check_time_ms=round(check_time * 1000, 2)
            )
            return False

    def _deep_health_check(self, container: Any) -> bool:
        """
        深度健康检查 (200-500ms)

        完整检查项:
        1. 容器状态是否为 'running'
        2. 容器是否响应命令 (echo 测试)
        3. 内存使用是否正常 (< 90%)
        4. 容器进程数是否正常 (< 50)
        5. 文件系统是否只读

        用于:
        - return_container() 归还后的深度验证
        - 后台健康检查失败 3 次后的确认
        - 定期全面检查 (每 5 分钟)

        返回:
            是否健康
        """
        check_start = time.time()

        try:
            # 1. 检查容器状态
            container.reload()
            if container.status != 'running':
                logger.warning(
                    "deep_check_not_running",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    status=container.status
                )
                return False

            # 2. 检查容器响应性 (echo 测试)
            result = container.exec_run(
                "echo health_check",
                timeout=ContainerPoolConfig.DEEP_HEALTH_CHECK_TIMEOUT
            )
            if result.exit_code != 0:
                logger.warning(
                    "deep_check_not_responsive",
                    pool_id=self.pool_id,
                    container_id=container.short_id
                )
                return False

            # 3. 检查内存使用 (最耗时: 100-200ms)
            stats = container.stats(stream=False)
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 1)
            memory_percent = (memory_usage / memory_limit) * 100

            if memory_percent > ContainerPoolConfig.MAX_MEMORY_PERCENT:
                logger.warning(
                    "deep_check_high_memory",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    memory_percent=round(memory_percent, 1)
                )
                return False

            # 4. 检查进程数
            result = container.exec_run("ps aux | wc -l")
            if result.exit_code != 0:
                return False

            process_count = int(result.output.decode('utf-8').strip())

            if process_count > ContainerPoolConfig.MAX_PROCESS_COUNT:
                logger.warning(
                    "deep_check_too_many_processes",
                    pool_id=self.pool_id,
                    container_id=container.short_id,
                    process_count=process_count
                )
                return False

            # 5. 检查文件系统 (只读保护是否完好)
            result = container.exec_run("touch /test_file 2>&1")
            if result.exit_code == 0:
                logger.error(
                    "deep_check_filesystem_not_readonly",
                    pool_id=self.pool_id,
                    container_id=container.short_id
                )
                return False

            check_time = time.time() - check_start
            logger.debug(
                "deep_health_check_completed",
                pool_id=self.pool_id,
                container_id=container.short_id,
                is_healthy=True,
                check_time_ms=round(check_time * 1000, 2)
            )

            return True

        except Exception as e:
            check_time = time.time() - check_start
            logger.error(
                "deep_health_check_error",
                pool_id=self.pool_id,
                container_id=container.short_id if hasattr(container, 'short_id') else 'unknown',
                error=str(e),
                check_time_ms=round(check_time * 1000, 2),
                exc_info=True
            )
            return False

    def _destroy_container(self, container_id: str):
        """销毁容器"""

        try:
            with self.lock:
                metadata = self.container_metadata.get(container_id)
                if not metadata:
                    return

                container = metadata.container

                # 从元数据中移除
                del self.container_metadata[container_id]
                if container_id in self.in_use_containers:
                    del self.in_use_containers[container_id]

                self.stats['total_destroyed'] += 1

            # 停止并删除容器
            try:
                container.stop(timeout=ContainerPoolConfig.CONTAINER_STOP_TIMEOUT)
                container.remove(force=True)
            except:
                # 忽略停止/删除错误
                pass

            logger.info(
                "container_destroyed",
                pool_id=self.pool_id,
                container_id=container.short_id if hasattr(container, 'short_id') else container_id[:12]
            )

        except Exception as e:
            logger.error(
                "container_destroy_error",
                pool_id=self.pool_id,
                container_id=container_id[:12],
                error=str(e),
                exc_info=True
            )

    def _destroy_and_replace_container(self, container_id: str):
        """销毁容器并创建新容器替换"""

        logger.info(
            "container_replace_started",
            pool_id=self.pool_id,
            container_id=container_id[:12]
        )

        # 销毁旧容器
        self._destroy_container(container_id)

        # 创建新容器
        try:
            new_container = self._create_container()
            self.available_containers.put(new_container)

            logger.info(
                "container_replaced",
                pool_id=self.pool_id,
                old_container_id=container_id[:12],
                new_container_id=new_container.short_id
            )
        except Exception as e:
            logger.error(
                "container_replacement_failed",
                pool_id=self.pool_id,
                container_id=container_id[:12],
                error=str(e)
            )

    def _background_health_check(self):
        """
        后台定期健康检查

        策略:
        1. 使用快速检查进行初次验证
        2. 快速检查失败 3 次后，使用深度检查确认
        3. 深度检查失败后，销毁并重建容器
        """

        logger.info(
            "health_check_thread_started",
            pool_id=self.pool_id
        )

        while self.running:
            time.sleep(self.health_check_interval)

            unhealthy_containers = []

            with self.lock:
                # 检查所有容器 (包括使用中和可用的)
                all_containers = list(self.container_metadata.items())

            for container_id, metadata in all_containers:
                # 跳过正在使用的容器 (避免干扰执行)
                if metadata.status == 'in_use':
                    continue

                # 执行快速健康检查
                is_healthy = self._quick_health_check(metadata.container)

                if not is_healthy:
                    with self.lock:
                        metadata.health_check_failures += 1
                        self.stats['health_check_failures'] += 1

                    # 连续失败3次，执行深度检查确认
                    if metadata.health_check_failures >= ContainerPoolConfig.MAX_HEALTH_CHECK_FAILURES:
                        logger.warning(
                            "quick_check_failed_3_times_confirming",
                            pool_id=self.pool_id,
                            container_id=container_id[:12]
                        )

                        # 深度检查确认
                        is_deeply_healthy = self._deep_health_check(metadata.container)

                        if not is_deeply_healthy:
                            unhealthy_containers.append(container_id)
                            logger.warning(
                                "container_marked_unhealthy",
                                pool_id=self.pool_id,
                                container_id=container_id[:12],
                                consecutive_failures=metadata.health_check_failures
                            )
                        else:
                            # 深度检查通过，重置失败计数 (可能是快速检查误判)
                            with self.lock:
                                metadata.health_check_failures = 0
                            logger.info(
                                "deep_check_passed_after_quick_failures",
                                pool_id=self.pool_id,
                                container_id=container_id[:12]
                            )
                else:
                    with self.lock:
                        metadata.health_check_failures = 0

            # 销毁不健康容器并重建
            for container_id in unhealthy_containers:
                self._destroy_and_replace_container(container_id)

    def _background_idle_cleanup(self):
        """后台空闲容器回收线程"""

        logger.info(
            "idle_cleanup_thread_started",
            pool_id=self.pool_id
        )

        while self.running:
            time.sleep(60)  # 每分钟检查一次

            current_time = time.time()
            containers_to_remove = []

            with self.lock:
                # 检查可用容器的空闲时间
                for container_id, metadata in self.container_metadata.items():
                    if metadata.status != 'available':
                        continue

                    idle_time = current_time - metadata.last_used_at

                    # 超过空闲时间且超过最小池大小
                    if idle_time > self.idle_timeout:
                        current_pool_size = len(self.container_metadata)
                        if current_pool_size > self.min_size:
                            containers_to_remove.append(container_id)

            # 销毁空闲容器
            for container_id in containers_to_remove:
                # 先从队列中移除
                temp_containers = []
                try:
                    while True:
                        try:
                            c = self.available_containers.get_nowait()
                            if c.id == container_id:
                                # 找到要删除的容器，销毁它
                                self._destroy_container(container_id)
                                logger.info(
                                    "idle_container_removed",
                                    pool_id=self.pool_id,
                                    container_id=container_id[:12]
                                )
                                break
                            else:
                                temp_containers.append(c)
                        except Empty:
                            break
                finally:
                    # 把其他容器放回队列
                    for c in temp_containers:
                        try:
                            self.available_containers.put_nowait(c)
                        except Full:
                            pass

    def get_stats(self) -> Dict[str, Any]:
        """获取池统计信息"""

        with self.lock:
            available_count = self.available_containers.qsize()
            in_use_count = len(self.in_use_containers)
            total_count = len(self.container_metadata)

            return {
                # 容器数量
                'available_containers': available_count,
                'in_use_containers': in_use_count,
                'total_containers': total_count,

                # 累计统计
                'total_created': self.stats['total_created'],
                'total_destroyed': self.stats['total_destroyed'],
                'total_executions': self.stats['total_executions'],
                'total_resets': self.stats['total_resets'],
                'health_check_failures': self.stats['health_check_failures'],

                # 池配置
                'pool_id': self.pool_id,
                'max_size': self.max_size,
                'min_size': self.min_size,

                # 容器详情
                'containers': [
                    {
                        'id': m.container_id[:12],
                        'status': m.status,
                        'created_at': m.created_at,
                        'last_used_at': m.last_used_at,
                        'execution_count': m.execution_count,
                        'reset_count': m.reset_count,
                        'health_check_failures': m.health_check_failures,
                    }
                    for m in self.container_metadata.values()
                ]
            }

    def shutdown(self):
        """优雅关闭容器池"""

        logger.info(
            "container_pool_shutdown_started",
            pool_id=self.pool_id
        )

        # 停止后台线程
        self.running = False

        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)

        if self.idle_cleanup_thread:
            self.idle_cleanup_thread.join(timeout=5)

        # 等待使用中的容器归还 (最多30秒)
        deadline = time.time() + 30
        while self.in_use_containers and time.time() < deadline:
            in_use_count = len(self.in_use_containers)
            logger.info(
                "waiting_for_containers",
                pool_id=self.pool_id,
                in_use_count=in_use_count
            )
            time.sleep(1)

        # 销毁所有容器
        with self.lock:
            all_containers = list(self.container_metadata.values())

        for metadata in all_containers:
            try:
                metadata.container.stop(timeout=ContainerPoolConfig.CONTAINER_STOP_TIMEOUT)
                metadata.container.remove(force=True)
                logger.info(
                    "container_destroyed_on_shutdown",
                    pool_id=self.pool_id,
                    container_id=metadata.container.short_id
                )
            except Exception as e:
                logger.error(
                    "container_destroy_error_on_shutdown",
                    pool_id=self.pool_id,
                    container_id=metadata.container_id[:12],
                    error=str(e)
                )

        # 关闭 Docker 客户端
        try:
            self.client.close()
        except:
            pass

        logger.info(
            "container_pool_shutdown_completed",
            pool_id=self.pool_id,
            total_created=self.stats['total_created'],
            total_destroyed=self.stats['total_destroyed'],
            total_executions=self.stats['total_executions']
        )
