import { type ButtonHTMLAttributes, type ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

const buttonVariants = cva(
  // 基础样式 - 遵循 Minimalism & Swiss Style
  'inline-flex items-center justify-center font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-bg-dark disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        // 主按钮 - Primary Blue (#3B82F6)
        primary: 'bg-primary hover:bg-primary/90 text-white focus:ring-primary',

        // 次要按钮 - 边框样式
        secondary: 'border border-border hover:bg-bg-elevated text-text-primary focus:ring-primary',

        // CTA 按钮 - 强调色
        cta: 'bg-cta hover:bg-cta/90 text-white focus:ring-cta',

        // 危险按钮
        destructive: 'bg-error hover:bg-error/90 text-white focus:ring-error',

        // Ghost 按钮
        ghost: 'hover:bg-bg-elevated text-text-primary',

        // Success 按钮
        success: 'bg-success hover:bg-success/90 text-white focus:ring-success',
      },
      size: {
        sm: 'h-8 px-3 text-sm rounded',
        md: 'h-10 px-4 text-sm rounded-md',
        lg: 'h-12 px-6 text-base rounded-md',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  children: ReactNode;
  isLoading?: boolean;
}

export function Button({
  variant,
  size,
  children,
  isLoading,
  disabled,
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
          加载中...
        </>
      ) : (
        children
      )}
    </button>
  );
}
