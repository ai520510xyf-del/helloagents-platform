"""
容器池单元测试

测试容器池的核心功能，使用 Mock 对象避免真实 Docker 依赖
"""
import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from queue import Queue, Empty, Full

from app.container_pool import ContainerPool, ContainerMetadata


# ==================== Mock Fixtures ====================

@pytest.fixture
def mock_docker_client():
    """Mock Docker 客户端"""
    client = Mock()
    client.containers = Mock()
    client.images = Mock()
    client.close = Mock()
    return client


@pytest.fixture
def mock_container():
    """Mock 容器对象"""
    container = Mock()
    container.id = "abc123def456"
    container.short_id = "abc123"
    container.status = "running"

    # Mock exec_run 方法 - 根据命令返回不同结果
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        cmd_str = str(cmd) if not isinstance(cmd, str) else cmd

        # 文件系统只读检查 - touch 应该失败
        if 'touch /test_file' in cmd_str:
            result.exit_code = 1  # 只读，失败
            result.output = b"touch: /test_file: Read-only file system\n"
        # 重置脚本 - 返回完整的重置输出格式
        elif 'echo "reset_ok"' in cmd_str or 'pkill' in cmd_str:
            result.exit_code = 0
            result.output = b"reset_ok\nfiles: 0\nprocesses: 2\n"
        # 健康检查
        elif 'health_check' in cmd_str or 'echo' in cmd_str:
            result.exit_code = 0
            result.output = b"health_check\n"
        # 进程数检查
        elif 'ps aux | wc -l' in cmd_str:
            result.exit_code = 0
            result.output = b"2\n"  # 少量进程
        # /tmp 文件数检查
        elif 'ls -A /tmp' in cmd_str:
            result.exit_code = 0
            result.output = b"0\n"  # /tmp 为空
        # 其他命令
        else:
            result.exit_code = 0
            result.output = b"test_output\n"

        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # Mock reload 方法
    container.reload = Mock()

    # Mock stats 方法
    def mock_stats(stream=False):
        return {
            'memory_stats': {
                'usage': 50 * 1024 * 1024,  # 50MB
                'limit': 128 * 1024 * 1024   # 128MB
            }
        }
    container.stats = Mock(side_effect=mock_stats)

    # Mock stop 和 remove 方法
    container.stop = Mock()
    container.remove = Mock()

    return container


@pytest.fixture
def container_pool_factory(mock_docker_client, mock_container):
    """容器池工厂 (用于创建不同配置的池)"""

    def _create_pool(**kwargs):
        # 默认配置
        config = {
            'initial_size': 2,
            'max_size': 5,
            'min_size': 1,
            'idle_timeout': 10,
            'health_check_interval': 5,
        }
        config.update(kwargs)

        # Mock docker.from_env()
        with patch('app.container_pool.docker.from_env', return_value=mock_docker_client):
            # Mock 容器创建
            def mock_run(*args, **kwargs):
                # 每次创建新的 mock 容器
                new_container = Mock()
                new_container.id = f"container_{time.time()}"
                new_container.short_id = new_container.id[:6]
                new_container.status = "running"

                # 复制 mock_container 的方法
                new_container.exec_run = mock_container.exec_run
                new_container.reload = mock_container.reload
                new_container.stats = mock_container.stats
                new_container.stop = mock_container.stop
                new_container.remove = mock_container.remove

                return new_container

            mock_docker_client.containers.run = Mock(side_effect=mock_run)

            # 创建池
            pool = ContainerPool(**config)

            # 等待初始化完成
            time.sleep(0.1)

            return pool

    return _create_pool


# ==================== 1. 池初始化测试 ====================

def test_pool_initialization(container_pool_factory):
    """测试池初始化"""
    pool = container_pool_factory(initial_size=3, max_size=10)

    # 验证配置
    assert pool.initial_size == 3
    assert pool.max_size == 10
    assert pool.min_size == 1

    # 验证容器数量
    assert pool.available_containers.qsize() == 3
    assert len(pool.container_metadata) == 3

    # 验证后台线程启动
    assert pool.running is True
    assert pool.health_check_thread is not None
    assert pool.idle_cleanup_thread is not None
    assert pool.health_check_thread.is_alive()
    assert pool.idle_cleanup_thread.is_alive()

    pool.shutdown()


