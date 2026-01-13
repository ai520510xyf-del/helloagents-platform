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
import requests

from app.database import get_db
from app.logger import get_logger
from app.api.response_models import success_response, error_response

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)

# DeepSeek 客户端延迟初始化
_deepseek_client = None

# Cloudflare Workers AI 配置
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
AI_PROVIDER = os.environ.get("AI_PROVIDER", "deepseek-chat")


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


def call_cloudflare_vision(messages: List[dict], images: List[str] = None):
    """
    调用 Cloudflare Workers AI 视觉模型

    Args:
        messages: 对话消息列表
        images: base64编码的图片列表

    Returns:
        str: AI 回复内容

    Raises:
        ValueError: 当 Cloudflare 配置缺失时
        Exception: API 调用失败时
    """
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        raise ValueError(
            "CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN must be set "
            "to use Cloudflare Workers AI vision features."
        )

    # 使用 Llama 3.2 Vision 模型
    model = "@cf/meta/llama-3.2-11b-vision-instruct"
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # 如果有图片，将最后一条用户消息转换为多模态格式
    if images and len(images) > 0:
        # 找到最后一条用户消息
        for i in range(len(messages) - 1, -1, -1):
            if messages[i]["role"] == "user":
                # 将文本内容转换为多模态格式
                text_content = messages[i]["content"]
                messages[i]["content"] = [
                    {"type": "text", "text": text_content}
                ]
                # 添加图片（只取第一张，因为模型限制）
                for img_base64 in images[:1]:  # 只使用第一张图片
                    # 确保 base64 字符串格式正确
                    if not img_base64.startswith("data:image/"):
                        img_base64 = f"data:image/jpeg;base64,{img_base64}"
                    messages[i]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": img_base64}
                    })
                break

    payload = {"messages": messages}

    logger.info(
        "cloudflare_ai_call_started",
        model=model,
        has_images=bool(images and len(images) > 0),
        message_count=len(messages)
    )

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()

        # Cloudflare Workers AI 返回格式：{"result": {"response": "..."}}
        if "result" in result and "response" in result["result"]:
            return result["result"]["response"]
        else:
            logger.error("cloudflare_ai_unexpected_format", response=result)
            raise Exception("Unexpected response format from Cloudflare AI")

    except requests.exceptions.Timeout:
        logger.error("cloudflare_ai_timeout")
        raise Exception("Cloudflare AI request timed out")
    except requests.exceptions.RequestException as e:
        logger.error("cloudflare_ai_request_failed", error=str(e))
        raise Exception(f"Cloudflare AI request failed: {str(e)}")


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
    images: Optional[List[str]] = Field(None, description="图片列表（base64编码）")


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
            has_images=bool(chat_request.images and len(chat_request.images) > 0),
            conversation_history_length=len(chat_request.conversation_history)
        )

        # 判断使用哪个 AI 提供商
        has_images = chat_request.images and len(chat_request.images) > 0
        use_vision = has_images or AI_PROVIDER == "cloudflare-vision"

        assistant_message = None
        total_tokens = None
        model_used = None

        if use_vision:
            # 使用 Cloudflare Workers AI 视觉模型
            try:
                assistant_message = call_cloudflare_vision(messages, chat_request.images)
                model_used = "cloudflare-llama-3.2-vision"
                total_tokens = None  # Cloudflare 不返回 token 信息
            except Exception as cf_error:
                logger.warning(
                    "cloudflare_ai_failed_fallback_to_deepseek",
                    error=str(cf_error)
                )
                # 降级到 DeepSeek（不支持图片）
                if has_images:
                    # 添加提示说明无法处理图片
                    messages.append({
                        "role": "system",
                        "content": "注意：用户上传了图片，但由于技术限制无法处理图片内容。请基于文本内容回答。"
                    })

                deepseek_client = get_deepseek_client()
                response = deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.7
                )
                assistant_message = response.choices[0].message.content
                total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else None
                model_used = "deepseek-chat (fallback)"
        else:
            # 使用 DeepSeek API（纯文本）
            deepseek_client = get_deepseek_client()
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            assistant_message = response.choices[0].message.content
            total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else None
            model_used = "deepseek-chat"

        # 记录 AI 调用完成
        logger.info(
            "ai_chat_completed",
            user_id=user_id,
            lesson_id=chat_request.lesson_id,
            response_length=len(assistant_message),
            model=model_used,
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
