#!/usr/bin/env python3
"""
数据库查询优化演示脚本

展示优化前后的查询性能对比
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.code_submission import CodeSubmission
from app.models.user_progress import UserProgress
from app.models.chat_message import ChatMessage
from app.db_utils import (
    get_user_submissions_with_lesson,
    get_user_dashboard_data,
    get_user_submission_stats,
    get_user_progress_with_lessons,
)
from app.db_monitoring import (
    query_stats,
    track_query_performance,
    query_performance_context,
    get_database_performance_report,
    suggest_optimizations,
)


def print_section(title: str):
    """打印章节标题"""
    print('\n' + '=' * 70)
    print(f'  {title}')
    print('=' * 70 + '\n')


def demo_n_plus_1_problem():
    """演示 N+1 查询问题"""
    print_section('演示 1: N+1 查询问题对比')

    db = SessionLocal()

    # ❌ 坏的方式: N+1 查询
    print('❌ 未优化的查询（N+1 问题）:')
    start = time.time()
    start_queries = query_stats.total_queries

    # 查询所有提交
    submissions = db.query(CodeSubmission)\
        .filter(CodeSubmission.user_id == 1)\
        .limit(10)\
        .all()

    # 访问关联的 lesson（触发 N 次额外查询）
    for submission in submissions:
        _ = submission.lesson.title if submission.lesson else None

    bad_duration = time.time() - start
    bad_query_count = query_stats.total_queries - start_queries

    print(f'  执行时间: {bad_duration * 1000:.2f}ms')
    print(f'  查询次数: {bad_query_count}')

    # ✅ 好的方式: 使用 joinedload 预加载
    print('\n✅ 优化后的查询（使用 joinedload）:')
    start = time.time()
    start_queries = query_stats.total_queries

    submissions = get_user_submissions_with_lesson(db, user_id=1, limit=10)

    # 访问关联的 lesson（不会触发额外查询）
    for submission in submissions:
        _ = submission.lesson.title if submission.lesson else None

    good_duration = time.time() - start
    good_query_count = query_stats.total_queries - start_queries

    print(f'  执行时间: {good_duration * 1000:.2f}ms')
    print(f'  查询次数: {good_query_count}')

    # 性能对比
    improvement = (bad_duration - good_duration) / bad_duration * 100
    print(f'\n📊 性能提升: {improvement:.1f}%')
    print(f'📊 查询次数减少: {bad_query_count - good_query_count} 次')

    db.close()


def demo_aggregate_queries():
    """演示聚合查询优化"""
    print_section('演示 2: 聚合查询优化')

    db = SessionLocal()

    # ❌ 坏的方式: 多次查询
    print('❌ 未优化的方式（多次查询）:')
    start = time.time()
    start_queries = query_stats.total_queries

    total = db.query(CodeSubmission).filter(CodeSubmission.user_id == 1).count()
    success = db.query(CodeSubmission)\
        .filter(CodeSubmission.user_id == 1)\
        .filter(CodeSubmission.status == 'success')\
        .count()
    error = db.query(CodeSubmission)\
        .filter(CodeSubmission.user_id == 1)\
        .filter(CodeSubmission.status == 'error')\
        .count()

    bad_duration = time.time() - start
    bad_query_count = query_stats.total_queries - start_queries

    print(f'  执行时间: {bad_duration * 1000:.2f}ms')
    print(f'  查询次数: {bad_query_count}')

    # ✅ 好的方式: 单次聚合查询
    print('\n✅ 优化后的方式（单次聚合查询）:')
    start = time.time()
    start_queries = query_stats.total_queries

    stats = get_user_submission_stats(db, user_id=1)

    good_duration = time.time() - start
    good_query_count = query_stats.total_queries - start_queries

    print(f'  执行时间: {good_duration * 1000:.2f}ms')
    print(f'  查询次数: {good_query_count}')

    # 性能对比
    improvement = (bad_duration - good_duration) / bad_duration * 100 if bad_duration else 0
    print(f'\n📊 性能提升: {improvement:.1f}%')
    print(f'📊 查询次数减少: {bad_query_count - good_query_count} 次')
    print(f'\n统计结果: {stats}')

    db.close()


def demo_dashboard_query():
    """演示仪表盘数据查询优化"""
    print_section('演示 3: 仪表盘数据查询优化')

    db = SessionLocal()

    print('使用优化的仪表盘查询函数:')

    with query_performance_context("dashboard_data"):
        dashboard_data = get_user_dashboard_data(db, user_id=1)

    print(f'\n仪表盘数据:')
    print(f'  学习进度: {dashboard_data["progress"]}')
    print(f'  提交统计: {dashboard_data["submissions"]}')
    print(f'  最近进度: {len(dashboard_data["recent_progress"])} 条')
    print(f'  最近提交: {len(dashboard_data["recent_submissions"])} 条')

    db.close()


def demo_query_monitoring():
    """演示查询监控功能"""
    print_section('演示 4: 查询性能监控')

    db = SessionLocal()

    # 执行一些查询
    print('执行一系列查询...\n')

    @track_query_performance("get_user_progress")
    def get_progress(db, user_id):
        return get_user_progress_with_lessons(db, user_id)

    progress = get_progress(db, user_id=1)
    submissions = get_user_submissions_with_lesson(db, user_id=1, limit=20)
    stats = get_user_submission_stats(db, user_id=1)

    # 显示统计信息
    print('\n查询统计:')
    stats_data = query_stats.get_stats()
    for key, value in stats_data.items():
        print(f'  {key}: {value}')

    # 显示慢查询
    slow_queries = query_stats.get_slow_queries(limit=5)
    if slow_queries:
        print('\n慢查询列表:')
        for i, sq in enumerate(slow_queries, 1):
            print(f'  {i}. {sq["duration"] * 1000:.2f}ms - {sq["statement"][:80]}...')

    db.close()


def demo_performance_report():
    """演示性能报告生成"""
    print_section('演示 5: 数据库性能报告')

    db = SessionLocal()

    print('生成数据库性能报告...\n')

    report = get_database_performance_report(db)

    print('数据库信息:')
    print(f'  文件大小: {report["database"]["size_mb"]:.2f} MB')
    print(f'  表数量: {report["database"]["table_count"]}')

    print('\n查询性能:')
    for key, value in report['query_performance'].items():
        print(f'  {key}: {value}')

    print('\n表统计:')
    for table in report['tables']:
        print(f'  {table["table_name"]}: {table["row_count"]} 行, {table["index_count"]} 个索引')

    db.close()


def demo_optimization_suggestions():
    """演示优化建议"""
    print_section('演示 6: 性能优化建议')

    db = SessionLocal()

    print('分析数据库并生成优化建议...\n')

    suggestions = suggest_optimizations(db)

    if suggestions:
        print(f'发现 {len(suggestions)} 个优化建议:\n')
        for i, suggestion in enumerate(suggestions, 1):
            print(f'{i}. [{suggestion["severity"].upper()}] {suggestion["type"]}')
            print(f'   问题: {suggestion["message"]}')
            print(f'   建议: {suggestion["recommendation"]}\n')
    else:
        print('✅ 未发现明显的性能问题')

    db.close()


def demo_index_usage():
    """演示索引使用情况"""
    print_section('演示 7: 索引使用效果对比')

    from app.db_migration import check_index_status, benchmark_query_performance

    print('当前索引状态:\n')
    status = check_index_status()
    print(f'总索引数: {status["total_indexes"]}')

    if status['missing_recommended_indexes']:
        print(f'\n⚠️  缺少 {len(status["missing_recommended_indexes"])} 个推荐索引')
    else:
        print('\n✅ 所有推荐索引都已创建')

    print('\n运行性能基准测试...')
    benchmark_query_performance()


def main():
    """主函数"""
    print('''
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           数据库查询优化演示 - HelloAgents Platform              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    ''')

    demos = [
        ('N+1 查询问题对比', demo_n_plus_1_problem),
        ('聚合查询优化', demo_aggregate_queries),
        ('仪表盘数据查询优化', demo_dashboard_query),
        ('查询性能监控', demo_query_monitoring),
        ('数据库性能报告', demo_performance_report),
        ('性能优化建议', demo_optimization_suggestions),
        ('索引使用效果', demo_index_usage),
    ]

    # 运行所有演示
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f'\n❌ 演示 "{name}" 执行失败: {e}')
            import traceback
            traceback.print_exc()

    print_section('演示完成')
    print('总结:')
    print('✅ 通过添加索引和优化查询，性能得到显著提升')
    print('✅ 使用 joinedload 避免 N+1 查询问题')
    print('✅ 使用聚合查询减少数据库往返')
    print('✅ 监控工具帮助识别性能瓶颈')
    print('\n建议:')
    print('1. 定期运行 ANALYZE 更新查询优化器统计信息')
    print('2. 监控慢查询日志，及时优化')
    print('3. 根据实际查询模式调整索引策略')
    print('4. 对于大数据量场景，考虑迁移到 PostgreSQL')


if __name__ == '__main__':
    main()
