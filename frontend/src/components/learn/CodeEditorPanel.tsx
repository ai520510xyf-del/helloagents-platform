/**
 * CodeEditorPanel 组件
 * 中间代码编辑器面板，包含文件标签栏、编辑器和操作栏
 */

import { Play, StopCircle, RotateCcw } from 'lucide-react';
import { CodeEditor } from '../CodeEditor';
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

export function CodeEditorPanel({
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
  return (
    <div className={`h-full grid grid-rows-[auto_1fr_auto] ${theme === 'dark' ? 'bg-bg-dark' : 'bg-white'}`}>
      {/* 文件标签栏 */}
      <div className={`h-10 border-b flex items-center px-4 gap-2 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}>
        <div className={`flex items-center gap-2 px-3 py-1 border-t-2 border-primary text-sm ${theme === 'dark' ? 'bg-bg-dark' : 'bg-white'}`}>
          <span>lesson_{currentLesson.id.replace('.', '_')}.py</span>
        </div>
      </div>

      {/* Monaco Editor */}
      <div className="overflow-hidden min-h-0">
        <CodeEditor
          value={code}
          onChange={(value) => onCodeChange(value || '')}
          onCursorChange={onCursorChange}
          language="python"
          height="100%"
          theme={theme}
        />
      </div>

      {/* 操作栏 */}
      <div className={`h-14 border-t flex items-center justify-between px-4 ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}>
        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={onRun}
            isLoading={isRunning}
            disabled={isRunning}
          >
            <Play className="h-4 w-4 mr-1" />
            运行代码
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={onStop}
            disabled={!isRunning}
          >
            <StopCircle className="h-4 w-4 mr-1" />
            停止
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={onReset}
            className={theme === 'dark' ? '' : 'border-gray-300 hover:bg-gray-100 text-gray-700'}
          >
            <RotateCcw className="h-4 w-4 mr-1" />
            重置
          </Button>
        </div>

        <div className={`text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
          行 {cursorPosition.line}, 列 {cursorPosition.column}
        </div>
      </div>
    </div>
  );
}
