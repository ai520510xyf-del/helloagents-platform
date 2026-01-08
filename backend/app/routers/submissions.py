"""
代码提交记录 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List

from ..database import get_db
from ..models.code_submission import CodeSubmission

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


# Pydantic 模型
class SubmissionCreate(BaseModel):
    user_id: int
    lesson_id: int
    code: str
    output: Optional[str] = None
    status: str  # success, error, timeout
    execution_time: Optional[float] = None


class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    code: str
    output: Optional[str]
    status: str
    execution_time: Optional[float]
    submitted_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=SubmissionResponse)
def create_submission(
    submission: SubmissionCreate,
    db: Session = Depends(get_db)
):
    """创建代码提交记录"""
    # 验证 status
    if submission.status not in ['success', 'error', 'timeout']:
        raise HTTPException(status_code=400, detail="Invalid status")

    db_submission = CodeSubmission(
        user_id=submission.user_id,
        lesson_id=submission.lesson_id,
        code=submission.code,
        output=submission.output,
        status=submission.status,
        execution_time=submission.execution_time
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    return db_submission.to_dict()


@router.get("/user/{user_id}", response_model=List[SubmissionResponse])
def get_user_submissions(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取用户的所有代码提交"""
    submissions = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == user_id
    ).order_by(desc(CodeSubmission.submitted_at)).limit(limit).all()

    return [s.to_dict() for s in submissions]


@router.get("/user/{user_id}/lesson/{lesson_id}", response_model=List[SubmissionResponse])
def get_lesson_submissions(
    user_id: int,
    lesson_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取特定课程的代码提交历史"""
    submissions = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == user_id,
        CodeSubmission.lesson_id == lesson_id
    ).order_by(desc(CodeSubmission.submitted_at)).limit(limit).all()

    return [s.to_dict() for s in submissions]


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """获取指定的代码提交"""
    submission = db.query(CodeSubmission).filter(
        CodeSubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission.to_dict()


@router.get("/user/{user_id}/stats")
def get_submission_stats(user_id: int, db: Session = Depends(get_db)):
    """获取用户的代码提交统计"""
    total = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == user_id
    ).count()

    success_count = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == user_id,
        CodeSubmission.status == 'success'
    ).count()

    error_count = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == user_id,
        CodeSubmission.status == 'error'
    ).count()

    timeout_count = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == user_id,
        CodeSubmission.status == 'timeout'
    ).count()

    # 平均执行时间
    from sqlalchemy import func
    avg_time = db.query(func.avg(CodeSubmission.execution_time)).filter(
        CodeSubmission.user_id == user_id,
        CodeSubmission.status == 'success'
    ).scalar() or 0.0

    return {
        "total_submissions": total,
        "success_count": success_count,
        "error_count": error_count,
        "timeout_count": timeout_count,
        "success_rate": round(success_count / total * 100, 1) if total > 0 else 0,
        "average_execution_time": round(avg_time, 3)
    }
