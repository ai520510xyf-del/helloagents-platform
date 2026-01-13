/**
 * API 服务模块
 *
 * 与后端 FastAPI 服务通信
 */

import { apiClient } from '../utils/apiClient';

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
  images?: string[];  // base64 编码的图片列表
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
  return apiClient.post<CodeExecutionResponse>('/api/execute', request, {
    timeout: 60000, // 60 seconds for code execution
  });
}

/**
 * 获取 AI 提示
 */
export async function getAIHint(request: AIHintRequest): Promise<AIHintResponse> {
  return apiClient.post<AIHintResponse>('/api/hint', request);
}

/**
 * 获取课程内容
 */
export async function getLessonContent(lessonId: string): Promise<LessonContentResponse> {
  return apiClient.get<LessonContentResponse>(`/api/lessons/${lessonId}`);
}

/**
 * 与 AI 助手聊天
 */
export async function chatWithAI(request: ChatRequest): Promise<ChatResponse> {
  return apiClient.post<ChatResponse>('/api/chat', request, {
    timeout: 60000, // 60 seconds for AI response
  });
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  return apiClient.get<{ status: string; timestamp: string }>('/health');
}
