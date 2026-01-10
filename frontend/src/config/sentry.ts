/**
 * Sentry 错误追踪和性能监控配置
 *
 * 提供前端错误追踪、性能监控(APM)和用户会话重放功能
 */

import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

/**
 * 初始化 Sentry
 *
 * 在应用启动时调用此函数
 */
export function initSentry() {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  const environment = import.meta.env.VITE_SENTRY_ENVIRONMENT || "development";

  // 只在配置了 DSN 时初始化
  if (!dsn) {
    console.warn("Sentry DSN not configured. Error tracking is disabled.");
    return;
  }

  Sentry.init({
    dsn,
    environment,

    // 性能监控 (APM)
    integrations: [
      new BrowserTracing({
        // 追踪所有路由变化
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          React.useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes
        ),
      }),
    ],

    // 性能监控采样率
    tracesSampleRate: environment === "production" ? 0.1 : 1.0,

    // 发布版本追踪
    release: import.meta.env.VITE_APP_VERSION || "unknown",

    // 环境标签
    tags: {
      app: "helloagents-frontend",
      platform: "web",
    },

    // 错误过滤
    beforeSend(event, hint) {
      // 开发环境打印错误到控制台
      if (environment === "development") {
        console.error("Sentry captured error:", hint.originalException || hint.syntheticException);
      }

      // 过滤掉某些已知的无关错误
      if (event.exception) {
        const exceptionMessage = event.exception.values?.[0]?.value || "";

        // 过滤浏览器扩展引起的错误
        if (exceptionMessage.includes("chrome-extension://")) {
          return null;
        }

        // 过滤网络错误 (这些应该在后端监控)
        if (exceptionMessage.includes("Network request failed")) {
          return null;
        }
      }

      return event;
    },

    // 面包屑配置 (调试信息)
    beforeBreadcrumb(breadcrumb, hint) {
      // 过滤敏感信息
      if (breadcrumb.category === "console") {
        // 不记录 console.log
        if (breadcrumb.level === "log") {
          return null;
        }
      }

      return breadcrumb;
    },

    // 忽略特定错误
    ignoreErrors: [
      // 浏览器扩展
      "top.GLOBALS",
      "ResizeObserver loop limit exceeded",
      "Non-Error promise rejection captured",
      // 网络错误
      "NetworkError",
      "Failed to fetch",
      // Safari 特有错误
      "webkit-masked-url",
    ],

    // 不发送默认的 PII (个人身份信息)
    sendDefaultPii: false,

    // 最大面包屑数量
    maxBreadcrumbs: 50,
  });

  // 设置用户上下文 (如果已登录)
  const userId = localStorage.getItem("user_id");
  if (userId) {
    Sentry.setUser({ id: userId });
  }
}

/**
 * 设置用户信息
 *
 * @param userId - 用户 ID
 * @param userInfo - 额外的用户信息
 */
export function setSentryUser(userId: string | number, userInfo?: Record<string, any>) {
  Sentry.setUser({
    id: String(userId),
    ...userInfo,
  });
}

/**
 * 清除用户信息 (登出时调用)
 */
export function clearSentryUser() {
  Sentry.setUser(null);
}

/**
 * 手动捕获错误
 *
 * @param error - 错误对象
 * @param context - 额外的上下文信息
 */
export function captureError(error: Error, context?: Record<string, any>) {
  Sentry.captureException(error, {
    contexts: {
      custom: context,
    },
  });
}

/**
 * 手动捕获消息
 *
 * @param message - 消息内容
 * @param level - 严重级别
 * @param context - 额外的上下文信息
 */
export function captureMessage(
  message: string,
  level: Sentry.SeverityLevel = "info",
  context?: Record<string, any>
) {
  Sentry.captureMessage(message, {
    level,
    contexts: {
      custom: context,
    },
  });
}

/**
 * 添加面包屑 (调试信息)
 *
 * @param message - 消息内容
 * @param category - 分类
 * @param data - 额外数据
 */
export function addBreadcrumb(
  message: string,
  category: string = "custom",
  data?: Record<string, any>
) {
  Sentry.addBreadcrumb({
    message,
    category,
    level: "info",
    data,
  });
}

/**
 * 开始性能追踪
 *
 * @param name - 追踪名称
 * @param operation - 操作类型
 * @returns 追踪对象
 */
export function startTransaction(name: string, operation: string) {
  return Sentry.startTransaction({
    name,
    op: operation,
  });
}

/**
 * 包装组件以进行错误边界处理
 *
 * @param Component - 要包装的组件
 * @param options - 错误边界选项
 */
export const withSentryErrorBoundary = Sentry.withErrorBoundary;

/**
 * 包装函数以进行性能追踪
 *
 * @param fn - 要包装的函数
 * @param name - 追踪名称
 */
export function withSentryTracing<T extends (...args: any[]) => any>(
  fn: T,
  name: string
): T {
  return ((...args: any[]) => {
    const transaction = startTransaction(name, "function");
    try {
      const result = fn(...args);

      // 如果返回 Promise,等待完成
      if (result instanceof Promise) {
        return result
          .then((res) => {
            transaction.finish();
            return res;
          })
          .catch((error) => {
            captureError(error);
            transaction.finish();
            throw error;
          });
      }

      transaction.finish();
      return result;
    } catch (error) {
      captureError(error as Error);
      transaction.finish();
      throw error;
    }
  }) as T;
}

// 导出 Sentry 实例供高级使用
export { Sentry };
