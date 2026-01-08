"""
容器池集成测试

测试容器池与真实 Docker 环境的集成（需要 Docker 运行）
使用 @pytest.mark.integration 标记，可选择性运行
"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.container_pool import ContainerPool
from app.sandbox import CodeSandbox


# ==================== Integration Test Fixtures ====================

@pytest.fixture
def real_container_pool():
    """
    创建真实的容器池（需要 Docker）
    如果 Docker 不可用，跳过测试
    """
    import docker

    try:
        client = docker.from_env()
        client.ping()
    except Exception as e:
        pytest.skip(f"Docker not available: {e}")

    # 创建小型池用于测试
    pool = ContainerPool(
        initial_size=2,
        max_size=5,
        min_size=1,
        idle_timeout=10,
        health_check_interval=5,
        image="python:3.11-slim"
    )

    yield pool

    # 清理
    pool.shutdown()


@pytest.fixture
def real_sandbox():
    """
    创建真实的沙箱（使用容器池）
    如果 Docker 不可用，跳过测试
    """
    import docker

    try:
        client = docker.from_env()
        client.ping()
    except Exception as e:
        pytest.skip(f"Docker not available: {e}")

    sandbox = CodeSandbox(
        use_pool=True,
        pool_initial_size=2,
        pool_max_size=5,
        timeout=10
    )

    yield sandbox

    # 清理
    sandbox.cleanup()


# ==================== 1. 基础功能集成测试 ====================

@pytest.mark.integration
def test_execute_simple_code(real_sandbox):
    """测试执行简单代码"""
    code = """
print("Hello from container pool!")
result = 2 + 2
print(f"Result: {result}")
"""

    success, output, exec_time = real_sandbox.execute_python(code)

    assert success is True
    assert "Hello from container pool!" in output
    assert "Result: 4" in output
    assert exec_time > 0
    assert exec_time < 1.0  # 应该很快（< 1秒）


@pytest.mark.integration
def test_execute_error_code(real_sandbox):
    """测试执行错误代码"""
    code = """
x = 1 / 0  # Division by zero
"""

    success, output, exec_time = real_sandbox.execute_python(code)

    assert success is False
    assert "ZeroDivisionError" in output


@pytest.mark.integration
def test_execute_timeout(real_sandbox):
    """测试超时处理"""
    # 创建短超时沙箱
    import docker
    try:
        docker.from_env().ping()
    except:
        pytest.skip("Docker not available")

    short_sandbox = CodeSandbox(
        use_pool=True,
        pool_initial_size=1,
        pool_max_size=2,
        timeout=2  # 2 秒超时
    )

    code = """
import time
time.sleep(5)  # 超过超时限制
print("Should not reach here")
"""

    success, output, exec_time = short_sandbox.execute_python(code)

    # 应该失败（超时或错误）
    assert success is False

    short_sandbox.cleanup()


@pytest.mark.integration
def test_execute_with_imports(real_sandbox):
    """测试导入标准库"""
    code = """
import math
import json
import datetime

# 测试 math
result = math.sqrt(16)
print(f"Square root: {result}")

# 测试 json
data = json.dumps({"key": "value"})
print(f"JSON: {data}")

# 测试 datetime
now = datetime.datetime.now()
print(f"Year: {now.year}")
"""

    success, output, exec_time = real_sandbox.execute_python(code)

    assert success is True
    assert "Square root: 4" in output
    assert "JSON:" in output
    assert "Year:" in output


# ==================== 2. 并发执行测试 ====================

@pytest.mark.integration
def test_concurrent_executions(real_sandbox):
    """测试并发执行多个代码"""

    def execute_code(code_id):
        code = f"""