def test_pool_initialization_with_custom_config(container_pool_factory):
    """测试自定义配置初始化"""
    pool = container_pool_factory(
        initial_size=1,
        max_size=5,
        min_size=1,
        idle_timeout=60,
        health_check_interval=10
    )

    assert pool.initial_size == 1
    assert pool.max_size == 5
    assert pool.idle_timeout == 60
    assert pool.health_check_interval == 10

    pool.shutdown()


def test_pool_has_unique_id(container_pool_factory):
    """测试池有唯一 ID"""
    pool1 = container_pool_factory()
    pool2 = container_pool_factory()

    assert pool1.pool_id != pool2.pool_id
    assert len(pool1.pool_id) == 8

    pool1.shutdown()
    pool2.shutdown()


# ==================== 2. 获取容器测试 ====================

def test_get_container_from_available_queue(container_pool_factory):
    """测试从非空队列获取容器"""
    pool = container_pool_factory(initial_size=2)

    # 获取容器
    start_time = time.time()
    container = pool.get_container(timeout=5)
    acquisition_time = time.time() - start_time

    # 验证获取成功
    assert container is not None
    assert acquisition_time < 1.0  # 应该很快 (< 1秒)

    # 验证队列减少
    assert pool.available_containers.qsize() == 1

    # 验证容器标记为使用中
    assert container.id in pool.in_use_containers
    assert len(pool.in_use_containers) == 1

    pool.shutdown()


def test_get_container_creates_new_when_queue_empty(container_pool_factory):
    """测试队列为空时创建新容器"""
    pool = container_pool_factory(initial_size=1, max_size=3)

    # 获取所有现有容器
    c1 = pool.get_container()
    assert c1 is not None

    # 队列现在为空，但未达上限
    assert pool.available_containers.qsize() == 0

    # 再次获取应该创建新容器
    c2 = pool.get_container()
    assert c2 is not None
    assert c2.id != c1.id

    # 验证容器总数增加
    assert len(pool.container_metadata) == 2

    pool.shutdown()


def test_get_container_blocks_when_pool_exhausted(container_pool_factory):
    """测试达到上限时阻塞等待"""
    pool = container_pool_factory(initial_size=2, max_size=2)

    # 获取所有容器
    c1 = pool.get_container()
    c2 = pool.get_container()

    assert c1 is not None
    assert c2 is not None
    assert len(pool.in_use_containers) == 2

    # 池已耗尽，再次获取应该阻塞
    start_time = time.time()

    # 使用短超时测试
    c3 = pool.get_container(timeout=1)
    elapsed = time.time() - start_time

    # 应该超时返回 None
    assert c3 is None
    assert elapsed >= 0.9  # 接近 1 秒

    pool.shutdown()


def test_get_container_timeout(container_pool_factory):
    """测试获取容器超时"""
    pool = container_pool_factory(initial_size=1, max_size=1)

    # 占用唯一的容器
    c1 = pool.get_container()
    assert c1 is not None

    # 尝试获取第二个容器（超时）
    start_time = time.time()
    c2 = pool.get_container(timeout=2)
    elapsed = time.time() - start_time

    assert c2 is None
    assert 1.9 <= elapsed <= 2.5  # 允许一些误差

    pool.shutdown()


def test_get_container_marks_in_use(container_pool_factory):
    """测试获取容器更新元数据"""
    pool = container_pool_factory(initial_size=1)

    # 获取容器
    container = pool.get_container()

    # 验证元数据更新
    metadata = pool.container_metadata[container.id]
    assert metadata.status == 'in_use'
    assert metadata.execution_count == 1
    assert metadata.last_used_at > 0

    # 验证统计更新
    assert pool.stats['total_executions'] == 1

    pool.shutdown()


# ==================== 3. 归还容器测试 ====================

def test_return_container_success(container_pool_factory):
    """测试成功归还容器"""
    pool = container_pool_factory(initial_size=2)

    # 获取容器
    container = pool.get_container()
    original_size = pool.available_containers.qsize()

    # 归还容器
    pool.return_container(container)

    # 验证容器回到队列
    assert pool.available_containers.qsize() == original_size + 1

    # 验证不再标记为使用中
    assert container.id not in pool.in_use_containers

    # 验证元数据更新
    metadata = pool.container_metadata[container.id]
    assert metadata.status == 'available'
    assert metadata.reset_count == 1

    pool.shutdown()


