"""
数据库查询工具测试

测试 db_utils.py 的所有优化查询函数
"""
import pytest
from datetime import datetime, timedelta
from app.db_utils import (
    get_user_submissions_with_lesson,
    get_lesson_submissions_with_users,
    get_user_submission_stats,
    get_user_chat_history,
    get_recent_conversations,
    get_user_progress_with_lessons,
    get_user_dashboard_data,
    get_lesson_stats,
    bulk_create_submissions,
    bulk_update_progress
)
from app.models.code_submission import CodeSubmission
from app.models.chat_message import ChatMessage
from app.models.user_progress import UserProgress
from app.models.user import User
from app.models.lesson import Lesson


# ==================== 代码提交查询测试 ====================

def test_get_user_submissions_with_lesson(db_session, sample_user, sample_lesson):
    """测试获取用户提交记录（预加载课程）"""
    # 创建测试数据
    submission1 = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test1')",
        status='success',
        output="test1\n",
        execution_time=0.1
    )
    submission2 = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test2')",
        status='error',
        output="error\n",
        execution_time=0.2
    )
    db_session.add_all([submission1, submission2])
    db_session.commit()

    # 执行查询
    submissions = get_user_submissions_with_lesson(db_session, sample_user.id, limit=50)

    # 验证结果
    assert len(submissions) == 2
    # 验证课程被预加载（不会触发额外查询）
    assert submissions[0].lesson is not None
    assert submissions[0].lesson.title == sample_lesson.title


def test_get_user_submissions_with_lesson_limit(db_session, sample_user, sample_lesson):
    """测试提交记录数量限制"""
    # 创建 10 个提交
    for i in range(10):
        submission = CodeSubmission(
            user_id=sample_user.id,
            lesson_id=sample_lesson.id,
            code=f"print('test{i}')",
            status='success',
            output=f"test{i}\n",
            execution_time=0.1
        )
        db_session.add(submission)
    db_session.commit()

    # 限制返回 5 个
    submissions = get_user_submissions_with_lesson(db_session, sample_user.id, limit=5)

    assert len(submissions) == 5


def test_get_user_submissions_with_lesson_order(db_session, sample_user, sample_lesson):
    """测试提交记录按时间倒序排列"""
    # 创建提交（有时间间隔）
    submission1 = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('first')",
        status='success',
        output="first\n",
        execution_time=0.1
    )
    db_session.add(submission1)
    db_session.commit()

    submission2 = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('second')",
        status='success',
        output="second\n",
        execution_time=0.1
    )
    db_session.add(submission2)
    db_session.commit()

    submissions = get_user_submissions_with_lesson(db_session, sample_user.id)

    # 最新的应该在前面
    assert submissions[0].code == "print('second')"
    assert submissions[1].code == "print('first')"


def test_get_user_submissions_empty(db_session, sample_user):
    """测试用户无提交记录"""
    submissions = get_user_submissions_with_lesson(db_session, sample_user.id)

    assert len(submissions) == 0


def test_get_lesson_submissions_with_users(db_session, sample_user, sample_lesson):
    """测试获取课程提交记录（预加载用户）"""
    # 创建提交
    submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        status='success',
        output="test\n",
        execution_time=0.1
    )
    db_session.add(submission)
    db_session.commit()

    submissions = get_lesson_submissions_with_users(db_session, sample_lesson.id)

    assert len(submissions) == 1
    # 验证用户被预加载
    assert submissions[0].user is not None
    assert submissions[0].user.username == sample_user.username


def test_get_lesson_submissions_with_status_filter(db_session, sample_user, sample_lesson):
    """测试按状态过滤课程提交"""
    # 创建成功和失败的提交
    success_submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('success')",
        output="success\n",
        execution_time=0.1,
        status='success'
    )
    error_submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print(x)",
        output="NameError\n",
        execution_time=0.1,
        status='error'
    )
    db_session.add_all([success_submission, error_submission])
    db_session.commit()

    # 只查询成功的
    submissions = get_lesson_submissions_with_users(db_session, sample_lesson.id, status='success')

    assert len(submissions) == 1
    assert submissions[0].status == 'success'


