/**
 * NavigationBar 组件
 * 顶部导航栏，包含标题、进度条和主题切换
 *
 * 性能优化：
 * - 使用 React.memo 避免不必要的重渲染
 * - 仅在 progress、theme 或 currentLesson.id 变化时更新
 */

import { memo } from 'react';
import { Code, Sun, Moon } from 'lucide-react';
import { type Lesson } from '../../data/courses';

interface NavigationBarProps {
  currentLesson: Lesson;
  progress: number;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const NavigationBar = memo(function NavigationBar({ currentLesson, progress, theme, onToggleTheme }: NavigationBarProps) {
  return (
    <header className={`h-14 border-b flex items-center justify-between px-6 flex-shrink-0 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-50 border-gray-200'}`}>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Code className="h-5 w-5 text-primary" />
          <span className="font-semibold text-lg">HelloAgents</span>
        </div>
        <div className={`text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>
          第{currentLesson.chapter}章 {currentLesson.title}
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* 进度 */}
        <div className="flex items-center gap-2">
          <div className={`text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>学习进度</div>
          <div className="flex items-center gap-2">
            <div className={`w-32 h-2 rounded-full overflow-hidden ${theme === 'dark' ? 'bg-border' : 'bg-gray-300'}`}>
              <div className="h-full bg-primary" style={{ width: `${progress}%` }} />
            </div>
            <span className={`text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>{progress}%</span>
          </div>
        </div>

        {/* 主题切换按钮 */}
        <button
          onClick={onToggleTheme}
          className={`h-9 w-9 rounded-lg flex items-center justify-center transition-colors ${
            theme === 'dark'
              ? 'bg-bg-elevated hover:bg-border'
              : 'bg-gray-200 hover:bg-gray-300'
          }`}
          title={theme === 'dark' ? '切换到亮色主题' : '切换到暗色主题'}
        >
          {theme === 'dark' ? (
            <Sun className="h-4 w-4 text-text-secondary" />
          ) : (
            <Moon className="h-4 w-4 text-gray-600" />
          )}
        </button>

        {/* 用户头像占位 */}
        <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs ${
          theme === 'dark'
            ? 'bg-bg-elevated text-text-secondary'
            : 'bg-gray-200 text-gray-600'
        }`}>
          👤
        </div>
      </div>
    </header>
  );
}, (prevProps, nextProps) => {
  // 自定义比较函数：仅在关键属性变化时重新渲染
  return (
    prevProps.progress === nextProps.progress &&
    prevProps.theme === nextProps.theme &&
    prevProps.currentLesson.id === nextProps.currentLesson.id &&
    prevProps.currentLesson.chapter === nextProps.currentLesson.chapter &&
    prevProps.currentLesson.title === nextProps.currentLesson.title
  );
});
