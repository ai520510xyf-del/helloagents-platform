# UI/UX 改进方案 - 代码示例

本文档包含关键改进方案的代码实现示例。

---

## 目录

1. [可访问性增强](#可访问性增强)
2. [Onboarding 引导系统](#onboarding-引导系统)
3. [AI 助手交互优化](#ai-助手交互优化)
4. [空状态和错误状态](#空状态和错误状态)
5. [键盘导航增强](#键盘导航增强)

---

## 可访问性增强

### 1. 增强型 AI 聊天输入框

```typescript
// frontend/src/components/learn/AccessibleChatInput.tsx

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '../ui/Button';

interface AccessibleChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
  theme: 'light' | 'dark';
  maxChars?: number;
}

export function AccessibleChatInput({
  value,
  onChange,
  onSend,
  isLoading,
  theme,
  maxChars = 500,
}: AccessibleChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [inputError, setInputError] = useState<string | null>(null);

  // 自动调整 textarea 高度
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [value]);

  // 移动端虚拟键盘适配
  useEffect(() => {
    const handleResize = () => {
      if (textareaRef.current && document.activeElement === textareaRef.current) {
        textareaRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;

    if (newValue.length <= maxChars) {
      onChange(newValue);
      setInputError(null);
    } else {
      setInputError(`最多输入 ${maxChars} 个字符`);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter 发送，Shift+Enter 换行
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      if (value.trim()) {
        onSend();
      }
    }
    // Escape 清空输入
    else if (e.key === 'Escape') {
      onChange('');
      setInputError(null);
    }
  };

  const isNearLimit = value.length > maxChars * 0.9;
  const canSend = value.trim().length > 0 && !isLoading;

  return (
    <div className={`p-4 border-t ${theme === 'dark' ? 'border-border' : 'border-gray-200'}`}>
      <div className="flex flex-col gap-2">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="输入你的问题..."
          rows={1}
          maxLength={maxChars}
          disabled={isLoading}
          // ✅ 可访问性属性
          aria-label="AI助手聊天输入框"
          aria-describedby="char-count chat-hint"
          aria-invalid={inputError ? 'true' : 'false'}
          aria-errormessage={inputError ? 'input-error' : undefined}
          className={`
            flex-1 px-3 py-2 border rounded text-sm resize-none
            focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20
            transition-all
            ${theme === 'dark'
              ? 'bg-bg-elevated border-border text-text-primary placeholder-text-muted'
              : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'
            }
            ${inputError ? 'border-error' : ''}
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          style={{ minHeight: '40px', maxHeight: '120px' }}
        />

        {/* 错误提示 */}
        {inputError && (
          <div
            id="input-error"
            role="alert"
            className="text-xs text-error"
          >
            {inputError}
          </div>
        )}

        {/* 底部栏 */}
        <div className="flex items-center justify-between">
          {/* 字数统计 */}
          <span
            id="char-count"
            aria-live="polite"
            className={`text-xs ${
              isNearLimit
                ? 'text-error font-medium'
                : theme === 'dark'
                ? 'text-text-muted'
                : 'text-gray-500'
            }`}
          >
            {value.length} / {maxChars}
          </span>

          <div className="flex items-center gap-2">
            {/* 提示文字 */}
            <span
              id="chat-hint"
              className={`text-xs hidden sm:inline ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}
            >
              Enter 发送，Shift+Enter 换行
            </span>

            {/* 发送按钮 */}
            <Button
              variant="primary"
              size="sm"
              onClick={onSend}
              disabled={!canSend}
              aria-label={isLoading ? '发送中' : '发送消息'}
              className="min-w-[80px]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-1.5" />
                  <span className="hidden sm:inline">发送中</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-1.5" />
                  <span className="hidden sm:inline">发送</span>
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 2. 状态公告组件（用于屏幕阅读器）

```typescript
// frontend/src/components/ui/LiveAnnouncer.tsx

import { useEffect, useState } from 'react';

interface LiveAnnouncerProps {
  message: string;
  priority?: 'polite' | 'assertive';
}

/**
 * LiveAnnouncer 组件
 * 用于向屏幕阅读器公告状态变化，对视障用户友好
 *
 * @example
 * <LiveAnnouncer message={isRunning ? '代码正在运行' : '代码执行完毕'} />
 */
export function LiveAnnouncer({ message, priority = 'polite' }: LiveAnnouncerProps) {
  const [announcement, setAnnouncement] = useState('');

  useEffect(() => {
    // 清空后重新设置，确保屏幕阅读器能捕获变化
    setAnnouncement('');
    const timer = setTimeout(() => {
      setAnnouncement(message);
    }, 100);

    return () => clearTimeout(timer);
  }, [message]);

  if (!announcement) return null;

  return (
    <div
      role="status"
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  );
}

// 使用示例
function CodeEditorPanel({ isRunning, output, ...props }: CodeEditorPanelProps) {
  return (
    <div>
      {/* 其他内容 */}

      {/* 代码执行状态公告 */}
      <LiveAnnouncer
        message={
          isRunning
            ? '代码正在运行，请稍候'
            : output
            ? '代码执行完毕，输出已显示在终端'
            : ''
        }
      />
    </div>
  );
}
```

### 3. Skip Links（跳转链接）

```typescript
// frontend/src/components/SkipLinks.tsx

interface SkipLinksProps {
  theme: 'light' | 'dark';
}

/**
 * SkipLinks 组件
 * 提供键盘导航快捷跳转，符合 WCAG 2.1 要求
 */
export function SkipLinks({ theme }: SkipLinksProps) {
  const links = [
    { href: '#main-content', label: '跳转到主内容' },
    { href: '#course-menu', label: '跳转到课程目录' },
    { href: '#code-editor', label: '跳转到代码编辑器' },
    { href: '#ai-assistant', label: '跳转到 AI 助手' },
  ];

  return (
    <nav aria-label="快捷导航" className="sr-only focus-within:not-sr-only">
      <ul className="fixed top-4 left-4 z-50 flex flex-col gap-2">
        {links.map((link) => (
          <li key={link.href}>
            <a
              href={link.href}
              className={`
                inline-block px-4 py-2 rounded font-medium text-sm
                focus:outline-none focus:ring-2 focus:ring-offset-2
                transition-all
                ${theme === 'dark'
                  ? 'bg-primary text-white focus:ring-primary'
                  : 'bg-primary text-white focus:ring-primary'
                }
                hover:bg-primary/90
              `}
            >
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}

// 在 LearnPage.tsx 中使用
export function LearnPage() {
  return (
    <>
      <SkipLinks theme={theme} />

      <div className="h-screen flex flex-col">
        {/* 添加 ID 用于跳转 */}
        <main id="main-content" className="flex-1">
          <nav id="course-menu">
            <CourseMenu ... />
          </nav>

          <section id="code-editor">
            <CodeEditorPanel ... />
          </section>

          <aside id="ai-assistant">
            <ContentPanel ... />
          </aside>
        </main>
      </div>
    </>
  );
}
```

---

## Onboarding 引导系统

### 1. 欢迎模态框

```typescript
// frontend/src/components/onboarding/WelcomeModal.tsx

import { Bot, BookOpen, Code, MessageCircle } from 'lucide-react';
import { Button } from '../ui/Button';

interface WelcomeModalProps {
  onStart: () => void;
  onSkip: () => void;
  theme: 'light' | 'dark';
}

export function WelcomeModal({ onStart, onSkip, theme }: WelcomeModalProps) {
  const steps = [
    {
      icon: BookOpen,
      title: '选择课程',
      description: '从左侧课程目录开始',
    },
    {
      icon: Code,
      title: '编写代码',
      description: '在中间编辑器中实践',
    },
    {
      icon: MessageCircle,
      title: 'AI 助手',
      description: '遇到问题随时咨询 AI',
    },
  ];

  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="welcome-title"
    >
      <div
        className={`
          rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl border animate-scale-in
          ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-white border-gray-200'}
        `}
      >
        {/* 顶部 */}
        <div className="text-center mb-6">
          <div className="h-20 w-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Bot className="h-10 w-10 text-primary" />
          </div>
          <h2
            id="welcome-title"
            className={`text-2xl font-bold mb-2 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}
          >
            欢迎来到 HelloAgents
          </h2>
          <p className={`text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>
            一个交互式的 AI Agent 学习平台
          </p>
        </div>

        {/* 步骤列表 */}
        <div className="space-y-4 mb-6">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="flex items-start gap-3">
                <div className="h-10 w-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 pt-1">
                  <p className={`text-sm font-medium mb-0.5 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>
                    {step.title}
                  </p>
                  <p className={`text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* 底部按钮 */}
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={onSkip}
            className="flex-1"
            aria-label="跳过引导"
          >
            跳过
          </Button>
          <Button
            variant="primary"
            onClick={onStart}
            className="flex-1"
            aria-label="开始引导教程"
          >
            开始引导
          </Button>
        </div>
      </div>
    </div>
  );
}
```

### 2. 引导高亮组件

```typescript
// frontend/src/components/onboarding/OnboardingSpotlight.tsx

import { useEffect, useState } from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '../ui/Button';

interface OnboardingStep {
  target: string; // CSS selector
  title: string;
  description: string;
  placement: 'top' | 'bottom' | 'left' | 'right';
}

interface OnboardingSpotlightProps {
  steps: OnboardingStep[];
  currentStep: number;
  onNext: () => void;
  onPrevious: () => void;
  onFinish: () => void;
  onSkip: () => void;
  theme: 'light' | 'dark';
}

export function OnboardingSpotlight({
  steps,
  currentStep,
  onNext,
  onPrevious,
  onFinish,
  onSkip,
  theme,
}: OnboardingSpotlightProps) {
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

  const step = steps[currentStep];
  const isFirst = currentStep === 0;
  const isLast = currentStep === steps.length - 1;

  // 获取目标元素位置
  useEffect(() => {
    const targetElement = document.querySelector(step.target);
    if (targetElement) {
      const rect = targetElement.getBoundingClientRect();
      setTargetRect(rect);
      // 滚动到目标元素
      targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [step.target]);

  if (!targetRect) return null;

  // 计算提示框位置
  const getTooltipPosition = () => {
    const padding = 16;
    switch (step.placement) {
      case 'top':
        return {
          top: targetRect.top - 160 - padding,
          left: targetRect.left + targetRect.width / 2,
          transform: 'translateX(-50%)',
        };
      case 'bottom':
        return {
          top: targetRect.bottom + padding,
          left: targetRect.left + targetRect.width / 2,
          transform: 'translateX(-50%)',
        };
      case 'left':
        return {
          top: targetRect.top + targetRect.height / 2,
          left: targetRect.left - 320 - padding,
          transform: 'translateY(-50%)',
        };
      case 'right':
        return {
          top: targetRect.top + targetRect.height / 2,
          left: targetRect.right + padding,
          transform: 'translateY(-50%)',
        };
    }
  };

  const tooltipPosition = getTooltipPosition();

  return (
    <>
      {/* 遮罩层 */}
      <div
        className="fixed inset-0 z-40 pointer-events-none"
        style={{
          background: 'rgba(0, 0, 0, 0.7)',
          mask: `radial-gradient(
            circle at ${targetRect.left + targetRect.width / 2}px ${targetRect.top + targetRect.height / 2}px,
            transparent ${Math.max(targetRect.width, targetRect.height) / 2 + 10}px,
            black ${Math.max(targetRect.width, targetRect.height) / 2 + 20}px
          )`,
        }}
      />

      {/* 高亮边框 */}
      <div
        className="fixed z-50 pointer-events-none border-4 border-primary rounded-lg animate-pulse-glow"
        style={{
          top: targetRect.top - 4,
          left: targetRect.left - 4,
          width: targetRect.width + 8,
          height: targetRect.height + 8,
        }}
      />

      {/* 提示框 */}
      <div
        className={`
          fixed z-50 w-80 rounded-lg shadow-2xl border p-5 animate-scale-in
          ${theme === 'dark' ? 'bg-bg-surface border-border' : 'bg-white border-gray-200'}
        `}
        style={tooltipPosition}
        role="dialog"
        aria-labelledby="onboarding-title"
      >
        {/* 关闭按钮 */}
        <button
          onClick={onSkip}
          className={`absolute top-2 right-2 p-1 rounded hover:bg-bg-hover transition-colors`}
          aria-label="关闭引导"
        >
          <X className="h-4 w-4" />
        </button>

        {/* 标题 */}
        <h3
          id="onboarding-title"
          className={`text-lg font-semibold mb-2 pr-6 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}
        >
          {step.title}
        </h3>

        {/* 描述 */}
        <p className={`text-sm mb-4 ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>
          {step.description}
        </p>

        {/* 进度指示器 */}
        <div className="flex items-center gap-1.5 mb-4">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`h-1.5 rounded-full flex-1 transition-colors ${
                index === currentStep ? 'bg-primary' : 'bg-border'
              }`}
              aria-label={`步骤 ${index + 1}${index === currentStep ? ' (当前)' : ''}`}
            />
          ))}
        </div>

        {/* 按钮组 */}
        <div className="flex items-center justify-between">
          <span className={`text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
            {currentStep + 1} / {steps.length}
          </span>

          <div className="flex gap-2">
            {!isFirst && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onPrevious}
                aria-label="上一步"
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                上一步
              </Button>
            )}

            {isLast ? (
              <Button
                variant="primary"
                size="sm"
                onClick={onFinish}
                aria-label="完成引导"
              >
                完成
              </Button>
            ) : (
              <Button
                variant="primary"
                size="sm"
                onClick={onNext}
                aria-label="下一步"
              >
                下一步
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

// 使用示例
const onboardingSteps: OnboardingStep[] = [
  {
    target: '[data-testid="course-menu"]',
    title: '课程目录',
    description: '从这里选择你想学习的 Agent 课程，从基础到进阶，循序渐进',
    placement: 'right',
  },
  {
    target: '[data-testid="code-editor"]',
    title: '代码编辑器',
    description: '在这里编写和运行 Python 代码，实时查看执行结果',
    placement: 'top',
  },
  {
    target: '[data-testid="ai-tab"]',
    title: 'AI 学习助手',
    description: '遇到问题？点击这里与 AI 助手对话，获得即时帮助和代码分析',
    placement: 'bottom',
  },
  {
    target: '[data-testid="run-button"]',
    title: '运行代码',
    description: '编写好代码后，点击这里执行，查看终端输出',
    placement: 'top',
  },
];
```

---

## AI 助手交互优化

### 1. AI 消息组件（带复制功能）

```typescript
// frontend/src/components/learn/AIMessage.tsx

import { useState } from 'react';
import { Bot, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

interface AIMessageProps {
  content: string;
  timestamp: Date;
  theme: 'light' | 'dark';
}

export function AIMessage({ content, timestamp, theme }: AIMessageProps) {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="flex gap-3" role="article" aria-label="AI助手回复">
      {/* AI 头像 */}
      <div className="h-8 w-8 bg-ai/10 rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="h-4 w-4 text-ai" />
      </div>

      {/* 消息内容 */}
      <div className="flex-1 min-w-0">
        <div
          className={`rounded-lg p-3 ${
            theme === 'dark' ? 'bg-bg-elevated' : 'bg-gray-100'
          }`}
        >
          <div className={`prose prose-sm max-w-none ${theme === 'dark' ? 'prose-invert' : ''}`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={{
                // 代码块 - 添加复制按钮
                code: (props) => {
                  const { inline, children, className } = props;
                  const code = String(children).trim();

                  if (inline) {
                    return (
                      <code
                        className={`px-1.5 py-0.5 rounded text-xs font-mono ${
                          theme === 'dark' ? 'bg-bg-dark text-primary' : 'bg-gray-200 text-primary'
                        }`}
                      >
                        {children}
                      </code>
                    );
                  }

                  const language = className?.replace('language-', '');
                  const isCopied = copiedCode === code;

                  return (
                    <div className="relative group my-2">
                      {/* 语言标签 */}
                      {language && (
                        <div
                          className={`absolute top-2 left-2 px-2 py-0.5 rounded text-2xs font-medium ${
                            theme === 'dark' ? 'bg-bg-dark text-text-muted' : 'bg-gray-200 text-gray-600'
                          }`}
                        >
                          {language}
                        </div>
                      )}

                      {/* 复制按钮 */}
                      <button
                        onClick={() => handleCopyCode(code)}
                        className={`
                          absolute top-2 right-2 p-1.5 rounded opacity-0 group-hover:opacity-100
                          transition-opacity focus:opacity-100
                          ${theme === 'dark' ? 'bg-bg-dark/80 hover:bg-bg-dark' : 'bg-gray-200/80 hover:bg-gray-200'}
                        `}
                        aria-label={isCopied ? '已复制' : '复制代码'}
                      >
                        {isCopied ? (
                          <Check className="h-4 w-4 text-success" />
                        ) : (
                          <Copy className="h-4 w-4 text-text-muted" />
                        )}
                      </button>

                      {/* 代码内容 */}
                      <pre
                        className={`p-3 rounded overflow-x-auto text-xs font-mono ${
                          theme === 'dark' ? 'bg-bg-dark' : 'bg-gray-200'
                        }`}
                      >
                        <code className={className}>{children}</code>
                      </pre>
                    </div>
                  );
                },

                // 其他 Markdown 组件...
                p: ({ children }) => (
                  <p className={`mb-2 text-sm leading-relaxed ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className={`list-disc list-inside space-y-1 mb-2 text-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-700'}`}>
                    {children}
                  </ul>
                ),
                li: ({ children }) => <li className="ml-4">{children}</li>,
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </div>

        {/* 时间戳 */}
        <span className={`text-xs mt-1 block ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
          {formatTimestamp(timestamp)}
        </span>
      </div>
    </div>
  );
}
```

### 2. 打字机效果组件

```typescript
// frontend/src/components/learn/StreamingMessage.tsx

import { useState, useEffect } from 'react';
import { AIMessage } from './AIMessage';

interface StreamingMessageProps {
  content: string;
  timestamp: Date;
  theme: 'light' | 'dark';
  speed?: number; // 字符/秒
}

export function StreamingMessage({
  content,
  timestamp,
  theme,
  speed = 50, // 默认 50 字符/秒
}: StreamingMessageProps) {
  const [displayedContent, setDisplayedContent] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (displayedContent.length >= content.length) {
      setIsComplete(true);
      return;
    }

    const charsPerInterval = Math.ceil(speed / 50); // 每 20ms 显示的字符数
    const intervalMs = 20;

    const interval = setInterval(() => {
      setDisplayedContent((prev) => {
        const nextLength = Math.min(prev.length + charsPerInterval, content.length);
        return content.slice(0, nextLength);
      });
    }, intervalMs);

    return () => clearInterval(interval);
  }, [content, displayedContent.length, speed]);

  return (
    <div className="relative">
      <AIMessage content={displayedContent} timestamp={timestamp} theme={theme} />

      {/* 光标动画 */}
      {!isComplete && (
        <span className="inline-block w-1 h-4 bg-primary animate-pulse ml-1 align-middle" />
      )}
    </div>
  );
}
```

---

## 空状态和错误状态

### 1. AI 助手空状态

```typescript
// frontend/src/components/learn/EmptyChatState.tsx

import { Bot, Sparkles } from 'lucide-react';

interface EmptyChatStateProps {
  onStartChat: (query: string) => void;
  theme: 'light' | 'dark';
}

export function EmptyChatState({ onStartChat, theme }: EmptyChatStateProps) {
  const suggestions = [
    {
      icon: '💡',
      text: '解释核心概念',
      query: '请解释这一章的核心概念',
      color: 'text-yellow-500',
    },
    {
      icon: '🐛',
      text: '检查代码问题',
      query: '请帮我检查代码中的问题',
      color: 'text-red-500',
    },
    {
      icon: '🚀',
      text: '实现指导',
      query: '如何实现 ReAct 循环？',
      color: 'text-blue-500',
    },
    {
      icon: '📚',
      text: '学习资源',
      query: '有哪些推荐的学习资源？',
      color: 'text-green-500',
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center">
      {/* AI 图标 */}
      <div className="relative mb-6">
        <div className="h-20 w-20 bg-ai/10 rounded-full flex items-center justify-center animate-pulse-glow">
          <Bot className="h-10 w-10 text-ai" />
        </div>
        <Sparkles className="h-5 w-5 text-ai absolute -top-1 -right-1 animate-bounce-subtle" />
      </div>

      {/* 标题和描述 */}
      <h3 className={`text-xl font-bold mb-2 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>
        AI 学习助手已就绪
      </h3>
      <p className={`text-sm mb-8 max-w-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>
        我会根据当前课程内容和你的代码，为你提供个性化的学习建议和答疑
      </p>

      {/* 快速问题建议 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg mb-6">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onStartChat(suggestion.query)}
            className={`
              flex items-center gap-3 p-4 rounded-lg border transition-all text-left
              hover:scale-105 hover:shadow-lg active:scale-95
              ${theme === 'dark'
                ? 'bg-bg-elevated border-border hover:border-primary'
                : 'bg-white border-gray-200 hover:border-primary'
              }
            `}
            aria-label={`快速提问: ${suggestion.text}`}
          >
            <span className="text-2xl">{suggestion.icon}</span>
            <div className="flex-1">
              <span className={`text-sm font-medium ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>
                {suggestion.text}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* 提示 */}
      <div className={`flex items-center gap-2 text-xs ${theme === 'dark' ? 'text-text-muted' : 'text-gray-500'}`}>
        <Sparkles className="h-3 w-3" />
        <span>AI 助手可以访问你的代码和课程内容</span>
      </div>
    </div>
  );
}
```

### 2. 错误状态组件

```typescript
// frontend/src/components/learn/ErrorState.tsx

import { AlertCircle, RefreshCw, Wifi, Clock, Server } from 'lucide-react';
import { Button } from '../ui/Button';

interface ErrorStateProps {
  error: {
    type: 'network' | 'timeout' | 'server' | 'unknown';
    message?: string;
  };
  onRetry: () => void;
  theme: 'light' | 'dark';
}

export function ErrorState({ error, onRetry, theme }: ErrorStateProps) {
  const errorConfigs = {
    network: {
      icon: Wifi,
      title: '网络连接失败',
      description: '请检查你的网络连接，然后重试',
      color: 'text-error',
    },
    timeout: {
      icon: Clock,
      title: '请求超时',
      description: 'AI 助手响应时间过长，请稍后重试',
      color: 'text-warning',
    },
    server: {
      icon: Server,
      title: '服务器错误',
      description: '服务暂时不可用，我们正在修复，请稍后再试',
      color: 'text-error',
    },
    unknown: {
      icon: AlertCircle,
      title: '出现错误',
      description: error.message || '抱歉，出现了意外错误',
      color: 'text-error',
    },
  };

  const config = errorConfigs[error.type];
  const Icon = config.icon;

  return (
    <div
      className={`
        flex flex-col items-center justify-center p-8 rounded-lg border text-center
        ${theme === 'dark' ? 'bg-error/5 border-error/20' : 'bg-red-50 border-red-200'}
      `}
      role="alert"
      aria-live="assertive"
    >
      <div className={`h-16 w-16 rounded-full flex items-center justify-center mb-4 ${
        theme === 'dark' ? 'bg-error/10' : 'bg-red-100'
      }`}>
        <Icon className={`h-8 w-8 ${config.color}`} />
      </div>

      <h3 className={`text-lg font-semibold mb-2 ${theme === 'dark' ? 'text-text-primary' : 'text-gray-900'}`}>
        {config.title}
      </h3>

      <p className={`text-sm mb-6 max-w-sm ${theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'}`}>
        {config.description}
      </p>

      <Button
        variant="secondary"
        size="sm"
        onClick={onRetry}
        aria-label="重试操作"
      >
        <RefreshCw className="h-4 w-4 mr-1.5" />
        重试
      </Button>
    </div>
  );
}
```

---

## 键盘导航增强

### 1. 课程菜单键盘导航

```typescript
// frontend/src/components/learn/KeyboardNavigableCourseMenu.tsx

import { useState, useRef, useEffect } from 'react';
import { Check } from 'lucide-react';
import { type Lesson } from '../../data/courses';

interface KeyboardNavigableCourseMenuProps {
  lessons: Lesson[];
  currentLesson: Lesson;
  onLessonChange: (lessonId: string) => void;
  theme: 'light' | 'dark';
}

export function KeyboardNavigableCourseMenu({
  lessons,
  currentLesson,
  onLessonChange,
  theme,
}: KeyboardNavigableCourseMenuProps) {
  const [focusedIndex, setFocusedIndex] = useState(() =>
    lessons.findIndex((l) => l.id === currentLesson.id)
  );
  const itemRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex((prev) => Math.min(prev + 1, lessons.length - 1));
        break;

      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex((prev) => Math.max(prev - 1, 0));
        break;

      case 'Home':
        e.preventDefault();
        setFocusedIndex(0);
        break;

      case 'End':
        e.preventDefault();
        setFocusedIndex(lessons.length - 1);
        break;

      case 'Enter':
      case ' ':
        e.preventDefault();
        onLessonChange(lessons[focusedIndex].id);
        break;

      default:
        // 字母快捷键 - 跳转到以该字母开头的课程
        if (e.key.length === 1 && /[a-zA-Z0-9]/.test(e.key)) {
          const index = lessons.findIndex(
            (lesson, i) =>
              i > focusedIndex &&
              lesson.title.toLowerCase().startsWith(e.key.toLowerCase())
          );
          if (index !== -1) {
            setFocusedIndex(index);
          }
        }
        break;
    }
  };

  useEffect(() => {
    itemRefs.current[focusedIndex]?.focus();
  }, [focusedIndex]);

  return (
    <nav
      role="menu"
      aria-label="课程目录"
      onKeyDown={handleKeyDown}
      className="p-4 space-y-1"
    >
      {lessons.map((lesson, index) => {
        const isActive = lesson.id === currentLesson.id;
        const isFocused = index === focusedIndex;

        return (
          <button
            key={lesson.id}
            ref={(el) => (itemRefs.current[index] = el)}
            role="menuitem"
            tabIndex={isFocused ? 0 : -1}
            aria-current={isActive ? 'true' : undefined}
            onClick={() => onLessonChange(lesson.id)}
            className={`
              w-full text-left px-3 py-2 rounded-lg text-sm transition-all
              flex items-center justify-between gap-2
              ${isActive
                ? 'bg-primary text-white font-medium'
                : theme === 'dark'
                ? 'text-text-secondary hover:bg-bg-elevated hover:text-text-primary'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }
              ${isFocused ? 'ring-2 ring-primary ring-offset-2 ring-offset-bg-dark' : ''}
            `}
          >
            <span>{lesson.title}</span>
            {isActive && <Check className="h-4 w-4" />}
          </button>
        );
      })}
    </nav>
  );
}
```

---

## 总结

以上代码示例展示了关键的UI/UX改进方案实现：

1. **可访问性增强**: ARIA标签、键盘导航、屏幕阅读器支持
2. **Onboarding系统**: 欢迎模态框和引导高亮
3. **AI助手优化**: 复制功能、打字机效果、改进的输入框
4. **空状态/错误状态**: 友好的引导和错误处理
5. **键盘导航**: 完整的键盘操作支持

这些改进将显著提升用户体验和可访问性，使平台更加专业和易用。

---

**相关文档**:
- [UI/UX评审报告](./UI_UX_REVIEW_REPORT.md)
- [设计系统文档](./frontend/DESIGN_SYSTEM.md)
