"""
Database Migration Utilities - 数据库迁移工具

提供索引创建、数据迁移和版本管理功能
"""

from sqlalchemy import text, inspect
from app.database import engine, SessionLocal
from app.logger import get_logger

logger = get_logger(__name__)


# ============================================
# 索引迁移
# ============================================

def create_performance_indexes():
    """
    创建性能优化索引

    这个函数会为现有数据库添加优化索引
    如果索引已存在，会被安全跳过
    """
    with SessionLocal() as db:
        try:
            logger.info("index_migration_started")

            # CodeSubmission 表索引
            indexes_to_create = [
                # CodeSubmission
                ("CREATE INDEX IF NOT EXISTS idx_user_lesson ON code_submissions(user_id, lesson_id)", "idx_user_lesson"),
                ("CREATE INDEX IF NOT EXISTS idx_user_submitted ON code_submissions(user_id, submitted_at)", "idx_user_submitted"),
                ("CREATE INDEX IF NOT EXISTS idx_lesson_submitted ON code_submissions(lesson_id, submitted_at)", "idx_lesson_submitted"),
                ("CREATE INDEX IF NOT EXISTS idx_lesson_user_status ON code_submissions(lesson_id, user_id, status)", "idx_lesson_user_status"),

                # ChatMessage
                ("CREATE INDEX IF NOT EXISTS idx_chat_user_created ON chat_messages(user_id, created_at)", "idx_chat_user_created"),
                ("CREATE INDEX IF NOT EXISTS idx_chat_user_lesson ON chat_messages(user_id, lesson_id)", "idx_chat_user_lesson"),
                ("CREATE INDEX IF NOT EXISTS idx_chat_lesson_created ON chat_messages(lesson_id, created_at)", "idx_chat_lesson_created"),
                ("CREATE INDEX IF NOT EXISTS idx_chat_user_lesson_created ON chat_messages(user_id, lesson_id, created_at)", "idx_chat_user_lesson_created"),

                # UserProgress
                ("CREATE INDEX IF NOT EXISTS idx_progress_user_completed ON user_progress(user_id, completed)", "idx_progress_user_completed"),
                ("CREATE INDEX IF NOT EXISTS idx_progress_user_accessed ON user_progress(user_id, last_accessed)", "idx_progress_user_accessed"),
                ("CREATE INDEX IF NOT EXISTS idx_progress_lesson_completed ON user_progress(lesson_id, completed)", "idx_progress_lesson_completed"),
                ("CREATE INDEX IF NOT EXISTS idx_progress_user_completed_accessed ON user_progress(user_id, completed, last_accessed)", "idx_progress_user_completed_accessed"),
            ]

            created_count = 0
            for sql, index_name in indexes_to_create:
                try:
                    db.execute(text(sql))
                    created_count += 1
                    logger.info(
                        "index_created",
                        index_name=index_name
                    )
                except Exception as e:
                    # 索引已存在或其他错误
                    logger.debug(
                        "index_creation_skipped",
                        index_name=index_name,
                        reason=str(e)
                    )

            db.commit()

            logger.info(
                "index_migration_completed",
                indexes_created=created_count,
                total_indexes=len(indexes_to_create)
            )

            print(f'✅ 索引迁移完成: {created_count}/{len(indexes_to_create)} 个索引已创建')

        except Exception as e:
            db.rollback()
            logger.error(
                "index_migration_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise


def drop_performance_indexes():
    """
    删除性能优化索引（用于回滚）

    警告: 仅在测试环境使用
    """
    with SessionLocal() as db:
        try:
            logger.warning("index_removal_started")

            indexes_to_drop = [
                # CodeSubmission
                "DROP INDEX IF EXISTS idx_user_lesson",
                "DROP INDEX IF EXISTS idx_user_submitted",
                "DROP INDEX IF EXISTS idx_lesson_submitted",
                "DROP INDEX IF EXISTS idx_lesson_user_status",

                # ChatMessage
                "DROP INDEX IF EXISTS idx_chat_user_created",
                "DROP INDEX IF EXISTS idx_chat_user_lesson",
                "DROP INDEX IF EXISTS idx_chat_lesson_created",
                "DROP INDEX IF EXISTS idx_chat_user_lesson_created",

                # UserProgress
                "DROP INDEX IF EXISTS idx_progress_user_completed",
                "DROP INDEX IF EXISTS idx_progress_user_accessed",
                "DROP INDEX IF EXISTS idx_progress_lesson_completed",
                "DROP INDEX IF EXISTS idx_progress_user_completed_accessed",
            ]

            for sql in indexes_to_drop:
                db.execute(text(sql))

            db.commit()

            logger.warning(
                "index_removal_completed",
                indexes_dropped=len(indexes_to_drop)
            )

            print(f'⚠️  索引已删除: {len(indexes_to_drop)} 个')

        except Exception as e:
            db.rollback()
            logger.error(
                "index_removal_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise


# ============================================
# 数据库分析
# ============================================

def analyze_database():
    """
    执行 SQLite ANALYZE 命令

    更新查询优化器的统计信息，提升查询性能
    建议定期执行（如每周一次）
    """
    with SessionLocal() as db:
        try:
            logger.info("database_analysis_started")

            # 执行 ANALYZE
            db.execute(text("ANALYZE"))
            db.commit()

            logger.info("database_analysis_completed")
            print('✅ 数据库分析完成（查询优化器统计信息已更新）')

        except Exception as e:
            logger.error(
                "database_analysis_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise


def vacuum_database():
    """
    执行 SQLite VACUUM 命令

    重建数据库文件，回收空间，优化性能
    警告: 操作期间会锁定数据库
    """
    with SessionLocal() as db:
        try:
            logger.info("database_vacuum_started")

            # VACUUM 需要在事务外执行
            db.connection().connection.isolation_level = None
            db.execute(text("VACUUM"))
            db.connection().connection.isolation_level = ""

            logger.info("database_vacuum_completed")
            print('✅ 数据库 VACUUM 完成（空间已优化）')

        except Exception as e:
            logger.error(
                "database_vacuum_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise


# ============================================
# 索引状态检查
# ============================================

def check_index_status() -> dict:
    """
    检查数据库索引状态

    Returns:
        索引状态报告
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    report = {
        'tables': {},
        'total_indexes': 0,
        'missing_recommended_indexes': []
    }

    # 推荐的索引列表
    recommended_indexes = {
        'code_submissions': ['idx_user_lesson', 'idx_user_submitted', 'idx_lesson_submitted', 'idx_lesson_user_status'],
        'chat_messages': ['idx_chat_user_created', 'idx_chat_user_lesson', 'idx_chat_lesson_created', 'idx_chat_user_lesson_created'],
        'user_progress': ['idx_progress_user_completed', 'idx_progress_user_accessed', 'idx_progress_lesson_completed', 'idx_progress_user_completed_accessed'],
    }

    for table_name in tables:
        indexes = inspector.get_indexes(table_name)
        index_names = [idx['name'] for idx in indexes]

        report['tables'][table_name] = {
            'index_count': len(indexes),
            'indexes': index_names
        }
        report['total_indexes'] += len(indexes)

        # 检查推荐索引
        if table_name in recommended_indexes:
            for recommended_idx in recommended_indexes[table_name]:
                if recommended_idx not in index_names:
                    report['missing_recommended_indexes'].append({
                        'table': table_name,
                        'index': recommended_idx
                    })

    return report


def print_index_report():
    """打印索引状态报告"""
    report = check_index_status()

    print('\n' + '=' * 60)
    print('数据库索引状态报告')
    print('=' * 60)

    print(f'\n总索引数: {report["total_indexes"]}')

    print('\n各表索引情况:')
    for table_name, table_info in report['tables'].items():
        print(f'  {table_name}: {table_info["index_count"]} 个索引')
        for idx_name in table_info['indexes']:
            print(f'    - {idx_name}')

    if report['missing_recommended_indexes']:
        print(f'\n⚠️  缺少 {len(report["missing_recommended_indexes"])} 个推荐索引:')
        for missing in report['missing_recommended_indexes']:
            print(f'    {missing["table"]}.{missing["index"]}')
        print('\n提示: 运行 create_performance_indexes() 创建缺失的索引')
    else:
        print('\n✅ 所有推荐索引都已创建')

    print('=' * 60 + '\n')


# ============================================
# 性能基准测试
# ============================================

def benchmark_query_performance():
    """
    基准测试：对比索引优化前后的查询性能

    测试常见查询的执行时间
    """
    import time
    from app.models.code_submission import CodeSubmission
    from app.models.user_progress import UserProgress
    from app.models.chat_message import ChatMessage

    with SessionLocal() as db:
        benchmarks = []

        # 测试 1: 用户提交历史查询
        start = time.time()
        db.query(CodeSubmission)\
            .filter(CodeSubmission.user_id == 1)\
            .order_by(CodeSubmission.submitted_at.desc())\
            .limit(50)\
            .all()
        duration1 = time.time() - start
        benchmarks.append(('用户提交历史查询', duration1))

        # 测试 2: 课程提交统计
        start = time.time()
        db.query(CodeSubmission)\
            .filter(CodeSubmission.lesson_id == 1)\
            .filter(CodeSubmission.status == 'success')\
            .count()
        duration2 = time.time() - start
        benchmarks.append(('课程提交统计', duration2))

        # 测试 3: 用户进度查询
        start = time.time()
        db.query(UserProgress)\
            .filter(UserProgress.user_id == 1)\
            .filter(UserProgress.completed == 1)\
            .all()
        duration3 = time.time() - start
        benchmarks.append(('用户进度查询', duration3))

        # 测试 4: 聊天历史查询
        start = time.time()
        db.query(ChatMessage)\
            .filter(ChatMessage.user_id == 1)\
            .filter(ChatMessage.lesson_id == 1)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(20)\
            .all()
        duration4 = time.time() - start
        benchmarks.append(('聊天历史查询', duration4))

        print('\n' + '=' * 60)
        print('查询性能基准测试')
        print('=' * 60)

        total_time = 0
        for name, duration in benchmarks:
            print(f'{name:30s}: {duration * 1000:6.2f}ms')
            total_time += duration

        print(f'{"总耗时":30s}: {total_time * 1000:6.2f}ms')
        print('=' * 60 + '\n')

        # 性能评估
        if total_time < 0.1:
            print('✅ 优秀: 查询性能非常好 (< 100ms)')
        elif total_time < 0.5:
            print('✓ 良好: 查询性能可接受 (< 500ms)')
        else:
            print('⚠️  警告: 查询性能较慢 (> 500ms), 考虑添加更多索引')


# ============================================
# 命令行接口
# ============================================

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('数据库迁移工具')
        print('\n使用方法:')
        print('  python -m app.db_migration create_indexes   - 创建性能优化索引')
        print('  python -m app.db_migration drop_indexes     - 删除性能优化索引')
        print('  python -m app.db_migration check_indexes    - 检查索引状态')
        print('  python -m app.db_migration analyze          - 执行数据库分析（更新统计信息）')
        print('  python -m app.db_migration vacuum           - 执行 VACUUM（优化空间）')
        print('  python -m app.db_migration benchmark        - 运行性能基准测试')
        sys.exit(1)

    command = sys.argv[1]

    if command == 'create_indexes':
        create_performance_indexes()
    elif command == 'drop_indexes':
        drop_performance_indexes()
    elif command == 'check_indexes':
        print_index_report()
    elif command == 'analyze':
        analyze_database()
    elif command == 'vacuum':
        vacuum_database()
    elif command == 'benchmark':
        benchmark_query_performance()
    else:
        print(f'未知命令: {command}')
        sys.exit(1)
