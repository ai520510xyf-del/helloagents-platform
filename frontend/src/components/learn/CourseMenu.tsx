/**
 * CourseMenu 组件
 * 左侧课程目录
 */

import { BookOpen } from 'lucide-react';
import { allChapters, type Lesson } from '../../data/courses';

interface CourseMenuProps {
  currentLesson: Lesson;
  theme: 'light' | 'dark';
  onLessonChange: (lessonId: string) => void;
}

// 获取状态图标
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed': return '✅';
    case 'current': return '🔄';
    case 'available': return '⭕';
    default: return '⭕';
  }
};

export function CourseMenu({ currentLesson, theme, onLessonChange }: CourseMenuProps) {
  return (
    <div className={`h-full overflow-y-auto border-r custom-scrollbar ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-50 border-gray-200'}`}>
      <div className="p-4">
        <div className="flex items-center gap-2 text-sm font-semibold mb-4">
          <BookOpen className="h-4 w-4" />
          <span>课程目录</span>
        </div>

        <nav className="space-y-1">
          {allChapters.map((chapter, chapterIndex) => (
            <div key={chapter.id}>
              {chapterIndex > 0 && <div className="h-4" />}
              <div className={`text-xs mb-2 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                第{chapter.id}章 {chapter.title}
              </div>
              {chapter.lessons.map((lesson) => {
                const isCurrent = currentLesson.id === lesson.id;

                return (
                  <button
                    key={lesson.id}
                    onClick={() => onLessonChange(lesson.id)}
                    className={`
                      w-full text-left px-3 py-2 text-sm rounded transition-colors cursor-pointer
                      ${isCurrent
                        ? 'bg-primary/10 border-l-2 border-primary' + (theme === 'dark' ? ' text-text-primary' : ' text-gray-900')
                        : (theme === 'dark' ? 'hover:bg-bg-elevated text-text-secondary' : 'hover:bg-gray-200 text-gray-700')}
                    `}
                  >
                    {getStatusIcon(lesson.status)} {lesson.id} {lesson.title}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
      </div>
    </div>
  );
}
