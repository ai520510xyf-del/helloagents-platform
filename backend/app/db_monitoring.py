"""
Database Performance Monitoring - 数据库性能监控

提供查询性能分析、慢查询日志和性能指标收集
"""

import time
import functools
from contextlib import contextmanager
from typing import Callable, Any
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.logger import get_logger

logger = get_logger(__name__)


# ============================================
# 查询性能统计
# ============================================

class QueryPerformanceStats:
    """查询性能统计收集器"""

    def __init__(self):
        self.total_queries = 0
        self.total_time = 0.0
        self.slow_queries = []
        self.slow_query_threshold = 0.1  # 100ms

    def record_query(self, duration: float, statement: str):
        """记录查询"""
        self.total_queries += 1
        self.total_time += duration

        if duration > self.slow_query_threshold:
            self.slow_queries.append({
                'duration': duration,
                'statement': statement[:200],  # 限制长度
                'timestamp': time.time()
            })

            # 只保留最近 100 条慢查询
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'total_queries': self.total_queries,
            'total_time_seconds': round(self.total_time, 3),
            'avg_time_ms': round((self.total_time / self.total_queries * 1000), 2) if self.total_queries else 0,
            'slow_queries_count': len(self.slow_queries),
            'slow_query_threshold_ms': self.slow_query_threshold * 1000,
        }

    def get_slow_queries(self, limit: int = 10) -> list:
        """获取最慢的查询"""
        return sorted(
            self.slow_queries,
            key=lambda x: x['duration'],
            reverse=True
        )[:limit]

    def reset(self):
        """重置统计"""
        self.total_queries = 0
        self.total_time = 0.0
        self.slow_queries = []


# 全局统计实例
query_stats = QueryPerformanceStats()


# ============================================
# SQLAlchemy 事件监听（查询日志）
# ============================================

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """查询执行前记录时间"""
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """查询执行后计算耗时"""
    total_time = time.time() - conn.info['query_start_time'].pop()

    # 记录到统计
    query_stats.record_query(total_time, statement)

    # 慢查询日志
    if total_time > query_stats.slow_query_threshold:
        logger.warning(
            "slow_query_detected",
            duration_ms=round(total_time * 1000, 2),
            statement=statement[:200],
            parameters=str(parameters)[:100] if parameters else None
        )


# ============================================
# 装饰器：查询性能追踪
# ============================================

