"""
Database Configuration - PostgreSQL/SQLite + SQLAlchemy
支持 PostgreSQL (生产环境) 和 SQLite (本地开发)
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool, QueuePool
from .logger import get_logger

logger = get_logger(__name__)

# 环境配置
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true'
LOG_SQL_QUERIES = os.environ.get('LOG_SQL_QUERIES', 'false').lower() == 'true'

# 数据库 URL（支持环境变量配置）
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # 本地开发：使用 SQLite
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE_PATH = BASE_DIR / 'helloagents.db'
    DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
    IS_POSTGRES = False
else:
    # 生产环境：使用 PostgreSQL
    IS_POSTGRES = DATABASE_URL.startswith('postgresql')
    DATABASE_PATH = None

# SQLAlchemy 引擎配置
if IS_POSTGRES:
    # PostgreSQL 配置
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=LOG_SQL_QUERIES,
    )
else:
    # SQLite 配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            'check_same_thread': False,
            'timeout': 30,
        },
        poolclass=StaticPool,
        echo=LOG_SQL_QUERIES,
        pool_recycle=3600,
        pool_pre_ping=True,
    )


# 启用 SQLite 外键约束和性能优化（仅 SQLite）
if not IS_POSTGRES:
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
        cursor.execute("PRAGMA journal_mode = WAL")

        # 3. 优化同步模式（NORMAL 平衡性能和安全）
        cursor.execute("PRAGMA synchronous = NORMAL")

        # 4. 设置缓存大小（128MB）
        cursor.execute("PRAGMA cache_size = -128000")

        # 5. 临时文件存储在内存中
        cursor.execute("PRAGMA temp_store = MEMORY")

        # 6. 内存映射 I/O（提升读性能）
        cursor.execute("PRAGMA mmap_size = 268435456")

        # 7. 优化查询规划器
        cursor.execute("PRAGMA analysis_limit = 1000")

        # 8. 自动 VACUUM 模式
        cursor.execute("PRAGMA auto_vacuum = INCREMENTAL")

        cursor.close()

        logger.debug(
            "sqlite_connection_established",
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
    db_info = f"PostgreSQL ({DATABASE_URL.split('@')[1].split('/')[0]})" if IS_POSTGRES else str(DATABASE_PATH)
    logger.info("database_initialization_started", database_info=db_info)

    try:
        # 导入所有模型（确保 Base.metadata 知道所有表）
        from . import models  # noqa: F401

        # 创建所有表
        Base.metadata.create_all(bind=engine)

        # 获取统计信息
        tables = list(Base.metadata.tables.keys())

        logger.info(
            "database_initialization_completed",
            database_type="PostgreSQL" if IS_POSTGRES else "SQLite",
            tables_count=len(tables),
            tables=tables
        )
        print(f'✅ Database initialized: {db_info}')

    except Exception as e:
        logger.error(
            "database_initialization_failed",
            database_info=db_info,
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
    获取数据库统计信息（支持 PostgreSQL 和 SQLite）
    """
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    stats = {
        'database_type': 'PostgreSQL' if IS_POSTGRES else 'SQLite',
        'tables': {},
    }

    # SQLite 特定：添加数据库文件信息
    if not IS_POSTGRES and DATABASE_PATH:
        stats['database_path'] = str(DATABASE_PATH)
        stats['database_size_mb'] = DATABASE_PATH.stat().st_size / (1024 * 1024) if DATABASE_PATH.exists() else 0

    # PostgreSQL 特定：添加连接信息（隐藏敏感信息）
    if IS_POSTGRES:
        stats['database_url'] = DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'N/A'

    with SessionLocal() as session:
        for table in tables:
            result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.scalar()
            stats['tables'][table] = {'row_count': count}

    return stats


if __name__ == '__main__':
    # 命令行测试
    print('Database Configuration:')
    print(f'  Type: {"PostgreSQL" if IS_POSTGRES else "SQLite"}')
    print(f'  URL: {DATABASE_URL}')

    if not IS_POSTGRES:
        print(f'  Path: {DATABASE_PATH}')
        print(f'  Exists: {DATABASE_PATH.exists()}')

        if not DATABASE_PATH.exists():
            print('\nInitializing database...')
            init_db()
        else:
            print('\nDatabase stats:')
            import json
            print(json.dumps(get_db_stats(), indent=2))
    else:
        print('\nDatabase stats:')
        import json
        print(json.dumps(get_db_stats(), indent=2))
