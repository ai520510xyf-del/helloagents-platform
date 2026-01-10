"""
Lesson Repository Interface

课程仓储接口：定义课程数据访问的抽象方法
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.lesson_entity import LessonEntity


class ILessonRepository(ABC):
    """
    课程仓储接口

    定义课程数据访问的所有操作
    """

    @abstractmethod
    def create(self, lesson: LessonEntity) -> LessonEntity:
        """
        创建课程

        Args:
            lesson: 课程实体

        Returns:
            创建后的课程实体（包含ID）

        Raises:
            ConflictError: 课程已存在
        """
        pass

    @abstractmethod
    def get_by_id(self, lesson_id: int) -> Optional[LessonEntity]:
        """
        根据ID获取课程

        Args:
            lesson_id: 课程ID

        Returns:
            课程实体，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def get_by_lesson_id(self, lesson_id: str) -> Optional[LessonEntity]:
        """
        根据课程ID字符串获取课程（如 "1.2"）

        Args:
            lesson_id: 课程ID字符串

        Returns:
            课程实体，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def get_by_chapter_and_lesson(self, chapter: int, lesson: int) -> Optional[LessonEntity]:
        """
        根据章节号和课时号获取课程

        Args:
            chapter: 章节号
            lesson: 课时号

        Returns:
            课程实体，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def update(self, lesson: LessonEntity) -> LessonEntity:
        """
        更新课程

        Args:
            lesson: 课程实体

        Returns:
            更新后的课程实体

        Raises:
            ResourceNotFoundError: 课程不存在
        """
        pass

    @abstractmethod
    def delete(self, lesson_id: int) -> bool:
        """
        删除课程

        Args:
            lesson_id: 课程ID

        Returns:
            删除成功返回 True，课程不存在返回 False
        """
        pass

    @abstractmethod
    def list_by_chapter(self, chapter: int) -> List[LessonEntity]:
        """
        列出指定章节的所有课程

        Args:
            chapter: 章节号

        Returns:
            课程实体列表
        """
        pass

    @abstractmethod
    def list_all(self, limit: int = 100, offset: int = 0) -> List[LessonEntity]:
        """
        列出所有课程

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            课程实体列表
        """
        pass
