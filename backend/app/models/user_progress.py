"""
UserProgress Model - 用户学习进度
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class UserProgress(Base):
    __tablename__ = 'user_progress'
    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='uk_user_lesson'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False, index=True)
    completed = Column(Integer, default=0, index=True)  # SQLite: 0=false, 1=true
    current_code = Column(Text)  # 当前编辑的代码（自动保存）
    cursor_position = Column(Text, default='{"line": 1, "column": 1}')  # JSON: Monaco 光标位置
    started_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    completed_at = Column(String)
    last_accessed = Column(String, default=lambda: datetime.utcnow().isoformat(), index=True)

    # 关系
    user = relationship('User', back_populates='progress')
    lesson = relationship('Lesson', back_populates='progress')

    def __repr__(self):
        return f'<UserProgress(user_id={self.user_id}, lesson_id={self.lesson_id}, completed={bool(self.completed)})>'

    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'completed': self.completed,
            'current_code': self.current_code,
            'cursor_position': json.loads(self.cursor_position) if self.cursor_position else {'line': 1, 'column': 1},
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'last_accessed': self.last_accessed,
        }
