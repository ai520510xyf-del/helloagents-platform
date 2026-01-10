/**
 * API 客户端工具
 *
 * 提供统一的 API 请求处理、错误处理和重试逻辑
 */

import { logger } from './logger';

export class ApiError extends Error {
  public status?: number;
  public data?: any;

  constructor(
    message: string,
    status?: number,
    data?: any
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export interface RequestConfig extends RequestInit {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

class ApiClient {
  private baseURL: string;
  private defaultTimeout: number = 30000; // 30 seconds
  private defaultRetries: number = 0;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  /**
   * 发送 HTTP 请求（带超时和重试）
   */
  private async fetchWithTimeout(
    url: string,
    config: RequestConfig = {}
  ): Promise<Response> {
    const {
      timeout = this.defaultTimeout,
      retries = this.defaultRetries,
      retryDelay = 1000,
      ...fetchConfig
    } = config;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    let lastError: Error | null = null;
    let attempt = 0;

    while (attempt <= retries) {
      try {
        const response = await fetch(url, {
          ...fetchConfig,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        return response;
      } catch (error) {
        lastError = error as Error;
        attempt++;

        if (attempt <= retries) {
          logger.warn(`Request failed, retrying (${attempt}/${retries})...`, {
            url,
            error: lastError.message,
          });
          await this.delay(retryDelay * attempt);
        }
      }
    }

    clearTimeout(timeoutId);
    throw lastError;
  }

  /**
   * 延迟函数
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 处理响应
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    const isJson = contentType?.includes('application/json');

    if (!response.ok) {
      let errorData: any;
      try {
        errorData = isJson ? await response.json() : await response.text();
      } catch {
        errorData = null;
      }

      const message = errorData?.message || errorData?.detail || `HTTP ${response.status}: ${response.statusText}`;
      logger.error('API request failed', {
        status: response.status,
        statusText: response.statusText,
        data: errorData,
      });

      throw new ApiError(message, response.status, errorData);
    }

    if (isJson) {
      return await response.json();
    }

    return await response.text() as T;
  }

  /**
   * GET 请求
   */
  async get<T>(path: string, config?: RequestConfig): Promise<T> {
    const url = `${this.baseURL}${path}`;
    logger.debug(`GET ${url}`);

    try {
      const response = await this.fetchWithTimeout(url, {
        method: 'GET',
        ...config,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      logger.error(`GET ${url} failed`, error);
      throw error;
    }
  }

  /**
   * POST 请求
   */
  async post<T>(path: string, data?: any, config?: RequestConfig): Promise<T> {
    const url = `${this.baseURL}${path}`;
    logger.debug(`POST ${url}`, data);

    try {
      const response = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...config?.headers,
        },
        body: data ? JSON.stringify(data) : undefined,
        ...config,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      logger.error(`POST ${url} failed`, error);
      throw error;
    }
  }

  /**
   * PUT 请求
   */
  async put<T>(path: string, data?: any, config?: RequestConfig): Promise<T> {
    const url = `${this.baseURL}${path}`;
    logger.debug(`PUT ${url}`, data);

    try {
      const response = await this.fetchWithTimeout(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...config?.headers,
        },
        body: data ? JSON.stringify(data) : undefined,
        ...config,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      logger.error(`PUT ${url} failed`, error);
      throw error;
    }
  }

  /**
   * DELETE 请求
   */
  async delete<T>(path: string, config?: RequestConfig): Promise<T> {
    const url = `${this.baseURL}${path}`;
    logger.debug(`DELETE ${url}`);

    try {
      const response = await this.fetchWithTimeout(url, {
        method: 'DELETE',
        ...config,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      logger.error(`DELETE ${url} failed`, error);
      throw error;
    }
  }

  /**
   * PATCH 请求
   */
  async patch<T>(path: string, data?: any, config?: RequestConfig): Promise<T> {
    const url = `${this.baseURL}${path}`;
    logger.debug(`PATCH ${url}`, data);

    try {
      const response = await this.fetchWithTimeout(url, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...config?.headers,
        },
        body: data ? JSON.stringify(data) : undefined,
        ...config,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      logger.error(`PATCH ${url} failed`, error);
      throw error;
    }
  }
}

// 导出默认实例
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const apiClient = new ApiClient(API_BASE_URL);
