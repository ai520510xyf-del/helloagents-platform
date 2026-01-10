"""
Lesson Domain Entity

课程领域实体：封装课程相关的业务逻辑
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import json


@dataclass
class LessonEntity:
    """
    课程领域实体

    职责：
    - 封装课程核心业务逻辑
    - 维护课程内容的完整性
    - 提供课程相关的业务操作
    """

    id: Optional[int] = None
    chapter_number: int = 0
    lesson_number: int = 0
    title: str = ""
    content: str = ""
    starter_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """初始化后验证"""
        if not self.title:
            raise ValueError("Lesson title cannot be empty")

        if self.chapter_number <= 0:
            raise ValueError("Chapter number must be positive")

        if self.lesson_number < 0:
            raise ValueError("Lesson number cannot be negative")

        if self.created_at is None:
            self.created_at = datetime.utcnow()

        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    @property
    def lesson_id(self) -> str:
        """
        获取课程ID字符串

        Returns:
            格式化的课程ID (如 "1.2" 或 "1")
        """
        if self.lesson_number == 0:
            return str(self.chapter_number)
        return f"{self.chapter_number}.{self.lesson_number}"

    @property
    def difficulty(self) -> str:
        """获取难度等级"""
        return self.metadata.get('difficulty', 'medium')

    @property
    def estimated_time(self) -> int:
        """获取预计完成时间（分钟）"""
        return self.metadata.get('estimated_time', 30)

    @property
    def tags(self) -> list:
        """获取标签列表"""
        return self.metadata.get('tags', [])

    def update_content(self, title: Optional[str] = None, content: Optional[str] = None,
                      starter_code: Optional[str] = None):
        """
        更新课程内容

        Args:
            title: 课程标题
            content: 课程内容（Markdown）
            starter_code: 起始代码
        """
        if title is not None:
            if not title:
                raise ValueError("Title cannot be empty")
            self.title = title

        if content is not None:
            self.content = content

        if starter_code is not None:
            self.starter_code = starter_code

        self.updated_at = datetime.utcnow()

    def update_metadata(self, metadata: Dict[str, Any]):
        """
        更新元数据

        Args:
            metadata: 元数据字典
        """
        self.metadata.update(metadata)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'chapter_number': self.chapter_number,
            'lesson_number': self.lesson_number,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'content': self.content,
            'starter_code': self.starter_code,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LessonEntity':
        """从字典创建实体"""
        # 处理日期字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])

        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])

        # 处理 metadata/extra_data
        if 'extra_data' in data and isinstance(data['extra_data'], str):
            data['metadata'] = json.loads(data['extra_data'])
            del data['extra_data']
        elif 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])

        # 移除计算属性
        data.pop('lesson_id', None)

        return cls(**data)
