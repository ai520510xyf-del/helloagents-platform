/**
 * LoadingSpinner 加载指示器组件
 * 提供多种尺寸和变体的加载动画
 */

import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/utils';

const spinnerVariants = cva(
  'animate-spin rounded-full border-2 border-current',
  {
    variants: {
      size: {
        xs: 'h-3 w-3 border',
        sm: 'h-4 w-4 border',
        md: 'h-6 w-6 border-2',
        lg: 'h-8 w-8 border-2',
        xl: 'h-12 w-12 border-4',
      },
      variant: {
        primary: 'border-primary border-t-transparent',
        white: 'border-white border-t-transparent',
        current: 'border-current border-t-transparent',
      },
    },
    defaultVariants: {
      size: 'md',
      variant: 'primary',
    },
  }
);

export interface LoadingSpinnerProps extends VariantProps<typeof spinnerVariants> {
  className?: string;
  label?: string;
}

export function LoadingSpinner({ size, variant, className, label }: LoadingSpinnerProps) {
  return (
    <div className="inline-flex items-center gap-2">
      <div
        className={cn(spinnerVariants({ size, variant }), className)}
        role="status"
        aria-label={label || '加载中'}
      >
        <span className="sr-only">{label || '加载中'}</span>
      </div>
      {label && <span className="text-sm text-current">{label}</span>}
    </div>
  );
}

// 全屏加载覆盖层
export interface LoadingOverlayProps {
  show: boolean;
  message?: string;
  theme?: 'light' | 'dark';
}

export function LoadingOverlay({ show, message = '加载中...', theme = 'dark' }: LoadingOverlayProps) {
  if (!show) return null;

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 flex flex-col items-center justify-center gap-4',
        'backdrop-blur-sm transition-opacity duration-300',
        theme === 'dark' ? 'bg-black/50' : 'bg-white/50'
      )}
      role="dialog"
      aria-modal="true"
      aria-label="加载中"
    >
      <LoadingSpinner size="xl" variant={theme === 'dark' ? 'white' : 'primary'} />
      <p className={cn(
        'text-sm font-medium',
        theme === 'dark' ? 'text-white' : 'text-gray-900'
      )}>
        {message}
      </p>
    </div>
  );
}

// 骨架屏组件
export interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  circle?: boolean;
}

export function Skeleton({ className, width, height, circle }: SkeletonProps) {
  return (
    <div
      className={cn(
        'skeleton',
        circle ? 'rounded-full' : 'rounded',
        className
      )}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
      }}
    />
  );
}

// 脉冲加载动画
export interface PulseLoaderProps {
  count?: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function PulseLoader({ count = 3, size = 'md', className }: PulseLoaderProps) {
  const sizeMap = {
    sm: 'h-1.5 w-1.5',
    md: 'h-2 w-2',
    lg: 'h-3 w-3',
  };

  return (
    <div className={cn('flex items-center gap-1', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'rounded-full bg-current animate-pulse',
            sizeMap[size]
          )}
          style={{
            animationDelay: `${i * 150}ms`,
          }}
        />
      ))}
    </div>
  );
}

// 进度条组件
export interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  showLabel?: boolean;
  variant?: 'primary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
}

export function ProgressBar({
  value,
  max = 100,
  className,
  showLabel = false,
  variant = 'primary',
  size = 'md',
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const variantMap = {
    primary: 'bg-primary',
    success: 'bg-success',
    warning: 'bg-warning',
    error: 'bg-error',
  };

  const sizeMap = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  return (
    <div className={cn('w-full', className)}>
      <div className={cn(
        'w-full rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700',
        sizeMap[size]
      )}>
        <div
          className={cn(
            'h-full transition-all duration-300 ease-out',
            variantMap[variant]
          )}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 text-right">
          {percentage.toFixed(0)}%
        </p>
      )}
    </div>
  );
}
