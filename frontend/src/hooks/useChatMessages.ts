/**
 * useChatMessages Hook
 * 管理聊天消息状态
 */

import { useState, useEffect } from 'react';
import { chatWithAI, type ChatMessage } from '../services/api';

const CHAT_STORAGE_PREFIX = 'helloagents_lesson_chat_';

export function useChatMessages(lessonId: string, code: string) {
  // 从本地存储加载聊天历史
  const loadChatFromStorage = (id: string): ChatMessage[] => {
    try {
      const savedChat = localStorage.getItem(CHAT_STORAGE_PREFIX + id);
      return savedChat ? JSON.parse(savedChat) : [];
    } catch (error) {
      console.error('加载聊天历史失败:', error);
      return [];
    }
  };

  // 保存聊天历史到本地存储
  const saveChatToStorage = (id: string, messages: ChatMessage[]) => {
    try {
      localStorage.setItem(CHAT_STORAGE_PREFIX + id, JSON.stringify(messages));
    } catch (error) {
      console.error('保存聊天历史失败:', error);
    }
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
      console.error('发送消息失败:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: '抱歉，我现在无法回复。请稍后再试。'
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
