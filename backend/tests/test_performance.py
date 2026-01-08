"""
性能测试脚本

用于验证容器池性能优化效果
"""

import time
import pytest
from app.container_pool import ContainerPool


class TestContainerPoolPerformance:
    """容器池性能测试"""

    @pytest.fixture
    def pool(self):
        """创建容器池实例"""
        pool = ContainerPool(
            initial_size=2,
            max_size=5,
            min_size=1,
            image="python:3.11-slim"
        )
        yield pool
        pool.shutdown()

    def test_quick_health_check_performance(self, pool):
        """测试快速健康检查性能 (应该 < 100ms)"""
        container = pool.get_container(timeout=30)
        assert container is not None

        # 执行多次快速健康检查,记录平均耗时
        check_times = []
        for _ in range(10):
            start = time.time()
            is_healthy = pool._quick_health_check(container)
            elapsed = (time.time() - start) * 1000  # 转换为毫秒

            assert is_healthy, "容器应该是健康的"
            check_times.append(elapsed)

        avg_time = sum(check_times) / len(check_times)
        print(f"\n快速健康检查平均耗时: {avg_time:.2f}ms")

        # 验证性能目标
        assert avg_time < 100, f"快速健康检查应该 < 100ms, 实际: {avg_time:.2f}ms"
        assert max(check_times) < 150, f"最大耗时应该 < 150ms"

        pool.return_container(container)

    def test_deep_health_check_performance(self, pool):
        """测试深度健康检查性能 (应该 < 600ms)"""
        container = pool.get_container(timeout=30)
        assert container is not None

        # 执行多次深度健康检查,记录平均耗时
        check_times = []
        for _ in range(5):
            start = time.time()
            is_healthy = pool._deep_health_check(container)
            elapsed = (time.time() - start) * 1000

            assert is_healthy, "容器应该是健康的"
            check_times.append(elapsed)

        avg_time = sum(check_times) / len(check_times)
        print(f"\n深度健康检查平均耗时: {avg_time:.2f}ms")

        # 验证性能目标
        assert avg_time < 600, f"深度健康检查应该 < 600ms, 实际: {avg_time:.2f}ms"

        pool.return_container(container)

    def test_container_reset_performance(self, pool):
        """测试容器重置性能 (应该 < 300ms)"""
        container = pool.get_container(timeout=30)
        assert container is not None

        # 在容器中创建一些状态
        container.exec_run("python3 -c 'import time; time.sleep(0.1)'", detach=True)
        container.exec_run("sh -c 'echo test > /tmp/test.txt'")

        # 执行多次重置,记录平均耗时
        reset_times = []
        for _ in range(5):
            start = time.time()
            success = pool._reset_container(container)
            elapsed = (time.time() - start) * 1000

            assert success, "容器重置应该成功"
            reset_times.append(elapsed)

        avg_time = sum(reset_times) / len(reset_times)
        print(f"\n容器重置平均耗时: {avg_time:.2f}ms")

        # 验证性能目标
        assert avg_time < 300, f"容器重置应该 < 300ms, 实际: {avg_time:.2f}ms"
        assert max(reset_times) < 400, f"最大耗时应该 < 400ms"

        pool.return_container(container)

    def test_container_acquisition_performance(self, pool):
        """测试容器获取性能 (应该 < 150ms)"""
        # 执行多次容器获取,记录平均耗时
        acquisition_times = []

        for _ in range(10):
            start = time.time()
            container = pool.get_container(timeout=30)
            elapsed = (time.time() - start) * 1000

            assert container is not None, "应该成功获取容器"
            acquisition_times.append(elapsed)

            pool.return_container(container)
            time.sleep(0.5)  # 等待容器重置完成

        avg_time = sum(acquisition_times) / len(acquisition_times)
        print(f"\n容器获取平均耗时: {avg_time:.2f}ms")

        # 验证性能目标
        assert avg_time < 150, f"容器获取应该 < 150ms, 实际: {avg_time:.2f}ms"

    def test_container_return_performance(self, pool):
        """测试容器归还性能 (应该 < 400ms)"""
        # 执行多次容器归还,记录平均耗时
        return_times = []

        for _ in range(5):
            container = pool.get_container(timeout=30)
            assert container is not None

            # 在容器中执行一些操作
            container.exec_run("python3 -c 'print(\"test\")'")

            start = time.time()
            pool.return_container(container)
            elapsed = (time.time() - start) * 1000

            return_times.append(elapsed)
            time.sleep(0.2)

        avg_time = sum(return_times) / len(return_times)
        print(f"\n容器归还平均耗时: {avg_time:.2f}ms")

        # 验证性能目标
        assert avg_time < 400, f"容器归还应该 < 400ms, 实际: {avg_time:.2f}ms"

    def test_concurrent_container_operations(self, pool):
        """测试并发容器操作性能"""
        import threading

        operation_times = []
        errors = []

        def container_operation():
            try:
                start = time.time()

                # 获取容器
                container = pool.get_container(timeout=30)
                if container is None:
                    errors.append("获取容器失败")
                    return

                # 执行操作
                container.exec_run("echo test")

                # 归还容器
                pool.return_container(container)

                elapsed = (time.time() - start) * 1000
                operation_times.append(elapsed)

            except Exception as e:
                errors.append(str(e))

        # 启动 10 个并发线程
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=container_operation)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0, f"并发操作出现错误: {errors}"
        assert len(operation_times) == 10, "应该完成 10 次操作"

        avg_time = sum(operation_times) / len(operation_times)
        print(f"\n并发容器操作平均耗时: {avg_time:.2f}ms")

        # 验证性能目标 (并发场景可能稍慢)
        assert avg_time < 1000, f"并发操作应该 < 1000ms, 实际: {avg_time:.2f}ms"


def test_performance_comparison():
    """
    性能对比测试

    比较优化前后的性能差异
    """
    print("\n" + "=" * 60)
    print("性能优化对比")
    print("=" * 60)

    print("\n优化目标:")
    print("- 快速健康检查: < 100ms (优化前: 200-500ms)")
    print("- 容器重置: < 300ms (优化前: 300-500ms)")
    print("- 容器获取: < 150ms (包含快速健康检查)")

    print("\n运行性能测试以验证优化效果...")
    print("使用 pytest 运行: pytest backend/tests/test_performance.py -v -s")


if __name__ == "__main__":
    test_performance_comparison()
