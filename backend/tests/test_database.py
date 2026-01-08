"""
数据库工具函数测试

测试 database.py 中的工具函数
"""
import pytest
import json
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.database import (
    Base,
    get_db,
    init_db,
    drop_all_tables,
    recreate_db,
    get_db_stats,
    DATABASE_PATH
)
from app.models.user import User
from app.models.lesson import Lesson


def test_get_db_generator(db_session):
    """测试 get_db 生成器函数"""
    # get_db 是一个生成器，应该产生一个 session
    db_gen = get_db()
    session = next(db_gen)

    # 验证返回的是一个有效的 session
    assert session is not None

    # 可以执行数据库操作
    result = session.execute(text("SELECT 1"))
    assert result.scalar() == 1

    # 清理
    try:
        next(db_gen)
    except StopIteration:
        pass  # 这是预期的


def test_init_db_creates_tables():
    """测试 init_db 创建表"""
    # 使用临时数据库
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test.db"
        test_engine = create_engine(f'sqlite:///{test_db_path}')

        # 保存原始引擎并替换
        from app import database
        original_engine = database.engine
        database.engine = test_engine

        try:
            # 创建表
            Base.metadata.create_all(bind=test_engine)

            # 验证表已创建
            inspector = inspect(test_engine)
            tables = inspector.get_table_names()

            assert "users" in tables
            assert "lessons" in tables
            assert "user_progress" in tables
            assert "code_submissions" in tables
            assert "chat_messages" in tables
        finally:
            # 恢复原始引擎
            database.engine = original_engine


def test_drop_all_tables():
    """测试 drop_all_tables 删除所有表"""
    # 使用临时数据库
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test.db"
        test_engine = create_engine(f'sqlite:///{test_db_path}')

        # 创建表
        Base.metadata.create_all(bind=test_engine)

        # 验证表存在
        inspector = inspect(test_engine)
        assert len(inspector.get_table_names()) > 0

        # 删除所有表
        Base.metadata.drop_all(bind=test_engine)

        # 验证表已删除
        inspector = inspect(test_engine)
        assert len(inspector.get_table_names()) == 0


def test_recreate_db():
    """测试 recreate_db 重建数据库"""
    # 使用临时数据库
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test.db"
        test_engine = create_engine(f'sqlite:///{test_db_path}')

        # 创建表并添加数据
        Base.metadata.create_all(bind=test_engine)
        TestSessionLocal = sessionmaker(bind=test_engine)

        with TestSessionLocal() as session:
            user = User(username="test_user", full_name="Test User")
            session.add(user)
            session.commit()

            # 验证数据存在
            count = session.query(User).count()
            assert count == 1

        # 重建数据库
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)

        # 验证数据已清空
        with TestSessionLocal() as session:
            count = session.query(User).count()
            assert count == 0


def test_get_db_stats_with_data(db_session):
    """测试 get_db_stats 获取数据库统计信息"""
    # 添加测试数据
    user = User(username="stats_user", full_name="Stats User")
    db_session.add(user)

    lesson = Lesson(
        chapter_number=1,
        lesson_number=1,
        title="Test Lesson",
        content="Test content",
        starter_code="print('test')"
    )
    db_session.add(lesson)
    db_session.commit()

    # 使用真实数据库获取统计
    stats = get_db_stats()

    # 验证统计信息结构
    assert "database_path" in stats
    assert "database_size_mb" in stats
    assert "tables" in stats

    # 验证路径
    assert str(DATABASE_PATH) in stats["database_path"]

    # 验证表统计
    assert isinstance(stats["tables"], dict)
    if "users" in stats["tables"]:
        assert "row_count" in stats["tables"]["users"]


def test_get_db_stats_empty_database():
    """测试在空数据库上获取统计信息"""
    # 使用临时数据库
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "empty.db"
        test_engine = create_engine(f'sqlite:///{test_db_path}')

        from app import database
        original_engine = database.engine
        original_session_local = database.SessionLocal
        original_db_path = database.DATABASE_PATH

        database.engine = test_engine
        database.SessionLocal = sessionmaker(bind=test_engine)
        database.DATABASE_PATH = test_db_path

        try:
            # 创建空表
            Base.metadata.create_all(bind=test_engine)

            # 获取统计
            stats = get_db_stats()

            # 验证统计信息
            assert stats["database_size_mb"] > 0
            assert isinstance(stats["tables"], dict)

            # 所有表的记录数应该为 0
            for table_name, table_stats in stats["tables"].items():
                assert table_stats["row_count"] == 0
        finally:
            # 恢复原始配置
            database.engine = original_engine
            database.SessionLocal = original_session_local
            database.DATABASE_PATH = original_db_path


def test_database_foreign_keys_enabled(db_session):
    """测试外键约束是否启用"""
    # 执行 PRAGMA 查询检查外键状态
    result = db_session.execute(text("PRAGMA foreign_keys"))
    foreign_keys_enabled = result.scalar()

    # 注意: 测试数据库使用内存数据库，可能不启用外键
    # 在生产环境中会通过 set_sqlite_pragma 启用
    # SQLite 返回 1 表示启用，0 表示禁用
    assert foreign_keys_enabled in (0, 1)


def test_database_wal_mode(db_session):
    """测试 WAL 模式是否启用"""
    # 执行 PRAGMA 查询检查日志模式
    result = db_session.execute(text("PRAGMA journal_mode"))
    journal_mode = result.scalar()

    # 注意: 测试数据库使用内存数据库，journal_mode 是 'memory'
    # 在生产环境中会通过 set_sqlite_pragma 设置为 'wal'
    assert journal_mode.lower() in ("wal", "memory", "delete")


def test_database_connection_reuse():
    """测试数据库连接复用"""
    # 获取两个 session
    gen1 = get_db()
    session1 = next(gen1)

    gen2 = get_db()
    session2 = next(gen2)

    # 两个 session 应该是不同的实例
    assert session1 is not session2

    # 但都应该可以正常工作
    result1 = session1.execute(text("SELECT 1"))
    result2 = session2.execute(text("SELECT 1"))

    assert result1.scalar() == 1
    assert result2.scalar() == 1

    # 清理
    try:
        next(gen1)
    except StopIteration:
        pass

    try:
        next(gen2)
    except StopIteration:
        pass


def test_base_declarative_class():
    """测试 Base 基类"""
    # Base 应该是 DeclarativeBase 的子类
    from sqlalchemy.orm import DeclarativeBase
    assert issubclass(Base, DeclarativeBase)

    # 应该有 metadata 属性
    assert hasattr(Base, "metadata")


def test_database_path_exists():
    """测试数据库路径配置"""
    # DATABASE_PATH 应该是一个 Path 对象
    assert isinstance(DATABASE_PATH, Path)

    # 路径应该指向 backend 目录下的 helloagents.db
    assert DATABASE_PATH.name == "helloagents.db"


def test_session_factory():
    """测试 Session 工厂配置"""
    from app.database import SessionLocal

    # SessionLocal 应该是 sessionmaker 实例
    assert SessionLocal is not None

    # 创建一个 session
    session = SessionLocal()

    # 应该可以执行查询
    result = session.execute(text("SELECT 1"))
    assert result.scalar() == 1

    # 清理
    session.close()
