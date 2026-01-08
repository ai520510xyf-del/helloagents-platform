import { AxiosError } from 'axios';
import { toast } from 'react-toastify';
import { logger } from './logger';

/**
 * 错误详情类型 (支持任意键值对)
 */
export interface ErrorDetails {
  [key: string]: string | number | boolean | null | undefined | ErrorDetails | ErrorDetails[];
}

/**
 * React 错误信息接口
 */
export interface ReactErrorInfo {
  componentStack?: string | null;
  digest?: string;
}

/**
 * API 错误接口 (与后端错误格式对应)
 */
export interface APIError {
  code: string;
  message: string;
  details?: ErrorDetails;
  path?: string;
  timestamp?: number;
}

/**
 * Toast 管理器
 *
 * 功能:
 * - Toast 去重 (避免重复显示相同消息)
 * - 批处理 (合并多个相同错误)
 * - 性能优化 (减少 Toast 渲染次数)
 */
class ToastManager {
  private static toastQueue: Map<
    string,
    {
      count: number;
      firstSeen: number;
      timeout: ReturnType<typeof setTimeout>;
    }
  > = new Map();

  private static readonly DEDUPE_WINDOW = 3000; // 3 秒去重窗口
  private static readonly MAX_BATCH_SIZE = 5; // 最大批量大小

  /**
   * 显示 Toast 通知 (带去重和批处理)
   */
  static showToast(
    message: string,
    type: 'error' | 'warning' | 'info' | 'success' = 'error'
  ): void {
    const key = `${type}:${message}`;
    const now = Date.now();

    // 检查是否在去重窗口内
    const existing = this.toastQueue.get(key);
    if (existing && now - existing.firstSeen < this.DEDUPE_WINDOW) {
      // 增加计数
      existing.count++;

      // 重置超时
      clearTimeout(existing.timeout);
      existing.timeout = setTimeout(() => {
        this.flushBatchedToast(key, existing.count, type, message);
        this.toastQueue.delete(key);
      }, this.DEDUPE_WINDOW);

      logger.debug('Toast deduplicated', {
        message,
        type,
        count: existing.count,
      });

      return;
    }

    // 新 Toast
    this.toastQueue.set(key, {
      count: 1,
      firstSeen: now,
      timeout: setTimeout(() => {
        this.flushBatchedToast(key, 1, type, message);
        this.toastQueue.delete(key);
      }, this.DEDUPE_WINDOW),
    });

    logger.debug('Toast queued', { message, type });
  }

  /**
   * 刷新批处理的 Toast
   */
  private static flushBatchedToast(
    _key: string,
    count: number,
    type: 'error' | 'warning' | 'info' | 'success',
    message: string
  ): void {
    if (count === 1) {
      // 单个 Toast
      toast[type](message, {
        position: 'top-right',
        autoClose: 5000,
      });
    } else if (count <= this.MAX_BATCH_SIZE) {
      // 批量 Toast (显示次数)
      toast[type](`${message} (${count} 次)`, {
        position: 'top-right',
        autoClose: 6000,
      });
    } else {
      // 超过阈值，显示汇总
      toast[type](`${message} (${count} 个相同错误)`, {
        position: 'top-right',
        autoClose: 7000,
      });
    }

    logger.info('Toast flushed', {
      message,
      type,
      count,
      batched: count > 1,
    });
  }

  /**
   * 清理所有待处理的 Toast
   */
  static clear(): void {
    this.toastQueue.forEach((entry) => {
      clearTimeout(entry.timeout);
    });
    this.toastQueue.clear();
    logger.info('Toast queue cleared');
  }

  /**
   * 获取队列统计信息
   */
  static getStats(): {
    queueSize: number;
    totalPending: number;
  } {
    let totalPending = 0;
    this.toastQueue.forEach((entry) => {
      totalPending += entry.count;
    });

    return {
      queueSize: this.toastQueue.size,
      totalPending,
    };
  }
}

/**
 * 全局错误处理器类
 *
 * 提供统一的错误处理方法，包括 API 错误、React 错误和全局错误
 */
