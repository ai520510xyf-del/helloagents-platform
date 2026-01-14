"""
代码执行和 AI 提示 API (v1)

提供代码执行沙箱和智能提示功能
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.sandbox import sandbox
from app.logger import get_logger
from app.api.response_models import success_response, error_response

logger = get_logger(__name__)

router = APIRouter(prefix="/code", tags=["code"])
limiter = Limiter(key_func=get_remote_address)


# ============================================
# 数据模型
# ============================================

class CodeExecutionRequest(BaseModel):
    """代码执行请求"""
    code: str = Field(..., min_length=1, description="要执行的代码")
    language: str = Field(default="python", description="编程语言")
    timeout: int = Field(default=30, ge=1, le=60, description="超时时间（秒）")


class CodeExecutionResponse(BaseModel):
    """代码执行响应"""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = Field(..., description="执行时间（秒）")


class AIHintRequest(BaseModel):
    """AI 提示请求"""
    code: str = Field(..., description="当前代码")
    cursor_line: int = Field(..., ge=1, description="光标所在行号")
    cursor_column: int = Field(..., ge=0, description="光标所在列号")
    language: str = Field(default="python", description="编程语言")


class AIHintResponse(BaseModel):
    """AI 提示响应"""
    current_context: str = Field(..., description="当前位置上下文")
    hint: str = Field(..., description="智能提示")
    reference_code: Optional[str] = Field(None, description="参考代码")
    key_concepts: List[str] = Field(..., description="关键概念")


# ============================================
# API 端点
# ============================================

@router.post("/execute")
@limiter.limit("30/minute")
async def execute_code(
    request: Request,
    code_request: CodeExecutionRequest,
    user_id: Optional[int] = None,
    lesson_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    执行用户代码

    使用 Docker 容器作为安全沙箱环境执行代码
    可选：保存代码提交记录到数据库

    **速率限制:** 30次/分钟

    **请求参数:**
    - code: 要执行的代码
    - language: 编程语言（当前仅支持 python）
    - timeout: 超时时间（1-60秒）

    **响应格式:**
    ```json
    {
        "success": true,
        "data": {
            "output": "Hello World",
            "execution_time": 0.123,
            "error": null
        },
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
    """
    logger.info(
        "code_execution_started",
        user_id=user_id,
        lesson_id=lesson_id,
        code_length=len(code_request.code),
        language=code_request.language
    )

    try:
        # 使用沙箱执行代码
        success, output, execution_time = sandbox.execute_python(code_request.code)

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
                code=code_request.code,
                output=output if success else None,
                status='success' if success else 'error',
                execution_time=execution_time
            )
            db.add(submission)
            db.commit()

        # 返回统一格式的响应
        return success_response(
            data={
                "output": output if success else "",
                "execution_time": execution_time,
                "error": None if success else output
            },
            message="代码执行完成" if success else "代码执行失败"
        )

    except Exception as e:
        logger.error(
            "code_execution_failed",
            user_id=user_id,
            lesson_id=lesson_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        return error_response(
            code="CODE_EXECUTION_ERROR",
            message="代码执行失败",
            details={"error": str(e), "error_type": type(e).__name__}
        )


@router.post("/hint")
@limiter.limit("60/minute")
async def get_ai_hint(
    request: Request,
    hint_request: AIHintRequest
):
    """
    获取 AI 智能提示

    根据当前代码和光标位置，提供实时的编程提示

    **速率限制:** 60次/分钟

    **请求参数:**
    - code: 当前代码
    - cursor_line: 光标所在行号（从1开始）
    - cursor_column: 光标所在列号（从0开始）
    - language: 编程语言

    **响应格式:**
    ```json
    {
        "success": true,
        "data": {
            "current_context": "上下文描述",
            "hint": "智能提示",
            "reference_code": "参考代码",
            "key_concepts": ["概念1", "概念2"]
        },
        "timestamp": "2024-01-08T10:00:00Z"
    }
    ```
    """
    try:
        # TODO: 集成真实的 Claude API 生成提示
        # 目前使用规则引擎模拟

        # 获取光标所在行的代码
        lines = hint_request.code.split('\n')
        current_line = lines[hint_request.cursor_line - 1] if hint_request.cursor_line <= len(lines) else ""

        # 简单的上下文分析
        hint_data = None
        if "def __init__" in current_line:
            hint_data = {
                "current_context": "ReActAgent.__init__() 初始化方法",
                "hint": "你正在编写 ReAct Agent 的初始化方法。需要接收 llm_client 和 tool_executor 两个参数，分别代表大脑（推理）和手脚（执行）。",
                "reference_code": """def __init__(self, llm_client, tool_executor):
    self.llm_client = llm_client
    self.tool_executor = tool_executor
    self.history = []
    self.max_steps = 5""",
                "key_concepts": [
                    "llm_client: LLM 客户端，负责推理和决策",
                    "tool_executor: 工具执行器，负责执行具体操作",
                    "history: 记录执行历史",
                    "max_steps: 防止无限循环"
                ]
            }
        elif "def run" in current_line:
            hint_data = {
                "current_context": "ReActAgent.run() 核心运行方法",
                "hint": "这是 ReAct Agent 的核心方法，需要实现 Thought-Action-Observation 循环。",
                "reference_code": """def run(self, question: str) -> str:
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
                "key_concepts": [
                    "循环执行: 使用 for 循环控制最大步数",
                    "Thought: LLM 推理思考",
                    "Action: 解析并执行工具",
                    "Observation: 记录执行结果",
                    "终止条件: 检查是否得到最终答案"
                ]
            }
        else:
            # 默认提示
            hint_data = {
                "current_context": "编写 ReAct Agent",
                "hint": "ReAct (Reasoning + Acting) 是一种结合推理和行动的 Agent 范式。核心思想是让 AI 边思考边执行。",
                "reference_code": None,
                "key_concepts": [
                    "ReAct = Reasoning + Acting",
                    "循环执行 Thought-Action-Observation",
                    "LLM 负责推理，Tools 负责执行"
                ]
            }

        # 返回统一格式的响应
        return success_response(data=hint_data, message="AI提示生成成功")

    except Exception as e:
        logger.error(
            "ai_hint_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        return error_response(
            code="AI_HINT_ERROR",
            message="AI提示生成失败",
            details={"error": str(e), "error_type": type(e).__name__}
        )
