/**
 * API 服务模块
 *
 * 与后端 FastAPI 服务通信
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================
// 类型定义
// ============================================

export interface CodeExecutionRequest {
  code: string;
  language?: string;
  timeout?: number;
}

export interface CodeExecutionResponse {
  success: boolean;
  output: string;
  error?: string;
  execution_time: number;
}

export interface AIHintRequest {
  code: string;
  cursor_line: number;
  cursor_column: number;
  language?: string;
}

export interface AIHintResponse {
  current_context: string;
  hint: string;
  reference_code?: string;
  key_concepts: string[];
}

export interface LessonContentResponse {
  lesson_id: string;
  title: string;
  content: string;  // Markdown 格式的课程内容
  code_template: string;  // 代码模板
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
  lesson_id?: string;
  code?: string;
}

export interface ChatResponse {
  message: string;
  success: boolean;
}

// ============================================
// API 函数
// ============================================

/**
 * 执行代码
 */
export async function executeCode(request: CodeExecutionRequest): Promise<CodeExecutionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('代码执行失败:', error);
    throw error;
  }
}

/**
 * 获取 AI 提示
 */
export async function getAIHint(request: AIHintRequest): Promise<AIHintResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/hint`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('获取 AI 提示失败:', error);
    throw error;
  }
}

/**
 * 获取课程内容
 */
export async function getLessonContent(lessonId: string): Promise<LessonContentResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/lessons/${lessonId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('获取课程内容失败:', error);
    throw error;
  }
}

/**
 * 与 AI 助手聊天
 */
export async function chatWithAI(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('AI 聊天失败:', error);
    throw error;
  }
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  } catch (error) {
    console.error('健康检查失败:', error);
    throw error;
  }
}
