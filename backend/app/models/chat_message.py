"""
ChatMessage Model - AI 对话消息
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from ..database import Base


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name='chk_role'),
        # 复合索引：按用户和时间查询聊天历史（最常见查询）
        Index('idx_user_created', 'user_id', 'created_at'),
        # 复合索引：按用户和课程查询课程相关对话
        Index('idx_user_lesson', 'user_id', 'lesson_id'),
        # 复合索引：按课程和时间查询课程讨论
        Index('idx_lesson_created', 'lesson_id', 'created_at'),
        # 复合索引：按用户、课程和时间查询（获取最近对话）
        Index('idx_user_lesson_created', 'user_id', 'lesson_id', 'created_at'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='SET NULL'))
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    extra_data = Column(Text, default='{}')  # JSON: model, tokens, context_type等 (renamed from 'metadata' - reserved word)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # 关系
    user = relationship('User', back_populates='chat_messages')
    lesson = relationship('Lesson', back_populates='chat_messages')

    def __repr__(self):
        return f'<ChatMessage(id={self.id}, user_id={self.user_id}, role={self.role})>'

    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'role': self.role,
            'content': self.content,
            'metadata': json.loads(self.extra_data) if self.extra_data else {},  # Return as 'metadata' for API compatibility
            'created_at': self.created_at,
        }
