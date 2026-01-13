/**
 * ConfirmDialog 确认对话框组件
 *
 * 功能：
 * - 通用确认对话框
 * - 支持自定义标题、内容、按钮文字
 * - 移动端友好的触摸交互
 * - 键盘导航支持（Escape取消，Enter确认）
 * - 遮罩层点击关闭（可配置）
 */

import { useEffect, useRef } from 'react';
import { AlertTriangle, Info, AlertCircle } from 'lucide-react';
import { Button } from './Button';
import { cn } from '../../lib/utils';

export type ConfirmDialogType = 'warning' | 'danger' | 'info';

export interface ConfirmDialogProps {
  isOpen: boolean;
  type?: ConfirmDialogType;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  theme?: 'light' | 'dark';
  closeOnOverlayClick?: boolean;
}

const icons = {
  warning: AlertTriangle,
  danger: AlertCircle,
  info: Info,
};

const iconColors = {
  warning: 'text-warning',
  danger: 'text-error',
  info: 'text-info',
};

export function ConfirmDialog({
  isOpen,
  type = 'warning',
  title,
  message,
  confirmText = '确认',
  cancelText = '取消',
  onConfirm,
  onCancel,
  theme = 'dark',
  closeOnOverlayClick = true,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const Icon = icons[type];

  // 键盘事件处理
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onCancel();
      } else if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        onConfirm();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel, onConfirm]);

  // 焦点管理
  useEffect(() => {
    if (isOpen && dialogRef.current) {
      const firstButton = dialogRef.current.querySelector('button');
      firstButton?.focus();
    }
  }, [isOpen]);

  // 阻止body滚动
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      aria-describedby="dialog-message"
    >
      {/* 遮罩层 */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={closeOnOverlayClick ? onCancel : undefined}
        aria-hidden="true"
      />

      {/* 对话框内容 */}
      <div
        ref={dialogRef}
        className={cn(
          'relative w-full max-w-md rounded-lg shadow-2xl animate-scale-in',
          'p-6 touch-manipulation',
          theme === 'dark'
            ? 'bg-bg-surface border border-border'
            : 'bg-white border border-gray-200'
        )}
      >
        {/* 图标和标题 */}
        <div className="flex items-start gap-4 mb-4">
          <div className={cn('flex-shrink-0 p-2 rounded-full', {
            'bg-warning/10': type === 'warning',
            'bg-error/10': type === 'danger',
            'bg-info/10': type === 'info',
          })}>
            <Icon className={cn('h-6 w-6', iconColors[type])} aria-hidden="true" />
          </div>

          <div className="flex-1 min-w-0">
            <h2
              id="dialog-title"
              className={cn(
                'text-lg font-semibold mb-2',
                theme === 'dark' ? 'text-text-primary' : 'text-gray-900'
              )}
            >
              {title}
            </h2>
            <p
              id="dialog-message"
              className={cn(
                'text-sm leading-relaxed',
                theme === 'dark' ? 'text-text-secondary' : 'text-gray-600'
              )}
            >
              {message}
            </p>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-3 justify-end mt-6">
          <Button
            variant="secondary"
            size="md"
            onClick={onCancel}
            className="touch-manipulation"
            data-testid="confirm-dialog-cancel"
          >
            {cancelText}
          </Button>
          <Button
            variant={type === 'danger' ? 'destructive' : 'primary'}
            size="md"
            onClick={onConfirm}
            className="touch-manipulation"
            data-testid="confirm-dialog-confirm"
          >
            {confirmText}
          </Button>
        </div>

        {/* 键盘提示 */}
        <p className={cn(
          'text-xs mt-4 text-center',
          theme === 'dark' ? 'text-text-muted' : 'text-gray-500'
        )}>
          Esc 取消 · Ctrl/Cmd + Enter 确认
        </p>
      </div>
    </div>
  );
}

/**
 * useConfirmDialog Hook
 * 简化确认对话框的使用
 */
import { useState, useCallback } from 'react';

export interface UseConfirmDialogOptions {
  type?: ConfirmDialogType;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
}

export function useConfirmDialog() {
  const [isOpen, setIsOpen] = useState(false);
  const [config, setConfig] = useState<UseConfirmDialogOptions | null>(null);
  const [resolveCallback, setResolveCallback] = useState<((value: boolean) => void) | null>(null);

  const confirm = useCallback((options: UseConfirmDialogOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      setConfig(options);
      setIsOpen(true);
      setResolveCallback(() => resolve);
    });
  }, []);

  const handleConfirm = useCallback(() => {
    setIsOpen(false);
    if (resolveCallback) {
      resolveCallback(true);
      setResolveCallback(null);
    }
  }, [resolveCallback]);

  const handleCancel = useCallback(() => {
    setIsOpen(false);
    if (resolveCallback) {
      resolveCallback(false);
      setResolveCallback(null);
    }
  }, [resolveCallback]);

  return {
    confirm,
    isOpen,
    config,
    handleConfirm,
    handleCancel,
  };
}
