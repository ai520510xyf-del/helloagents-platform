/**
 * useToast Hook
 * Toast通知管理Hook
 */

import { useState } from 'react';
import type { ToastProps, ToastType } from '../components/ui/Toast';

// 生成唯一ID的辅助函数
let toastIdCounter = 0;
function generateToastId(): string {
  toastIdCounter += 1;
  return `toast-${Date.now()}-${toastIdCounter}`;
}

export function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([]);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  const addToast = (type: ToastType, message: string, duration?: number) => {
    const id = generateToastId();
    const newToast: ToastProps = {
      id,
      type,
      message,
      duration,
      onClose: removeToast,
    };
    setToasts((prev) => [...prev, newToast]);
    return id;
  };

  const success = (message: string, duration?: number) => addToast('success', message, duration);
  const error = (message: string, duration?: number) => addToast('error', message, duration);
  const warning = (message: string, duration?: number) => addToast('warning', message, duration);
  const info = (message: string, duration?: number) => addToast('info', message, duration);

  return {
    toasts,
    success,
    error,
    warning,
    info,
    removeToast,
  };
}