def test_get_user_submission_stats(db_session, sample_user, sample_lesson):
    """测试获取用户提交统计"""
    # 创建多个提交
    for i in range(5):
        submission = CodeSubmission(
            user_id=sample_user.id,
            lesson_id=sample_lesson.id,
            code=f"print('test{i}')",
            output=f"test{i}\n",
            execution_time=0.1,
            status='success' if i % 2 == 0 else 'error'
        )
        db_session.add(submission)
    db_session.commit()

    stats = get_user_submission_stats(db_session, sample_user.id)

    # 验证统计信息
    assert stats['total_submissions'] == 5
    assert stats['unique_lessons'] == 1
    assert stats['success_count'] == 3
    assert stats['error_count'] == 2
    assert 50 < stats['success_rate'] < 70  # 约 60%


def test_get_user_submission_stats_empty(db_session, sample_user):
    """测试无提交的用户统计"""
    stats = get_user_submission_stats(db_session, sample_user.id)

    assert stats['total_submissions'] == 0
    assert stats['success_count'] == 0
    assert stats['success_rate'] == 0


# ==================== 聊天消息查询测试 ====================

def test_get_user_chat_history(db_session, sample_user, sample_lesson):
    """测试获取用户聊天历史"""
    # 创建聊天消息
    message1 = ChatMessage(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        role="user",
        content="How do I print?"
    )
    message2 = ChatMessage(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        role="user",
        content="What is a variable?"
    )
    db_session.add_all([message1, message2])
    db_session.commit()

    messages = get_user_chat_history(db_session, sample_user.id)

    assert len(messages) == 2
    # 验证课程被预加载
    assert messages[0].lesson is not None


def test_get_user_chat_history_with_lesson_filter(db_session, sample_user, sample_lesson):
    """测试按课程过滤聊天历史"""
    # 创建另一个课程
    lesson2 = Lesson(
        chapter_number=2,
        lesson_number=1,
        title="Lesson 2",
        content="Content 2",
        starter_code="# code 2"
    )
    db_session.add(lesson2)
    db_session.commit()

    # 为不同课程创建消息
    message1 = ChatMessage(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        role="user",
        content="Message for lesson 1"
    )
    message2 = ChatMessage(
        user_id=sample_user.id,
        lesson_id=lesson2.id,
        role="user",
        content="Message for lesson 2"
    )
    db_session.add_all([message1, message2])
    db_session.commit()

    # 只查询 lesson 1 的消息
    messages = get_user_chat_history(db_session, sample_user.id, lesson_id=sample_lesson.id)

    assert len(messages) == 1
    assert messages[0].lesson_id == sample_lesson.id


def test_get_user_chat_history_limit(db_session, sample_user, sample_lesson):
    """测试聊天历史数量限制"""
    # 创建 20 条消息
    for i in range(20):
        message = ChatMessage(
            user_id=sample_user.id,
            lesson_id=sample_lesson.id,
            role="user",
            content=f"Message {i}"
        )
        db_session.add(message)
    db_session.commit()

    messages = get_user_chat_history(db_session, sample_user.id, limit=10)

    assert len(messages) == 10


def test_get_recent_conversations(db_session, sample_user, sample_lesson):
    """测试获取最近对话"""
    # 创建消息
    for i in range(5):
        message = ChatMessage(
            user_id=sample_user.id,
            lesson_id=sample_lesson.id,
            role="user",
            content=f"Message {i}"
        )
        db_session.add(message)
    db_session.commit()

    messages = get_recent_conversations(db_session, sample_user.id, limit=3)

    # 应该返回最近 3 条，且顺序反转（最旧的在前）
    assert len(messages) == 3


def test_get_recent_conversations_with_lesson(db_session, sample_user, sample_lesson):
    """测试获取指定课程的最近对话"""
    # 创建另一个课程
    lesson2 = Lesson(
        chapter_number=2,
        lesson_number=1,
        title="Lesson 2",
        content="Content 2",
        starter_code="# code 2"
    )
    db_session.add(lesson2)
    db_session.commit()

    # 为不同课程创建消息
    message1 = ChatMessage(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        role="user",
        content="Message 1"
    )
    message2 = ChatMessage(
        user_id=sample_user.id,
        lesson_id=lesson2.id,
        role="user",
        content="Message 2"
    )
    db_session.add_all([message1, message2])
    db_session.commit()

    messages = get_recent_conversations(db_session, sample_user.id, lesson_id=sample_lesson.id)

    assert len(messages) == 1
    assert messages[0].lesson_id == sample_lesson.id


# ==================== 学习进度查询测试 ====================

def test_get_user_progress_with_lessons(db_session, sample_user, sample_lesson):
    """测试获取用户学习进度（预加载课程）"""
    # 创建进度
    progress = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=True
    )
    db_session.add(progress)
    db_session.commit()

    progress_list = get_user_progress_with_lessons(db_session, sample_user.id)

    assert len(progress_list) == 1
    # 验证课程被预加载
    assert progress_list[0].lesson is not None
    assert progress_list[0].lesson.title == sample_lesson.title


