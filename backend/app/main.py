"""
HelloAgents 学习平台 - 后端 API 服务
基于 FastAPI 构建，提供代码执行和 AI 助手功能
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import json
import asyncio
from datetime import datetime
import os
import time
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化 Sentry（如果配置了 DSN）
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "development")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        # 发送默认的个人身份信息
        send_default_pii=False,
        # 附加请求体
        attach_stacktrace=True,
    )

# 初始化日志系统
from app.logger import get_logger
logger = get_logger(__name__)

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

# 导入 API 版本模块
from app.api.v1 import api_router as api_v1_router
from app.api.version import router as version_router

# 初始化速率限制器
limiter = Limiter(key_func=get_remote_address)

# 创建 FastAPI 应用
app = FastAPI(
    title="HelloAgents Learning Platform API",
    description="AI Agent 互动学习平台后端服务",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# 将速率限制器绑定到 app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# 添加中间件 (顺序很重要 - 后添加的先执行)
from app.middleware.logging_middleware import (
    LoggingMiddleware,
    PerformanceMonitoringMiddleware,
    ErrorLoggingMiddleware
)
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.version_middleware import APIVersionMiddleware

# 错误处理中间件 (最先添加，最后执行，确保能捕获所有错误)
app.add_middleware(ErrorHandlerMiddleware)

# 版本控制中间件
app.add_middleware(APIVersionMiddleware, default_version="v1")

# 日志中间件
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold_ms=1000.0)
app.add_middleware(LoggingMiddleware)

# 配置 CORS - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 开发服务器
        "https://helloagents-platform.pages.dev",  # Cloudflare Pages 生产环境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入异常处理器
from app.exceptions import HelloAgentsException, ValidationError

# 注册版本化路由
app.include_router(api_v1_router, prefix="/api/v1")

# 注册版本信息路由
app.include_router(version_router)

# 注册现有路由（保持向后兼容）
app.include_router(users.router)
app.include_router(progress.router)
app.include_router(submissions.router)
app.include_router(chat.router)
app.include_router(migrate.router)

# ============================================
# 异常处理器
# ============================================

@app.exception_handler(HelloAgentsException)
async def helloagents_exception_handler(request: Request, exc: HelloAgentsException):
    """
    处理 HelloAgents 自定义异常

    返回统一格式的错误响应
    """
    # 根据状态码决定日志级别
    if exc.status_code >= 500:
        logger.error(
            "helloagents_exception",
            error_code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url),
            method=request.method,
            details=exc.details
        )
    else:
        logger.warning(
            "helloagents_exception",
            error_code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url),
            method=request.method,
            details=exc.details
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "path": str(request.url),
                "timestamp": time.time(),
                **({"details": exc.details} if exc.details else {})
            }
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理 FastAPI HTTPException

    返回统一格式的错误响应
    """
    logger.warning(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=str(request.url),
        method=request.method
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "path": str(request.url),
                "timestamp": time.time()
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证错误

    返回详细的验证错误信息
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        "validation_error",
        path=str(request.url),
        method=request.method,
        errors=errors
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "path": str(request.url),
                "timestamp": time.time(),
                "details": {
                    "validation_errors": errors
                }
            }
        }
    )

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
    """
    完整健康检查端点

    检查所有系统组件的健康状态：
    - API 服务状态
    - 数据库连接
    - 沙箱容器池
    - AI 服务配置
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {}
    }

    # 检查数据库连接
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        logger.error("health_check_database_failed", error=str(e))

    # 检查沙箱容器池
    try:
        if sandbox.pool:
            pool_stats = sandbox.pool.get_stats()
            health_status["components"]["sandbox_pool"] = {
                "status": "healthy",
                "available_containers": pool_stats.get("available_containers", 0),
                "in_use_containers": pool_stats.get("in_use_containers", 0)
            }
        else:
            health_status["components"]["sandbox_pool"] = {
                "status": "disabled",
                "message": "Container pool is not enabled"
            }
    except Exception as e:
        health_status["components"]["sandbox_pool"] = {
            "status": "error",
            "message": f"Container pool check failed: {str(e)}"
        }
        logger.error("health_check_sandbox_failed", error=str(e))

    # 检查 AI 服务配置
    try:
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        if deepseek_api_key:
            health_status["components"]["ai_service"] = {
                "status": "configured",
                "message": "AI service API key is configured"
            }
        else:
            health_status["components"]["ai_service"] = {
                "status": "not_configured",
                "message": "AI service API key is not configured"
            }
    except Exception as e:
        health_status["components"]["ai_service"] = {
            "status": "error",
            "message": f"AI service check failed: {str(e)}"
        }

    # 如果任何组件不健康，返回 503 状态码
    status_code = 200 if health_status["status"] == "healthy" else 503

    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


@app.get("/health/ready")
async def readiness_check():
    """
    就绪检查端点 (Readiness Probe)

    检查应用是否准备好接收流量
    只检查关键依赖项（数据库）
    """
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/health/live")
async def liveness_check():
    """
    存活检查端点 (Liveness Probe)

    检查应用是否还在运行
    只做基本的响应检查
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# 向后兼容端点（重定向到 v1）
# ============================================
# 这些端点保持向后兼容，实际调用 v1 版本的实现

