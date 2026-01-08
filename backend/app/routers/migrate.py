"""
数据迁移 API - 从 localStorage 迁移到 SQLite
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.user_progress import UserProgress
from ..models.code_submission import CodeSubmission
from ..models.chat_message import ChatMessage
from ..models.lesson import Lesson

router = APIRouter(prefix="/api/migrate", tags=["migrate"])


# Pydantic 模型
class ProgressData(BaseModel):
    chapter: int
    lesson: int
    completed: bool = False
    code: Optional[str] = None


class ChatMessageData(BaseModel):
    role: str
    content: str


class LessonChatData(BaseModel):
    lesson_key: str  # e.g., "1-1"
    messages: List[ChatMessageData]


class MigrationRequest(BaseModel):
    """localStorage 数据迁移请求"""
    username: Optional[str] = "local_user"
    progress_list: Optional[List[ProgressData]] = []
    last_code: Optional[Dict[str, str]] = {}  # {"1-1": "code...", ...}
    chat_history: Optional[List[LessonChatData]] = []


class MigrationResponse(BaseModel):
    """迁移响应"""
    success: bool
    message: str
    user_id: int
    migrated_progress: int
    migrated_submissions: int
    migrated_chat_messages: int


def parse_lesson_key(lesson_key: str) -> Optional[int]:
    """
    解析课程键为 lesson_id

    假设映射规则：
    - "1" → lesson_id = 1
    - "1-1" → lesson_id = 1 (chapter 1, lesson 1)
    - "2-1" → lesson_id = 2 (chapter 2, lesson 1)

    实际映射应根据 lessons 表的数据
    """
    try:
        parts = lesson_key.split('-')
        if len(parts) == 1:
            return int(parts[0])
        elif len(parts) == 2:
            chapter, lesson = int(parts[0]), int(parts[1])
            # 简化映射：chapter * 10 + lesson
            # 例如：1-1 → 11, 1-2 → 12, 2-1 → 21
            return chapter * 10 + lesson
        return None
    except:
        return None


@router.post("/", response_model=MigrationResponse)
def migrate_localstorage_data(
    data: MigrationRequest,
    db: Session = Depends(get_db)
):
    """
    从 localStorage 迁移数据到 SQLite

    接收前端 localStorage 的所有数据，批量导入到数据库
    """
    try:
        # 1. 获取或创建用户
        user = db.query(User).filter(User.username == data.username).first()
        if not user:
            user = User(
                username=data.username,
                full_name=data.username,
                settings=json.dumps({
                    "theme": "dark",
                    "editor": {"fontSize": 14, "tabSize": 4, "wordWrap": True}
                })
            )
            db.add(user)
            db.commit()
            # refresh 在测试环境中可能有问题，直接使用对象

        migrated_progress = 0
        migrated_submissions = 0
        migrated_chat = 0

        # 2. 迁移学习进度
        for prog in data.progress_list:
            # 查找或创建 lesson（如果不存在，暂时跳过）
            lesson_id = parse_lesson_key(f"{prog.chapter}-{prog.lesson}")
            if not lesson_id:
                continue

            # 检查课程是否存在
            lesson = db.query(Lesson).filter(
                Lesson.chapter_number == prog.chapter,
                Lesson.lesson_number == prog.lesson
            ).first()

            if not lesson:
                # 课程不存在，创建占位符课程
                lesson = Lesson(
                    chapter_number=prog.chapter,
                    lesson_number=prog.lesson,
                    title=f"第{prog.chapter}章 第{prog.lesson}节",
                    content="待导入",
                    starter_code="# 待导入"
                )
                db.add(lesson)
                db.commit()
                # refresh 在测试环境中可能有问题，直接使用对象

            # 创建或更新进度
            existing_progress = db.query(UserProgress).filter(
                UserProgress.user_id == user.id,
                UserProgress.lesson_id == lesson.id
            ).first()

            if not existing_progress:
                progress = UserProgress(
                    user_id=user.id,
                    lesson_id=lesson.id,
                    completed=1 if prog.completed else 0,
                    current_code=prog.code,
                    completed_at=datetime.utcnow().isoformat() if prog.completed else None
                )
                db.add(progress)
                migrated_progress += 1

        # 3. 迁移代码（作为代码提交记录）
        for lesson_key, code in (data.last_code or {}).items():
            lesson_id = parse_lesson_key(lesson_key)
            if not lesson_id:
                continue

            # 查找课程
            parts = lesson_key.split('-')
            if len(parts) == 2:
                chapter, lesson_num = int(parts[0]), int(parts[1])
                lesson = db.query(Lesson).filter(
                    Lesson.chapter_number == chapter,
                    Lesson.lesson_number == lesson_num
                ).first()

                if lesson:
                    # 创建代码提交记录
                    submission = CodeSubmission(
                        user_id=user.id,
                        lesson_id=lesson.id,
                        code=code,
                        output="[从 localStorage 迁移]",
                        status='success'
                    )
                    db.add(submission)
                    migrated_submissions += 1

        # 4. 迁移聊天历史
        for chat_data in data.chat_history:
            lesson_id = parse_lesson_key(chat_data.lesson_key)
            if not lesson_id:
                continue

            # 查找课程
            parts = chat_data.lesson_key.split('-')
            if len(parts) == 2:
                chapter, lesson_num = int(parts[0]), int(parts[1])
                lesson = db.query(Lesson).filter(
                    Lesson.chapter_number == chapter,
                    Lesson.lesson_number == lesson_num
                ).first()

                if lesson:
                    for msg in chat_data.messages:
                        chat_msg = ChatMessage(
                            user_id=user.id,
                            lesson_id=lesson.id,
                            role=msg.role,
                            content=msg.content,
                            extra_data=json.dumps({"migrated": True})
                        )
                        db.add(chat_msg)
                        migrated_chat += 1

        # 提交所有更改
        db.commit()

        return MigrationResponse(
            success=True,
            message=f"成功迁移数据：{migrated_progress} 个进度，{migrated_submissions} 个代码提交，{migrated_chat} 条聊天记录",
            user_id=user.id,
            migrated_progress=migrated_progress,
            migrated_submissions=migrated_submissions,
            migrated_chat_messages=migrated_chat
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"迁移失败: {str(e)}")


@router.get("/example")
def get_migration_example():
    """
    获取迁移数据示例（用于前端参考）
    """
    return {
        "example_request": {
            "username": "local_user",
            "progress_list": [
                {
                    "chapter": 1,
                    "lesson": 1,
                    "completed": True,
                    "code": "print('Hello ReAct')"
                },
                {
                    "chapter": 1,
                    "lesson": 2,
                    "completed": False,
                    "code": "# 学习中..."
                }
            ],
            "last_code": {
                "1-1": "print('completed')",
                "1-2": "# in progress"
            },
            "chat_history": [
                {
                    "lesson_key": "1-1",
                    "messages": [
                        {
                            "role": "user",
                            "content": "什么是 ReAct？"
                        },
                        {
                            "role": "assistant",
                            "content": "ReAct 是..."
                        }
                    ]
                }
            ]
        },
        "description": "将此格式的数据 POST 到 /api/migrate/ 进行迁移"
    }