def test_get_user_progress_order(db_session, sample_user, sample_lesson):
    """测试进度按最后访问时间排序"""
    # 创建另一个课程
    lesson2 = Lesson(
        chapter_number=2,
        lesson_number=1,
        title="Lesson 2",
        content="Content 2",
        starter_code="# code 2"
    )
    db_session.add(lesson2)
    db_session.commit()

    # 创建进度
    progress1 = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=False
    )
    db_session.add(progress1)
    db_session.commit()

    # 更新 last_accessed
    import time
    time.sleep(0.01)

    progress2 = UserProgress(
        user_id=sample_user.id,
        lesson_id=lesson2.id,
        completed=False
    )
    db_session.add(progress2)
    db_session.commit()

    progress_list = get_user_progress_with_lessons(db_session, sample_user.id)

    # 最近访问的应该在前面
    assert progress_list[0].lesson_id == lesson2.id


def test_get_user_progress_empty(db_session, sample_user):
    """测试无学习进度的用户"""
    progress_list = get_user_progress_with_lessons(db_session, sample_user.id)

    assert len(progress_list) == 0


# ==================== 仪表盘数据测试 ====================

def test_get_user_dashboard_data(db_session, sample_user, sample_lesson):
    """测试获取用户仪表盘数据"""
    # 创建学习进度
    progress = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=True
    )
    db_session.add(progress)

    # 创建代码提交
    submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        output="test\n",
        execution_time=0.1,
        status='success'
    )
    db_session.add(submission)
    db_session.commit()

    dashboard_data = get_user_dashboard_data(db_session, sample_user.id)

    # 验证数据结构
    assert 'progress' in dashboard_data
    assert 'submissions' in dashboard_data
    assert 'recent_progress' in dashboard_data
    assert 'recent_submissions' in dashboard_data

    # 验证进度统计
    assert dashboard_data['progress']['total_lessons'] == 1
    assert dashboard_data['progress']['completed_lessons'] == 1
    assert dashboard_data['progress']['completion_rate'] == 100

    # 验证提交统计
    assert dashboard_data['submissions']['total_submissions'] == 1
    assert dashboard_data['submissions']['success_count'] == 1


def test_get_user_dashboard_data_empty(db_session, sample_user):
    """测试空仪表盘数据"""
    dashboard_data = get_user_dashboard_data(db_session, sample_user.id)

    assert dashboard_data['progress']['total_lessons'] == 0
    assert dashboard_data['submissions']['total_submissions'] == 0


def test_get_user_dashboard_data_recent_items(db_session, sample_user, sample_lesson):
    """测试仪表盘最近项目限制"""
    # 创建 10 个进度（从lesson_number=2开始，因为sample_lesson已经是1）
    for i in range(10):
        lesson = Lesson(
            chapter_number=1,
            lesson_number=i + 2,  # 从2开始避免与sample_lesson冲突
            title=f"Lesson {i + 2}",
            content=f"Content {i + 2}",
            starter_code="# code"
        )
        db_session.add(lesson)
        db_session.commit()

        progress = UserProgress(
            user_id=sample_user.id,
            lesson_id=lesson.id,
            completed=False
        )
        db_session.add(progress)

    db_session.commit()

    dashboard_data = get_user_dashboard_data(db_session, sample_user.id)

    # 应该只返回最近 5 个
    assert len(dashboard_data['recent_progress']) == 5


# ==================== 课程统计测试 ====================

def test_get_lesson_stats(db_session, sample_user, sample_lesson):
    """测试获取课程统计"""
    # 创建提交
    submission1 = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        output="test\n",
        execution_time=0.1,
        status='success'
    )
    submission2 = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print(x)",
        output="error\n",
        execution_time=0.2,
        status='error'
    )
    db_session.add_all([submission1, submission2])

    # 创建进度
    progress = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=True
    )
    db_session.add(progress)
    db_session.commit()

    stats = get_lesson_stats(db_session, sample_lesson.id)

    # 验证提交统计
    assert stats['submissions']['total'] == 2
    assert stats['submissions']['unique_users'] == 1
    assert stats['submissions']['success_count'] == 1
    assert 40 < stats['submissions']['success_rate'] < 60

    # 验证进度统计
    assert stats['progress']['total_students'] == 1
    assert stats['progress']['completed_students'] == 1


