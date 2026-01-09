/**
 * TerminalOutput 组件
 * 底部终端输出面板
 * 增强版：更好的视觉反馈、状态指示、错误高亮
 */

import { Terminal, Trash2, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { useMemo } from 'react';

interface TerminalOutputProps {
  output: string;
  isRunning: boolean;
  theme: 'light' | 'dark';
  onClear: () => void;
}

export function TerminalOutput({ output, isRunning, theme, onClear }: TerminalOutputProps) {
  // 分析输出内容，检测是否有错误
  const hasError = useMemo(() => {
    return output.toLowerCase().includes('error') ||
           output.toLowerCase().includes('traceback') ||
           output.toLowerCase().includes('exception');
  }, [output]);

  const hasSuccess = useMemo(() => {
    return output && !hasError && !isRunning;
  }, [output, hasError, isRunning]);

  return (
    <div className={`h-full border-t flex flex-col ${theme === 'dark' ? 'bg-bg-dark border-border' : 'bg-white border-gray-200'}`}>
      {/* 头部栏 */}
      <div className={`h-10 md:h-12 flex items-center justify-between px-3 md:px-4 border-b ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-gray-100 border-gray-200'}`}>
        <div className={`flex items-center gap-2 text-xs md:text-sm ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>
          <Terminal className="h-4 w-4 text-primary" />
          <span className="font-medium">终端输出</span>

          {/* 运行状态指示器 */}
          {isRunning && (
            <span className="flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full bg-warning/10 text-warning border border-warning/20">
              <span className="h-2 w-2 rounded-full bg-warning animate-pulse" />
              运行中
            </span>
          )}

          {/* 成功指示器 */}
          {hasSuccess && (
            <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-success/10 text-success border border-success/20">
              <CheckCircle className="h-3 w-3" />
              <span className="hidden sm:inline">执行成功</span>
            </span>
          )}

          {/* 错误指示器 */}
          {hasError && !isRunning && (
            <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-error/10 text-error border border-error/20">
              <XCircle className="h-3 w-3" />
              <span className="hidden sm:inline">执行失败</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            disabled={!output}
            className="text-xs touch-manipulation"
            data-testid="clear-button"
            aria-label="清空输出"
          >
            <Trash2 className="h-3.5 w-3.5 md:mr-1" />
            <span className="hidden md:inline">清空</span>
          </Button>
        </div>
      </div>

      {/* 输出内容区域 */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 md:p-4 font-mono text-xs md:text-sm" data-testid="terminal-output">
        {output ? (
          <pre className={`whitespace-pre-wrap leading-relaxed ${
            hasError
              ? 'text-error'
              : theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'
          }`}>
            {output}
          </pre>
        ) : (
          <div className={`flex flex-col items-center justify-center h-full text-center py-8 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
            <Terminal className={`h-10 w-10 mb-3 opacity-30 ${theme === 'dark' ? 'text-text-muted' : 'text-gray-400'}`} />
            <p className="text-sm font-medium mb-1">等待代码执行</p>
            <p className="text-xs">
              点击 &quot;运行代码&quot; 按钮开始执行
              <span className="hidden md:inline"> • 快捷键: Cmd/Ctrl + Enter</span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
