/**
 * CodeBlock 组件
 * 带复制按钮的代码块
 */

import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface CodeBlockProps {
  children: React.ReactNode;
  inline?: boolean;
  className?: string;
  theme: 'light' | 'dark';
}

export function CodeBlock({ children, inline, className, theme }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  // 提取语言标识符
  const match = /language-(\w+)/.exec(className || '');
  const language = match ? match[1] : '';

  // 获取代码内容
  const codeContent = String(children).replace(/\n$/, '');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codeContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy code:', error);
    }
  };

  // 内联代码（不需要复制按钮）
  if (inline) {
    return (
      <code
        className={`px-1 py-0.5 rounded text-xs font-mono ${
          theme === 'dark' ? 'bg-bg-dark text-primary' : 'bg-gray-200 text-primary'
        }`}
      >
        {children}
      </code>
    );
  }

  // 代码块（带复制按钮）
  return (
    <div className="relative group my-1">
      {/* 语言标签和复制按钮 */}
      <div
        className={`flex items-center justify-between px-3 py-1 text-xs rounded-t ${
          theme === 'dark'
            ? 'bg-bg-dark/50 text-text-muted border-b border-border/50'
            : 'bg-gray-100/50 text-gray-500 border-b border-gray-300/50'
        }`}
      >
        <span className="font-mono">{language || 'code'}</span>
        <button
          onClick={handleCopy}
          className={`flex items-center gap-1 px-2 py-0.5 rounded transition-all opacity-0 group-hover:opacity-100 md:opacity-100 hover:scale-105 active:scale-95 ${
            copied
              ? theme === 'dark'
                ? 'bg-green-500/20 text-green-400'
                : 'bg-green-100 text-green-600'
              : theme === 'dark'
                ? 'hover:bg-bg-elevated text-text-muted hover:text-text-primary'
                : 'hover:bg-gray-200 text-gray-500 hover:text-gray-700'
          }`}
          aria-label={copied ? '已复制' : '复制代码'}
          title={copied ? '已复制' : '复制代码'}
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
      </div>

      {/* 代码内容 */}
      <div
        className={`p-3 rounded-b overflow-x-auto ${
          theme === 'dark' ? 'bg-bg-dark' : 'bg-gray-200'
        }`}
      >
        <code
          className={`block text-xs font-mono ${
            theme === 'dark' ? 'text-text-secondary' : 'text-gray-800'
          }`}
        >
          {children}
        </code>
      </div>
    </div>
  );
}
