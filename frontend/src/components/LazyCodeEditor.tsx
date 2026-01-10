import { lazy, Suspense, useState, useEffect, useCallback } from 'react';
import type { CodeEditorProps } from './CodeEditor';
import { SimpleMobileEditor } from './SimpleMobileEditor';

// 懒加载 Monaco Editor 组件
const CodeEditor = lazy(() =>
  import(/* webpackChunkName: "code-editor" */ './CodeEditor').then(module => ({
    default: module.CodeEditor,
  }))
);

// 检测移动设备
function isMobileDevice(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;
}

// 网络感知：检测网络连接质量
function getNetworkQuality(): 'fast' | 'slow' | 'unknown' {
  const nav = navigator as any;
  const connection = nav.connection || nav.mozConnection || nav.webkitConnection;

  if (!connection) return 'unknown';

  // 检查有效连接类型
  const effectiveType = connection.effectiveType;
  if (effectiveType === '4g' || effectiveType === 'wifi') {
    return 'fast';
  } else if (effectiveType === '3g' || effectiveType === '2g' || effectiveType === 'slow-2g') {
    return 'slow';
  }

  return 'unknown';
}

/**
 * 代码编辑器骨架屏组件
 * 在 Monaco Editor 加载时显示
 */
function CodeEditorSkeleton({ theme = 'dark', isMobile = false }: { theme?: 'light' | 'dark'; isMobile?: boolean }) {
  const bgClass = theme === 'dark' ? 'bg-[#1e1e1e]' : 'bg-white';
  const borderClass = theme === 'dark' ? 'border-gray-700' : 'border-gray-200';
  const lineClass = theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200';
  const textClass = theme === 'dark' ? 'text-gray-400' : 'text-gray-500';

  return (
    <div className={`h-full w-full ${bgClass} ${borderClass} border rounded-md overflow-hidden`}>
      {/* 编辑器工具栏骨架 */}
      <div className={`flex items-center justify-between px-4 py-2 ${borderClass} border-b`}>
        <div className="flex gap-2">
          <div className={`w-20 h-6 ${lineClass} rounded animate-pulse`} />
          <div className={`w-16 h-6 ${lineClass} rounded animate-pulse`} />
        </div>
        <div className={`w-24 h-6 ${lineClass} rounded animate-pulse`} />
      </div>

      {/* 代码区域骨架 */}
      <div className="p-4 space-y-2">
        {/* 行号和代码行 */}
        {[...Array(isMobile ? 8 : 15)].map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            {/* 行号 */}
            <div className={`w-6 h-4 ${lineClass} rounded opacity-50 animate-pulse`} style={{ animationDelay: `${i * 50}ms` }} />
            {/* 代码行 */}
            <div
              className={`h-4 ${lineClass} rounded animate-pulse`}
              style={{
                width: `${Math.random() * 40 + 40}%`,
                animationDelay: `${i * 50}ms`,
              }}
            />
          </div>
        ))}
      </div>

      {/* 加载提示 */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className={`flex flex-col items-center gap-3 px-6 py-4 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-50'} ${borderClass} border shadow-lg`}>
          {/* 加载动画 */}
          <div className="relative">
            <div className="w-10 h-10 border-4 border-gray-600 border-t-blue-500 rounded-full animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 3.5a1 1 0 011 1V8h3.5a1 1 0 110 2H11v3.5a1 1 0 11-2 0V10H5.5a1 1 0 110-2H9V4.5a1 1 0 011-1z" />
              </svg>
            </div>
          </div>

          {/* 加载文本 */}
          <div className="text-center">
            <p className={`text-sm font-medium ${textClass}`}>加载代码编辑器...</p>
            {isMobile && (
              <p className={`text-xs ${textClass} mt-1 opacity-75`}>移动端首次加载可能需要几秒钟</p>
            )}
          </div>

          {/* 加载进度条 */}
          <div className={`w-32 h-1 ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-300'} rounded-full overflow-hidden`}>
            <div className="h-full bg-blue-500 rounded-full animate-loading-progress" />
          </div>
        </div>
      </div>

      {/* CSS 动画 */}
      <style>{`
        @keyframes loading-progress {
          0% {
            width: 0%;
            margin-left: 0%;
          }
          50% {
            width: 50%;
            margin-left: 25%;
          }
          100% {
            width: 0%;
            margin-left: 100%;
          }
        }
        .animate-loading-progress {
          animation: loading-progress 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}

/**
 * 懒加载的代码编辑器组件 - Phase 1 移动端优化版
 *
 * 性能优化策略:
 * 1. 移动端优先使用 SimpleMobileEditor (< 5KB)
 * 2. 2秒后或用户主动点击时加载完整 Monaco Editor
 * 3. 网络感知：慢速网络延长加载时间
 * 4. 桌面端立即加载 Monaco Editor
 *
 * 预期效果:
 * - 移动端首屏加载时间 < 1.5s
 * - LCP 改善 2-3 秒
 * - FCP 改善 1-2 秒
 * - 初始包大小减少 ~12MB
 */
export function LazyCodeEditor(props: CodeEditorProps) {
  const [useFullEditor, setUseFullEditor] = useState(false);
  const [autoUpgradeTimer, setAutoUpgradeTimer] = useState<NodeJS.Timeout | null>(null);
  const isMobile = isMobileDevice();
  const networkQuality = getNetworkQuality();

  // 移动端：延迟加载策略
  useEffect(() => {
    if (!isMobile || useFullEditor) {
      return;
    }

    // 根据网络质量决定延迟时间
    const delayTime = networkQuality === 'slow' ? 5000 : 2000;

    // 设置自动升级定时器
    const timer = setTimeout(() => {
      setUseFullEditor(true);
    }, delayTime);

    setAutoUpgradeTimer(timer);

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isMobile, networkQuality, useFullEditor]);

  // 用户主动升级到完整编辑器
  const handleUpgradeToFull = useCallback(() => {
    if (autoUpgradeTimer) {
      clearTimeout(autoUpgradeTimer);
    }
    setUseFullEditor(true);
  }, [autoUpgradeTimer]);

  // 桌面端：直接使用 Monaco Editor
  if (!isMobile) {
    return (
      <Suspense fallback={<CodeEditorSkeleton theme={props.theme} isMobile={false} />}>
        <CodeEditor {...props} />
      </Suspense>
    );
  }

  // 移动端：根据状态选择编辑器
  if (useFullEditor) {
    return (
      <Suspense fallback={<CodeEditorSkeleton theme={props.theme} isMobile={true} />}>
        <CodeEditor {...props} />
      </Suspense>
    );
  }

  // 移动端：使用轻量级编辑器
  return (
    <SimpleMobileEditor
      {...props}
      onUpgradeToFull={handleUpgradeToFull}
    />
  );
}

// 添加 displayName 以支持 React Fast Refresh
LazyCodeEditor.displayName = 'LazyCodeEditor';
