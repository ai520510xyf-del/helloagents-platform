"""
API 端点性能测试

测试各个 API 端点的响应时间和吞吐量
运行命令: pytest tests/test_api_performance.py --benchmark-only
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


# ============================================
# 代码执行 API 性能测试
# ============================================

@pytest.mark.benchmark(group="api_code")
def test_code_execute_endpoint_performance(benchmark, client, mock_docker_container):
    """
    测试 /api/v1/code/execute 端点性能

    性能目标:
    - 响应时间 < 300ms (P95)
    - 吞吐量 > 10 RPS
    """

    # Mock 代码执行
    def mock_execute(code):
        return True, "Hello, World!\n", 0.05

    with patch('app.sandbox.sandbox.execute_python', side_effect=mock_execute):
        request_data = {
            "code": "print('Hello, World!')",
            "language": "python",
            "timeout": 30
        }

        def execute_api_call():
            response = client.post("/api/v1/code/execute", json=request_data)
            return response

        # 基准测试
        response = benchmark(execute_api_call)

        # 验证
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        stats = benchmark.stats.stats
        assert stats.mean < 0.3, f"API 响应时间 {stats.mean:.3f}s 超过 300ms"


@pytest.mark.benchmark(group="api_code")
def test_code_validation_endpoint_performance(benchmark, client):
    """
    测试代码验证性能（安全检查）

    性能目标:
    - 验证时间 < 50ms
    """

    with patch('app.sandbox.sandbox.execute_python') as mock_execute:
        # Mock 执行，但仍会经过验证
        mock_execute.return_value = (True, "output", 0.05)

        safe_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""

        request_data = {
            "code": safe_code,
            "language": "python"
        }

        def execute_with_validation():
            return client.post("/api/v1/code/execute", json=request_data)

        # 基准测试
        response = benchmark(execute_with_validation)

        assert response.status_code == 200


@pytest.mark.benchmark(group="api_code")
def test_code_hint_endpoint_performance(benchmark, client):
    """
    测试 AI 提示端点性能

    性能目标:
    - 响应时间 < 100ms (规则引擎)
    """

    request_data = {
        "code": "def __init__(self, llm_client, tool_executor):\n    ",
        "cursor_line": 1,
        "cursor_column": 0,
        "language": "python"
    }

    def get_hint():
        return client.post("/api/v1/code/hint", json=request_data)

    # 基准测试
    response = benchmark(get_hint)

    # 验证
    assert response.status_code == 200
    data = response.json()
    assert 'hint' in data
    assert 'key_concepts' in data

    stats = benchmark.stats.stats
    assert stats.mean < 0.1, f"提示生成时间 {stats.mean:.3f}s 超过 100ms"


# ============================================
# 课程 API 性能测试
# ============================================

@pytest.mark.benchmark(group="api_lessons")
def test_lessons_list_endpoint_performance(benchmark, client, db_session, lesson_factory):
    """
    测试课程列表端点性能

    性能目标:
    - 响应时间 < 100ms (数据库查询)
    """

    # 创建测试课程数据
    for i in range(20):
        lesson_factory(
            chapter_number=i // 5 + 1,
            lesson_number=i % 5 + 1,
            title=f"Lesson {i+1}"
        )

    def get_lessons():
        return client.get("/api/v1/lessons")

    # 基准测试
    response = benchmark(get_lessons)

    # 验证
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20

    stats = benchmark.stats.stats
    assert stats.mean < 0.1, f"课程列表响应时间 {stats.mean:.3f}s 超过 100ms"


@pytest.mark.benchmark(group="api_lessons")
def test_lesson_detail_endpoint_performance(benchmark, client, sample_lesson):
    """
    测试课程详情端点性能

    性能目标:
    - 响应时间 < 50ms (单条查询)
    """

    def get_lesson_detail():
        return client.get(f"/api/v1/lessons/{sample_lesson.id}")

    # 基准测试
    response = benchmark(get_lesson_detail)

    # 验证
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == sample_lesson.id

    stats = benchmark.stats.stats
    assert stats.mean < 0.05, f"课程详情响应时间 {stats.mean:.3f}s 超过 50ms"


# ============================================
# 用户进度 API 性能测试
# ============================================

@pytest.mark.benchmark(group="api_progress")
def test_progress_update_performance(benchmark, client, sample_user, sample_lesson, db_session):
    """
    测试进度更新性能

    性能目标:
    - 响应时间 < 100ms (数据库写入)
    """

    request_data = {
        "user_id": sample_user.id,
        "lesson_id": sample_lesson.id,
        "completed": 1,
        "current_code": "print('test')"
    }

    def update_progress():
        return client.post("/api/v1/progress", json=request_data)

    # 基准测试
    response = benchmark(update_progress)

    # 验证
    assert response.status_code == 200


@pytest.mark.benchmark(group="api_progress")
def test_progress_get_performance(benchmark, client, sample_progress):
    """
    测试进度查询性能

    性能目标:
    - 响应时间 < 50ms
    """

    def get_progress():
        return client.get(
            f"/api/v1/progress?user_id={sample_progress.user_id}&lesson_id={sample_progress.lesson_id}"
        )

    # 基准测试
    response = benchmark(get_progress)

    # 验证
    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == sample_progress.user_id


# ============================================
# 并发 API 性能测试
# ============================================

@pytest.mark.concurrent
@pytest.mark.benchmark(group="api_concurrent")
def test_concurrent_code_execution(benchmark, client):
    """
    测试并发代码执行

    性能目标:
    - 10 个并发请求 < 500ms 总时间
    - 成功率 > 95%
    """

    with patch('app.sandbox.sandbox.execute_python') as mock_execute:
        mock_execute.return_value = (True, "output", 0.05)

        def concurrent_requests():
            import threading
            results = []

            def make_request():
                response = client.post("/api/v1/code/execute", json={
                    "code": "print('test')",
                    "language": "python"
                })
                results.append(response.status_code == 200)

            # 10 个并发请求
            threads = [threading.Thread(target=make_request) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            return sum(results), len(results)

        # 基准测试
        success_count, total = benchmark(concurrent_requests)

        # 验证
        success_rate = success_count / total
        assert success_rate >= 0.95, f"并发成功率 {success_rate:.1%} 低于 95%"


# ============================================
# 数据库性能测试
# ============================================

@pytest.mark.benchmark(group="database")
def test_bulk_progress_query_performance(benchmark, db_session, progress_factory, sample_user):
    """
    测试批量进度查询性能

    性能目标:
    - 查询 100 条记录 < 100ms
    """

    from app.models.user_progress import UserProgress

    # 创建 100 条进度记录
    for i in range(100):
        progress_factory(user_id=sample_user.id, lesson_id=i+1)

    def bulk_query():
        return db_session.query(UserProgress).filter(
            UserProgress.user_id == sample_user.id
        ).all()

    # 基准测试
    results = benchmark(bulk_query)

    # 验证
    assert len(results) == 100

    stats = benchmark.stats.stats
    assert stats.mean < 0.1, f"批量查询时间 {stats.mean:.3f}s 超过 100ms"


@pytest.mark.benchmark(group="database")
def test_bulk_insert_performance(benchmark, db_session, sample_user):
    """
    测试批量插入性能

    性能目标:
    - 插入 50 条记录 < 200ms
    """

    from app.models.code_submission import CodeSubmission

    def bulk_insert():
        submissions = [
            CodeSubmission(
                user_id=sample_user.id,
                lesson_id=i+1,
                code=f"print({i})",
                output=str(i),
                status='success',
                execution_time=0.05
            )
            for i in range(50)
        ]

        db_session.bulk_save_objects(submissions)
        db_session.commit()

    # 基准测试
    benchmark(bulk_insert)

    stats = benchmark.stats.stats
    assert stats.mean < 0.2, f"批量插入时间 {stats.mean:.3f}s 超过 200ms"


# ============================================
# API 响应时间分布测试
# ============================================

@pytest.mark.distribution
def test_api_response_time_distribution(client):
    """
    测试 API 响应时间分布

    收集多次请求的响应时间，分析 P50/P95/P99
    """

    import time

    with patch('app.sandbox.sandbox.execute_python') as mock_execute:
        mock_execute.return_value = (True, "output", 0.05)

        times = []

        # 执行 100 次请求
        for _ in range(100):
            start = time.time()
            response = client.post("/api/v1/code/execute", json={
                "code": "print('test')",
                "language": "python"
            })
            elapsed = time.time() - start
            times.append(elapsed * 1000)  # 转为 ms

            assert response.status_code == 200

        # 计算百分位数
        times.sort()
        p50 = times[49]  # 50th percentile
        p95 = times[94]  # 95th percentile
        p99 = times[98]  # 99th percentile

        print(f"\n响应时间分布:")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")

        # 验证性能目标
        assert p50 < 200, f"P50 {p50:.2f}ms 超过 200ms"
        assert p95 < 300, f"P95 {p95:.2f}ms 超过 300ms"
        assert p99 < 500, f"P99 {p99:.2f}ms 超过 500ms"


# ============================================
# 错误处理性能测试
# ============================================

@pytest.mark.benchmark(group="error_handling")
def test_validation_error_handling_performance(benchmark, client):
    """
    测试验证错误处理性能

    性能目标:
    - 错误响应 < 50ms (快速失败)
    """

    invalid_request = {
        "code": "os.system('rm -rf /')",  # 危险代码
        "language": "python"
    }

    def handle_validation_error():
        return client.post("/api/v1/code/execute", json=invalid_request)

    # 基准测试
    response = benchmark(handle_validation_error)

    # 验证
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is False
    assert 'error' in data

    stats = benchmark.stats.stats
    assert stats.mean < 0.05, f"错误处理时间 {stats.mean:.3f}s 超过 50ms"


# ============================================
# 性能目标总结
# ============================================

"""
API 性能目标总结:

1. 代码执行 API
   - /api/v1/code/execute: < 300ms (P95)
   - /api/v1/code/hint: < 100ms

2. 课程 API
   - GET /api/v1/lessons: < 100ms (列表)
   - GET /api/v1/lessons/{id}: < 50ms (详情)

3. 进度 API
   - POST /api/v1/progress: < 100ms (更新)
   - GET /api/v1/progress: < 50ms (查询)

4. 并发性能
   - 10 并发请求: < 500ms 总时间
   - 成功率: > 95%

5. 数据库性能
   - 批量查询 (100条): < 100ms
   - 批量插入 (50条): < 200ms

6. 错误处理
   - 验证错误: < 50ms (快速失败)

运行方法:
  # 运行所有 API 性能测试
  pytest tests/test_api_performance.py --benchmark-only

  # 查看响应时间分布
  pytest tests/test_api_performance.py::test_api_response_time_distribution -v

  # 测试并发性能
  pytest tests/test_api_performance.py -m concurrent --benchmark-only
"""
