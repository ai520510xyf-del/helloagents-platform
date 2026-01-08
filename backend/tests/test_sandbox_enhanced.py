"""
沙箱增强测试 - 补充覆盖率

针对 sandbox.py 的未覆盖代码路径进行测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import docker.errors
from app.sandbox import CodeSandbox
from app.exceptions import (
    ValidationError,
    SandboxExecutionError,
    ContainerPoolError,
    TimeoutError as HelloAgentsTimeoutError
)


# ==================== 初始化测试 ====================

def test_sandbox_init_with_pool():
    """测试启用容器池的初始化"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client

        # Mock 镜像存在
        mock_client.images.get.return_value = Mock()

        with patch('app.sandbox.ContainerPool') as mock_pool_class:
            sandbox = CodeSandbox(use_pool=True, pool_initial_size=2, pool_max_size=5)

            assert sandbox.use_pool is True
            assert sandbox.pool is not None
            mock_pool_class.assert_called_once_with(
                initial_size=2,
                max_size=5,
                image="python:3.11-slim"
            )


def test_sandbox_init_without_pool():
    """测试禁用容器池的初始化"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        sandbox = CodeSandbox(use_pool=False)

        assert sandbox.use_pool is False
        assert sandbox.pool is None


def test_sandbox_init_image_not_found():
    """测试镜像不存在时的拉取逻辑"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client

        # 第一次调用抛出 ImageNotFound，第二次成功
        mock_client.images.get.side_effect = docker.errors.ImageNotFound("image not found")
        mock_client.images.pull.return_value = Mock()

        sandbox = CodeSandbox(use_pool=False)

        # 验证调用了 pull
        mock_client.images.pull.assert_called_once_with("python:3.11-slim")
        assert sandbox.client is not None


def test_sandbox_init_docker_unavailable():
    """测试 Docker 不可用时的降级处理"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_docker.side_effect = Exception("Docker daemon not running")

        sandbox = CodeSandbox()

        # 应该降级到本地执行
        assert sandbox.client is None
        assert sandbox.pool is None


# ==================== 代码安全检查测试 ====================

def test_check_code_safety_valid_code():
    """测试安全代码通过检查"""
    sandbox = CodeSandbox()

    code = "print('Hello, World!')"
    # 不应该抛出异常
    sandbox._check_code_safety(code)


def test_check_code_safety_all_dangerous_patterns():
    """测试所有危险模式都被检测"""
    sandbox = CodeSandbox()

    dangerous_codes = [
        ("os.system('ls')", "os.system"),
        ("subprocess.run(['ls'])", "subprocess."),
        ("eval('1+1')", "eval("),
        ("exec('print(1)')", "exec("),
        ("compile('1', '<string>', 'exec')", "compile("),
        ("__import__('os')", "__import__"),
        ("open('/tmp/file')", "open("),
        ("file('/tmp/file')", "file("),
        ("input('name')", "input("),
        ("raw_input('name')", "input("),  # raw_input 会匹配 input( 模式
    ]

    for code, pattern in dangerous_codes:
        with pytest.raises(ValidationError) as exc_info:
            sandbox._check_code_safety(code)

        assert pattern in str(exc_info.value.details)


def test_check_code_safety_code_length_exact_limit():
    """测试代码长度恰好等于限制"""
    sandbox = CodeSandbox()

    # 恰好 10000 字节
    code = "x = " + "1" * 9996
    assert len(code) == 10000

    # 不应该抛出异常
    sandbox._check_code_safety(code)


def test_check_code_safety_code_length_over_limit():
    """测试代码长度超过限制"""
    sandbox = CodeSandbox()

    # 10001 字节
    code = "x = " + "1" * 9997
    assert len(code) == 10001

    with pytest.raises(ValidationError) as exc_info:
        sandbox._check_code_safety(code)

    assert "代码长度超过限制" in exc_info.value.message
    assert exc_info.value.details["code_length"] == 10001
    assert exc_info.value.details["max_length"] == 10000


# ==================== 容器池执行测试 ====================

def test_execute_with_pool_success():
    """测试使用容器池成功执行"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        # Mock 容器池
        mock_pool = Mock()
        mock_container = Mock()

        # Mock exec_run 返回成功结果
        exec_result = Mock()
        exec_result.exit_code = 0
        exec_result.output = (b"Hello, World!\n", b"")
        mock_container.exec_run.return_value = exec_result

        mock_pool.get_container.return_value = mock_container

        with patch('app.sandbox.ContainerPool', return_value=mock_pool):
            sandbox = CodeSandbox(use_pool=True)
            sandbox.pool = mock_pool

            success, output, exec_time = sandbox.execute_python("print('Hello, World!')")

            assert success is True
            assert "Hello, World!" in output
            assert exec_time > 0

            # 验证容器被归还
            mock_pool.return_container.assert_called_once_with(mock_container)