def test_get_lesson_stats_empty(db_session, sample_lesson):
    """测试无数据的课程统计"""
    stats = get_lesson_stats(db_session, sample_lesson.id)

    assert stats['submissions']['total'] == 0
    assert stats['progress']['total_students'] == 0


def test_get_lesson_stats_multiple_users(db_session, sample_user, sample_lesson):
    """测试多用户的课程统计"""
    # 创建另一个用户
    user2 = User(username="user2", full_name="User 2")
    db_session.add(user2)
    db_session.commit()

    # 两个用户都提交
    submission1 = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        output="test\n",
        execution_time=0.1,
        status='success'
    )
    submission2 = CodeSubmission(
        user_id=user2.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        output="test\n",
        execution_time=0.1,
        status='success'
    )
    db_session.add_all([submission1, submission2])
    db_session.commit()

    stats = get_lesson_stats(db_session, sample_lesson.id)

    assert stats['submissions']['total'] == 2
    assert stats['submissions']['unique_users'] == 2


# ==================== 批量操作测试 ====================

def test_bulk_create_submissions(db_session, sample_user, sample_lesson):
    """测试批量创建代码提交"""
    submissions_data = [
        {
            'user_id': sample_user.id,
            'lesson_id': sample_lesson.id,
            'code': f"print('test{i}')",
            'success': True,
            'output': f"test{i}\n",
            'execution_time': 0.1,
            'status': 'success'
        }
        for i in range(10)
    ]

    count = bulk_create_submissions(db_session, submissions_data)

    assert count == 10

    # 验证数据被创建
    submissions = db_session.query(CodeSubmission).filter(
        CodeSubmission.user_id == sample_user.id
    ).all()

    assert len(submissions) == 10


def test_bulk_create_submissions_empty(db_session):
    """测试批量创建空列表"""
    count = bulk_create_submissions(db_session, [])

    assert count == 0


def test_bulk_update_progress(db_session, sample_user, sample_lesson):
    """测试批量更新学习进度"""
    # 创建进度
    progress1 = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=False
    )
    db_session.add(progress1)
    db_session.commit()

    # 批量更新
    progress_updates = [
        {
            'id': progress1.id,
            'completed': True,
            'current_code': "print('updated')"
        }
    ]

    count = bulk_update_progress(db_session, progress_updates)

    assert count == 1

    # 验证更新
    db_session.refresh(progress1)
    assert progress1.completed == True
    assert progress1.current_code == "print('updated')"


def test_bulk_update_progress_empty(db_session):
    """测试批量更新空列表"""
    count = bulk_update_progress(db_session, [])

    assert count == 0


def test_bulk_update_progress_multiple(db_session, sample_user, sample_lesson):
    """测试批量更新多个进度"""
    # 创建另一个课程
    lesson2 = Lesson(
        chapter_number=2,
        lesson_number=1,
        title="Lesson 2",
        content="Content 2",
        starter_code="# code 2"
    )
    db_session.add(lesson2)
    db_session.commit()

    # 创建多个进度
    progress1 = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=False
    )
    progress2 = UserProgress(
        user_id=sample_user.id,
        lesson_id=lesson2.id,
        completed=False
    )
    db_session.add_all([progress1, progress2])
    db_session.commit()

    # 批量更新
    progress_updates = [
        {'id': progress1.id, 'completed': True},
        {'id': progress2.id, 'completed': True}
    ]

    count = bulk_update_progress(db_session, progress_updates)

    assert count == 2

    # 验证更新
    db_session.refresh(progress1)
    db_session.refresh(progress2)
    assert progress1.completed == True
    assert progress2.completed == True


# ==================== 边界情况测试 ====================

def test_get_user_submissions_nonexistent_user(db_session):
    """测试不存在的用户"""
    submissions = get_user_submissions_with_lesson(db_session, 99999)

    assert len(submissions) == 0


def test_get_lesson_submissions_nonexistent_lesson(db_session):
    """测试不存在的课程"""
    submissions = get_lesson_submissions_with_users(db_session, 99999)

    assert len(submissions) == 0


def test_get_user_submission_stats_nonexistent_user(db_session):
    """测试不存在的用户统计"""
    stats = get_user_submission_stats(db_session, 99999)

    assert stats['total_submissions'] == 0


def test_get_user_dashboard_data_nonexistent_user(db_session):
    """测试不存在的用户仪表盘"""
    dashboard_data = get_user_dashboard_data(db_session, 99999)

    assert dashboard_data['progress']['total_lessons'] == 0


