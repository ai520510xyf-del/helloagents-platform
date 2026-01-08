"""
测试数据库模型
"""
import pytest
import json
from datetime import datetime


def test_user_model_creation(db_session):
    """测试用户模型创建"""
    from app.models.user import User

    user = User(
        username="test_user",
        full_name="Test User",
        settings=json.dumps({"theme": "dark"})
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "test_user"
    assert user.created_at is not None


def test_user_to_dict(sample_user):
    """测试用户模型 to_dict 方法"""
    data = sample_user.to_dict()

    assert data["id"] == sample_user.id
    assert data["username"] == sample_user.username
    assert isinstance(data["settings"], dict)


def test_lesson_model_creation(db_session):
    """测试课程模型创建"""
    from app.models.lesson import Lesson

    lesson = Lesson(
        chapter_number=1,
        lesson_number=1,
        title="Test Lesson",
        content="# Test Content",
        starter_code="print('hello')",
        extra_data=json.dumps({"difficulty": "easy"})
    )
    db_session.add(lesson)
    db_session.commit()

    assert lesson.id is not None
    assert lesson.chapter_number == 1


def test_lesson_to_dict(sample_lesson):
    """测试课程模型 to_dict 方法"""
    data = sample_lesson.to_dict()

    assert data["id"] == sample_lesson.id
    assert data["title"] == sample_lesson.title
    # extra_data 应该被映射回 metadata
    assert "metadata" in data
    assert isinstance(data["metadata"], dict)


def test_progress_model_creation(db_session, sample_user, sample_lesson):
    """测试学习进度模型创建"""
    from app.models.user_progress import UserProgress

    progress = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=0,
        current_code="print('test')"
    )
    db_session.add(progress)
    db_session.commit()

    assert progress.id is not None
    assert progress.user_id == sample_user.id
    assert progress.lesson_id == sample_lesson.id


def test_progress_to_dict(sample_progress):
    """测试学习进度模型 to_dict 方法"""
    data = sample_progress.to_dict()

    assert data["user_id"] == sample_progress.user_id
    assert data["lesson_id"] == sample_progress.lesson_id
    assert isinstance(data["cursor_position"], dict)


def test_code_submission_model(db_session, sample_user, sample_lesson):
    """测试代码提交模型"""
    from app.models.code_submission import CodeSubmission

    submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        output="test",
        status="success",
        execution_time=0.5
    )
    db_session.add(submission)
    db_session.commit()

    assert submission.id is not None
    assert submission.status == "success"


def test_chat_message_model(db_session, sample_user, sample_lesson):
    """测试聊天消息模型"""
    from app.models.chat_message import ChatMessage

    message = ChatMessage(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        role="user",
        content="Test message",
        extra_data=json.dumps({})
    )
    db_session.add(message)
    db_session.commit()

    assert message.id is not None
    assert message.role == "user"


def test_user_relationships(sample_progress):
    """测试用户关系（级联）"""
    user = sample_progress.user
    assert user is not None
    assert len(user.progress) > 0


def test_lesson_unique_constraint(db_session, sample_lesson):
    """测试课程唯一约束"""
    from app.models.lesson import Lesson
    from sqlalchemy.exc import IntegrityError

    # 尝试创建相同的 chapter_number 和 lesson_number
    duplicate_lesson = Lesson(
        chapter_number=sample_lesson.chapter_number,
        lesson_number=sample_lesson.lesson_number,
        title="Duplicate",
        content="Duplicate content",
        starter_code=""
    )
    db_session.add(duplicate_lesson)

    with pytest.raises(IntegrityError):
        db_session.commit()
