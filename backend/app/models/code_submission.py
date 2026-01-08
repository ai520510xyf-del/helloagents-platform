"""
CodeSubmission Model - 代码提交记录
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from ..database import Base


class CodeSubmission(Base):
    __tablename__ = 'code_submissions'
    __table_args__ = (
        CheckConstraint("status IN ('success', 'error', 'timeout')", name='chk_status'),
        # 复合索引：按用户和课程查询提交记录（最常见查询）
        Index('idx_user_lesson', 'user_id', 'lesson_id'),
        # 复合索引：按用户和时间查询提交历史
        Index('idx_user_submitted', 'user_id', 'submitted_at'),
        # 复合索引：按课程和时间查询提交记录
        Index('idx_lesson_submitted', 'lesson_id', 'submitted_at'),
        # 复合索引：按课程、用户和状态查询（用于统计成功率）
        Index('idx_lesson_user_status', 'lesson_id', 'user_id', 'status'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False)
    code = Column(Text, nullable=False)
    output = Column(Text)  # stdout + stderr
    status = Column(String(20), nullable=False)  # success, error, timeout
    execution_time = Column(Float)  # 执行时间（秒）
    submitted_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # 关系
    user = relationship('User', back_populates='submissions')
    lesson = relationship('Lesson', back_populates='submissions')

    def __repr__(self):
        return f'<CodeSubmission(id={self.id}, user_id={self.user_id}, lesson_id={self.lesson_id}, status={self.status})>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'code': self.code,
            'output': self.output,
            'status': self.status,
            'execution_time': self.execution_time,
            'submitted_at': self.submitted_at,
        }
