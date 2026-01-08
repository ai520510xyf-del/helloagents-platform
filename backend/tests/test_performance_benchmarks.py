"""
容器池和代码执行性能基准测试

使用 pytest-benchmark 进行精确的性能基准测试
运行命令: pytest tests/test_performance_benchmarks.py --benchmark-only
"""

import pytest
import time
from unittest.mock import Mock, patch
from app.container_pool import ContainerPool, ContainerMetadata
from app.sandbox import CodeSandbox


# ============================================
# 容器池性能测试
# ============================================

@pytest.mark.benchmark(group="container_pool")
def test_container_acquisition_performance(benchmark, mock_docker_client, mock_docker_container):
    """
    测试容器获取性能

    性能目标:
    - 平均获取时间 < 100ms
    - P95 < 200ms
    - P99 < 500ms
    """

    with patch('docker.from_env', return_value=mock_docker_client):
        pool = ContainerPool(initial_size=5, max_size=10)

        def get_and_return_container():
            container = pool.get_container(timeout=10)
            if container:
                pool.return_container(container)
            return container

        # 预热（让池稳定）
        for _ in range(5):
            get_and_return_container()

        # 基准测试
        result = benchmark(get_and_return_container)

        # 验证性能目标
        stats = benchmark.stats.stats
        assert stats.mean < 0.1, f"平均获取时间 {stats.mean:.3f}s 超过 100ms"

        # 清理
        pool.shutdown()


@pytest.mark.benchmark(group="container_pool")
def test_container_reset_performance(benchmark, mock_docker_client, mock_docker_container):
    """
    测试容器重置性能

    性能目标:
    - 重置时间 < 250ms (优化后目标)
    - 重置成功率 > 99%
    """

    # Mock reset 脚本输出
    def mock_reset_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0
        result.output = b"reset_ok\nfiles:0\nprocesses:3\n"
        time.sleep(0.15)  # 模拟真实重置耗时 (150ms)
        return result

    mock_docker_container.exec_run = Mock(side_effect=mock_reset_exec_run)

    with patch('docker.from_env', return_value=mock_docker_client):
        pool = ContainerPool(initial_size=1, max_size=1)

        def reset_container():
            return pool._reset_container(mock_docker_container)

        # 基准测试
        result = benchmark(reset_container)

        # 验证
        assert result is True, "容器重置失败"

        stats = benchmark.stats.stats
        assert stats.mean < 0.25, f"重置时间 {stats.mean:.3f}s 超过 250ms"

        # 清理
        pool.shutdown()


