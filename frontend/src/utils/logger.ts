/**
 * 前端日志工具
 *
 * 提供统一的日志记录接口，支持不同的日志级别和格式化输出
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  data?: any;
}

class Logger {
  private isDevelopment: boolean;

  constructor() {
    this.isDevelopment = import.meta.env.DEV;
  }

  /**
   * 格式化日志消息
   */
  private formatMessage(level: LogLevel, message: string, data?: any): string {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;

    if (data) {
      return `${prefix} ${message}\n${JSON.stringify(data, null, 2)}`;
    }

    return `${prefix} ${message}`;
  }

  /**
   * 创建日志条目
   */
  private createLogEntry(level: LogLevel, message: string, data?: any): LogEntry {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      data,
    };
  }

  /**
   * 发送日志到服务器 (可选)
   */
  private async sendToServer(entry: LogEntry): Promise<void> {
    // 只在生产环境发送 error 和 warn 级别的日志
    if (!this.isDevelopment && (entry.level === 'error' || entry.level === 'warn')) {
      try {
        // TODO: 实现日志上报接口
        // await fetch('/api/logs', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(entry),
        // });
      } catch (error) {
        // 上报失败时静默处理，避免影响用户体验
        console.error('Failed to send log to server:', error);
      }
    }
  }

  /**
   * Debug 级别日志 (仅开发环境)
   */
  debug(message: string, data?: any): void {
    if (!this.isDevelopment) return;

    const formatted = this.formatMessage('debug', message, data);
    console.debug(formatted);
  }

  /**
   * Info 级别日志
   */
  info(message: string, data?: any): void {
    const formatted = this.formatMessage('info', message, data);
    console.info(formatted);

    const entry = this.createLogEntry('info', message, data);
    this.sendToServer(entry);
  }

  /**
   * Warning 级别日志
   */
  warn(message: string, data?: any): void {
    const formatted = this.formatMessage('warn', message, data);
    console.warn(formatted);

    const entry = this.createLogEntry('warn', message, data);
    this.sendToServer(entry);
  }

  /**
   * Error 级别日志
   */
  error(message: string, data?: any): void {
    const formatted = this.formatMessage('error', message, data);
    console.error(formatted);

    const entry = this.createLogEntry('error', message, data);
    this.sendToServer(entry);
  }

  /**
   * 记录性能指标
   */
  performance(metric: string, value: number, unit: string = 'ms'): void {
    const message = `Performance: ${metric} = ${value}${unit}`;
    this.info(message, { metric, value, unit });
  }

  /**
   * 记录用户行为
   */
  userAction(action: string, details?: any): void {
    this.info(`User Action: ${action}`, details);
  }
}

// 导出单例实例
export const logger = new Logger();
