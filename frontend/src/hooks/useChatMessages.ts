/**
 * useChatMessages Hook
 * 管理聊天消息状态
 */

import { useState, useEffect } from 'react';
import { chatWithAI, type ChatMessage } from '../services/api';
import { chatStorage } from '../utils/storage';
import { logger } from '../utils/logger';

export function useChatMessages(lessonId: string, code: string) {
  // 从本地存储加载聊天历史
  const loadChatFromStorage = (id: string): ChatMessage[] => {
    return chatStorage.get<ChatMessage[]>(`${id}_history`, []) || [];
  };

  // 保存聊天历史到本地存储
  const saveChatToStorage = (id: string, messages: ChatMessage[]) => {
    chatStorage.set(`${id}_history`, messages);
  };

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(loadChatFromStorage(lessonId));
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);

  // 当课程切换时，加载该课程的聊天历史
  useEffect(() => {
    const savedChat = loadChatFromStorage(lessonId);
    setChatMessages(savedChat);
  }, [lessonId]);

  // 自动保存聊天历史到本地存储
  useEffect(() => {
    if (chatMessages.length > 0) {
      saveChatToStorage(lessonId, chatMessages);
    }
  }, [chatMessages, lessonId]);

  // 发送聊天消息
  const sendMessage = async () => {
    if (!chatInput.trim() || isChatLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput
    };

    // 添加用户消息到聊天历史
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsChatLoading(true);

    try {
      // 调用 AI 聊天 API
      const response = await chatWithAI({
        message: chatInput,
        conversation_history: chatMessages,
        lesson_id: lessonId,
        code: code
      });

      // 添加 AI 回复到聊天历史
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.message
      };
      setChatMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      logger.error('发送消息失败', error);

      // 详细的错误信息
      let errorContent = '抱歉，我现在无法回复。\n\n';

      if (error instanceof Error) {
        if (error.message.includes('fetch') || error.message.includes('network')) {
          errorContent += '**原因**：无法连接到AI服务\n\n';
          errorContent += '**可能的解决方案**：\n';
          errorContent += '1. 检查后端服务是否运行\n';
          errorContent += '2. 确认AI API配置是否正确\n';
          errorContent += '3. 检查网络连接\n\n';
        } else if (error.message.includes('timeout')) {
          errorContent += '**原因**：请求超时\n\n';
          errorContent += 'AI服务响应时间过长，请稍后重试。\n\n';
        } else {
          errorContent += `**错误详情**：${error.message}\n\n`;
        }
      }

      errorContent += '💡 **提示**：您可以稍后重新发送消息，或者查阅课程内容继续学习。';

      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: errorContent
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsChatLoading(false);
    }
  };

  return {
    chatMessages,
    chatInput,
    setChatInput,
    isChatLoading,
    sendMessage,
    setChatMessages
  };
}
