"""
学习进度管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
import json
from datetime import datetime

from ..database import get_db
from ..models.user_progress import UserProgress
from ..models.lesson import Lesson

router = APIRouter(prefix="/api/progress", tags=["progress"])


# Pydantic 模型
class ProgressCreate(BaseModel):
    user_id: int
    lesson_id: int
    current_code: Optional[str] = None
    cursor_position: Optional[dict] = None


class ProgressUpdate(BaseModel):
    completed: Optional[int] = None
    current_code: Optional[str] = None
    cursor_position: Optional[dict] = None


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    completed: int
    current_code: Optional[str]
    cursor_position: dict
    started_at: str
    completed_at: Optional[str]
    last_accessed: str

    class Config:
        from_attributes = True


@router.post("/", response_model=ProgressResponse)
def create_or_update_progress(
    progress: ProgressCreate,
    db: Session = Depends(get_db)
):
    """
    创建或更新学习进度

    如果进度记录已存在，更新 last_accessed 和 current_code
    """
    # 查找现有进度
    existing = db.query(UserProgress).filter(
        UserProgress.user_id == progress.user_id,
        UserProgress.lesson_id == progress.lesson_id
    ).first()

    if existing:
        # 更新现有进度
        existing.last_accessed = datetime.utcnow().isoformat()
        if progress.current_code is not None:
            existing.current_code = progress.current_code
        if progress.cursor_position:
            existing.cursor_position = json.dumps(progress.cursor_position)

        db.commit()
        # refresh 在测试环境中可能有问题，直接返回对象
        return existing.to_dict()

    # 创建新进度
    db_progress = UserProgress(
        user_id=progress.user_id,
        lesson_id=progress.lesson_id,
        current_code=progress.current_code,
        cursor_position=json.dumps(progress.cursor_position or {"line": 1, "column": 1})
    )
    db.add(db_progress)
    db.commit()
    # refresh 在测试环境中可能有问题，直接返回对象

    return db_progress.to_dict()


@router.get("/user/{user_id}", response_model=List[ProgressResponse])
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    """获取用户的所有学习进度"""
    progress_list = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).order_by(desc(UserProgress.last_accessed)).all()

    return [p.to_dict() for p in progress_list]


@router.get("/user/{user_id}/recent", response_model=List[ProgressResponse])
def get_recent_progress(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """获取用户最近学习的课程"""
    progress_list = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).order_by(desc(UserProgress.last_accessed)).limit(limit).all()

    return [p.to_dict() for p in progress_list]


@router.get("/user/{user_id}/lesson/{lesson_id}", response_model=ProgressResponse)
def get_lesson_progress(
    user_id: int,
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """获取特定课程的学习进度"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.lesson_id == lesson_id
    ).first()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")

    return progress.to_dict()


@router.put("/user/{user_id}/lesson/{lesson_id}", response_model=ProgressResponse)
def update_progress(
    user_id: int,
    lesson_id: int,
    progress_update: ProgressUpdate,
    db: Session = Depends(get_db)
):
    """更新学习进度"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.lesson_id == lesson_id
    ).first()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")

    # 更新字段
    if progress_update.completed is not None:
        progress.completed = progress_update.completed
        if progress_update.completed:
            progress.completed_at = datetime.utcnow().isoformat()

    if progress_update.current_code is not None:
        progress.current_code = progress_update.current_code

    if progress_update.cursor_position is not None:
        progress.cursor_position = json.dumps(progress_update.cursor_position)

    progress.last_accessed = datetime.utcnow().isoformat()

    db.commit()
    # refresh 在测试环境中可能有问题，直接返回对象

    return progress.to_dict()


@router.post("/user/{user_id}/lesson/{lesson_id}/complete")
def mark_lesson_completed(
    user_id: int,
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """标记课程为已完成"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.lesson_id == lesson_id
    ).first()

    if not progress:
        # 创建新进度记录
        progress = UserProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            completed=1,
            completed_at=datetime.utcnow().isoformat()
        )
        db.add(progress)
    else:
        progress.completed = 1
        progress.completed_at = datetime.utcnow().isoformat()

    db.commit()
    # refresh 在测试环境中可能有问题，直接返回对象

    return progress.to_dict()


@router.get("/user/{user_id}/stats")
def get_progress_stats(user_id: int, db: Session = Depends(get_db)):
    """获取学习进度统计"""
    total_progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).count()

    completed_count = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.completed == 1
    ).count()

    # 获取总课程数
    total_lessons = db.query(Lesson).count()

    return {
        "total_lessons": total_lessons,
        "started_lessons": total_progress,
        "completed_lessons": completed_count,
        "completion_rate": round(completed_count / total_lessons * 100, 1) if total_lessons > 0 else 0
    }
