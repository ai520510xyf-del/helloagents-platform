/**
 * TerminalOutput 组件
 * 底部终端输出面板
 */

import { Button } from '../ui/Button';

interface TerminalOutputProps {
  output: string;
  isRunning: boolean;
  theme: 'light' | 'dark';
  onClear: () => void;
}

export function TerminalOutput({ output, isRunning, theme, onClear }: TerminalOutputProps) {
  return (
    <div className={`h-full border-t flex flex-col ${theme === 'dark' ? 'bg-bg-dark border-border' : 'bg-white border-gray-200'}`}>
      <div className={`h-10 flex items-center justify-between px-4 border-b ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}>
        <div className={`flex items-center gap-2 text-sm ${theme === 'dark' ? '' : 'text-gray-900'}`}>
          <span>📟</span>
          <span className="font-medium">终端输出</span>
          {isRunning && (
            <span className="text-xs text-warning flex items-center gap-1">
              <span className="animate-pulse">⏳</span>
              运行中
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            className="text-xs"
            data-testid="clear-button"
          >
            清空
          </Button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 font-mono text-sm" data-testid="terminal-output">
        {output ? (
          <pre className={`whitespace-pre-wrap ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>{output}</pre>
        ) : (
          <div className={`text-center py-8 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
            点击 "运行代码" 按钮开始执行 • 快捷键: Cmd/Ctrl + Enter
          </div>
        )}
      </div>
    </div>
  );
}