def test_execute_with_pool_error_exit_code():
    """测试容器池执行返回错误退出码"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_pool = Mock()
        mock_container = Mock()

        # Mock exec_run 返回错误结果
        exec_result = Mock()
        exec_result.exit_code = 1
        exec_result.output = (b"", b"NameError: name 'x' is not defined\n")
        mock_container.exec_run.return_value = exec_result

        mock_pool.get_container.return_value = mock_container

        with patch('app.sandbox.ContainerPool', return_value=mock_pool):
            sandbox = CodeSandbox(use_pool=True)
            sandbox.pool = mock_pool

            success, output, exec_time = sandbox.execute_python("print(x)")

            assert success is False
            assert "NameError" in output
            assert exec_time > 0


def test_execute_with_pool_get_container_fails():
    """测试从容器池获取容器失败"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_pool = Mock()
        mock_pool.get_container.return_value = None  # 获取失败
        mock_pool.get_stats.return_value = {"available": 0, "in_use": 10}

        with patch('app.sandbox.ContainerPool', return_value=mock_pool):
            sandbox = CodeSandbox(use_pool=True)
            sandbox.pool = mock_pool

            with pytest.raises(ContainerPoolError) as exc_info:
                sandbox.execute_python("print('test')")

            assert "无法获取容器" in exc_info.value.message


def test_execute_with_pool_docker_exception():
    """测试容器池执行时 Docker 异常"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_pool = Mock()
        mock_container = Mock()
        mock_container.exec_run.side_effect = docker.errors.APIError("Docker API error")
        mock_pool.get_container.return_value = mock_container

        with patch('app.sandbox.ContainerPool', return_value=mock_pool):
            sandbox = CodeSandbox(use_pool=True)
            sandbox.pool = mock_pool

            with pytest.raises(SandboxExecutionError) as exc_info:
                sandbox.execute_python("print('test')")

            assert "Docker 执行错误" in exc_info.value.message
            # 验证容器仍然被归还
            mock_pool.return_container.assert_called_once()


def test_execute_with_pool_generic_exception():
    """测试容器池执行时通用异常"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_pool = Mock()
        mock_container = Mock()
        mock_container.exec_run.side_effect = RuntimeError("Unexpected error")
        mock_pool.get_container.return_value = mock_container

        with patch('app.sandbox.ContainerPool', return_value=mock_pool):
            sandbox = CodeSandbox(use_pool=True)
            sandbox.pool = mock_pool

            with pytest.raises(SandboxExecutionError) as exc_info:
                sandbox.execute_python("print('test')")

            assert "沙箱执行错误" in exc_info.value.message


def test_execute_with_pool_large_output():
    """测试容器池执行时输出过大被截断"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_pool = Mock()
        mock_container = Mock()

        # 创建超过 10KB 的输出
        large_output = b"x" * 15000
        exec_result = Mock()
        exec_result.exit_code = 0
        exec_result.output = (large_output, b"")
        mock_container.exec_run.return_value = exec_result

        mock_pool.get_container.return_value = mock_container

        with patch('app.sandbox.ContainerPool', return_value=mock_pool):
            sandbox = CodeSandbox(use_pool=True)
            sandbox.pool = mock_pool

            success, output, exec_time = sandbox.execute_python("print('x' * 15000)")

            assert success is True
            assert len(output) <= 10100  # 10KB + 截断提示
            assert "输出被截断" in output


# ==================== 临时容器执行测试 ====================

def test_execute_with_temp_container_success():
    """测试使用临时容器成功执行"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.return_value = b"Hello, World!\n"

        mock_client.containers.run.return_value = mock_container

        sandbox = CodeSandbox(use_pool=False)

        success, output, exec_time = sandbox.execute_python("print('Hello, World!')")

        assert success is True
        assert "Hello, World!" in output
        assert exec_time > 0


def test_execute_with_temp_container_error():
    """测试使用临时容器执行错误"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 1}
        mock_container.logs.return_value = b"NameError: name 'x' is not defined\n"

        mock_client.containers.run.return_value = mock_container

        sandbox = CodeSandbox(use_pool=False)

        success, output, exec_time = sandbox.execute_python("print(x)")

        assert success is False
        assert "NameError" in output


def test_execute_with_temp_container_error_exception():
    """测试临时容器执行时 ContainerError"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        error = docker.errors.ContainerError(
            container="test",
            exit_status=1,
            command="python",
            image="python:3.11-slim",
            stderr=b"Syntax error"
        )
        mock_client.containers.run.side_effect = error

        sandbox = CodeSandbox(use_pool=False)

        with pytest.raises(SandboxExecutionError) as exc_info:
            sandbox.execute_python("print('test'")

        assert "容器执行错误" in exc_info.value.message


