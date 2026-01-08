/* eslint-disable react-refresh/only-export-components */
import { ToastContainer, toast } from 'react-toastify';
import type { ToastOptions } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

/**
 * Toast 提供者组件
 *
 * 配置全局 Toast 通知容器
 */
export const ToastProvider = () => (
  <ToastContainer
    position="top-right"
    autoClose={5000}
    hideProgressBar={false}
    newestOnTop
    closeOnClick
    rtl={false}
    pauseOnFocusLoss
    draggable
    pauseOnHover
    theme="light"
    style={{ zIndex: 9999 }}
  />
);

/**
 * 默认的 Toast 配置选项
 */
const defaultOptions: ToastOptions = {
  position: 'top-right',
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
};

/**
 * 自定义 Toast 通知方法
 *
 * 提供更简洁的 API 和默认配置
 */
export const notify = {
  /**
   * 成功通知
   */
  success: (message: string, options?: ToastOptions) => {
    toast.success(message, { ...defaultOptions, ...options });
  },

  /**
   * 错误通知
   */
  error: (message: string, options?: ToastOptions) => {
    toast.error(message, { ...defaultOptions, ...options });
  },

  /**
   * 警告通知
   */
  warning: (message: string, options?: ToastOptions) => {
    toast.warning(message, { ...defaultOptions, ...options });
  },

  /**
   * 信息通知
   */
  info: (message: string, options?: ToastOptions) => {
    toast.info(message, { ...defaultOptions, ...options });
  },

  /**
   * 加载中通知
   */
  loading: (message: string, options?: ToastOptions) => {
    return toast.loading(message, { ...defaultOptions, ...options });
  },

  /**
   * 更新 Toast
   */
  update: (toastId: string | number, options: ToastOptions) => {
    toast.update(toastId, options);
  },

  /**
   * 关闭指定 Toast
   */
  dismiss: (toastId?: string | number) => {
    toast.dismiss(toastId);
  },

  /**
   * Promise Toast
   * 根据 Promise 状态自动显示不同的通知
   */
  promise: <T,>(
    promise: Promise<T>,
    messages: {
      pending: string;
      success: string;
      error: string;
    },
    options?: ToastOptions
  ) => {
    return toast.promise(
      promise,
      {
        pending: messages.pending,
        success: messages.success,
        error: messages.error,
      },
      { ...defaultOptions, ...options }
    );
  },
};

/**
 * Toast 工具函数
 */
export const toastUtils = {
  /**
   * 检查是否有激活的 Toast
   */
  isActive: (toastId: string | number) => {
    return toast.isActive(toastId);
  },

  /**
   * 清除所有 Toast
   */
  clearAll: () => {
    toast.dismiss();
  },
};