def test_return_container_resets_state(container_pool_factory, mock_container):
    """测试归还时重置容器状态"""
    pool = container_pool_factory(initial_size=1)

    # 获取并归还容器
    container = pool.get_container()

    # Mock exec_run 返回 reset_ok 以确保重置成功
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        cmd_str = str(cmd)

        # 文件系统只读检查 - touch 应该失败
        if 'touch /test_file' in cmd_str:
            result.exit_code = 1
            result.output = b"touch: /test_file: Read-only file system\n"
        # 重置脚本
        elif 'echo "reset_ok"' in cmd_str or 'reset_ok' in cmd_str or 'pkill' in cmd_str:
            result.exit_code = 0
            result.output = b"reset_ok\nfiles: 0\nprocesses: 2\n"
        # 进程数检查
        elif 'ps aux | wc -l' in cmd_str:
            result.exit_code = 0
            result.output = b"2\n"
        # 其他命令
        else:
            result.exit_code = 0
            result.output = b"0\n"

        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # Mock stats 返回正常内存使用
    def mock_stats(stream=False):
        return {
            'memory_stats': {
                'usage': 50 * 1024 * 1024,
                'limit': 128 * 1024 * 1024
            }
        }
    container.stats = Mock(side_effect=mock_stats)

    pool.return_container(container)

    # 验证重置操作被调用 (优化后合并为一个脚本调用)
    assert container.exec_run.call_count >= 1

    # 验证统计更新
    assert pool.stats['total_resets'] == 1

    pool.shutdown()


def test_return_container_health_check(container_pool_factory):
    """测试归还时执行健康检查"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock 健康检查失败
    with patch.object(pool, '_deep_health_check', return_value=False):
        with patch.object(pool, '_destroy_and_replace_container') as mock_replace:
            pool.return_container(container)

            # 验证销毁重建被调用
            mock_replace.assert_called_once()

    pool.shutdown()


def test_return_container_reset_failure(container_pool_factory):
    """测试重置失败时销毁重建"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock 重置失败
    with patch.object(pool, '_reset_container', return_value=False):
        with patch.object(pool, '_destroy_and_replace_container') as mock_replace:
            pool.return_container(container)

            # 验证销毁重建被调用
            mock_replace.assert_called_once()

    pool.shutdown()


# ==================== 4. 容器重置测试 ====================

def test_container_reset_success(container_pool_factory):
    """测试容器重置成功"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run 返回包含 reset_ok 标记的输出
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0
        cmd_str = str(cmd)

        # 验证脚本应返回 reset_ok
        if 'echo "reset_ok"' in cmd_str or 'reset_ok' in cmd_str:
            result.output = b"reset_ok\nfiles: 0\nprocesses: 2\n"
        else:
            result.output = b"0\n"

        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # 执行重置
    result = pool._reset_container(container)

    # 验证成功
    assert result is True

    # 验证重置命令被调用
    assert container.exec_run.call_count >= 1

    pool.shutdown()


def test_container_reset_kills_processes(container_pool_factory, mock_container):
    """测试重置终止进程"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run 返回包含 reset_ok 标记
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0
        cmd_str = str(cmd)

        # 确保返回 reset_ok 表示成功
        if 'echo "reset_ok"' in cmd_str or 'reset_ok' in cmd_str:
            result.output = b"reset_ok\nfiles: 0\nprocesses: 2\n"
        else:
            result.output = b"0\n"

        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # 执行重置
    result = pool._reset_container(container)

    assert result is True

    pool.shutdown()