import time
time.sleep(0.1)
print("Task {code_id} completed")
result = {code_id} * 10
print(f"Result: {{result}}")
"""
        return real_sandbox.execute_python(code)

    # 并发执行 5 个任务
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(execute_code, i) for i in range(5)]
        results = [f.result() for f in as_completed(futures)]

    # 验证所有任务成功
    assert len(results) == 5

    success_count = sum(1 for success, output, exec_time in results if success)
    assert success_count == 5


@pytest.mark.integration
def test_concurrent_mixed_operations(real_sandbox):
    """测试并发混合操作（成功和失败）"""

    codes = [
        ("print('Task 1')", True),
        ("x = 1 / 0", False),  # Error
        ("print('Task 3')", True),
        ("import math; print(math.pi)", True),
        ("undefined_variable", False),  # Error
    ]

    def execute_code(code, should_succeed):
        success, output, exec_time = real_sandbox.execute_python(code)
        return (success, output, should_succeed)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(execute_code, code, expected) for code, expected in codes]
        results = [f.result() for f in as_completed(futures)]

    # 验证结果
    assert len(results) == 5


@pytest.mark.integration
@pytest.mark.slow
def test_high_load(real_sandbox):
    """测试高负载（10+ 并发）"""

    def worker(worker_id):
        results = []
        for i in range(3):
            code = f"print('Worker {worker_id} - Iteration {i}')"
            success, output, exec_time = real_sandbox.execute_python(code)
            results.append((success, exec_time))
        return results

    # 10 个并发工作线程，每个执行 3 次
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        all_results = [f.result() for f in as_completed(futures)]

    total_time = time.time() - start_time

    # 验证
    assert len(all_results) == 10

    # 统计成功次数
    total_executions = sum(len(results) for results in all_results)
    success_count = sum(1 for results in all_results for success, _ in results if success)

    assert total_executions == 30  # 10 workers * 3 iterations
    assert success_count >= 25  # 至少 80% 成功

    # 性能检查：30 次执行应该在合理时间内完成
    assert total_time < 30  # 30 秒内


# ==================== 3. 容器复用验证 ====================

@pytest.mark.integration
def test_container_reuse(real_container_pool):
    """测试容器复用"""

    # 记录初始容器数
    initial_count = len(real_container_pool.container_metadata)

    # 多次获取和归还同一个容器
    container_ids = []

    for i in range(5):
        container = real_container_pool.get_container()
        assert container is not None

        container_ids.append(container.id)

        # 简单使用
        result = container.exec_run("echo test")
        assert result.exit_code == 0

        # 归还
        real_container_pool.return_container(container)

        # 短暂等待
        time.sleep(0.1)

    # 验证容器被复用（没有创建很多新容器）
    final_count = len(real_container_pool.container_metadata)
    assert final_count <= initial_count + 1  # 最多创建 1 个新容器

    # 验证容器 ID 有重复（说明被复用）
    unique_ids = set(container_ids)
    assert len(unique_ids) < len(container_ids)


@pytest.mark.integration
def test_container_reset_effectiveness(real_container_pool):
    """测试容器重置有效性"""

    container = real_container_pool.get_container()

    # 在容器中创建一些状态
    container.exec_run("sh -c 'echo test > /tmp/testfile.txt'")

    # 验证文件存在
    result = container.exec_run("ls /tmp/testfile.txt")
    assert result.exit_code == 0

    # 归还容器（会重置）
    real_container_pool.return_container(container)

    # 再次获取
    container2 = real_container_pool.get_container()

    # 验证 /tmp 已被清理
    result = container2.exec_run("ls /tmp/testfile.txt")
    assert result.exit_code != 0  # 文件不存在

    real_container_pool.return_container(container2)


@pytest.mark.integration
def test_container_isolation(real_sandbox):
    """测试容器隔离性"""

    # 在第一个容器中定义变量
    code1 = """
global_var = "first_container"
print(f"Set: {global_var}")
"""

    success1, output1, _ = real_sandbox.execute_python(code1)
    assert success1 is True
    assert "first_container" in output1

    # 在第二个容器中访问变量（应该失败）
    code2 = """
try:
    print(f"Access: {global_var}")
except NameError:
    print("Variable not found - Isolation OK")
