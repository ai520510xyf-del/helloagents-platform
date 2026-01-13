/**
 * OptimizedMarkdown - 优化的 Markdown 渲染组件
 *
 * 性能优化策略:
 * 1. 懒加载 react-markdown (仅在需要时加载)
 * 2. 使用 React.memo 避免不必要的重渲染
 * 3. 骨架屏提供更好的加载体验
 * 4. 直接导入插件，避免类型问题
 */

import { lazy, Suspense, memo } from 'react';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

// 懒加载 Markdown 组件
const ReactMarkdown = lazy(() =>
  import('react-markdown').then(mod => ({ default: mod.default }))
);

interface OptimizedMarkdownProps {
  children: string;
  className?: string;
  theme?: 'light' | 'dark';
  enableGfm?: boolean;
  enableHtml?: boolean;
}

/**
 * Markdown 加载骨架屏
 */
function MarkdownSkeleton({ theme = 'dark' }: { theme?: 'light' | 'dark' }) {
  const bgClass = theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100';
  const lineClass = theme === 'dark' ? 'bg-gray-700' : 'bg-gray-300';

  return (
    <div className={`p-4 space-y-3 ${bgClass} rounded-lg animate-pulse`}>
      {/* 标题 */}
      <div className={`h-6 ${lineClass} rounded w-2/3`} />

      {/* 段落 */}
      <div className="space-y-2">
        <div className={`h-4 ${lineClass} rounded w-full`} />
        <div className={`h-4 ${lineClass} rounded w-5/6`} />
        <div className={`h-4 ${lineClass} rounded w-4/5`} />
      </div>

      {/* 列表 */}
      <div className="space-y-2 pl-4">
        <div className={`h-4 ${lineClass} rounded w-full`} />
        <div className={`h-4 ${lineClass} rounded w-3/4`} />
        <div className={`h-4 ${lineClass} rounded w-4/5`} />
      </div>

      {/* 代码块 */}
      <div className={`h-24 ${lineClass} rounded w-full`} />
    </div>
  );
}

/**
 * 延迟加载的 Markdown 组件包装器
 */
function MarkdownRenderer({
  children,
  className,
  enableGfm = true,
  enableHtml = false,
}: OptimizedMarkdownProps) {
  return (
    <Suspense fallback={<MarkdownSkeleton />}>
      <div className={className}>
        <ReactMarkdown
          remarkPlugins={enableGfm ? [remarkGfm] : []}
          rehypePlugins={enableHtml ? [rehypeRaw] : []}
        >
          {children}
        </ReactMarkdown>
      </div>
    </Suspense>
  );
}

/**
 * 优化的 Markdown 组件 (使用 memo)
 */
export const OptimizedMarkdown = memo(
  MarkdownRenderer,
  (prevProps, nextProps) => {
    // 仅在内容或关键属性变化时重新渲染
    return (
      prevProps.children === nextProps.children &&
      prevProps.theme === nextProps.theme &&
      prevProps.className === nextProps.className
    );
  }
);

OptimizedMarkdown.displayName = 'OptimizedMarkdown';

/**
 * 简化版 Markdown (用于小文本，无需完整功能)
 */
export const SimpleMarkdown = memo(({ children, className }: { children: string; className?: string }) => {
  // 简单的 Markdown 转换 (支持基本语法)
  const processSimpleMarkdown = (text: string) => {
    return text
      // 标题
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      // 粗体和斜体
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // 链接
      .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
      // 换行
      .replace(/\n/g, '<br />');
  };

  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: processSimpleMarkdown(children) }}
    />
  );
});

SimpleMarkdown.displayName = 'SimpleMarkdown';
