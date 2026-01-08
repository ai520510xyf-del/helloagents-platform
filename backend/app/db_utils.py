"""
Database Query Utilities - 数据库查询优化工具

提供优化的查询方法，解决 N+1 查询问题，提升性能
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, desc

from app.models.user import User
from app.models.lesson import Lesson
from app.models.code_submission import CodeSubmission
from app.models.chat_message import ChatMessage
from app.models.user_progress import UserProgress
from app.logger import get_logger

logger = get_logger(__name__)


# ============================================
# 代码提交查询优化
# ============================================

def get_user_submissions_with_lesson(
    db: Session,
    user_id: int,
    limit: int = 50
) -> List[CodeSubmission]:
    """
    获取用户的代码提交记录（预加载课程信息）

    优化: 使用 joinedload 避免 N+1 查询

    Args:
        db: 数据库会话
        user_id: 用户ID
        limit: 返回数量限制

    Returns:
        代码提交记录列表
    """
    submissions = db.query(CodeSubmission)\
        .options(joinedload(CodeSubmission.lesson))\
        .filter(CodeSubmission.user_id == user_id)\
        .order_by(desc(CodeSubmission.submitted_at))\
        .limit(limit)\
        .all()

    logger.debug(
        "user_submissions_queried",
        user_id=user_id,
        count=len(submissions),
        with_eager_loading=True
    )

    return submissions


def get_lesson_submissions_with_users(
    db: Session,
    lesson_id: int,
    status: Optional[str] = None,
    limit: int = 100
) -> List[CodeSubmission]:
    """
    获取课程的代码提交记录（预加载用户信息）

    优化: 使用 joinedload 避免 N+1 查询

    Args:
        db: 数据库会话
        lesson_id: 课程ID
        status: 可选的状态过滤 (success, error, timeout)
        limit: 返回数量限制

    Returns:
        代码提交记录列表
    """
    query = db.query(CodeSubmission)\
        .options(joinedload(CodeSubmission.user))\
        .filter(CodeSubmission.lesson_id == lesson_id)

    if status:
        query = query.filter(CodeSubmission.status == status)

    submissions = query\
        .order_by(desc(CodeSubmission.submitted_at))\
        .limit(limit)\
        .all()

    logger.debug(
        "lesson_submissions_queried",
        lesson_id=lesson_id,
        status=status,
        count=len(submissions),
        with_eager_loading=True
    )

    return submissions


def get_user_submission_stats(db: Session, user_id: int) -> dict:
    """
    获取用户的提交统计信息（优化查询）

    优化: 使用聚合查询，一次性获取所有统计数据

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        统计信息字典
    """
    # 单次聚合查询获取所有统计数据
    from sqlalchemy import case

    stats = db.query(
        func.count(CodeSubmission.id).label('total_submissions'),
        func.count(func.distinct(CodeSubmission.lesson_id)).label('unique_lessons'),
        func.sum(case((CodeSubmission.status == 'success', 1), else_=0)).label('success_count'),
        func.sum(case((CodeSubmission.status == 'error', 1), else_=0)).label('error_count'),
        func.avg(CodeSubmission.execution_time).label('avg_execution_time'),
    ).filter(CodeSubmission.user_id == user_id).first()

    return {
        'total_submissions': stats.total_submissions or 0,
        'unique_lessons': stats.unique_lessons or 0,
        'success_count': stats.success_count or 0,
        'error_count': stats.error_count or 0,
        'success_rate': (stats.success_count / stats.total_submissions * 100) if stats.total_submissions else 0,
        'avg_execution_time': round(stats.avg_execution_time or 0, 3),
    }


# ============================================
# 聊天消息查询优化
# ============================================

def get_user_chat_history(
    db: Session,
    user_id: int,
    lesson_id: Optional[int] = None,
    limit: int = 50
) -> List[ChatMessage]:
    """
    获取用户的聊天历史（预加载课程信息）

    优化: 使用 joinedload 避免 N+1 查询

    Args:
        db: 数据库会话
        user_id: 用户ID
        lesson_id: 可选的课程ID过滤
        limit: 返回数量限制

    Returns:
        聊天消息列表
    """
    query = db.query(ChatMessage)\
        .options(joinedload(ChatMessage.lesson))\
        .filter(ChatMessage.user_id == user_id)

    if lesson_id is not None:
        query = query.filter(ChatMessage.lesson_id == lesson_id)

    messages = query\
        .order_by(desc(ChatMessage.created_at))\
        .limit(limit)\
        .all()

    logger.debug(
        "user_chat_history_queried",
        user_id=user_id,
        lesson_id=lesson_id,
        count=len(messages),
        with_eager_loading=True
    )

    return messages


def get_recent_conversations(
    db: Session,
    user_id: int,
    lesson_id: Optional[int] = None,
    limit: int = 20
) -> List[ChatMessage]:
    """
    获取最近的对话（优化查询）

    优化: 使用索引 idx_user_lesson_created 快速查询

    Args:
        db: 数据库会话
        user_id: 用户ID
        lesson_id: 可选的课程ID
        limit: 返回数量限制

    Returns:
        最近的聊天消息列表
    """
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)

    if lesson_id is not None:
        query = query.filter(ChatMessage.lesson_id == lesson_id)

    messages = query\
        .order_by(desc(ChatMessage.created_at))\
        .limit(limit)\
        .all()

    # 反转顺序（最旧的在前）
    messages.reverse()

    return messages


# ============================================
# 学习进度查询优化
# ============================================

def get_user_progress_with_lessons(
    db: Session,
    user_id: int
) -> List[UserProgress]:
    """
    获取用户的学习进度（预加载课程信息）

    优化: 使用 joinedload 避免 N+1 查询

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        学习进度列表
    """
    progress_list = db.query(UserProgress)\
        .options(joinedload(UserProgress.lesson))\
        .filter(UserProgress.user_id == user_id)\
        .order_by(UserProgress.last_accessed.desc())\
        .all()

    logger.debug(
        "user_progress_queried",
        user_id=user_id,
        count=len(progress_list),
        with_eager_loading=True
    )

    return progress_list


def get_user_dashboard_data(db: Session, user_id: int) -> dict:
    """
    获取用户仪表盘数据（优化查询）

    优化: 使用聚合查询和预加载，减少数据库往返

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        仪表盘数据字典
    """
    # 1. 学习进度统计（单次聚合查询）
    progress_stats = db.query(
        func.count(UserProgress.id).label('total_lessons'),
        func.sum(UserProgress.completed).label('completed_lessons'),
    ).filter(UserProgress.user_id == user_id).first()

    # 2. 代码提交统计（复用已优化的函数）
    submission_stats = get_user_submission_stats(db, user_id)

    # 3. 最近学习的课程（预加载课程信息）
    recent_progress = db.query(UserProgress)\
        .options(joinedload(UserProgress.lesson))\
        .filter(UserProgress.user_id == user_id)\
        .order_by(desc(UserProgress.last_accessed))\
        .limit(5)\
        .all()

    # 4. 最近的提交（预加载课程信息）
    recent_submissions = db.query(CodeSubmission)\
        .options(joinedload(CodeSubmission.lesson))\
        .filter(CodeSubmission.user_id == user_id)\
        .order_by(desc(CodeSubmission.submitted_at))\
        .limit(5)\
        .all()

    return {
        'progress': {
            'total_lessons': progress_stats.total_lessons or 0,
            'completed_lessons': progress_stats.completed_lessons or 0,
            'completion_rate': (progress_stats.completed_lessons / progress_stats.total_lessons * 100)
                if progress_stats.total_lessons else 0,
        },
        'submissions': submission_stats,
        'recent_progress': [p.to_dict() for p in recent_progress],
        'recent_submissions': [s.to_dict() for s in recent_submissions],
    }


def get_lesson_stats(db: Session, lesson_id: int) -> dict:
    """
    获取课程统计信息（优化查询）

    优化: 使用聚合查询，避免多次查询

    Args:
        db: 数据库会话
        lesson_id: 课程ID

    Returns:
        课程统计信息字典
    """
    # 提交统计
    from sqlalchemy import case

    submission_stats = db.query(
        func.count(CodeSubmission.id).label('total_submissions'),
        func.count(func.distinct(CodeSubmission.user_id)).label('unique_users'),
        func.sum(case((CodeSubmission.status == 'success', 1), else_=0)).label('success_count'),
        func.avg(CodeSubmission.execution_time).label('avg_execution_time'),
    ).filter(CodeSubmission.lesson_id == lesson_id).first()

    # 学习进度统计
    progress_stats = db.query(
        func.count(UserProgress.id).label('total_students'),
        func.sum(UserProgress.completed).label('completed_students'),
    ).filter(UserProgress.lesson_id == lesson_id).first()

    return {
        'submissions': {
            'total': submission_stats.total_submissions or 0,
            'unique_users': submission_stats.unique_users or 0,
            'success_count': submission_stats.success_count or 0,
            'success_rate': (submission_stats.success_count / submission_stats.total_submissions * 100)
                if submission_stats.total_submissions else 0,
            'avg_execution_time': round(submission_stats.avg_execution_time or 0, 3),
        },
        'progress': {
            'total_students': progress_stats.total_students or 0,
            'completed_students': progress_stats.completed_students or 0,
            'completion_rate': (progress_stats.completed_students / progress_stats.total_students * 100)
                if progress_stats.total_students else 0,
        }
    }


# ============================================
# 批量操作优化
# ============================================

def bulk_create_submissions(
    db: Session,
    submissions_data: List[dict]
) -> int:
    """
    批量创建代码提交记录（优化性能）

    优化: 使用 bulk_insert_mappings 批量插入

    Args:
        db: 数据库会话
        submissions_data: 提交数据列表

    Returns:
        创建的记录数
    """
    if not submissions_data:
        return 0

    db.bulk_insert_mappings(CodeSubmission, submissions_data)
    db.commit()

    logger.info(
        "bulk_submissions_created",
        count=len(submissions_data)
    )

    return len(submissions_data)


def bulk_update_progress(
    db: Session,
    progress_updates: List[dict]
) -> int:
    """
    批量更新学习进度（优化性能）

    优化: 使用 bulk_update_mappings 批量更新

    Args:
        db: 数据库会话
        progress_updates: 更新数据列表，每项必须包含 'id'

    Returns:
        更新的记录数
    """
    if not progress_updates:
        return 0

    db.bulk_update_mappings(UserProgress, progress_updates)
    db.commit()

    logger.info(
        "bulk_progress_updated",
        count=len(progress_updates)
    )

    return len(progress_updates)
