"""
Database Configuration - SQLite + SQLAlchemy
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 数据库文件路径
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / 'helloagents.db'
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# SQLAlchemy 引擎配置
engine = create_engine(
    DATABASE_URL,
    connect_args={
        'check_same_thread': False,  # SQLite 多线程支持
        'timeout': 10,  # 锁超时时间（秒）
    },
    echo=False,  # 生产环境设为 False，开发时可设为 True 查看 SQL
)


# 启用 SQLite 外键约束和优化
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    连接时执行 SQLite PRAGMA 优化
    """
    cursor = dbapi_conn.cursor()
    # 启用外键约束
    cursor.execute("PRAGMA foreign_keys = ON")
    # 启用 WAL 模式（Write-Ahead Logging）
    cursor.execute("PRAGMA journal_mode = WAL")
    # 优化同步模式
    cursor.execute("PRAGMA synchronous = NORMAL")
    # 设置缓存大小（64MB）
    cursor.execute("PRAGMA cache_size = -64000")
    # 临时文件存储在内存中
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.close()


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
    # 导入所有模型（确保 Base.metadata 知道所有表）
    from . import models  # noqa: F401

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print(f'✅ Database initialized: {DATABASE_PATH}')


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
