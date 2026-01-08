/**
 * useLesson Hook
 * 管理课程状态和切换逻辑
 */

import { useState, useEffect } from 'react';
import { findLessonById, type Lesson } from '../data/courses';
import { getLessonContent } from '../services/api';

const LAST_LESSON_ID_KEY = 'helloagents_last_lesson_id';

export function useLesson() {
  // 获取初始课程
  const getInitialLesson = (): Lesson => {
    try {
      const lastLessonId = localStorage.getItem(LAST_LESSON_ID_KEY);
      if (lastLessonId) {
        const lesson = findLessonById(lastLessonId);
        if (lesson) {
          return lesson;
        }
      }
    } catch (error) {
      console.error('加载上次选择的课程失败:', error);
    }
    return findLessonById('1') || { id: '1', chapter: 1, title: '第一章', status: 'current', codeTemplate: '', description: '', content: '' };
  };

  const [currentLesson, setCurrentLesson] = useState<Lesson>(getInitialLesson());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 页面加载时从后端获取当前课程内容
  useEffect(() => {
    const loadInitialLesson = async () => {
      if (currentLesson) {
        try {
          setIsLoading(true);
          localStorage.setItem(LAST_LESSON_ID_KEY, currentLesson.id);
          const lessonData = await getLessonContent(currentLesson.id);

          // 使用不可变更新方式更新状态
          setCurrentLesson(prevLesson => ({
            ...prevLesson,
            content: lessonData.content,
            codeTemplate: lessonData.code_template
          }));

          setError(null);
        } catch (error) {
          console.error('加载初始课程内容失败:', error);
          setError('加载课程内容失败');
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadInitialLesson();
  }, []); // 只在组件挂载时执行一次

  // 切换课程
  const changeLesson = async (lessonId: string) => {
    const lesson = findLessonById(lessonId);
    if (lesson) {
      try {
        setIsLoading(true);
        setError(null);

        // 保存当前选择的课程ID到本地存储
        localStorage.setItem(LAST_LESSON_ID_KEY, lessonId);

        // 从后端API获取完整的课程内容
        const lessonData = await getLessonContent(lessonId);

        // 使用不可变更新方式更新课程内容
        setCurrentLesson({
          ...lesson,
          content: lessonData.content,
          codeTemplate: lessonData.code_template
        });
      } catch (error) {
        console.error('加载课程内容失败:', error);
        setError('加载课程内容失败');

        // 如果后端加载失败，使用本地数据
        localStorage.setItem(LAST_LESSON_ID_KEY, lessonId);
        setCurrentLesson(lesson);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return {
    currentLesson,
    isLoading,
    error,
    changeLesson
  };
}
