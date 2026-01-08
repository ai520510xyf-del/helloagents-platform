"""
代码执行沙箱模块

使用 Docker 容器提供安全的代码执行环境
"""

import docker
import time
from typing import Tuple, Optional

class CodeSandbox:
    """
    代码执行沙箱

    使用 Docker 容器隔离执行用户代码，提供安全保障
    """

    def __init__(self, image: str = "python:3.11-slim", timeout: int = 30):
        """
        初始化沙箱

        Args:
            image: Docker 镜像名称
            timeout: 执行超时时间（秒）
        """
        self.image = image
        self.timeout = timeout
        self.client = None

        try:
            self.client = docker.from_env()
            # 检查镜像是否存在，不存在则拉取
            try:
                self.client.images.get(self.image)
            except docker.errors.ImageNotFound:
                print(f"📦 拉取 Docker 镜像: {self.image}")
                self.client.images.pull(self.image)
        except Exception as e:
            print(f"⚠️  Docker 未连接: {str(e)}")
            print("⚠️  将使用本地执行模式（不安全，仅用于开发）")
            self.client = None

    def _check_code_safety(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        检查代码安全性

        Args:
            code: 要检查的代码

        Returns:
            (是否安全, 错误信息)
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
                return False, f'安全检查失败: {message}'

        # 检查代码长度（防止 DoS）
        if len(code) > 10000:  # 10KB
            return False, '代码长度超过限制（最大 10KB）'

        return True, None

    def execute_python(self, code: str) -> Tuple[bool, str, float]:
        """
        在沙箱中执行 Python 代码

        Args:
            code: 要执行的代码

        Returns:
            (成功标志, 输出/错误信息, 执行时间)
        """
        # 预检查代码安全性
        is_safe, error_msg = self._check_code_safety(code)
        if not is_safe:
            return False, error_msg, 0.0

        if self.client is None:
            # Docker 不可用，使用本地执行（仅开发环境）
            return self._execute_local(code)

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

                # 磁盘 I/O 限制（字节/秒）
                # 注意：需要 Docker 配置支持 blkio
                # device_write_bps=[{'Path': '/dev/sda', 'Rate': 10485760}],  # 10MB/s 写入
                # device_read_bps=[{'Path': '/dev/sda', 'Rate': 10485760}],   # 10MB/s 读取

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
                return True, output, execution_time
            else:
                return False, output, execution_time

        except docker.errors.ContainerError as e:
            # 容器执行错误
            return False, f"执行错误:\n{e.stderr.decode('utf-8')}", 0.0

        except Exception as e:
            return False, f"沙箱错误: {str(e)}", 0.0

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
        if self.client:
            self.client.close()

# 创建全局沙箱实例
sandbox = CodeSandbox()
