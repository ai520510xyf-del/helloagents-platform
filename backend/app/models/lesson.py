"""
Lesson Model - 课程/课时
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class Lesson(Base):
    __tablename__ = 'lessons'
    __table_args__ = (
        UniqueConstraint('chapter_number', 'lesson_number', name='uk_chapter_lesson'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_number = Column(Integer, nullable=False, index=True)
    lesson_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Markdown 格式
    starter_code = Column(Text)  # 初始代码模板
    extra_data = Column(Text, default='{}')  # JSON: 难度、标签、预计时长等 (renamed from 'metadata' - reserved word)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # 关系
    progress = relationship('UserProgress', back_populates='lesson', cascade='all, delete-orphan')
    submissions = relationship('CodeSubmission', back_populates='lesson', cascade='all, delete-orphan')
    chat_messages = relationship('ChatMessage', back_populates='lesson')

    def __repr__(self):
        return f'<Lesson(id={self.id}, chapter={self.chapter_number}, lesson={self.lesson_number}, title={self.title})>'

    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'chapter_number': self.chapter_number,
            'lesson_number': self.lesson_number,
            'title': self.title,
            'content': self.content,
            'starter_code': self.starter_code,
            'metadata': json.loads(self.extra_data) if self.extra_data else {},  # Return as 'metadata' for API compatibility
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
