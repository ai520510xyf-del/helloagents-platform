"""
课程内容管理 API (v1)

提供课程列表和内容查询功能
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.courses import course_manager
from app.logger import get_logger
from app.api.response_models import success_response, error_response

logger = get_logger(__name__)

router = APIRouter(prefix="/lessons", tags=["lessons"])
limiter = Limiter(key_func=get_remote_address)


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

@router.get("")
@router.get("/", include_in_schema=False)
@limiter.limit("100/minute")
async def get_all_lessons(request: Request):
    """
    获取所有课程列表

    返回完整的课程目录结构，包括所有章节和子章节

    **速率限制:** 100次/分钟

    **响应格式:**
    ```json
    {
        "success": true,
        "data": {
            "lessons": [...],
            "total": 10
        },
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
    """
    try:
        lessons = course_manager.get_all_lessons()
        logger.info(
            "lessons_list_requested",
            total_lessons=len(lessons) if lessons else 0
        )
        return success_response(
            data={
                "lessons": lessons,
                "total": len(lessons) if lessons else 0
            },
            message="课程列表获取成功"
        )
    except Exception as e:
        logger.error(
            "lessons_list_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        return error_response(
            code="LESSONS_LIST_ERROR",
            message="课程列表获取失败",
            details={"error": str(e), "error_type": type(e).__name__}
        )


@router.get("/{lesson_id}")
@limiter.limit("100/minute")
async def get_lesson_content(request: Request, lesson_id: str):
    """
    获取指定课程的完整内容

    返回课程的标题、Markdown 内容和代码模板

    **速率限制:** 100次/分钟

    **路径参数:**
    - lesson_id: 课程ID，如 "1", "2", "4.1"

    **响应格式:**
    ```json
    {
        "success": true,
        "data": {
            "lesson_id": "1",
            "title": "课程标题",
            "content": "Markdown内容...",
            "code_template": "代码模板..."
        },
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
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
            return error_response(
                code="LESSON_NOT_FOUND",
                message=f"课程 {lesson_id} 不存在",
                status_code=404
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

        return success_response(
            data={
                "lesson_id": lesson_id,
                "title": title,
                "content": content,
                "code_template": code_template or ""
            },
            message="课程内容获取成功"
        )

    except Exception as e:
        logger.error(
            "lesson_content_failed",
            lesson_id=lesson_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        return error_response(
            code="LESSON_CONTENT_ERROR",
            message="课程内容获取失败",
            details={"error": str(e), "error_type": type(e).__name__}
        )
