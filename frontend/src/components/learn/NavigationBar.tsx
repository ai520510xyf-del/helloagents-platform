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
    <header
      className={`h-14 md:h-16 border-b flex items-center justify-between px-3 md:px-6 flex-shrink-0 safe-area-inset-top ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-50 border-gray-200'}`}
      data-testid="navbar"
    >
      {/* 左侧：Logo和标题 */}
      <div className="flex items-center gap-2 md:gap-4 min-w-0 flex-1">
        <div className="flex items-center gap-1.5 md:gap-2 flex-shrink-0">
          <Code className="h-4 w-4 md:h-5 md:w-5 text-primary" />
          <span className="font-semibold text-base md:text-lg" data-testid="app-title">HelloAgents</span>
        </div>
        <div
          className={`text-xs md:text-sm truncate ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}
          data-testid="lesson-title"
        >
          <span className="hidden sm:inline">第{currentLesson.chapter}章 </span>
          <span className="truncate">{currentLesson.title}</span>
        </div>
      </div>

      {/* 右侧：进度、主题切换、用户 */}
      <div className="flex items-center gap-2 md:gap-4 flex-shrink-0">
        {/* 进度 - 桌面端显示详细，移动端显示简洁 */}
        <div className="flex items-center gap-2" data-testid="progress-container">
          <div className={`text-xs md:text-sm hidden md:block ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>学习进度</div>
          <div className="flex items-center gap-1.5 md:gap-2">
            <div className={`w-16 md:w-32 h-1.5 md:h-2 rounded-full overflow-hidden ${theme === 'dark' ? 'bg-border' : 'bg-gray-300'}`}>
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${progress}%` }}
                data-testid="progress-bar"
              />
            </div>
            <span
              className={`text-xs md:text-sm font-medium ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}
              data-testid="progress-text"
            >
              {progress}%
            </span>
          </div>
        </div>

        {/* 主题切换按钮 */}
        <button
          onClick={onToggleTheme}
          className={`h-8 w-8 md:h-9 md:w-9 rounded-lg flex items-center justify-center transition-all duration-200 active:scale-95 touch-manipulation ${
            theme === 'dark'
              ? 'bg-bg-elevated hover:bg-border'
              : 'bg-gray-200 hover:bg-gray-300'
          }`}
          title={theme === 'dark' ? '切换到亮色主题' : '切换到暗色主题'}
          aria-label={theme === 'dark' ? '切换到亮色主题' : '切换到暗色主题'}
          data-testid="theme-toggle"
        >
          {theme === 'dark' ? (
            <Sun className="h-3.5 w-3.5 md:h-4 md:w-4 text-text-secondary transition-transform hover:rotate-180 duration-300" />
          ) : (
            <Moon className="h-3.5 w-3.5 md:h-4 md:w-4 text-gray-600 transition-transform hover:-rotate-12 duration-300" />
          )}
        </button>

        {/* 用户头像占位 - 移动端隐藏 */}
        <div className={`h-7 w-7 md:h-8 md:w-8 rounded-full hidden sm:flex items-center justify-center text-xs ${
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