@app.get("/api/sandbox/pool/stats")
async def get_pool_stats():
    """
    获取容器池统计信息

    **已弃用**: 请使用 `/api/v1/sandbox/pool/stats`

    返回容器池的当前状态、性能指标和容器详情
    """
    if sandbox.pool is None:
        return {
            "pool_enabled": False,
            "message": "Container pool is not enabled",
            "timestamp": datetime.now().isoformat()
        }

    stats = sandbox.pool.get_stats()
    stats["pool_enabled"] = True
    stats["timestamp"] = datetime.now().isoformat()

    logger.info(
        "pool_stats_requested",
        available_containers=stats.get('available_containers', 0),
        in_use_containers=stats.get('in_use_containers', 0),
        total_executions=stats.get('total_executions', 0)
    )

    return stats

@app.post("/api/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    user_id: Optional[int] = None,
    lesson_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    执行用户代码

    **已弃用**: 请使用 `/api/v1/code/execute`

    使用 Docker 容器作为安全沙箱环境执行代码
    可选：保存代码提交记录到数据库
    """
    logger.info(
        "code_execution_started",
        user_id=user_id,
        lesson_id=lesson_id,
        code_length=len(request.code),
        language=request.language
    )

    try:
        # 使用沙箱执行代码
        success, output, execution_time = sandbox.execute_python(request.code)

        logger.info(
            "code_execution_completed",
            user_id=user_id,
            lesson_id=lesson_id,
            success=success,
            execution_time_ms=round(execution_time * 1000, 2),
            output_length=len(output)
        )

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

    except ValidationError as e:
        # 代码安全检查失败 - 抛出ValidationError让中间件处理
        raise e
    except HelloAgentsException:
        # 其他HelloAgents异常 - 让中间件处理
        raise
    except (SyntaxError, NameError, TypeError, ValueError, AttributeError, ImportError, KeyError, IndexError) as e:
        # 代码执行相关的异常 - 返回200的错误响应（用户代码问题，不是服务器问题）
        return CodeExecutionResponse(
            success=False,
            output="",
            error=str(e),
            execution_time=0.0
        )
    except Exception as e:
        # 未知异常 - 让中间件处理为500错误
        raise e

@app.get("/api/lessons")
async def get_all_lessons():
    """
    获取所有课程列表

    **已弃用**: 请使用 `/api/v1/lessons`

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

    **已弃用**: 请使用 `/api/v1/lessons/{lesson_id}`

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

    **已弃用**: 请使用 `/api/v1/chat`

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

        # 记录 AI 调用开始
        logger.info(
            "ai_chat_started",
            user_id=user_id,
            lesson_id=request.lesson_id,
            message_length=len(request.message),
            has_code_context=bool(request.code),
            conversation_history_length=len(request.conversation_history)
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
        logger.info(
            "ai_chat_completed",
            user_id=user_id,
            lesson_id=request.lesson_id,
            response_length=len(assistant_message),
            model="deepseek-chat",
            total_tokens=response.usage.total_tokens if hasattr(response, 'usage') else None
        )

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
        logger.error(
            "ai_chat_failed",
            user_id=user_id,
            lesson_id=request.lesson_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        return ChatResponse(
            message="抱歉，AI 助手暂时无法回复。请稍后再试。",
            success=False
        )

@app.post("/api/hint", response_model=AIHintResponse)
async def get_ai_hint(request: AIHintRequest):
    """
    获取 AI 智能提示

    **已弃用**: 请使用 `/api/v1/code/hint`

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

    # 优雅关闭容器池
    if sandbox.pool:
        logger.info("shutting_down_container_pool")
        print("🔄 正在关闭容器池...")
        sandbox.cleanup()
        print("✅ 容器池已关闭")

    logger.info("application_shutdown_completed")
    print("✅ 应用已完全关闭")
