"""
测试工厂函数演示
展示如何使用新的测试工厂函数
"""
import pytest
from tests.factories import (
    create_user_data,
    create_lesson_data,
    create_multiple,
    MockScenarios
)


def test_user_factory_basic(user_factory):
    """测试基本的用户工厂"""
    user = user_factory()
    assert user.id is not None
    assert user.username is not None
    assert user.full_name is not None


def test_user_factory_with_custom_data(user_factory):
    """测试自定义用户数据"""
    user = user_factory(
        username="custom_user",
        full_name="Custom User"
    )
    assert user.username == "custom_user"
    assert user.full_name == "Custom User"


def test_lesson_factory(lesson_factory):
    """测试课程工厂"""
    lesson = lesson_factory(
        chapter_number=1,
        lesson_number=1,
        title="Test Lesson"
    )
    assert lesson.chapter_number == 1
    assert lesson.lesson_number == 1
    assert lesson.title == "Test Lesson"


def test_progress_factory(progress_factory, user_factory, lesson_factory):
    """测试进度工厂"""
    user = user_factory()
    lesson = lesson_factory()

    progress = progress_factory(
        user_id=user.id,
        lesson_id=lesson.id,
        completed=1
    )

    assert progress.user_id == user.id
    assert progress.lesson_id == lesson.id
    assert progress.completed == 1


def test_create_multiple_users(db_session):
    """测试批量创建用户"""
    users = create_multiple(create_user_data, 5, db_session)

    assert len(users) == 5
    assert all(user.id is not None for user in users)
    assert len(set(user.username for user in users)) == 5  # 所有用户名唯一


def test_mock_scenario_new_user(db_session):
    """测试新用户场景"""
    user = MockScenarios.new_user(db_session)

    assert user.username == "new_user"
    assert user.full_name == "New User"


def test_mock_scenario_experienced_user(db_session):
    """测试有经验用户场景"""
    user = MockScenarios.experienced_user_with_progress(db_session)

    assert user.username == "experienced_user"
    # 应该有 3 个已完成的课程
    assert len(user.progress) == 3
    assert all(p.completed == 1 for p in user.progress)


def test_mock_scenario_first_lesson(db_session):
    """测试第一课场景"""
    lesson = MockScenarios.first_lesson(db_session)

    assert lesson.chapter_number == 1
    assert lesson.lesson_number == 1
    assert lesson.title == "Introduction to Programming"


def test_mock_scenario_submissions(db_session):
    """测试代码提交场景"""
    success = MockScenarios.successful_submission(db_session)
    failure = MockScenarios.failed_submission(db_session)

    assert success.status == 'success'
    assert success.output == "Hello, World!"

    assert failure.status == 'error'
    assert "Error:" in failure.output


def test_submission_factory(submission_factory, user_factory, lesson_factory):
    """测试提交工厂"""
    user = user_factory()
    lesson = lesson_factory()

    submission = submission_factory(
        user_id=user.id,
        lesson_id=lesson.id,
        status='success',
        output="Test output"
    )

    assert submission.user_id == user.id
    assert submission.lesson_id == lesson.id
    assert submission.status == 'success'
    assert submission.output == "Test output"


def test_chat_message_factory(chat_message_factory, user_factory):
    """测试聊天消息工厂"""
    user = user_factory()

    message = chat_message_factory(
        user_id=user.id,
        role='user',
        content="Test question"
    )

    assert message.user_id == user.id
    assert message.role == 'user'
    assert message.content == "Test question"
