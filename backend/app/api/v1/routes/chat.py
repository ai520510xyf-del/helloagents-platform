"""
AI 聊天助手 API (v1)

提供与 AI 学习助手的对话功能
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

from openai import OpenAI

from app.database import get_db
from app.logger import get_logger
from app.api.response_models import success_response, error_response

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)

# DeepSeek 客户端延迟初始化
_deepseek_client = None


def get_deepseek_client():
    """
    获取 DeepSeek 客户端实例（延迟初始化）

    只在真正需要时才创建客户端，避免在导入时要求 API_KEY

    Raises:
        ValueError: 当 DEEPSEEK_API_KEY 环境变量未设置时

    Returns:
        OpenAI: DeepSeek 客户端实例
    """
    global _deepseek_client
    if _deepseek_client is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY environment variable is not set. "
                "Please set it to use AI chat features."
            )
        _deepseek_client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
    return _deepseek_client


# ============================================
# 数据模型
# ============================================

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="消息角色：user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """AI 聊天请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    conversation_history: List[ChatMessage] = Field(
        default=[],
        description="对话历史"
    )
    lesson_id: Optional[str] = Field(None, description="当前课程ID（用于提供上下文）")
    code: Optional[str] = Field(None, description="当前代码（用于提供上下文）")


class ChatResponse(BaseModel):
    """AI 聊天响应"""
    message: str = Field(..., description="AI 回复")
    success: bool = Field(default=True, description="请求是否成功")


# ============================================
# API 端点
# ============================================

@router.post("")
@router.post("/", include_in_schema=False)
@limiter.limit("20/minute")
async def chat_with_ai(
    request_obj: Request,
    chat_request: ChatRequest,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    与 AI 学习助手聊天

    提供课程学习过程中的问答支持，可选保存聊天消息到数据库

    **速率限制:** 20次/分钟

    **请求参数:**
    - message: 用户消息（必填）
    - conversation_history: 对话历史（可选，最多保留最近10轮）
    - lesson_id: 当前课程ID（可选，用于提供上下文）
    - code: 当前代码（可选，用于提供上下文）

    **响应格式:**
    ```json
    {
        "success": true,
        "data": {
            "message": "AI助手回复",
            "model": "deepseek-chat",
            "tokens": 150
        },
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
    """
    try:
        # 构建系统提示
        system_prompt = """你是 HelloAgents 学习平台的 AI 学习助手。你的任务是帮助学习者理解 AI Agent 相关的概念和技术。

你应该：
- 用简洁、清晰的语言解释复杂概念
- 提供具体的代码示例和实践建议
- 鼓励学习者动手实践
- 如果学习者遇到困难，提供逐步指导

请注意：
- 保持友好、耐心的态度
- 不要直接给出完整答案，而是引导学习者思考
- 当学习者提供代码时，帮助他们理解和改进"""

        # 添加当前课程上下文
        if chat_request.lesson_id:
            system_prompt += f"\n\n当前学习章节：第{chat_request.lesson_id}章"

        # 添加当前代码上下文
        if chat_request.code and len(chat_request.code.strip()) > 0:
            system_prompt += f"\n\n学习者当前的代码：\n```python\n{chat_request.code[:1000]}\n```"

        # 构建消息历史 (OpenAI 格式)
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 添加对话历史（只保留最近10轮对话）
        for msg in chat_request.conversation_history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": chat_request.message
        })

        # 记录 AI 调用开始
        logger.info(
            "ai_chat_started",
            user_id=user_id,
            lesson_id=chat_request.lesson_id,
            message_length=len(chat_request.message),
            has_code_context=bool(chat_request.code),
            conversation_history_length=len(chat_request.conversation_history)
        )

        # 调用 DeepSeek API
        deepseek_client = get_deepseek_client()
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )

        # 提取回复内容
        assistant_message = response.choices[0].message.content

        # 记录 AI 调用完成
        total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else None
        logger.info(
            "ai_chat_completed",
            user_id=user_id,
            lesson_id=chat_request.lesson_id,
            response_length=len(assistant_message),
            model="deepseek-chat",
            total_tokens=total_tokens
        )

        # 保存聊天记录到数据库（如果提供了 user_id）
        if user_id:
            from app.models.chat_message import ChatMessage as ChatMessageModel
            import json

            # 解析 lesson_id
            lesson_id_int = None
            if chat_request.lesson_id:
                try:
                    lesson_id_int = int(chat_request.lesson_id)
                except:
                    pass

            # 保存用户消息
            user_msg = ChatMessageModel(
                user_id=user_id,
                lesson_id=lesson_id_int,
                role='user',
                content=chat_request.message,
                extra_data=json.dumps({})
            )
            db.add(user_msg)

            # 保存助手回复
            assistant_msg = ChatMessageModel(
                user_id=user_id,
                lesson_id=lesson_id_int,
                role='assistant',
                content=assistant_message,
                extra_data=json.dumps({
                    'model': 'deepseek-chat',
                    'tokens': total_tokens
                })
            )
            db.add(assistant_msg)
            db.commit()

        # 返回统一格式的成功响应
        return success_response(
            data={
                "message": assistant_message,
                "model": "deepseek-chat",
                "tokens": total_tokens
            },
            message="AI助手回复成功"
        )

    except Exception as e:
        logger.error(
            "ai_chat_failed",
            user_id=user_id,
            lesson_id=chat_request.lesson_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        # 返回统一格式的错误响应
        return error_response(
            code="AI_CHAT_ERROR",
            message="抱歉，AI 助手暂时无法回复。请稍后再试。",
            details={"error_type": type(e).__name__}
        )
