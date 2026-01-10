/**
 * MessageActions 组件
 * AI消息的交互按钮（重新生成、复制）
 */

import { useState } from 'react';
import { Copy, RefreshCw, Check } from 'lucide-react';

interface MessageActionsProps {
  content: string;
  onRegenerate: () => void;
  isRegenerating: boolean;
  theme: 'light' | 'dark';
}

export function MessageActions({
  content,
  onRegenerate,
  isRegenerating,
  theme
}: MessageActionsProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  return (
    <div className="flex items-center gap-1 mt-2 pt-2 border-t border-current/10">
      <button
        onClick={handleCopy}
        disabled={copied}
        className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-all hover:scale-105 active:scale-95 ${
          copied
            ? theme === 'dark'
              ? 'bg-green-500/20 text-green-400'
              : 'bg-green-100 text-green-600'
            : theme === 'dark'
              ? 'hover:bg-bg-dark text-text-muted hover:text-text-primary'
              : 'hover:bg-gray-200 text-gray-500 hover:text-gray-700'
        }`}
        aria-label={copied ? '已复制' : '复制消息'}
        title={copied ? '已复制' : '复制消息'}
      >
        {copied ? (
          <>
            <Check className="h-3 w-3" />
            <span>已复制</span>
          </>
        ) : (
          <>
            <Copy className="h-3 w-3" />
            <span className="hidden sm:inline">复制</span>
          </>
        )}
      </button>

      <button
        onClick={onRegenerate}
        disabled={isRegenerating}
        className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-all hover:scale-105 active:scale-95 ${
          isRegenerating
            ? theme === 'dark'
              ? 'opacity-50 cursor-not-allowed text-text-muted'
              : 'opacity-50 cursor-not-allowed text-gray-400'
            : theme === 'dark'
              ? 'hover:bg-bg-dark text-text-muted hover:text-text-primary'
              : 'hover:bg-gray-200 text-gray-500 hover:text-gray-700'
        }`}
        aria-label="重新生成"
        title="重新生成回答"
      >
        <RefreshCw className={`h-3 w-3 ${isRegenerating ? 'animate-spin' : ''}`} />
        <span className="hidden sm:inline">
          {isRegenerating ? '生成中...' : '重新生成'}
        </span>
      </button>
    </div>
  );
}
