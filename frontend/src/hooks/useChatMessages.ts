/**
 * useChatMessages Hook
 * 管理聊天消息状态
 */

import { useState, useEffect } from 'react';
import { chatWithAI, type ChatMessage } from '../services/api';
import { chatStorage } from '../utils/storage';
import { logger } from '../utils/logger';
import type { UploadedImage } from '../components/learn/ImageUpload';

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
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);

  // 当课程切换时，加载该课程的聊天历史
  useEffect(() => {
    const savedChat = loadChatFromStorage(lessonId);
    setChatMessages(savedChat);
    // 清空图片列表
    setUploadedImages([]);
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

    // 如果有图片，暂时只在前端显示提示，不发送到后端
    let userContent = chatInput;
    if (uploadedImages.length > 0) {
      userContent += `\n\n[📷 已上传 ${uploadedImages.length} 张图片，但当前AI模型暂不支持图片分析]`;
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content: userContent
    };

    // 添加用户消息到聊天历史
    setChatMessages(prev => [...prev, userMessage]);
    const currentInput = chatInput; // 保存当前输入
    setChatInput('');
    // 清空图片列表
    // const currentImages = [...uploadedImages]; // 保留图片数据，供后续使用
    setUploadedImages([]);
    setIsChatLoading(true);

    try {
      // 调用 AI 聊天 API（暂不发送图片数据到后端）
      const response = await chatWithAI({
        message: currentInput,
        conversation_history: chatMessages,
        lesson_id: lessonId,
        code: code
        // TODO: 当切换到支持多模态的AI时，添加图片数据
        // images: uploadedImages.map(img => img.base64)
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

  // 重新生成消息
  const regenerateMessage = async (messageIndex: number) => {
    // 找到要重新生成的消息
    const messageToRegenerate = chatMessages[messageIndex];
    if (!messageToRegenerate || messageToRegenerate.role !== 'assistant') {
      return;
    }

    // 找到对应的用户消息（前一条消息）
    const userMessage = chatMessages[messageIndex - 1];
    if (!userMessage || userMessage.role !== 'user') {
      return;
    }

    setIsChatLoading(true);

    try {
      // 获取重新生成之前的对话历史（不包含要重新生成的消息）
      const historyBeforeRegeneration = chatMessages.slice(0, messageIndex);

      // 调用 AI 聊天 API
      const response = await chatWithAI({
        message: userMessage.content,
        conversation_history: historyBeforeRegeneration,
        lesson_id: lessonId,
        code: code
      });

      // 替换 AI 回复
      const newAiMessage: ChatMessage = {
        role: 'assistant',
        content: response.message
      };

      // 更新消息列表，替换指定位置的消息
      setChatMessages(prev => {
        const newMessages = [...prev];
        newMessages[messageIndex] = newAiMessage;
        return newMessages;
      });
    } catch (error) {
      logger.error('重新生成消息失败', error);

      // 错误处理
      let errorContent = '抱歉，重新生成失败。\n\n';

      if (error instanceof Error) {
        if (error.message.includes('fetch') || error.message.includes('network')) {
          errorContent += '**原因**：无法连接到AI服务\n\n';
        } else if (error.message.includes('timeout')) {
          errorContent += '**原因**：请求超时\n\n';
        } else {
          errorContent += `**错误详情**：${error.message}\n\n`;
        }
      }

      errorContent += '请稍后重试。';

      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: errorContent
      };

      // 更新消息列表，替换指定位置的消息
      setChatMessages(prev => {
        const newMessages = [...prev];
        newMessages[messageIndex] = errorMessage;
        return newMessages;
      });
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
    setChatMessages,
    regenerateMessage,
    uploadedImages,
    setUploadedImages
  };
}