def track_query_performance(operation_name: str):
    """
    装饰器：追踪函数的数据库查询性能

    使用示例：
        @track_query_performance("get_user_submissions")
        def get_user_submissions(db, user_id):
            return db.query(CodeSubmission).filter(...).all()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            start_queries = query_stats.total_queries

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                query_count = query_stats.total_queries - start_queries

                logger.info(
                    "query_operation_completed",
                    operation=operation_name,
                    duration_ms=round(duration * 1000, 2),
                    query_count=query_count,
                    avg_query_ms=round(duration / query_count * 1000, 2) if query_count else 0
                )

        return wrapper
    return decorator


@contextmanager
def query_performance_context(operation_name: str):
    """
    上下文管理器：追踪代码块的查询性能

    使用示例：
        with query_performance_context("dashboard_queries"):
            progress = db.query(UserProgress).filter(...).all()
            submissions = db.query(CodeSubmission).filter(...).all()
    """
    start_time = time.time()
    start_queries = query_stats.total_queries

    try:
        yield
    finally:
        duration = time.time() - start_time
        query_count = query_stats.total_queries - start_queries

        logger.info(
            "query_context_completed",
            context=operation_name,
            duration_ms=round(duration * 1000, 2),
            query_count=query_count,
            avg_query_ms=round(duration / query_count * 1000, 2) if query_count else 0
        )


# ============================================
# 查询分析工具
# ============================================

def explain_query(db, query):
    """
    执行 EXPLAIN QUERY PLAN 分析查询

    Args:
        db: 数据库会话
        query: SQLAlchemy 查询对象

    Returns:
        查询计划文本
    """
    from sqlalchemy import text

    # 获取编译后的 SQL
    compiled = query.statement.compile(compile_kwargs={"literal_binds": True})
    sql = str(compiled)

    # 执行 EXPLAIN
    explain_sql = f"EXPLAIN QUERY PLAN {sql}"
    result = db.execute(text(explain_sql))

    # 格式化输出
    plan = []
    for row in result:
        plan.append(f"  {row}")

    return "\n".join(plan)


def analyze_table_stats(db, table_name: str) -> dict:
    """
    分析表的统计信息

    Args:
        db: 数据库会话
        table_name: 表名

    Returns:
        表统计信息
    """
    from sqlalchemy import text

    # 行数统计
    count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
    row_count = count_result.scalar()

    # 索引信息
    index_result = db.execute(text(f"PRAGMA index_list({table_name})"))
    indexes = []
    for row in index_result:
        index_name = row[1]
        # 获取索引详情
        index_info = db.execute(text(f"PRAGMA index_info({index_name})"))
        columns = [col[2] for col in index_info]
        indexes.append({
            'name': index_name,
            'columns': columns,
            'unique': bool(row[2])
        })

    return {
        'table_name': table_name,
        'row_count': row_count,
        'indexes': indexes,
        'index_count': len(indexes)
    }


def get_database_performance_report(db) -> dict:
    """
    获取数据库性能报告

    Args:
        db: 数据库会话

    Returns:
        性能报告字典
    """
    from sqlalchemy import text, inspect

    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()

    # 查询统计
    query_report = query_stats.get_stats()
    slow_queries = query_stats.get_slow_queries(limit=10)

    # 表统计
    table_stats = []
    for table_name in tables:
        try:
            stats = analyze_table_stats(db, table_name)
            table_stats.append(stats)
        except Exception as e:
            logger.error(f"Failed to analyze table {table_name}: {e}")

    # 数据库文件大小
    from app.database import DATABASE_PATH
    db_size_mb = DATABASE_PATH.stat().st_size / (1024 * 1024) if DATABASE_PATH.exists() else 0

    return {
        'database': {
            'size_mb': round(db_size_mb, 2),
            'table_count': len(tables),
        },
        'query_performance': query_report,
        'slow_queries': slow_queries,
        'tables': table_stats,
    }


# ============================================
# 性能建议分析
# ============================================

def suggest_optimizations(db) -> list:
    """
    分析并提供性能优化建议

    Args:
        db: 数据库会话

    Returns:
        优化建议列表
    """
    suggestions = []

    # 1. 检查慢查询
    slow_queries = query_stats.get_slow_queries(limit=5)
    if slow_queries:
        suggestions.append({
            'type': 'slow_queries',
            'severity': 'high',
            'message': f'检测到 {len(query_stats.slow_queries)} 个慢查询 (>{query_stats.slow_query_threshold * 1000}ms)',
            'recommendation': '使用 EXPLAIN QUERY PLAN 分析慢查询，考虑添加索引或优化查询逻辑',
            'examples': slow_queries[:3]
        })

    # 2. 检查缺少索引的外键
    from sqlalchemy import inspect
    inspector = inspect(db.get_bind())

    for table_name in inspector.get_table_names():
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        index_columns = set()
        for idx in indexes:
            index_columns.update(idx['column_names'])

        for fk in foreign_keys:
            fk_columns = fk['constrained_columns']
            if not any(col in index_columns for col in fk_columns):
                suggestions.append({
                    'type': 'missing_index',
                    'severity': 'medium',
                    'message': f'表 {table_name} 的外键 {fk_columns} 缺少索引',
                    'recommendation': f'考虑在 {table_name}.{fk_columns[0]} 上创建索引以提升 JOIN 性能'
                })

    # 3. 检查表大小
    for table_name in inspector.get_table_names():
        stats = analyze_table_stats(db, table_name)
        if stats['row_count'] > 10000 and stats['index_count'] < 2:
            suggestions.append({
                'type': 'large_table_few_indexes',
                'severity': 'medium',
                'message': f'表 {table_name} 有 {stats["row_count"]} 行但只有 {stats["index_count"]} 个索引',
                'recommendation': '考虑根据常用查询条件添加复合索引'
            })

    # 4. 查询效率建议
    avg_time = query_stats.total_time / query_stats.total_queries if query_stats.total_queries else 0
    if avg_time > 0.05:  # 平均超过 50ms
        suggestions.append({
            'type': 'high_avg_query_time',
            'severity': 'medium',
            'message': f'平均查询时间较高: {round(avg_time * 1000, 2)}ms',
            'recommendation': '考虑使用 joinedload/selectinload 优化关联查询，或添加查询缓存'
        })

    return suggestions


# ============================================
# 便捷函数
# ============================================

def reset_query_stats():
    """重置查询统计"""
    query_stats.reset()
    logger.info("query_stats_reset")


def set_slow_query_threshold(threshold_ms: float):
    """
    设置慢查询阈值

    Args:
        threshold_ms: 阈值（毫秒）
    """
    query_stats.slow_query_threshold = threshold_ms / 1000
    logger.info(
        "slow_query_threshold_updated",
        threshold_ms=threshold_ms
    )
