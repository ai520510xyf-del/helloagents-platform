"""
ChatMessage Model - AI 对话消息
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name='chk_role'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='SET NULL'), index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    extra_data = Column(Text, default='{}')  # JSON: model, tokens, context_type等 (renamed from 'metadata' - reserved word)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat(), index=True)

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