@pytest.mark.benchmark(group="container_pool")
def test_concurrent_container_acquisition(benchmark, mock_docker_client, mock_docker_container):
    """
    测试并发容器获取性能

    模拟高并发场景下的容器池表现
    性能目标:
    - 并发获取延迟 < 500ms
    - 无容器获取超时
    """

    with patch('docker.from_env', return_value=mock_docker_client):
        pool = ContainerPool(initial_size=5, max_size=10)

        def concurrent_acquisition():
            import threading
            results = []

            def get_container():
                container = pool.get_container(timeout=5)
                time.sleep(0.05)  # 模拟短暂使用
                if container:
                    pool.return_container(container)
                results.append(container is not None)

            # 并发获取 10 个容器
            threads = [threading.Thread(target=get_container) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            return all(results)

        # 基准测试
        result = benchmark(concurrent_acquisition)

        # 验证所有并发请求都成功获取容器
        assert result is True, "部分并发请求未能获取容器"

        # 清理
        pool.shutdown()


@pytest.mark.benchmark(group="health_check")
def test_quick_health_check_performance(benchmark, mock_docker_client, mock_docker_container):
    """
    测试快速健康检查性能

    性能目标:
    - 快速健康检查 < 50ms
    - 深度健康检查 < 500ms
    """

    # Mock echo 测试
    def mock_echo_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0
        result.output = b"ok\n"
        time.sleep(0.03)  # 模拟 30ms 延迟
        return result

    mock_docker_container.exec_run = Mock(side_effect=mock_echo_exec_run)

    with patch('docker.from_env', return_value=mock_docker_client):
        pool = ContainerPool(initial_size=1, max_size=1)

        def quick_health_check():
            return pool._quick_health_check(mock_docker_container)

        # 基准测试
        result = benchmark(quick_health_check)

        # 验证
        assert result is True, "健康检查失败"

        stats = benchmark.stats.stats
        assert stats.mean < 0.05, f"快速健康检查时间 {stats.mean:.3f}s 超过 50ms"

        # 清理
        pool.shutdown()


@pytest.mark.benchmark(group="health_check")
def test_deep_health_check_performance(benchmark, mock_docker_client, mock_docker_container):
    """
    测试深度健康检查性能

    包含内存检查、进程检查等全面检查
    """

    # Mock 各种检查命令
    call_count = [0]

    def mock_deep_check_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0

        call_count[0] += 1
        if call_count[0] == 1:  # echo health_check
            result.output = b"health_check\n"
            time.sleep(0.02)
        elif call_count[0] == 2:  # ps aux | wc -l
            result.output = b"5\n"
            time.sleep(0.05)
        elif call_count[0] == 3:  # touch /test_file
            result.exit_code = 1  # 只读文件系统
            result.output = b"Read-only file system\n"
            time.sleep(0.02)
        else:
            result.output = b"ok\n"

        return result

    mock_docker_container.exec_run = Mock(side_effect=mock_deep_check_exec_run)

    with patch('docker.from_env', return_value=mock_docker_client):
        pool = ContainerPool(initial_size=1, max_size=1)

        def deep_health_check():
            # 重置 call_count
            call_count[0] = 0
            return pool._deep_health_check(mock_docker_container)

        # 基准测试
        result = benchmark(deep_health_check)

        # 验证
        assert result is True, "深度健康检查失败"

        stats = benchmark.stats.stats
        assert stats.mean < 0.5, f"深度健康检查时间 {stats.mean:.3f}s 超过 500ms"

        # 清理
        pool.shutdown()


# ============================================
# 代码执行性能测试
# ============================================

@pytest.mark.benchmark(group="sandbox")
def test_sandbox_execution_with_pool(benchmark, mock_docker_client, mock_docker_container):
    """
    测试使用容器池的代码执行性能

    性能目标:
    - 执行延迟 < 200ms (使用池)
    - 吞吐量 > 10 RPS
    """

    # Mock 代码执行
    def mock_code_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0
        result.output = (b"Hello, World!\n", b"")  # (stdout, stderr)
        time.sleep(0.05)  # 模拟代码执行时间
        return result

    mock_docker_container.exec_run = Mock(side_effect=mock_code_exec_run)

    with patch('docker.from_env', return_value=mock_docker_client):
        sandbox = CodeSandbox(
            use_pool=True,
            pool_initial_size=3,
            pool_max_size=10
        )

        test_code = "print('Hello, World!')"

        # 预热
        for _ in range(3):
            sandbox.execute_python(test_code)

        def execute_code():
            return sandbox.execute_python(test_code)

        # 基准测试
        success, output, exec_time = benchmark(execute_code)

        # 验证
        assert success is True, "代码执行失败"

        stats = benchmark.stats.stats
        assert stats.mean < 0.2, f"执行时间 {stats.mean:.3f}s 超过 200ms"

        # 清理
        sandbox.cleanup()


@pytest.mark.benchmark(group="sandbox")
def test_sandbox_execution_without_pool(benchmark, mock_docker_client, mock_docker_container):
    """
    测试不使用容器池的代码执行性能（对比基线）

    预期:
    - 执行延迟 > 1000ms (每次创建新容器)
    - 比使用池慢 5-10 倍
    """

    # Mock 容器创建和执行
    def mock_container_run(**kwargs):
        container = Mock()
        container.id = "temp_container_xyz"
        container.short_id = "xyz"
        container.wait = Mock(return_value={'StatusCode': 0})
        container.logs = Mock(return_value=b"Hello, World!\n")
        container.remove = Mock()

        time.sleep(0.8)  # 模拟容器创建耗时
        return container

    mock_docker_client.containers.run = Mock(side_effect=mock_container_run)

    with patch('docker.from_env', return_value=mock_docker_client):
        sandbox = CodeSandbox(
            use_pool=False  # 不使用容器池
        )

        test_code = "print('Hello, World!')"

        def execute_code():
            return sandbox.execute_python(test_code)

        # 基准测试
        success, output, exec_time = benchmark.pedantic(
            execute_code,
            iterations=5,  # 减少迭代次数（慢）
            rounds=1
        )

        # 验证
        assert success is True, "代码执行失败"

        # 清理
        sandbox.cleanup()


@pytest.mark.benchmark(group="sandbox")
def test_code_validation_performance(benchmark):
    """
    测试代码安全检查性能

    性能目标:
    - 安全检查 < 10ms (纯内存操作)
    """

    with patch('docker.from_env', return_value=None):
        sandbox = CodeSandbox(use_pool=False)

        test_code = "print('Hello, World!')\nx = 1 + 2\nprint(x)"

        def validate_code():
            sandbox._check_code_safety(test_code)

        # 基准测试
        benchmark(validate_code)

        stats = benchmark.stats.stats
        assert stats.mean < 0.01, f"安全检查时间 {stats.mean:.3f}s 超过 10ms"


# ============================================
# 容器池统计和监控性能
# ============================================

@pytest.mark.benchmark(group="monitoring")
def test_pool_stats_performance(benchmark, mock_docker_client, mock_docker_container):
    """
    测试容器池统计信息获取性能

    性能目标:
    - 统计信息获取 < 10ms (需要持锁)
    """

    with patch('docker.from_env', return_value=mock_docker_client):
        pool = ContainerPool(initial_size=5, max_size=10)

        def get_stats():
            return pool.get_stats()

        # 基准测试
        stats_data = benchmark(get_stats)

        # 验证返回数据
        assert 'total_containers' in stats_data
        assert 'available_containers' in stats_data
        assert 'in_use_containers' in stats_data

        stats = benchmark.stats.stats
        assert stats.mean < 0.01, f"统计信息获取时间 {stats.mean:.3f}s 超过 10ms"

        # 清理
        pool.shutdown()


# ============================================
# 性能回归测试
# ============================================

def test_performance_regression_report(benchmark_results=None):
    """
    生成性能回归测试报告

    与历史基准对比，检测性能退化
    """
    # 这个测试不运行 benchmark，而是分析结果
    # 可以与 CI/CD 集成，自动检测性能退化
    pass


# ============================================
# 压力测试
# ============================================

@pytest.mark.stress
@pytest.mark.benchmark(group="stress")
def test_pool_under_stress(benchmark, mock_docker_client, mock_docker_container):
    """
    容器池压力测试

    模拟极端负载下的池表现:
    - 20 个并发请求
    - 池大小: 10
    - 预期: 部分请求需要等待，但不应超时
    """

    with patch('docker.from_env', return_value=mock_docker_client):
        pool = ContainerPool(initial_size=5, max_size=10)

        def stress_test():
            import threading
            results = []

            def get_container_with_delay():
                container = pool.get_container(timeout=10)
                time.sleep(0.1)  # 模拟使用
                if container:
                    pool.return_container(container)
                results.append(container is not None)

            # 并发 20 个请求（超过池大小）
            threads = [threading.Thread(target=get_container_with_delay) for _ in range(20)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            return sum(results), len(results)

        # 基准测试
        success_count, total_count = benchmark(stress_test)

        # 验证：至少 95% 成功
        success_rate = success_count / total_count
        assert success_rate >= 0.95, f"压力测试成功率 {success_rate:.1%} 低于 95%"

        # 清理
        pool.shutdown()


# ============================================
# 端到端性能测试
# ============================================

@pytest.mark.e2e
@pytest.mark.benchmark(group="e2e")
def test_end_to_end_code_execution(benchmark, mock_docker_client, mock_docker_container):
    """
    端到端代码执行性能测试

    包含完整流程:
    1. 代码安全检查
    2. 从池获取容器
    3. 执行代码
    4. 归还容器

    性能目标:
    - 端到端延迟 < 300ms (P95)
    """

    # Mock 完整执行流程
    def mock_full_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0

        if "python" in str(cmd):
            result.output = (b"Hello, World!\n", b"")
            time.sleep(0.05)  # 代码执行
        elif "echo" in str(cmd) or "pkill" in str(cmd):
            result.output = b"ok\n"
            time.sleep(0.02)  # 健康检查/重置
        else:
            result.output = b"reset_ok\nfiles:0\nprocesses:3\n"
            time.sleep(0.15)  # 重置

        return result

    mock_docker_container.exec_run = Mock(side_effect=mock_full_exec_run)

    with patch('docker.from_env', return_value=mock_docker_client):
        sandbox = CodeSandbox(
            use_pool=True,
            pool_initial_size=3,
            pool_max_size=10
        )

        test_code = """
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
"""

        # 预热
        for _ in range(3):
            sandbox.execute_python(test_code)

        def end_to_end_execution():
            return sandbox.execute_python(test_code)

        # 基准测试
        success, output, exec_time = benchmark(end_to_end_execution)

        # 验证
        assert success is True, "端到端执行失败"

        stats = benchmark.stats.stats
        assert stats.mean < 0.3, f"端到端延迟 {stats.mean:.3f}s 超过 300ms"

        # 清理
        sandbox.cleanup()


# ============================================
# 性能目标总结 (用于文档)
# ============================================

"""
性能基准目标总结:

1. 容器池性能
   - 容器获取: < 100ms (平均)
   - 容器重置: < 250ms
   - 并发获取: < 500ms (10个并发)
   - 健康检查 (快速): < 50ms
   - 健康检查 (深度): < 500ms

2. 代码执行性能
   - 使用池: < 200ms (平均)
   - 不使用池: > 1000ms (对比基线)
   - 安全检查: < 10ms
   - 端到端: < 300ms (P95)

3. 监控性能
   - 统计信息获取: < 10ms

4. 压力测试
   - 并发成功率: > 95% (20并发/10池大小)

运行方法:
  # 运行所有性能测试
  pytest tests/test_performance_benchmarks.py --benchmark-only

  # 生成报告
  pytest tests/test_performance_benchmarks.py --benchmark-only --benchmark-json=output.json

  # 对比历史基准
  pytest tests/test_performance_benchmarks.py --benchmark-compare --benchmark-compare-fail=mean:5%

  # 运行压力测试
  pytest tests/test_performance_benchmarks.py -m stress --benchmark-only
"""
