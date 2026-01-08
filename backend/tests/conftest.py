"""
pytest 配置文件

定义测试 fixtures 和共享配置
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.database import Base, get_db
# 导入所有模型以确保它们注册到 Base.metadata
from app.models.user import User
from app.models.lesson import Lesson
from app.models.user_progress import UserProgress
from app.models.code_submission import CodeSubmission
from app.models.chat_message import ChatMessage


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///:memory:"  # 使用内存数据库

# 使用 StaticPool 确保所有连接共享同一个内存数据库实例
# 这对于 SQLite :memory: 数据库至关重要，因为不同的连接会创建不同的数据库
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=pool.StaticPool  # 关键：确保所有连接使用同一个内存数据库
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    创建测试数据库会话
    每个测试函数独立的数据库会话
    """
    # 创建所有表
    Base.metadata.create_all(bind=test_engine)

    # 创建会话
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # 清理：删除所有表
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    创建测试客户端
    使用测试数据库会话
    """
    def override_get_db():
        """
        依赖注入覆盖：返回测试数据库会话
        注意：不能在这里关闭 db_session，因为它由 db_session fixture 管理
        """
        yield db_session

    # 覆盖依赖注入
    app.dependency_overrides[get_db] = override_get_db

    try:
        # 创建测试客户端
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # 清理依赖覆盖
        app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """创建测试用户"""
    from app.models.user import User
    import json

    user = User(
        username="test_user",
        full_name="Test User",
        settings=json.dumps({
            "theme": "dark",
            "editor": {"fontSize": 14, "tabSize": 4}
        })
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def sample_lesson(db_session):
    """创建测试课程"""
    from app.models.lesson import Lesson

    lesson = Lesson(
        chapter_number=1,
        lesson_number=1,
        title="测试课程",
        content="# 测试课程内容\n\n这是一个测试课程。",
        starter_code="# 测试代码",
        extra_data='{"difficulty": "easy"}'
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)

    return lesson


@pytest.fixture
def sample_progress(db_session, sample_user, sample_lesson):
    """创建测试学习进度"""
    from app.models.user_progress import UserProgress

    progress = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=0,
        current_code="print('test')"
    )
    db_session.add(progress)
    db_session.commit()
    db_session.refresh(progress)

    return progress


@pytest.fixture
def sample_submission(db_session, sample_user, sample_lesson):
    """创建测试代码提交"""
    from app.models.code_submission import CodeSubmission

    submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('Hello, World!')",
        success=True,
        output="Hello, World!\n",
        execution_time=0.123
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)

    return submission


@pytest.fixture
def sample_chat_message(db_session, sample_user):
    """创建测试聊天消息"""
    from app.models.chat_message import ChatMessage

    chat_message = ChatMessage(
        user_id=sample_user.id,
        message="How do I print in Python?",
        response="You can use the print() function."
    )
    db_session.add(chat_message)
    db_session.commit()
    db_session.refresh(chat_message)

    return chat_message


# 导入测试工厂函数（使用时导入）
@pytest.fixture
def user_factory(db_session):
    """用户工厂fixture"""
    from tests.factories import create_user_data

    def _create_user(**kwargs):
        return create_user_data(db_session, **kwargs)

    return _create_user


@pytest.fixture
def lesson_factory(db_session):
    """课程工厂fixture"""
    from tests.factories import create_lesson_data

    def _create_lesson(**kwargs):
        return create_lesson_data(db_session, **kwargs)

    return _create_lesson


@pytest.fixture
def progress_factory(db_session):
    """进度工厂fixture"""
    from tests.factories import create_progress_data

    def _create_progress(**kwargs):
        return create_progress_data(db_session, **kwargs)

    return _create_progress


@pytest.fixture
def submission_factory(db_session):
    """提交工厂fixture"""
    from tests.factories import create_submission_data

    def _create_submission(**kwargs):
        return create_submission_data(db_session, **kwargs)

    return _create_submission


@pytest.fixture
def chat_message_factory(db_session):
    """聊天消息工厂fixture"""
    from tests.factories import create_chat_message_data

    def _create_chat_message(**kwargs):
        return create_chat_message_data(db_session, **kwargs)

    return _create_chat_message
