"""
CodeSubmission Model - 代码提交记录
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class CodeSubmission(Base):
    __tablename__ = 'code_submissions'
    __table_args__ = (
        CheckConstraint("status IN ('success', 'error', 'timeout')", name='chk_status'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False, index=True)
    code = Column(Text, nullable=False)
    output = Column(Text)  # stdout + stderr
    status = Column(String(20), nullable=False, index=True)  # success, error, timeout
    execution_time = Column(Float)  # 执行时间（秒）
    submitted_at = Column(String, default=lambda: datetime.utcnow().isoformat(), index=True)

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
