"""
HelloAgents 学习平台 - 后端 API 服务
基于 FastAPI 构建，提供代码执行和 AI 助手功能
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import json
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 导入数据库
from app.database import get_db, init_db

# 导入沙箱模块
from app.sandbox import sandbox

# 导入课程管理模块
from app.courses import course_manager

# 导入 OpenAI SDK (用于 DeepSeek)
from openai import OpenAI

# 导入路由
from app.routers import users, progress, submissions, chat, migrate

# 创建 FastAPI 应用
app = FastAPI(
    title="HelloAgents Learning Platform API",
    description="AI Agent 互动学习平台后端服务",
    version="1.0.0"
)

# 初始化 DeepSeek 客户端（使用 OpenAI SDK）
deepseek_client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"  # 需要添加 /v1 后缀
)

# 配置 CORS - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router)
app.include_router(progress.router)
app.include_router(submissions.router)
app.include_router(chat.router)
app.include_router(migrate.router)

# ============================================
# 数据模型
# ============================================

class CodeExecutionRequest(BaseModel):
    """代码执行请求"""
    code: str
    language: str = "python"
    timeout: int = 30  # 超时时间（秒）

class CodeExecutionResponse(BaseModel):
    """代码执行响应"""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float  # 执行时间（秒）

class AIHintRequest(BaseModel):
    """AI 提示请求"""
    code: str
    cursor_line: int
    cursor_column: int
    language: str = "python"

class AIHintResponse(BaseModel):
    """AI 提示响应"""
    current_context: str  # 当前位置上下文
    hint: str  # 智能提示
    reference_code: Optional[str] = None  # 参考代码
    key_concepts: List[str]  # 关键概念

class LessonContentRequest(BaseModel):
    """课程内容请求"""
    lesson_id: str  # 课程ID，如 "1", "2", "4.1"

class LessonContentResponse(BaseModel):
    """课程内容响应"""
    lesson_id: str
    title: str
    content: str  # Markdown 格式的课程内容
    code_template: str  # 代码模板

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # "user" 或 "assistant"
    content: str

class ChatRequest(BaseModel):
    """AI 聊天请求"""
    message: str  # 用户消息
    conversation_history: List[ChatMessage] = []  # 对话历史
    lesson_id: Optional[str] = None  # 当前课程ID（用于提供上下文）
    code: Optional[str] = None  # 当前代码（用于提供上下文）

class ChatResponse(BaseModel):
    """AI 聊天响应"""
    message: str  # AI 回复
    success: bool = True

# ============================================
# API 端点
# ============================================

@app.get("/")
async def root():
    """根端点 - 健康检查"""
    return {
        "status": "ok",
        "message": "HelloAgents Learning Platform API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    user_id: Optional[int] = None,
    lesson_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    执行用户代码

    使用 Docker 容器作为安全沙箱环境执行代码
    可选：保存代码提交记录到数据库
    """
    try:
        # 使用沙箱执行代码
        success, output, execution_time = sandbox.execute_python(request.code)

        # 保存到数据库（如果提供了 user_id 和 lesson_id）
        if user_id and lesson_id:
            from app.models.code_submission import CodeSubmission
            submission = CodeSubmission(
                user_id=user_id,
                lesson_id=lesson_id,
                code=request.code,
                output=output if success else None,
                status='success' if success else 'error',
                execution_time=execution_time
            )
            db.add(submission)
            db.commit()

        if success:
            return CodeExecutionResponse(
                success=True,
                output=output,
                execution_time=execution_time
            )
        else:
            return CodeExecutionResponse(
                success=False,
                output="",
                error=output,  # 错误信息
                execution_time=execution_time
            )

    except Exception as e:
        return CodeExecutionResponse(
            success=False,
            output="",
            error=str(e),
            execution_time=0.0
        )