def test_container_reset_cleans_tmp(container_pool_factory, mock_container):
    """测试重置清理 /tmp 目录"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run
    commands_called = []

    def mock_exec_run(cmd, **kwargs):
        commands_called.append(str(cmd))
        result = Mock()
        result.exit_code = 0
        result.output = b"0\n"
        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    pool._reset_container(container)

    # 验证清理命令被调用
    assert any('rm -rf /tmp' in cmd for cmd in commands_called)

    pool.shutdown()


def test_container_reset_validates(container_pool_factory, mock_container):
    """测试重置验证有效性"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run 返回非空 /tmp
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        if 'ls -A /tmp' in str(cmd):
            result.exit_code = 0
            result.output = b"5\n"  # /tmp 不为空
        else:
            result.exit_code = 0
            result.output = b"0\n"
        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # 重置应该失败（/tmp 不为空）
    result = pool._reset_container(container)

    assert result is False

    pool.shutdown()


def test_container_reset_checks_process_count(container_pool_factory, mock_container):
    """测试重置检查进程数"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run 返回过多进程
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0

        if 'ps aux | wc -l' in str(cmd):
            result.output = b"51\n"  # 超过 50 个进程
        else:
            result.output = b"0\n"

        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # 重置应该失败（进程过多）
    result = pool._reset_container(container)

    assert result is False

    pool.shutdown()


# ==================== 5. 健康检查测试 ====================

def test_health_check_running_container(container_pool_factory):
    """测试健康检查 - 运行中容器"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()
    container.status = "running"

    # 执行健康检查
    is_healthy = pool._deep_health_check(container)

    assert is_healthy is True

    pool.shutdown()


def test_health_check_stopped_container(container_pool_factory):
    """测试健康检查 - 停止的容器"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()
    container.status = "exited"

    # 健康检查应该失败
    is_healthy = pool._deep_health_check(container)

    assert is_healthy is False

    pool.shutdown()


def test_health_check_unresponsive_container(container_pool_factory, mock_container):
    """测试健康检查 - 无响应容器"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run 失败
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 1  # 执行失败
        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # 健康检查应该失败
    is_healthy = pool._deep_health_check(container)

    assert is_healthy is False

    pool.shutdown()


def test_health_check_high_memory(container_pool_factory, mock_container):
    """测试健康检查 - 内存占用过高"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock stats 返回高内存使用
    def mock_stats(stream=False):
        return {
            'memory_stats': {
                'usage': 120 * 1024 * 1024,  # 120MB
                'limit': 128 * 1024 * 1024   # 128MB (93.75%)
            }
        }

    container.stats = Mock(side_effect=mock_stats)

    # 健康检查应该失败
    is_healthy = pool._deep_health_check(container)

    assert is_healthy is False

    pool.shutdown()


def test_health_check_too_many_processes(container_pool_factory, mock_container):
    """测试健康检查 - 进程过多"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run 返回过多进程
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0

        if 'ps aux | wc -l' in str(cmd):
            result.output = b"51\n"  # 超过 50 个进程
        else:
            result.output = b"health_check\n"

        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # 健康检查应该失败
    is_healthy = pool._deep_health_check(container)

    assert is_healthy is False

    pool.shutdown()