export class GlobalErrorHandler {
  /**
   * 处理 API 错误
   */
  static handleAPIError(error: AxiosError<{ error: APIError }>): void {
    const apiError = error.response?.data?.error;

    if (apiError) {
      // 根据错误代码显示不同的用户友好提示
      switch (apiError.code) {
        case 'VALIDATION_ERROR':
          ToastManager.showToast(
            `输入验证失败: ${apiError.message}`,
            'error'
          );
          break;

        case 'AUTHENTICATION_ERROR':
          ToastManager.showToast('请先登录', 'error');
          // 跳转到登录页
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
          break;

        case 'AUTHORIZATION_ERROR':
          ToastManager.showToast('没有权限执行此操作', 'error');
          break;

        case 'RESOURCE_NOT_FOUND':
          ToastManager.showToast('请求的资源不存在', 'error');
          break;

        case 'SANDBOX_EXECUTION_ERROR':
          ToastManager.showToast(
            `代码执行错误: ${apiError.message}`,
            'error'
          );
          break;

        case 'CONTAINER_POOL_ERROR':
          ToastManager.showToast('服务暂时不可用，请稍后重试', 'error');
          break;

        case 'RATE_LIMIT_ERROR':
          ToastManager.showToast('请求过于频繁，请稍后再试', 'warning');
          break;

        case 'TIMEOUT_ERROR':
          ToastManager.showToast('请求超时，请重试', 'error');
          break;

        default:
          ToastManager.showToast(`错误: ${apiError.message}`, 'error');
      }

      // 记录错误到日志系统
      logger.error('API Error', {
        code: apiError.code,
        message: apiError.message,
        path: apiError.path,
        status: error.response?.status,
        details: apiError.details,
      });
    } else {
      // 处理网络错误或其他错误
      if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK_TIMEOUT') {
        ToastManager.showToast('请求超时，请检查网络连接', 'error');
      } else if (error.code === 'ERR_NETWORK') {
        ToastManager.showToast('网络连接失败，请检查网络', 'error');
      } else if (error.code === 'ERR_CANCELED') {
        // 请求被取消，通常不需要提示用户
        logger.info('Request canceled', { error: error.message });
      } else {
        ToastManager.showToast('发生未知错误，请稍后重试', 'error');
      }

      // 记录网络错误
      logger.error('Network Error', {
        code: error.code,
        message: error.message,
        url: error.config?.url,
        method: error.config?.method,
      });
    }
  }

  /**
   * 处理 React 错误
   */
  static handleReactError(error: Error, errorInfo?: ReactErrorInfo): void {
    ToastManager.showToast('页面出现异常，已自动报告', 'error');

    logger.error('React Error', {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo?.componentStack,
      digest: errorInfo?.digest,
    });
  }

  /**
   * 处理未捕获的 Promise rejection
   */
  static handleUnhandledRejection(event: PromiseRejectionEvent): void {
    ToastManager.showToast('发生未预期的错误', 'error');

    logger.error('Unhandled Promise Rejection', {
      reason: event.reason,
      promise: event.promise,
    });

    // 阻止默认的错误处理
    event.preventDefault();
  }

  /**
   * 处理全局错误
   */
  static handleGlobalError(event: ErrorEvent): void {
    ToastManager.showToast('页面发生错误', 'error');

    logger.error('Global Error', {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      error: event.error,
    });

    // 阻止默认的错误处理
    event.preventDefault();
  }

  /**
   * 初始化全局错误处理器
   */
  static init(): void {
    if (typeof window !== 'undefined') {
      // 注册全局错误事件监听器
      window.addEventListener('error', GlobalErrorHandler.handleGlobalError);

      // 注册 Promise rejection 监听器
      window.addEventListener(
        'unhandledrejection',
        GlobalErrorHandler.handleUnhandledRejection
      );

      logger.info('Global error handlers initialized');
    }
  }

  /**
   * 清理全局错误处理器
   */
  static cleanup(): void {
    if (typeof window !== 'undefined') {
      window.removeEventListener('error', GlobalErrorHandler.handleGlobalError);
      window.removeEventListener(
        'unhandledrejection',
        GlobalErrorHandler.handleUnhandledRejection
      );

      logger.info('Global error handlers cleaned up');
    }
  }
}

// 导出 ToastManager (供外部使用)
export { ToastManager };

// 自动初始化全局错误处理器
if (typeof window !== 'undefined') {
  GlobalErrorHandler.init();
}
