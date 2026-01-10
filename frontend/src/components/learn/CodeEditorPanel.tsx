/**
 * CodeEditorPanel 组件
 * 中间代码编辑器面板，包含文件标签栏、编辑器和操作栏
 *
 * 性能优化：
 * - 使用 React.memo 避免不必要的重渲染
 * - 仅在关键属性变化时更新
 *
 * 可访问性优化：
 * - 完整的 ARIA 标签和地标区域
 * - 键盘导航支持（Tab, Enter, Space, Escape）
 * - 屏幕阅读器友好
 * - WCAG 2.1 AA 标准
 */

import { memo, useEffect } from 'react';
import { Play, StopCircle, RotateCcw } from 'lucide-react';
import { LazyCodeEditor } from '../LazyCodeEditor';
import { Button } from '../ui/Button';
import { type Lesson } from '../../data/courses';

interface CodeEditorPanelProps {
  code: string;
  onCodeChange: (code: string) => void;
  cursorPosition: { line: number; column: number };
  onCursorChange: (position: { line: number; column: number }) => void;
  currentLesson: Lesson;
  theme: 'light' | 'dark';
  isRunning: boolean;
  onRun: () => void;
  onStop: () => void;
  onReset: () => void;
}

export const CodeEditorPanel = memo(function CodeEditorPanel({
  code,
  onCodeChange,
  cursorPosition,
  onCursorChange,
  currentLesson,
  theme,
  isRunning,
  onRun,
  onStop,
  onReset
}: CodeEditorPanelProps) {
  // 键盘快捷键支持
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Enter: 运行代码
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !isRunning) {
        e.preventDefault();
        onRun();
      }

      // Escape: 停止运行
      if (e.key === 'Escape' && isRunning) {
        e.preventDefault();
        onStop();
      }

      // Ctrl/Cmd + R: 重置代码
      if ((e.ctrlKey || e.metaKey) && e.key === 'r' && !isRunning) {
        e.preventDefault();
        onReset();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isRunning, onRun, onStop, onReset]);

  return (
    <div
      className={`h-full grid grid-rows-[auto_1fr_auto] ${theme === 'dark' ? 'bg-bg-dark' : 'bg-white'}`}
      role="main"
      aria-label="代码编辑器面板"
    >
      {/* 屏幕阅读器辅助说明 */}
      <div className="sr-only" role="region" aria-label="键盘快捷键说明">
        <h2>键盘快捷键</h2>
        <ul>
          <li>Ctrl + Enter 或 Command + Enter: 运行代码</li>
          <li>Escape: 停止运行</li>
          <li>Ctrl + R 或 Command + R: 重置代码</li>
          <li>Tab: 在控件间切换</li>
        </ul>
      </div>

      {/* 文件标签栏 */}
      <div
        className={`h-10 border-b flex items-center px-4 gap-2 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}
        role="tablist"
        aria-label="代码文件标签"
      >
        <div
          className={`flex items-center gap-2 px-3 py-1 border-t-2 border-primary text-sm ${theme === 'dark' ? 'bg-bg-dark' : 'bg-white'}`}
          role="tab"
          aria-selected="true"
          aria-label={`当前文件：lesson_${currentLesson.id.replace('.', '_')}.py`}
        >
          <span>lesson_{currentLesson.id.replace('.', '_')}.py</span>
        </div>
      </div>

      {/* Monaco Editor (Lazy Loaded) */}
      <div
        className="overflow-hidden min-h-0"
        role="region"
        aria-label="代码编辑区域"
      >
        <LazyCodeEditor
          value={code}
          onChange={(value) => onCodeChange(value || '')}
          onCursorChange={onCursorChange}
          language="python"
          height="100%"
          theme={theme}
        />
      </div>

      {/* 操作栏 */}
      <div
        className={`h-14 border-t flex items-center justify-between px-4 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}
        role="toolbar"
        aria-label="代码操作工具栏"
      >
        <div className="flex items-center gap-2" role="group" aria-label="代码执行控制">
          <Button
            variant="primary"
            size="sm"
            onClick={onRun}
            isLoading={isRunning}
            disabled={isRunning}
            data-testid="run-button"
            aria-label={isRunning ? "代码运行中" : "运行代码"}
          >
            <Play className="h-4 w-4 mr-1" aria-hidden="true" />
            运行代码
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={onStop}
            disabled={!isRunning}
            data-testid="stop-button"
            aria-label="停止代码执行"
          >
            <StopCircle className="h-4 w-4 mr-1" aria-hidden="true" />
            停止
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={onReset}
            className={theme === 'dark' ? '' : 'border-gray-300 hover:bg-gray-100 text-gray-700'}
            data-testid="reset-button"
            aria-label="重置代码到初始状态"
          >
            <RotateCcw className="h-4 w-4 mr-1" aria-hidden="true" />
            重置
          </Button>
        </div>

        <div
          className={`text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}
          data-testid="cursor-position"
          role="status"
          aria-live="polite"
          aria-label={`光标位置：第 ${cursorPosition.line} 行，第 ${cursorPosition.column} 列`}
        >
          行 {cursorPosition.line}, 列 {cursorPosition.column}
        </div>
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  // 仅在关键属性变化时重新渲染
  return (
    prevProps.code === nextProps.code &&
    prevProps.theme === nextProps.theme &&
    prevProps.isRunning === nextProps.isRunning &&
    prevProps.currentLesson.id === nextProps.currentLesson.id &&
    prevProps.cursorPosition.line === nextProps.cursorPosition.line &&
    prevProps.cursorPosition.column === nextProps.cursorPosition.column
  );
});
