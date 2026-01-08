"""
Database Configuration - SQLite + SQLAlchemy
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from .logger import get_logger

logger = get_logger(__name__)

# 数据库文件路径
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / 'helloagents.db'
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# 环境配置
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true'
LOG_SQL_QUERIES = os.environ.get('LOG_SQL_QUERIES', 'false').lower() == 'true'

# SQLAlchemy 引擎配置（SQLite 优化）
engine = create_engine(
    DATABASE_URL,
    connect_args={
        'check_same_thread': False,  # SQLite 多线程支持
        'timeout': 30,  # 锁超时时间（秒），提高并发性能
    },
    # SQLite 使用 StaticPool 提升性能（单文件数据库）
    poolclass=StaticPool,
    # 查询日志（开发环境开启）
    echo=LOG_SQL_QUERIES,
    # 连接回收时间（小时）
    pool_recycle=3600,
    # 连接前 ping 检查（确保连接有效）
    pool_pre_ping=True,
)


# 启用 SQLite 外键约束和性能优化
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    连接时执行 SQLite PRAGMA 优化

    性能优化说明：
    - WAL 模式: 提升并发读写性能
    - NORMAL 同步: 平衡性能和安全性
    - 大缓存: 减少磁盘 I/O
    - 内存临时存储: 加速临时表操作
    - mmap_size: 使用内存映射提升读性能
    """
    cursor = dbapi_conn.cursor()

    # 1. 启用外键约束（数据完整性）
    cursor.execute("PRAGMA foreign_keys = ON")

    # 2. 启用 WAL 模式（Write-Ahead Logging）
    # 优点: 读写并发，写入不阻塞读取
    cursor.execute("PRAGMA journal_mode = WAL")

    # 3. 优化同步模式（NORMAL 平衡性能和安全）
    # FULL: 最安全但最慢
    # NORMAL: 平衡选择（推荐）
    # OFF: 最快但有数据丢失风险
    cursor.execute("PRAGMA synchronous = NORMAL")

    # 4. 设置缓存大小（128MB）
    # 负数表示 KB，-128000 = 128MB
    cursor.execute("PRAGMA cache_size = -128000")

    # 5. 临时文件存储在内存中（加速临时表和排序）
    cursor.execute("PRAGMA temp_store = MEMORY")

    # 6. 内存映射 I/O（提升读性能）
    # 256MB 内存映射
    cursor.execute("PRAGMA mmap_size = 268435456")

    # 7. 优化查询规划器（启用查询分析）
    cursor.execute("PRAGMA analysis_limit = 1000")

    # 8. 自动 VACUUM 模式（渐进式清理，防止文件膨胀）
    cursor.execute("PRAGMA auto_vacuum = INCREMENTAL")

    cursor.close()

    logger.debug(
        "database_connection_established",
        database_path=str(DATABASE_PATH),
        optimizations_applied=True,
        cache_size_mb=128,
        mmap_size_mb=256
    )


# Session 工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# 模型基类
class Base(DeclarativeBase):
    pass


def get_db():
    """
    获取数据库会话（用于依赖注入）

    使用示例：
        from fastapi import Depends
        from app.database import get_db

        @app.get("/users/")
        def read_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库（创建所有表）

    注意：需要先导入所有模型，确保 Base.metadata 包含所有表
    """
    logger.info("database_initialization_started", database_path=str(DATABASE_PATH))

    try:
        # 导入所有模型（确保 Base.metadata 知道所有表）
        from . import models  # noqa: F401

        # 创建所有表
        Base.metadata.create_all(bind=engine)

        # 获取统计信息
        tables = list(Base.metadata.tables.keys())

        logger.info(
            "database_initialization_completed",
            database_path=str(DATABASE_PATH),
            tables_count=len(tables),
            tables=tables
        )
        print(f'✅ Database initialized: {DATABASE_PATH}')

    except Exception as e:
        logger.error(
            "database_initialization_failed",
            database_path=str(DATABASE_PATH),
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise


def drop_all_tables():
    """
    删除所有表（开发/测试用，生产环境慎用！）
    """
    Base.metadata.drop_all(bind=engine)
    print(f'❌ All tables dropped: {DATABASE_PATH}')


def recreate_db():
    """
    重新创建数据库（删除所有表并重建）
    """
    drop_all_tables()
    init_db()
    print(f'🔄 Database recreated: {DATABASE_PATH}')


def get_db_stats():
    """
    获取数据库统计信息
    """
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    stats = {
        'database_path': str(DATABASE_PATH),
        'database_size_mb': DATABASE_PATH.stat().st_size / (1024 * 1024) if DATABASE_PATH.exists() else 0,
        'tables': {},
    }

    with SessionLocal() as session:
        for table in tables:
            result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.scalar()
            stats['tables'][table] = {'row_count': count}

    return stats


if __name__ == '__main__':
    # 命令行测试
    print('Database Configuration:')
    print(f'  URL: {DATABASE_URL}')
    print(f'  Path: {DATABASE_PATH}')
    print(f'  Exists: {DATABASE_PATH.exists()}')

    if not DATABASE_PATH.exists():
        print('\nInitializing database...')
        init_db()
    else:
        print('\nDatabase stats:')
        import json
        print(json.dumps(get_db_stats(), indent=2))