def test_execute_with_temp_container_docker_exception():
    """测试临时容器执行时 Docker 异常"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_client.containers.run.side_effect = docker.errors.APIError("API error")

        sandbox = CodeSandbox(use_pool=False)

        with pytest.raises(SandboxExecutionError) as exc_info:
            sandbox.execute_python("print('test')")

        assert "Docker 错误" in exc_info.value.message


def test_execute_with_temp_container_generic_exception():
    """测试临时容器执行时通用异常"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_client.containers.run.side_effect = RuntimeError("Unexpected error")

        sandbox = CodeSandbox(use_pool=False)

        with pytest.raises(SandboxExecutionError) as exc_info:
            sandbox.execute_python("print('test')")

        assert "沙箱执行错误" in exc_info.value.message


def test_execute_with_temp_container_large_output():
    """测试临时容器输出过大被截断"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 0}
        # 超过 10KB 的输出
        mock_container.logs.return_value = b"x" * 15000

        mock_client.containers.run.return_value = mock_container

        sandbox = CodeSandbox(use_pool=False)

        success, output, exec_time = sandbox.execute_python("print('x' * 15000)")

        assert success is True
        assert len(output) <= 10100
        assert "输出被截断" in output


# ==================== 本地执行测试 ====================

def test_execute_local_success():
    """测试本地执行成功"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_docker.side_effect = Exception("Docker not available")

        sandbox = CodeSandbox()

        success, output, exec_time = sandbox.execute_python("print('Hello from local')")

        assert success is True
        assert "Hello from local" in output
        assert exec_time > 0


def test_execute_local_error():
    """测试本地执行错误"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_docker.side_effect = Exception("Docker not available")

        sandbox = CodeSandbox()

        success, output, exec_time = sandbox.execute_python("print(undefined_variable)")

        assert success is False
        assert "NameError" in output


def test_execute_local_timeout():
    """测试本地执行超时"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_docker.side_effect = Exception("Docker not available")

        sandbox = CodeSandbox(timeout=1)

        # 这个代码会超时
        code = """
import time
time.sleep(10)
print('Should not reach here')
"""
        success, output, exec_time = sandbox.execute_python(code)

        assert success is False
        assert "超时" in output


def test_execute_local_exception():
    """测试本地执行时的异常"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_docker.side_effect = Exception("Docker not available")

        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = OSError("OS error")

            sandbox = CodeSandbox()

            success, output, exec_time = sandbox.execute_python("print('test')")

            assert success is False
            assert "执行错误" in output


# ==================== 清理测试 ====================

def test_cleanup_with_pool():
    """测试清理时关闭容器池"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        mock_pool = Mock()

        with patch('app.sandbox.ContainerPool', return_value=mock_pool):
            sandbox = CodeSandbox(use_pool=True)
            sandbox.cleanup()

            # 验证池被关闭
            mock_pool.shutdown.assert_called_once()
            # 验证客户端被关闭
            mock_client.close.assert_called_once()


def test_cleanup_without_pool():
    """测试清理时无容器池"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        sandbox = CodeSandbox(use_pool=False)
        sandbox.cleanup()

        # 验证客户端被关闭
        mock_client.close.assert_called_once()


def test_cleanup_docker_unavailable():
    """测试 Docker 不可用时的清理"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_docker.side_effect = Exception("Docker not available")

        sandbox = CodeSandbox()
        # 不应该抛出异常
        sandbox.cleanup()


# ==================== 集成测试 ====================

def test_execute_python_validation_before_execution():
    """测试执行前先进行安全检查"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        sandbox = CodeSandbox(use_pool=False)

        # 危险代码应该在执行前被拦截
        with pytest.raises(ValidationError):
            sandbox.execute_python("os.system('rm -rf /')")

        # Docker 容器不应该被创建
        mock_client.containers.run.assert_not_called()


def test_execute_python_custom_timeout():
    """测试自定义超时配置"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        sandbox = CodeSandbox(timeout=60)

        assert sandbox.timeout == 60


def test_execute_python_custom_image():
    """测试自定义镜像配置"""
    with patch('app.sandbox.docker.from_env') as mock_docker:
        mock_client = Mock()
        mock_docker.return_value = mock_client
        mock_client.images.get.return_value = Mock()

        sandbox = CodeSandbox(image="python:3.12-alpine")

        assert sandbox.image == "python:3.12-alpine"
        mock_client.images.get.assert_called_with("python:3.12-alpine")