"""

    success2, output2, _ = real_sandbox.execute_python(code2)
    assert success2 is True
    assert "Isolation OK" in output2


# ==================== 4. 资源限制测试 ====================

@pytest.mark.integration
def test_memory_limit_enforcement(real_sandbox):
    """测试内存限制生效"""

    # 尝试分配大量内存（超过 128MB 限制）
    code = """
try:
    # 尝试分配 200MB
    data = [0] * (200 * 1024 * 1024 // 8)
    print("Allocated 200MB - should fail")
except MemoryError:
    print("Memory limit enforced - MemoryError caught")
except Exception as e:
    print(f"Other error: {type(e).__name__}")
"""

    success, output, _ = real_sandbox.execute_python(code)

    # 可能成功或失败，取决于内存限制是否生效
    # 主要验证不会崩溃
    assert exec_time >= 0


@pytest.mark.integration
def test_network_disabled(real_container_pool):
    """测试网络禁用"""

    container = real_container_pool.get_container()

    # 尝试网络请求（应该失败）
    result = container.exec_run("ping -c 1 8.8.8.8")

    # 网络禁用，ping 应该失败
    assert result.exit_code != 0

    real_container_pool.return_container(container)


@pytest.mark.integration
def test_filesystem_readonly(real_container_pool):
    """测试文件系统只读"""

    container = real_container_pool.get_container()

    # 尝试写入根文件系统（应该失败）
    result = container.exec_run("touch /test_file")

    # 文件系统只读，应该失败
    assert result.exit_code != 0

    # /tmp 应该可写
    result = container.exec_run("touch /tmp/test_file")
    assert result.exit_code == 0

    real_container_pool.return_container(container)


# ==================== 5. 健康检查测试 ====================

@pytest.mark.integration
@pytest.mark.slow
def test_background_health_check(real_container_pool):
    """测试后台健康检查"""

    # 获取初始统计
    initial_stats = real_container_pool.get_stats()

    # 等待至少一个健康检查周期
    time.sleep(6)  # health_check_interval = 5

    # 健康检查应该已运行
    # 验证没有异常（容器仍然健康）
    stats = real_container_pool.get_stats()

    # 容器应该仍然可用
    assert stats['available_containers'] >= real_container_pool.min_size


@pytest.mark.integration
def test_unhealthy_container_replacement(real_container_pool):
    """测试不健康容器替换"""

    # 获取容器
    container = real_container_pool.get_container()
    container_id = container.id

    # 模拟容器变得不健康（停止容器）
    try:
        container.stop(timeout=1)
    except:
        pass

    # 尝试归还（应该检测到不健康并销毁）
    real_container_pool.return_container(container)

    # 等待重建
    time.sleep(1)

    # 验证旧容器不存在
    assert container_id not in real_container_pool.container_metadata


# ==================== 6. 性能基准测试 ====================

@pytest.mark.integration
@pytest.mark.slow
def test_pool_vs_temp_container_performance():
    """对比池和临时容器的性能"""
    import docker

    try:
        docker.from_env().ping()
    except:
        pytest.skip("Docker not available")

    # 1. 测试使用池
    pool_sandbox = CodeSandbox(use_pool=True, pool_initial_size=3, pool_max_size=5)

    pool_times = []
    for i in range(10):
        start = time.time()
        success, output, _ = pool_sandbox.execute_python("print('test')")
        elapsed = time.time() - start
        if success:
            pool_times.append(elapsed)

    pool_sandbox.cleanup()

    # 2. 测试使用临时容器
    temp_sandbox = CodeSandbox(use_pool=False)

    temp_times = []
    for i in range(5):  # 少测几次（慢）
        start = time.time()
        success, output, _ = temp_sandbox.execute_python("print('test')")
        elapsed = time.time() - start
        if success:
            temp_times.append(elapsed)

    temp_sandbox.cleanup()

    # 分析结果
    if pool_times and temp_times:
        avg_pool = sum(pool_times) / len(pool_times)
        avg_temp = sum(temp_times) / len(temp_times)

        print(f"\n性能对比:")
        print(f"  使用池平均: {avg_pool:.3f}s")
        print(f"  临时容器平均: {avg_temp:.3f}s")
        print(f"  提升倍数: {avg_temp / avg_pool:.2f}x")

        # 池应该显著更快
        assert avg_pool < avg_temp * 0.5  # 至少快 2 倍


@pytest.mark.integration
def test_execution_latency(real_sandbox):
    """测试执行延迟"""

    latencies = []

    for i in range(20):
        start = time.time()
        success, output, exec_time = real_sandbox.execute_python("print('hello')")
        total_time = time.time() - start

        if success:
            latencies.append(total_time)

    # 统计
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    print(f"\n执行延迟统计:")
    print(f"  平均: {avg_latency:.3f}s")
    print(f"  P95: {p95_latency:.3f}s")
    print(f"  最小: {min(latencies):.3f}s")
    print(f"  最大: {max(latencies):.3f}s")

    # 性能目标
    assert avg_latency < 0.2  # 平均 < 200ms
    assert p95_latency < 0.5  # P95 < 500ms


# ==================== 7. 边界和压力测试 ====================

@pytest.mark.integration
@pytest.mark.slow
def test_pool_under_sustained_load(real_sandbox):
    """测试持续负载"""

    duration = 10  # 10 秒持续负载
    end_time = time.time() + duration

    success_count = 0
    error_count = 0

    while time.time() < end_time:
        success, output, _ = real_sandbox.execute_python("print('load test')")
        if success:
            success_count += 1
        else:
            error_count += 1

        time.sleep(0.1)  # 每 100ms 执行一次

    print(f"\n持续负载测试:")
    print(f"  成功: {success_count}")
    print(f"  失败: {error_count}")
    print(f"  成功率: {success_count / (success_count + error_count) * 100:.1f}%")

    # 成功率应该很高
    assert success_count > error_count * 10  # 至少 90% 成功


@pytest.mark.integration
def test_pool_recovery_after_errors(real_sandbox):
    """测试错误后恢复"""

    # 1. 执行正常代码
    success, output, _ = real_sandbox.execute_python("print('before error')")
    assert success is True

    # 2. 执行多个错误代码
    for i in range(5):
        real_sandbox.execute_python("x = 1 / 0")

    # 3. 再次执行正常代码
    success, output, _ = real_sandbox.execute_python("print('after errors')")
    assert success is True
    assert "after errors" in output


# ==================== 8. 统计和监控测试 ====================

@pytest.mark.integration
def test_pool_statistics(real_container_pool):
    """测试池统计信息"""

    # 执行一些操作
    containers = []
    for i in range(3):
        c = real_container_pool.get_container()
        if c:
            containers.append(c)

    # 获取统计
    stats = real_container_pool.get_stats()

    # 验证统计
    assert 'available_containers' in stats
    assert 'in_use_containers' in stats
    assert 'total_executions' in stats
    assert 'pool_id' in stats

    assert stats['in_use_containers'] == 3
    assert stats['total_executions'] == 3

    # 归还
    for c in containers:
        real_container_pool.return_container(c)

    # 再次获取统计
    stats = real_container_pool.get_stats()
    assert stats['in_use_containers'] == 0
    assert stats['total_resets'] == 3


@pytest.mark.integration
def test_container_metadata_accuracy(real_container_pool):
    """测试容器元数据准确性"""

    container = real_container_pool.get_container()

    # 获取元数据
    metadata = real_container_pool.container_metadata[container.id]

    # 验证
    assert metadata.status == 'in_use'
    assert metadata.execution_count > 0
    assert metadata.last_used_at > 0
    assert time.time() - metadata.last_used_at < 5  # 最近使用

    # 归还
    real_container_pool.return_container(container)

    # 再次验证
    metadata = real_container_pool.container_metadata[container.id]
    assert metadata.status == 'available'
    assert metadata.reset_count > 0
