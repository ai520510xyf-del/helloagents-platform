/**
 * Loading - 通用加载组件
 *
 * 用于页面/组件懒加载时的占位显示
 * 支持不同尺寸和主题
 */

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  fullScreen?: boolean;
  theme?: 'light' | 'dark';
}

export function Loading({
  size = 'md',
  text = '加载中...',
  fullScreen = false,
  theme = 'dark',
}: LoadingProps) {
  const sizeClasses = {
    sm: 'h-6 w-6 border-2',
    md: 'h-10 w-10 border-3',
    lg: 'h-16 w-16 border-4',
  };

  const containerClasses = fullScreen
    ? 'fixed inset-0 flex items-center justify-center z-50'
    : 'flex items-center justify-center w-full h-full min-h-[200px]';

  const bgClasses = theme === 'dark'
    ? 'bg-bg-dark text-text-secondary'
    : 'bg-white text-gray-600';

  const spinnerClasses = theme === 'dark'
    ? 'border-primary border-t-transparent'
    : 'border-blue-600 border-t-transparent';

  return (
    <div className={`${containerClasses} ${bgClasses}`}>
      <div className="flex flex-col items-center gap-4">
        {/* 旋转加载器 */}
        <div
          className={`animate-spin rounded-full ${sizeClasses[size]} ${spinnerClasses}`}
          role="status"
          aria-label="加载中"
        />

        {/* 加载文本 */}
        {text && (
          <p className="text-sm font-medium animate-pulse">
            {text}
          </p>
        )}
      </div>
    </div>
  );
}

/**
 * PageLoading - 全屏页面加载组件
 * 用于路由级别的懒加载
 */
export function PageLoading({ theme = 'dark' }: Pick<LoadingProps, 'theme'>) {
  return (
    <Loading
      size="lg"
      text="正在加载页面..."
      fullScreen
      theme={theme}
    />
  );
}

/**
 * ComponentLoading - 组件级加载
 * 用于组件懒加载
 */
export function ComponentLoading({ theme = 'dark' }: Pick<LoadingProps, 'theme'>) {
  return (
    <Loading
      size="md"
      text="正在加载..."
      fullScreen={false}
      theme={theme}
    />
  );
}

/**
 * InlineLoading - 行内加载器
 * 用于按钮或小区域
 */
export function InlineLoading({ theme = 'dark' }: Pick<LoadingProps, 'theme'>) {
  return (
    <Loading
      size="sm"
      text=""
      fullScreen={false}
      theme={theme}
    />
  );
}

// 添加 displayName
Loading.displayName = 'Loading';
PageLoading.displayName = 'PageLoading';
ComponentLoading.displayName = 'ComponentLoading';
InlineLoading.displayName = 'InlineLoading';