@app.get("/api/lessons")
async def get_all_lessons():
    """
    获取所有课程列表

    返回课程目录结构
    """
    try:
        lessons = course_manager.get_all_lessons()
        return {
            "success": True,
            "lessons": lessons
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lessons/{lesson_id}", response_model=LessonContentResponse)
async def get_lesson_content(lesson_id: str):
    """
    获取指定课程的完整内容

    Args:
        lesson_id: 课程ID，如 "1", "2", "4.1"

    Returns:
        课程内容和代码模板
    """
    try:
        # 获取课程内容
        content = course_manager.get_lesson_content(lesson_id)
        if content is None:
            raise HTTPException(status_code=404, detail=f"课程 {lesson_id} 不存在")

        # 获取代码模板
        code_template = course_manager.get_code_template(lesson_id)

        # 获取课程标题
        lesson_info = course_manager._course_structure.get(lesson_id, {})
        title = lesson_info.get("title", f"第{lesson_id}章")

        return LessonContentResponse(
            lesson_id=lesson_id,
            title=title,
            content=content,
            code_template=code_template or ""
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    与 AI 学习助手聊天

    提供课程学习过程中的问答支持
    可选：保存聊天消息到数据库
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
        if request.lesson_id:
            system_prompt += f"\n\n当前学习章节：第{request.lesson_id}章"

        # 添加当前代码上下文
        if request.code and len(request.code.strip()) > 0:
            system_prompt += f"\n\n学习者当前的代码：\n```python\n{request.code[:1000]}\n```"

        # 构建消息历史 (OpenAI 格式)
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 添加对话历史
        for msg in request.conversation_history[-10:]:  # 只保留最近10轮对话
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": request.message
        })

        # 调用 DeepSeek API
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )

        # 提取回复内容
        assistant_message = response.choices[0].message.content

        # 保存聊天记录到数据库（如果提供了 user_id）
        if user_id:
            from app.models.chat_message import ChatMessage as ChatMessageModel
            import json

            # 解析 lesson_id
            lesson_id_int = None
            if request.lesson_id:
                try:
                    lesson_id_int = int(request.lesson_id)
                except:
                    pass

            # 保存用户消息
            user_msg = ChatMessageModel(
                user_id=user_id,
                lesson_id=lesson_id_int,
                role='user',
                content=request.message,
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
                    'tokens': response.usage.total_tokens if hasattr(response, 'usage') else None
                })
            )
            db.add(assistant_msg)
            db.commit()

        return ChatResponse(
            message=assistant_message,
            success=True
        )

    except Exception as e:
        print(f"AI 聊天错误: {str(e)}")
        return ChatResponse(
            message="抱歉，AI 助手暂时无法回复。请稍后再试。",
            success=False
        )

@app.post("/api/hint", response_model=AIHintResponse)
async def get_ai_hint(request: AIHintRequest):
    """
    获取 AI 智能提示

    根据当前代码和光标位置，提供实时的编程提示
    """
    try:
        # TODO: 集成真实的 Claude API 生成提示
        # 目前使用规则引擎模拟

        # 获取光标所在行的代码
        lines = request.code.split('\n')
        current_line = lines[request.cursor_line - 1] if request.cursor_line <= len(lines) else ""

        # 简单的上下文分析
        if "def __init__" in current_line:
            return AIHintResponse(
                current_context="ReActAgent.__init__() 初始化方法",
                hint="你正在编写 ReAct Agent 的初始化方法。需要接收 llm_client 和 tool_executor 两个参数，分别代表大脑（推理）和手脚（执行）。",
                reference_code="""def __init__(self, llm_client, tool_executor):
    self.llm_client = llm_client
    self.tool_executor = tool_executor
    self.history = []
    self.max_steps = 5""",
                key_concepts=[
                    "llm_client: LLM 客户端，负责推理和决策",
                    "tool_executor: 工具执行器，负责执行具体操作",
                    "history: 记录执行历史",
                    "max_steps: 防止无限循环"
                ]
            )

        elif "def run" in current_line:
            return AIHintResponse(
                current_context="ReActAgent.run() 核心运行方法",
                hint="这是 ReAct Agent 的核心方法，需要实现 Thought-Action-Observation 循环。",
                reference_code="""def run(self, question: str) -> str:
    for step in range(self.max_steps):
        # 1. Thought: 思考下一步
        thought = self.llm_client.think(question, self.history)

        # 2. Action: 执行工具调用
        action = self.parse_action(thought)
        observation = self.tool_executor.execute(action)

        # 3. 记录历史
        self.history.append((thought, action, observation))

        # 4. 检查是否完成
        if self.is_final_answer(thought):
            return thought

    return "达到最大步数限制\"""",
                key_concepts=[
                    "循环执行: 使用 for 循环控制最大步数",
                    "Thought: LLM 推理思考",
                    "Action: 解析并执行工具",
                    "Observation: 记录执行结果",
                    "终止条件: 检查是否得到最终答案"
                ]
            )

        else:
            # 默认提示
            return AIHintResponse(
                current_context="编写 ReAct Agent",
                hint="ReAct (Reasoning + Acting) 是一种结合推理和行动的 Agent 范式。核心思想是让 AI 边思考边执行。",
                reference_code=None,
                key_concepts=[
                    "ReAct = Reasoning + Acting",
                    "循环执行 Thought-Action-Observation",
                    "LLM 负责推理，Tools 负责执行"
                ]
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# 启动事件
# ============================================

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("=" * 60)
    print("🚀 HelloAgents Learning Platform API 启动中...")
    print("=" * 60)

    # 初始化数据库
    try:
        init_db()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"⚠️  数据库初始化失败: {str(e)}")

    print("=" * 60)
    print("🚀 HelloAgents Learning Platform API 启动成功")
    print("📝 API 文档: http://localhost:8000/docs")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("👋 HelloAgents Learning Platform API 正在关闭...")