def test_get_lesson_stats_nonexistent_lesson(db_session):
    """测试不存在的课程统计"""
    stats = get_lesson_stats(db_session, 99999)

    assert stats['submissions']['total'] == 0


# ==================== 性能优化验证测试 ====================

def test_user_submissions_with_lesson_no_n_plus_1(db_session, sample_user, sample_lesson):
    """测试避免 N+1 查询问题"""
    # 创建多个提交
    for i in range(10):
        submission = CodeSubmission(
            user_id=sample_user.id,
            lesson_id=sample_lesson.id,
            code=f"print('test{i}')",
            status='success',
            output=f"test{i}\n",
            execution_time=0.1
        )
        db_session.add(submission)
    db_session.commit()

    # 获取提交（带预加载）
    submissions = get_user_submissions_with_lesson(db_session, sample_user.id)

    # 访问课程信息不应该触发额外查询
    for submission in submissions:
        _ = submission.lesson.title  # 应该已经加载


def test_dashboard_data_optimized_queries(db_session, sample_user, sample_lesson):
    """测试仪表盘数据使用优化的查询"""
    # 创建数据（从lesson_number=2开始）
    for i in range(20):
        lesson = Lesson(
            chapter_number=1,
            lesson_number=i + 2,  # 从2开始避免与sample_lesson冲突
            title=f"Lesson {i + 2}",
            content=f"Content {i + 2}",
            starter_code="# code"
        )
        db_session.add(lesson)
        db_session.commit()

        progress = UserProgress(
            user_id=sample_user.id,
            lesson_id=lesson.id,
            completed=i % 2 == 0
        )
        db_session.add(progress)

        submission = CodeSubmission(
            user_id=sample_user.id,
            lesson_id=lesson.id,
            code=f"print('test{i}')",
            output=f"test{i}\n",
            execution_time=0.1,
            status='success'
        )
        db_session.add(submission)

    db_session.commit()

    # 获取仪表盘数据（应该使用聚合查询和预加载）
    dashboard_data = get_user_dashboard_data(db_session, sample_user.id)

    # 验证统计信息正确
    assert dashboard_data['progress']['total_lessons'] == 20
    assert dashboard_data['progress']['completed_lessons'] == 10


# ==================== 集成测试 ====================

def test_full_user_data_flow(db_session, sample_user, sample_lesson):
    """测试完整的用户数据查询流程"""
    # 1. 创建学习数据
    progress = UserProgress(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        completed=False,
        current_code="print('draft')"
    )
    db_session.add(progress)

    submission = CodeSubmission(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        code="print('test')",
        output="test\n",
        execution_time=0.1,
        status='success'
    )
    db_session.add(submission)

    chat = ChatMessage(
        user_id=sample_user.id,
        lesson_id=sample_lesson.id,
        role="user",
        content="Help me"
    )
    db_session.add(chat)
    db_session.commit()

    # 2. 查询各种数据
    submissions = get_user_submissions_with_lesson(db_session, sample_user.id)
    stats = get_user_submission_stats(db_session, sample_user.id)
    chat_history = get_user_chat_history(db_session, sample_user.id)
    progress_list = get_user_progress_with_lessons(db_session, sample_user.id)
    dashboard = get_user_dashboard_data(db_session, sample_user.id)

    # 3. 验证所有查询都成功
    assert len(submissions) == 1
    assert stats['total_submissions'] == 1
    assert len(chat_history) == 1
    assert len(progress_list) == 1
    assert dashboard['progress']['total_lessons'] == 1


def test_full_lesson_data_flow(db_session, sample_user, sample_lesson):
    """测试完整的课程数据查询流程"""
    # 创建多个用户的学习数据
    user2 = User(username="user2", full_name="User 2")
    db_session.add(user2)
    db_session.commit()

    for user in [sample_user, user2]:
        submission = CodeSubmission(
            user_id=user.id,
            lesson_id=sample_lesson.id,
            code="print('test')",
            output="test\n",
            execution_time=0.1,
            status='success'
        )
        db_session.add(submission)

        progress = UserProgress(
            user_id=user.id,
            lesson_id=sample_lesson.id,
            completed=True
        )
        db_session.add(progress)

    db_session.commit()

    # 查询课程数据
    submissions = get_lesson_submissions_with_users(db_session, sample_lesson.id)
    stats = get_lesson_stats(db_session, sample_lesson.id)

    # 验证
    assert len(submissions) == 2
    assert stats['submissions']['unique_users'] == 2
    assert stats['progress']['total_students'] == 2