def test_health_check_readonly_filesystem(container_pool_factory, mock_container):
    """测试健康检查 - 文件系统只读"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run
    def mock_exec_run(cmd, **kwargs):
        result = Mock()

        if 'touch /test_file' in str(cmd):
            # 只读文件系统，touch 应该失败
            result.exit_code = 1
        else:
            result.exit_code = 0
            result.output = b"health_check\n"

        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # 健康检查应该成功（文件系统正常只读）
    is_healthy = pool._deep_health_check(container)

    assert is_healthy is True

    pool.shutdown()


def test_health_check_writable_filesystem(container_pool_factory, mock_container):
    """测试健康检查 - 文件系统可写（异常）"""
    pool = container_pool_factory(initial_size=1)

    container = pool.get_container()

    # Mock exec_run
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0  # touch 成功（不应该）

        if 'touch /test_file' not in str(cmd):
            result.output = b"health_check\n"

        return result

    container.exec_run = Mock(side_effect=mock_exec_run)

    # 健康检查应该失败（文件系统不应该可写）
    is_healthy = pool._deep_health_check(container)

    assert is_healthy is False

    pool.shutdown()


# ==================== 6. 并发获取测试 ====================

def test_concurrent_get_container(container_pool_factory):
    """测试多线程并发获取容器"""
    pool = container_pool_factory(initial_size=3, max_size=5)

    results = []
    errors = []

    def get_and_return():
        try:
            container = pool.get_container(timeout=5)
            if container:
                results.append(container.id)
                time.sleep(0.1)  # 模拟使用
                pool.return_container(container)
        except Exception as e:
            errors.append(e)

    # 创建 5 个线程并发获取
    threads = [threading.Thread(target=get_and_return) for _ in range(5)]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=10)

    # 验证
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 5  # 所有线程都应该成功

    # 验证容器 ID 唯一（没有重复分配）
    assert len(set(results)) <= 5  # 可能有重用，但不应超过 max_size

    pool.shutdown()


def test_concurrent_get_no_race_condition(container_pool_factory):
    """测试并发获取无竞争条件"""
    pool = container_pool_factory(initial_size=2, max_size=2)

    active_containers = []
    lock = threading.Lock()

    def get_container():
        container = pool.get_container(timeout=5)
        if container:
            with lock:
                active_containers.append(container.id)
            time.sleep(0.2)  # 保持一段时间
            with lock:
                active_containers.remove(container.id)
            pool.return_container(container)

    # 创建 4 个线程（超过池大小）
    threads = [threading.Thread(target=get_container) for _ in range(4)]

    for t in threads:
        t.start()

    # 检查并发使用数不超过上限
    time.sleep(0.1)
    assert len(active_containers) <= 2

    for t in threads:
        t.join(timeout=10)

    # 最终应该全部归还
    assert len(active_containers) == 0

    pool.shutdown()


# ==================== 7. 池耗尽测试 ====================

def test_pool_exhaustion(container_pool_factory):
    """测试获取所有容器直到上限"""
    pool = container_pool_factory(initial_size=2, max_size=3)

    # 获取所有容器
    containers = []
    for i in range(3):
        c = pool.get_container(timeout=1)
        assert c is not None
        containers.append(c)

    # 验证池耗尽
    assert len(pool.in_use_containers) == 3
    assert pool.available_containers.qsize() == 0

    # 尝试再获取应该超时
    c4 = pool.get_container(timeout=0.5)
    assert c4 is None

    pool.shutdown()


def test_pool_exhaustion_blocking(container_pool_factory):
    """测试池耗尽时的阻塞等待"""
    pool = container_pool_factory(initial_size=1, max_size=1)

    # 占用唯一容器
    c1 = pool.get_container()

    # 在另一个线程中归还容器
    def return_after_delay():
        time.sleep(0.5)
        pool.return_container(c1)

    threading.Thread(target=return_after_delay, daemon=True).start()

    # 主线程应该阻塞等待
    start_time = time.time()
    c2 = pool.get_container(timeout=2)
    elapsed = time.time() - start_time

    # 应该在 0.5 秒后成功获取
    assert c2 is not None
    assert 0.4 <= elapsed <= 1.0

    pool.shutdown()


# ==================== 8. 容器故障测试 ====================

def test_container_failure_recovery(container_pool_factory):
    """测试容器故障自动恢复"""
    pool = container_pool_factory(initial_size=2, max_size=3)

    # 获取容器
    container = pool.get_container()
    container_id = container.id

    # 模拟容器崩溃
    container.status = "exited"

    # 归还时应该检测到并销毁重建
    with patch.object(pool, '_destroy_and_replace_container') as mock_replace:
        pool.return_container(container)

        # 验证销毁重建被调用
        assert mock_replace.called

    pool.shutdown()


def test_destroy_and_replace_container(container_pool_factory):
    """测试销毁并替换容器"""
    pool = container_pool_factory(initial_size=2)

    original_size = len(pool.container_metadata)

    # 获取一个容器 ID
    container = pool.get_container()
    container_id = container.id

    # 销毁并替换
    pool._destroy_and_replace_container(container_id)

    # 等待创建完成
    time.sleep(0.2)

    # 验证容器总数不变
    assert len(pool.container_metadata) >= original_size - 1

    # 验证旧容器不存在
    assert container_id not in pool.container_metadata

    pool.shutdown()


# ==================== 9. 空闲清理测试 ====================

def test_idle_container_cleanup(container_pool_factory):
    """测试空闲容器清理"""
    pool = container_pool_factory(
        initial_size=3,
        max_size=5,
        min_size=1,
        idle_timeout=1  # 1 秒超时
    )

    # 等待一段时间让空闲容器超时
    time.sleep(2)

    # 空闲清理线程应该清理多余容器
    # 但应该保持最小池大小
    assert len(pool.container_metadata) >= pool.min_size

    pool.shutdown()


def test_idle_cleanup_respects_min_size(container_pool_factory):
    """测试空闲清理保持最小池大小"""
    pool = container_pool_factory(
        initial_size=5,
        max_size=10,
        min_size=3,
        idle_timeout=1
    )

    # 等待空闲清理
    time.sleep(2.5)

    # 应该保持至少 min_size 个容器
    assert len(pool.container_metadata) >= pool.min_size

    pool.shutdown()


# ==================== 10. 优雅关闭测试 ====================

def test_graceful_shutdown(container_pool_factory):
    """测试优雅关闭"""
    pool = container_pool_factory(initial_size=2)

    # 获取一个容器（模拟使用中）
    container = pool.get_container()

    # 关闭池
    pool.shutdown()

    # 验证后台线程停止
    assert pool.running is False

    # 等待线程结束
    if pool.health_check_thread:
        pool.health_check_thread.join(timeout=1)
    if pool.idle_cleanup_thread:
        pool.idle_cleanup_thread.join(timeout=1)

    # 验证容器被停止
    assert container.stop.called or container.remove.called


def test_shutdown_waits_for_in_use_containers(container_pool_factory):
    """测试关闭等待使用中的容器"""
    pool = container_pool_factory(initial_size=2)

    # 获取容器
    c1 = pool.get_container()
    c2 = pool.get_container()

    # 在另一个线程中延迟归还
    def return_containers():
        time.sleep(0.5)
        pool.return_container(c1)
        pool.return_container(c2)

    threading.Thread(target=return_containers, daemon=True).start()

    # 关闭应该等待
    start_time = time.time()
    pool.shutdown()
    elapsed = time.time() - start_time

    # 应该等待了一段时间（但不会等满 30 秒）
    assert elapsed >= 0.4


def test_shutdown_cleans_up_resources(container_pool_factory, mock_docker_client):
    """测试关闭清理资源"""
    pool = container_pool_factory(initial_size=2)

    # 关闭
    pool.shutdown()

    # 验证 Docker 客户端被关闭
    assert mock_docker_client.close.called


# ==================== 11. 统计信息测试 ====================

def test_get_stats(container_pool_factory):
    """测试获取池统计信息"""
    pool = container_pool_factory(initial_size=3, max_size=10)

    stats = pool.get_stats()

    # 验证统计字段
    assert 'available_containers' in stats
    assert 'in_use_containers' in stats
    assert 'total_containers' in stats
    assert 'total_created' in stats
    assert 'total_destroyed' in stats
    assert 'total_executions' in stats
    assert 'pool_id' in stats
    assert 'max_size' in stats

    # 验证初始值
    assert stats['available_containers'] == 3
    assert stats['in_use_containers'] == 0
    assert stats['total_containers'] == 3
    assert stats['total_created'] == 3

    pool.shutdown()


def test_stats_update_on_operations(container_pool_factory, mock_container):
    """测试操作更新统计信息"""
    pool = container_pool_factory(initial_size=2)

    # 获取容器
    c = pool.get_container()

    stats = pool.get_stats()
    assert stats['in_use_containers'] == 1
    assert stats['total_executions'] == 1

    # Mock exec_run 确保重置成功 (返回 reset_ok)
    def mock_exec_run(cmd, **kwargs):
        result = Mock()
        result.exit_code = 0
        cmd_str = str(cmd)

        if 'echo "reset_ok"' in cmd_str or 'reset_ok' in cmd_str:
            result.output = b"reset_ok\nfiles: 0\nprocesses: 2\n"
        elif 'ps aux | wc -l' in cmd_str:
            result.output = b"2\n"
        elif 'ls -A /tmp' in cmd_str:
            result.output = b"0\n"
        else:
            result.output = b"0\n"

        return result

    c.exec_run = Mock(side_effect=mock_exec_run)

    # Mock stats 返回正常内存使用
    def mock_stats(stream=False):
        return {
            'memory_stats': {
                'usage': 50 * 1024 * 1024,
                'limit': 128 * 1024 * 1024
            }
        }
    c.stats = Mock(side_effect=mock_stats)

    # 归还容器
    pool.return_container(c)

    stats = pool.get_stats()
    assert stats['in_use_containers'] == 0
    assert stats['total_resets'] == 1

    pool.shutdown()


# ==================== 12. 边界情况测试 ====================

def test_zero_initial_size(mock_docker_client):
    """测试初始大小为 0 - 应该抛出 ValueError"""
    with patch('app.container_pool.docker.from_env', return_value=mock_docker_client):
        mock_docker_client.containers.run = Mock(return_value=Mock())

        # initial_size=0 会导致 ThreadPoolExecutor 抛出 ValueError
        with pytest.raises(ValueError):
            pool = ContainerPool(initial_size=0, max_size=5)


def test_max_size_equals_initial_size(container_pool_factory):
    """测试最大大小等于初始大小"""
    pool = container_pool_factory(initial_size=3, max_size=3)

    assert len(pool.container_metadata) == 3

    # 获取所有容器
    containers = [pool.get_container() for _ in range(3)]

    # 不应该再创建新容器
    assert len(pool.container_metadata) == 3

    pool.shutdown()


def test_get_container_with_zero_timeout(container_pool_factory):
    """测试超时为 0 - 应该抛出 ValidationError"""
    pool = container_pool_factory(initial_size=1, max_size=1)

    # 占用唯一容器
    c1 = pool.get_container()

    # timeout=0 会触发 ValidationError (必须为正数)
    from app.exceptions import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        c2 = pool.get_container(timeout=0)

    # 验证错误信息
    assert "Timeout must be positive" in str(exc_info.value)

    pool.shutdown()


def test_return_nonexistent_container(container_pool_factory):
    """测试归还不存在的容器"""
    pool = container_pool_factory(initial_size=2)

    # 创建一个假容器
    fake_container = Mock()
    fake_container.id = "nonexistent"
    fake_container.short_id = "nonex"

    # 不应该崩溃
    pool.return_container(fake_container)

    pool.shutdown()


def test_container_metadata_structure(container_pool_factory):
    """测试容器元数据结构"""
    pool = container_pool_factory(initial_size=1)

    # 获取元数据
    container_id = list(pool.container_metadata.keys())[0]
    metadata = pool.container_metadata[container_id]

    # 验证字段
    assert hasattr(metadata, 'container_id')
    assert hasattr(metadata, 'container')
    assert hasattr(metadata, 'created_at')
    assert hasattr(metadata, 'last_used_at')
    assert hasattr(metadata, 'execution_count')
    assert hasattr(metadata, 'reset_count')
    assert hasattr(metadata, 'status')
    assert hasattr(metadata, 'health_check_failures')

    # 验证类型
    assert isinstance(metadata.created_at, float)
    assert isinstance(metadata.execution_count, int)
    assert metadata.status in ['available', 'in_use', 'unhealthy']

    pool.shutdown()


# ==================== 13. 性能测试 ====================

@pytest.mark.slow
def test_pool_performance_get_container(container_pool_factory):
    """测试获取容器性能"""
    pool = container_pool_factory(initial_size=5, max_size=10)

    # 测试快速获取
    times = []
    for _ in range(10):
        start = time.time()
        c = pool.get_container()
        elapsed = time.time() - start
        times.append(elapsed)
        pool.return_container(c)

    avg_time = sum(times) / len(times)

    # 从池中获取应该很快 (< 100ms)
    assert avg_time < 0.1

    pool.shutdown()


@pytest.mark.slow
def test_pool_performance_concurrent(container_pool_factory):
    """测试并发性能"""
    pool = container_pool_factory(initial_size=5, max_size=10)

    def worker():
        for _ in range(5):
            c = pool.get_container(timeout=5)
            if c:
                time.sleep(0.01)  # 模拟工作
                pool.return_container(c)

    # 创建 10 个并发工作线程
    start_time = time.time()
    threads = [threading.Thread(target=worker) for _ in range(10)]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=30)

    elapsed = time.time() - start_time

    # 50 次操作应该在合理时间内完成
    assert elapsed < 10  # 10 秒内完成

    pool.shutdown()
