"""
User Model - 本地用户配置
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    settings = Column(Text, default='{}')  # JSON 格式的用户设置
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    last_login = Column(String)

    # 关系
    progress = relationship('UserProgress', back_populates='user', cascade='all, delete-orphan')
    submissions = relationship('CodeSubmission', back_populates='user', cascade='all, delete-orphan')
    chat_messages = relationship('ChatMessage', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User(id={self.id}, username={self.username})>'

    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'settings': json.loads(self.settings) if self.settings else {},
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login,
        }
