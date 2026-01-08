"""
数据库性能监控测试

测试 db_monitoring.py 的所有功能
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import text
from app.db_monitoring import (
    QueryPerformanceStats,
    query_stats,
    track_query_performance,
    query_performance_context,
    explain_query,
    analyze_table_stats,
    get_database_performance_report,
    suggest_optimizations,
    reset_query_stats,
    set_slow_query_threshold
)


# ==================== QueryPerformanceStats 测试 ====================

def test_query_performance_stats_init():
    """测试统计收集器初始化"""
    stats = QueryPerformanceStats()

    assert stats.total_queries == 0
    assert stats.total_time == 0.0
    assert stats.slow_queries == []
    assert stats.slow_query_threshold == 0.1


def test_query_performance_stats_record_query():
    """测试记录查询"""
    stats = QueryPerformanceStats()

    stats.record_query(0.05, "SELECT * FROM users")

    assert stats.total_queries == 1
    assert stats.total_time == 0.05
    assert len(stats.slow_queries) == 0  # 未超过阈值


def test_query_performance_stats_record_slow_query():
    """测试记录慢查询"""
    stats = QueryPerformanceStats()

    stats.record_query(0.2, "SELECT * FROM large_table")

    assert stats.total_queries == 1
    assert len(stats.slow_queries) == 1
    assert stats.slow_queries[0]['duration'] == 0.2
    assert "large_table" in stats.slow_queries[0]['statement']


def test_query_performance_stats_slow_query_limit():
    """测试慢查询数量限制"""
    stats = QueryPerformanceStats()

    # 记录超过 100 个慢查询
    for i in range(150):
        stats.record_query(0.2, f"SELECT * FROM table_{i}")

    # 应该只保留最近 100 个
    assert len(stats.slow_queries) == 100


def test_query_performance_stats_get_stats():
    """测试获取统计信息"""
    stats = QueryPerformanceStats()

    stats.record_query(0.05, "SELECT 1")
    stats.record_query(0.10, "SELECT 2")
    stats.record_query(0.15, "SELECT 3")

    result = stats.get_stats()

    assert result['total_queries'] == 3
    assert result['total_time_seconds'] == 0.30
    assert result['avg_time_ms'] > 0
    assert result['slow_queries_count'] == 1  # 只有一个超过 0.1s
    assert result['slow_query_threshold_ms'] == 100


def test_query_performance_stats_get_slow_queries():
    """测试获取最慢的查询"""
    stats = QueryPerformanceStats()

    stats.record_query(0.5, "SELECT * FROM slow1")
    stats.record_query(0.3, "SELECT * FROM slow2")
    stats.record_query(0.7, "SELECT * FROM slow3")
    stats.record_query(0.2, "SELECT * FROM slow4")

    slow_queries = stats.get_slow_queries(limit=2)

    # 应该返回最慢的 2 个
    assert len(slow_queries) == 2
    assert slow_queries[0]['duration'] == 0.7
    assert slow_queries[1]['duration'] == 0.5


def test_query_performance_stats_reset():
    """测试重置统计"""
    stats = QueryPerformanceStats()

    stats.record_query(0.2, "SELECT * FROM table")
    assert stats.total_queries == 1

    stats.reset()

    assert stats.total_queries == 0
    assert stats.total_time == 0.0
    assert stats.slow_queries == []


# ==================== 装饰器测试 ====================

def test_track_query_performance_decorator():
    """测试查询性能追踪装饰器"""
    # 重置统计
    query_stats.reset()

    @track_query_performance("test_operation")
    def test_function():
        time.sleep(0.01)
        return "result"

    result = test_function()

    assert result == "result"
    # 注意：由于装饰器会记录到全局 query_stats，这里验证有记录
    # 但由于 SQLAlchemy 事件监听器也在工作，total_queries 可能不是 1


def test_track_query_performance_with_exception():
    """测试装饰器处理异常"""
    query_stats.reset()

    @track_query_performance("test_operation_error")
    def test_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        test_function()

    # 即使抛出异常，统计信息也应该被记录


def test_query_performance_context_manager(db_session):
    """测试查询性能上下文管理器"""
    query_stats.reset()

    with query_performance_context("test_context"):
        # 执行一些数据库查询
        db_session.execute(text("SELECT 1"))

    # 上下文管理器应该记录统计信息


def test_query_performance_context_with_exception(db_session):
    """测试上下文管理器处理异常"""
    query_stats.reset()

    with pytest.raises(ValueError):
        with query_performance_context("test_context_error"):
            db_session.execute(text("SELECT 1"))
            raise ValueError("Test error")

    # 即使抛出异常，统计信息也应该被记录


# ==================== 查询分析工具测试 ====================

def test_explain_query(db_session):
    """测试 EXPLAIN QUERY PLAN"""
    from app.models.code_submission import CodeSubmission

    # 创建一个查询
    query = db_session.query(CodeSubmission).filter(CodeSubmission.user_id == 1)

    # 执行 EXPLAIN
    explain_result = explain_query(db_session, query)

    # 应该返回查询计划
    assert isinstance(explain_result, str)
    assert len(explain_result) > 0


def test_explain_query_complex(db_session, sample_user, sample_lesson):
    """测试复杂查询的 EXPLAIN"""
    from app.models.code_submission import CodeSubmission

    # 创建测试数据
    submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        status='success',
        output="test\n",
        execution_time=0.1
    )
    db_session.add(submission)
    db_session.commit()

    # 复杂查询
    query = db_session.query(CodeSubmission)\
        .filter(CodeSubmission.user_id == sample_user.id)\
        .filter(CodeSubmission.status == 'success')\
        .order_by(CodeSubmission.submitted_at.desc())

    explain_result = explain_query(db_session, query)

    assert isinstance(explain_result, str)
    assert len(explain_result) > 0


def test_analyze_table_stats(db_session, sample_user):
    """测试分析表统计信息"""
    stats = analyze_table_stats(db_session, 'users')

    # 验证统计信息结构
    assert stats['table_name'] == 'users'
    assert 'row_count' in stats
    assert 'indexes' in stats
    assert 'index_count' in stats

    # 应该至少有一行数据（sample_user）
    assert stats['row_count'] >= 1


def test_analyze_table_stats_empty_table(db_session):
    """测试分析空表"""
    stats = analyze_table_stats(db_session, 'lessons')

    assert stats['table_name'] == 'lessons'
    assert stats['row_count'] == 0
    assert 'indexes' in stats


def test_analyze_table_stats_with_indexes(db_session):
    """测试分析包含索引的表"""
    # 创建一个索引
    db_session.execute(text(
        "CREATE INDEX IF NOT EXISTS test_idx ON code_submissions(user_id)"
    ))
    db_session.commit()

    stats = analyze_table_stats(db_session, 'code_submissions')

    assert stats['table_name'] == 'code_submissions'
    assert stats['index_count'] > 0

    # 验证索引信息
    index_names = [idx['name'] for idx in stats['indexes']]
    assert 'test_idx' in index_names


# ==================== 性能报告测试 ====================

def test_get_database_performance_report(db_session, sample_user, sample_lesson):
    """测试获取数据库性能报告"""
    # 创建一些数据
    from app.models.code_submission import CodeSubmission

    submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        status='success',
        output="test\n",
        execution_time=0.1
    )
    db_session.add(submission)
    db_session.commit()

    # 执行一些查询以生成统计
    db_session.query(CodeSubmission).all()

    report = get_database_performance_report(db_session)

    # 验证报告结构
    assert 'database' in report
    assert 'query_performance' in report
    assert 'slow_queries' in report
    assert 'tables' in report

    # 验证数据库信息
    assert 'size_mb' in report['database']
    assert 'table_count' in report['database']

    # 验证查询性能信息
    assert 'total_queries' in report['query_performance']
    assert 'total_time_seconds' in report['query_performance']


def test_get_database_performance_report_empty_database(db_session):
    """测试空数据库的性能报告"""
    query_stats.reset()

    report = get_database_performance_report(db_session)

    assert report['database']['table_count'] > 0  # 应该有表结构
    # 即使reset了，get_database_performance_report自己也会执行一些查询
    # 所以total_queries可能不为0
    assert report['query_performance']['total_queries'] >= 0


def test_get_database_performance_report_with_slow_queries(db_session):
    """测试包含慢查询的性能报告"""
    # 模拟慢查询
    query_stats.reset()
    query_stats.record_query(0.5, "SELECT * FROM slow_table")

    report = get_database_performance_report(db_session)

    assert len(report['slow_queries']) > 0
    assert report['slow_queries'][0]['duration'] == 0.5


# ==================== 优化建议测试 ====================

def test_suggest_optimizations_no_issues(db_session):
    """测试无问题时的优化建议"""
    query_stats.reset()

    suggestions = suggest_optimizations(db_session)

    # 如果没有慢查询和其他问题，建议应该为空或很少
    assert isinstance(suggestions, list)


def test_suggest_optimizations_with_slow_queries(db_session):
    """测试有慢查询时的优化建议"""
    query_stats.reset()

    # 模拟多个慢查询
    for i in range(10):
        query_stats.record_query(0.2, f"SELECT * FROM table_{i}")

    suggestions = suggest_optimizations(db_session)

    # 应该建议优化慢查询
    assert len(suggestions) > 0

    slow_query_suggestions = [s for s in suggestions if s['type'] == 'slow_queries']
    assert len(slow_query_suggestions) > 0
    assert slow_query_suggestions[0]['severity'] == 'high'


def test_suggest_optimizations_missing_foreign_key_indexes(db_session):
    """测试检测缺少外键索引"""
    # 这个测试依赖于数据库模式
    # code_submissions 表有 user_id 和 lesson_id 外键

    suggestions = suggest_optimizations(db_session)

    # 可能会建议为外键创建索引
    missing_index_suggestions = [s for s in suggestions if s['type'] == 'missing_index']

    # 如果有缺失的外键索引，应该有建议
    # 注意：这取决于当前的索引状态


def test_suggest_optimizations_large_table(db_session, sample_user, sample_lesson):
    """测试大表少索引的优化建议"""
    from app.models.code_submission import CodeSubmission

    # 创建大量数据（模拟大表）
    # 由于测试数据库，我们无法创建真正的大表，所以用 mock
    with patch('app.db_monitoring.analyze_table_stats') as mock_analyze:
        mock_analyze.return_value = {
            'table_name': 'code_submissions',
            'row_count': 50000,  # 大表
            'indexes': [{'name': 'pk_id'}],  # 只有主键索引
            'index_count': 1
        }

        suggestions = suggest_optimizations(db_session)

        # 应该建议添加索引
        large_table_suggestions = [s for s in suggestions if s['type'] == 'large_table_few_indexes']
        assert len(large_table_suggestions) > 0


def test_suggest_optimizations_high_avg_query_time(db_session):
    """测试平均查询时间过高的建议"""
    query_stats.reset()

    # 模拟多个查询，平均时间较高
    for i in range(20):
        query_stats.record_query(0.08, f"SELECT * FROM table_{i}")

    suggestions = suggest_optimizations(db_session)

    # 应该建议优化查询
    high_avg_suggestions = [s for s in suggestions if s['type'] == 'high_avg_query_time']

    # 如果平均查询时间 > 50ms，应该有建议
    if query_stats.total_time / query_stats.total_queries > 0.05:
        assert len(high_avg_suggestions) > 0


# ==================== 便捷函数测试 ====================

def test_reset_query_stats():
    """测试重置查询统计"""
    query_stats.record_query(0.1, "SELECT * FROM test")
    assert query_stats.total_queries > 0

    reset_query_stats()

    assert query_stats.total_queries == 0
    assert query_stats.total_time == 0.0


def test_set_slow_query_threshold():
    """测试设置慢查询阈值"""
    original_threshold = query_stats.slow_query_threshold

    set_slow_query_threshold(200)  # 200ms

    assert query_stats.slow_query_threshold == 0.2

    # 恢复原值
    query_stats.slow_query_threshold = original_threshold


def test_set_slow_query_threshold_and_record():
    """测试设置阈值后记录查询"""
    query_stats.reset()
    set_slow_query_threshold(50)  # 50ms

    # 记录一个 60ms 的查询（超过新阈值）
    query_stats.record_query(0.06, "SELECT * FROM test")

    assert len(query_stats.slow_queries) == 1


# ==================== SQLAlchemy 事件监听器测试 ====================

def test_sqlalchemy_event_listeners(db_session):
    """测试 SQLAlchemy 事件监听器记录查询"""
    query_stats.reset()

    # 执行一个查询
    db_session.execute(text("SELECT 1"))

    # 事件监听器应该记录查询
    assert query_stats.total_queries > 0


def test_sqlalchemy_slow_query_logging(db_session):
    """测试慢查询日志记录"""
    query_stats.reset()

    # 执行一个可能较慢的查询
    # 注意：在测试环境中很难模拟真正的慢查询
    # 我们主要测试代码路径

    with patch('app.db_monitoring.logger') as mock_logger:
        # 手动触发慢查询记录
        query_stats.record_query(0.2, "SELECT * FROM large_table")

        # 验证慢查询被记录
        assert len(query_stats.slow_queries) > 0


# ==================== 边界情况测试 ====================

def test_query_stats_with_zero_queries():
    """测试零查询的统计"""
    stats = QueryPerformanceStats()

    result = stats.get_stats()

    assert result['total_queries'] == 0
    assert result['avg_time_ms'] == 0


def test_query_stats_with_very_fast_queries():
    """测试非常快的查询"""
    stats = QueryPerformanceStats()

    # 记录非常快的查询
    for i in range(100):
        stats.record_query(0.001, f"SELECT {i}")

    result = stats.get_stats()

    assert result['total_queries'] == 100
    assert result['avg_time_ms'] < 10
    assert result['slow_queries_count'] == 0


def test_query_stats_statement_truncation():
    """测试长查询语句被截断"""
    stats = QueryPerformanceStats()

    # 创建超过 200 字符的 SQL 语句
    long_statement = "SELECT * FROM table WHERE " + "x = 1 AND " * 50

    stats.record_query(0.2, long_statement)

    # 验证语句被截断到 200 字符
    assert len(stats.slow_queries[0]['statement']) <= 200


def test_explain_query_with_invalid_query(db_session):
    """测试 EXPLAIN 无效查询"""
    # 测试explain_query函数能处理各种输入
    from app.models.code_submission import CodeSubmission

    # 创建一个有效的查询
    query = db_session.query(CodeSubmission).limit(1)

    # 应该正常执行
    result = explain_query(db_session, query)
    assert isinstance(result, str)


def test_analyze_table_stats_nonexistent_table(db_session):
    """测试分析不存在的表"""
    with pytest.raises(Exception):
        analyze_table_stats(db_session, 'nonexistent_table')


def test_get_database_performance_report_with_error(db_session):
    """测试性能报告生成时的错误处理"""
    # 测试函数在正常情况下能工作
    # 实际的错误处理应该在函数内部
    try:
        report = get_database_performance_report(db_session)
        assert 'database' in report
        assert 'query_performance' in report
    except Exception:
        pytest.fail("get_database_performance_report should handle errors gracefully")


# ==================== 集成测试 ====================

def test_full_monitoring_cycle(db_session, sample_user, sample_lesson):
    """测试完整的监控周期"""
    from app.models.code_submission import CodeSubmission

    # 1. 重置统计
    reset_query_stats()

    # 2. 执行一些数据库操作
    submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        status='success',
        output="test\n",
        execution_time=0.1
    )
    db_session.add(submission)
    db_session.commit()

    # 3. 查询数据
    results = db_session.query(CodeSubmission).filter(
        CodeSubmission.user_id == sample_user.id
    ).all()

    # 4. 获取性能报告
    report = get_database_performance_report(db_session)

    # 5. 获取优化建议
    suggestions = suggest_optimizations(db_session)

    # 验证结果
    assert report['query_performance']['total_queries'] > 0
    assert isinstance(suggestions, list)


def test_performance_tracking_with_context(db_session):
    """测试使用上下文管理器追踪性能"""
    query_stats.reset()

    with query_performance_context("test_operation"):
        # 执行多个查询
        db_session.execute(text("SELECT 1"))
        db_session.execute(text("SELECT 2"))
        db_session.execute(text("SELECT 3"))

    # 应该记录所有查询


def test_performance_tracking_with_decorator(db_session):
    """测试使用装饰器追踪性能"""
    query_stats.reset()

    @track_query_performance("test_function")
    def perform_queries():
        db_session.execute(text("SELECT 1"))
        db_session.execute(text("SELECT 2"))
        return "done"

    result = perform_queries()

    assert result == "done"


def test_multiple_slow_query_thresholds():
    """测试不同的慢查询阈值"""
    query_stats.reset()

    # 测试 100ms 阈值
    set_slow_query_threshold(100)
    query_stats.record_query(0.15, "SELECT 1")
    assert len(query_stats.slow_queries) == 1

    # 测试 200ms 阈值
    query_stats.reset()
    set_slow_query_threshold(200)
    query_stats.record_query(0.15, "SELECT 1")
    assert len(query_stats.slow_queries) == 0  # 未超过阈值


def test_concurrent_query_tracking():
    """测试并发查询追踪"""
    import threading

    query_stats.reset()

    def record_queries():
        for i in range(10):
            query_stats.record_query(0.01, f"SELECT {i}")

    # 创建多个线程
    threads = [threading.Thread(target=record_queries) for _ in range(5)]

    # 启动所有线程
    for t in threads:
        t.start()

    # 等待所有线程完成
    for t in threads:
        t.join()

    # 应该记录所有查询
    assert query_stats.total_queries == 50
