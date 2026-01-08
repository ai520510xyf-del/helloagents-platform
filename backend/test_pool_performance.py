#!/usr/bin/env python3
"""
容器池性能测试脚本

比较使用容器池和不使用容器池的性能差异
"""

import time
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.sandbox import CodeSandbox

def test_execution_performance(sandbox, test_name, iterations=10):
    """测试代码执行性能"""

    test_code = "print('Hello, World!')"
    times = []

    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"执行次数: {iterations}")
    print(f"{'='*60}\n")

    for i in range(iterations):
        start = time.time()
        success, output, exec_time = sandbox.execute_python(test_code)
        total_time = time.time() - start

        times.append(total_time * 1000)  # 转换为毫秒

        if success:
            print(f"执行 {i+1:2d}: {total_time * 1000:7.2f}ms (代码执行: {exec_time * 1000:6.2f}ms)")
        else:
            print(f"执行 {i+1:2d}: 失败 - {output}")

    # 计算统计信息
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        # 排除首次执行计算平均值（首次可能包含容器创建时间）
        if len(times) > 1:
            avg_time_excluding_first = sum(times[1:]) / len(times[1:])
        else:
            avg_time_excluding_first = avg_time

        print(f"\n统计信息:")
        print(f"  平均耗时: {avg_time:.2f}ms")
        print(f"  最小耗时: {min_time:.2f}ms")
        print(f"  最大耗时: {max_time:.2f}ms")
        print(f"  平均耗时(排除首次): {avg_time_excluding_first:.2f}ms")

        return {
            'avg': avg_time,
            'min': min_time,
            'max': max_time,
            'avg_excluding_first': avg_time_excluding_first,
            'times': times
        }

    return None

def main():
    """主函数"""

    print("\n" + "="*60)
    print("容器池性能对比测试")
    print("="*60)

    # 测试1: 使用容器池（默认配置）
    print("\n测试场景 1: 使用容器池")
    sandbox_with_pool = CodeSandbox(
        use_pool=True,
        pool_initial_size=3,
        pool_max_size=10
    )

    results_with_pool = test_execution_performance(
        sandbox_with_pool,
        "容器池模式",
        iterations=10
    )

    # 清理
    sandbox_with_pool.cleanup()

    # 测试2: 不使用容器池（一次性容器）
    print("\n\n测试场景 2: 不使用容器池（一次性容器）")
    sandbox_without_pool = CodeSandbox(
        use_pool=False
    )

    results_without_pool = test_execution_performance(
        sandbox_without_pool,
        "一次性容器模式",
        iterations=10
    )

    # 清理
    sandbox_without_pool.cleanup()

    # 性能对比
    print("\n" + "="*60)
    print("性能对比总结")
    print("="*60)

    if results_with_pool and results_without_pool:
        improvement = (
            (results_without_pool['avg_excluding_first'] - results_with_pool['avg_excluding_first'])
            / results_without_pool['avg_excluding_first']
            * 100
        )

        print(f"\n容器池模式:")
        print(f"  平均耗时(排除首次): {results_with_pool['avg_excluding_first']:.2f}ms")
        print(f"  最小耗时: {results_with_pool['min']:.2f}ms")

        print(f"\n一次性容器模式:")
        print(f"  平均耗时(排除首次): {results_without_pool['avg_excluding_first']:.2f}ms")
        print(f"  最小耗时: {results_without_pool['min']:.2f}ms")

        print(f"\n性能提升:")
        print(f"  提升比例: {improvement:.1f}%")
        print(f"  节省时间: {results_without_pool['avg_excluding_first'] - results_with_pool['avg_excluding_first']:.2f}ms")

        if improvement > 50:
            print(f"\n✅ 性能提升显著! 容器池使执行速度提高了 {improvement:.1f}%")
        elif improvement > 0:
            print(f"\n✅ 性能有所提升! 容器池使执行速度提高了 {improvement:.1f}%")
        else:
            print(f"\n⚠️  性能未达预期，可能需要调整配置或检查实现")

    print("\n" + "="*60)
    print("测试完成")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
