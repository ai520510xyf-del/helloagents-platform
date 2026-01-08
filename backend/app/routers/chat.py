"""
聊天消息管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
import json

from ..database import get_db
from ..models.chat_message import ChatMessage

router = APIRouter(prefix="/api/chat-history", tags=["chat"])


# Pydantic 模型
class MessageCreate(BaseModel):
    user_id: int
    lesson_id: Optional[int] = None
    role: str  # user, assistant, system
    content: str
    metadata: Optional[dict] = None


class MessageResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: Optional[int]
    role: str
    content: str
    metadata: dict
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=MessageResponse)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """保存聊天消息"""
    # 验证 role
    if message.role not in ['user', 'assistant', 'system']:
        raise HTTPException(status_code=400, detail="Invalid role")

    db_message = ChatMessage(
        user_id=message.user_id,
        lesson_id=message.lesson_id,
        role=message.role,
        content=message.content,
        extra_data=json.dumps(message.metadata or {})
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message.to_dict()


@router.get("/user/{user_id}", response_model=List[MessageResponse])
def get_user_messages(
    user_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户的所有聊天消息"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(desc(ChatMessage.created_at)).limit(limit).all()

    return [m.to_dict() for m in messages]


@router.get("/user/{user_id}/lesson/{lesson_id}", response_model=List[MessageResponse])
def get_lesson_messages(
    user_id: int,
    lesson_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取特定课程的聊天历史"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id,
        ChatMessage.lesson_id == lesson_id
    ).order_by(ChatMessage.created_at).limit(limit).all()

    return [m.to_dict() for m in messages]


@router.delete("/user/{user_id}/lesson/{lesson_id}")
def delete_lesson_messages(
    user_id: int,
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """删除特定课程的聊天历史"""
    deleted = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id,
        ChatMessage.lesson_id == lesson_id
    ).delete()

    db.commit()

    return {"success": True, "deleted_count": deleted}


@router.get("/user/{user_id}/stats")
def get_chat_stats(user_id: int, db: Session = Depends(get_db)):
    """获取聊天统计"""
    total = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).count()

    user_messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id,
        ChatMessage.role == 'user'
    ).count()

    assistant_messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id,
        ChatMessage.role == 'assistant'
    ).count()

    return {
        "total_messages": total,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "conversation_count": user_messages  # 以用户消息数作为对话轮次
    }
