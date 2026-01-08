"""
课程内容管理 API (v1)

提供课程列表和内容查询功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.courses import course_manager
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/lessons", tags=["lessons"])


# ============================================
# 数据模型
# ============================================

class LessonContentResponse(BaseModel):
    """课程内容响应"""
    lesson_id: str = Field(..., description="课程ID")
    title: str = Field(..., description="课程标题")
    content: str = Field(..., description="Markdown 格式的课程内容")
    code_template: str = Field(..., description="代码模板")


class LessonListResponse(BaseModel):
    """课程列表响应"""
    success: bool
    lessons: list


# ============================================
# API 端点
# ============================================

@router.get("", response_model=LessonListResponse)
@router.get("/", response_model=LessonListResponse, include_in_schema=False)
async def get_all_lessons():
    """
    获取所有课程列表

    返回完整的课程目录结构，包括所有章节和子章节

    **响应:**
    - success: 请求是否成功
    - lessons: 课程列表数组
    """
    try:
        lessons = course_manager.get_all_lessons()
        logger.info(
            "lessons_list_requested",
            total_lessons=len(lessons) if lessons else 0
        )
        return {
            "success": True,
            "lessons": lessons
        }
    except Exception as e:
        logger.error(
            "lessons_list_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lesson_id}", response_model=LessonContentResponse)
async def get_lesson_content(lesson_id: str):
    """
    获取指定课程的完整内容

    返回课程的标题、Markdown 内容和代码模板

    **路径参数:**
    - lesson_id: 课程ID，如 "1", "2", "4.1"

    **响应:**
    - lesson_id: 课程ID
    - title: 课程标题
    - content: Markdown 格式的课程内容
    - code_template: 初始代码模板
    """
    try:
        logger.info(
            "lesson_content_requested",
            lesson_id=lesson_id
        )

        # 获取课程内容
        content = course_manager.get_lesson_content(lesson_id)
        if content is None:
            logger.warning(
                "lesson_not_found",
                lesson_id=lesson_id
            )
            raise HTTPException(
                status_code=404,
                detail=f"课程 {lesson_id} 不存在"
            )

        # 获取代码模板
        code_template = course_manager.get_code_template(lesson_id)

        # 获取课程标题
        lesson_info = course_manager._course_structure.get(lesson_id, {})
        title = lesson_info.get("title", f"第{lesson_id}章")

        logger.info(
            "lesson_content_retrieved",
            lesson_id=lesson_id,
            title=title,
            content_length=len(content),
            has_code_template=bool(code_template)
        )

        return LessonContentResponse(
            lesson_id=lesson_id,
            title=title,
            content=content,
            code_template=code_template or ""
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "lesson_content_failed",
            lesson_id=lesson_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))
