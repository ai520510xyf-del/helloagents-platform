import axios from 'axios';
import type { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { GlobalErrorHandler } from '../utils/errorHandler';
import { logger } from '../utils/logger';

/**
 * 创建 Axios 实例，配置统一的请求和响应处理
 */
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 请求拦截器
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加请求时间戳，用于性能监控
    config.metadata = { startTime: Date.now() };

    // 添加认证 token (如果存在)
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 记录请求日志
    logger.debug('API Request', {
      method: config.method?.toUpperCase(),
      url: config.url,
      params: config.params,
      data: config.data,
    });

    return config;
  },
  (error: AxiosError) => {
    logger.error('Request interceptor error', { error: error.message });
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器
 */
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 计算请求耗时
    const startTime = response.config.metadata?.startTime;
    if (startTime) {
      const duration = Date.now() - startTime;
      logger.performance(
        `API ${response.config.method?.toUpperCase()} ${response.config.url}`,
        duration,
        'ms'
      );
    }

    // 记录响应日志
    logger.debug('API Response', {
      method: response.config.method?.toUpperCase(),
      url: response.config.url,
      status: response.status,
      data: response.data,
    });

    return response;
  },
  (error: AxiosError<{ error: { code: string; message: string } }>) => {
    // 统一错误处理
    GlobalErrorHandler.handleAPIError(error);

    // 记录错误响应
    if (error.response) {
      logger.error('API Response Error', {
        method: error.config?.method?.toUpperCase(),
        url: error.config?.url,
        status: error.response.status,
        data: error.response.data,
      });
    }

    return Promise.reject(error);
  }
);

// 扩展 AxiosRequestConfig 类型以支持 metadata
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}

export default api;
