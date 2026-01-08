/* eslint-disable @typescript-eslint/no-unused-expressions */
/**
 * 错误处理使用示例
 *
 * 这个文件展示了如何在实际组件中使用错误处理机制
 */

import React, { useState } from 'react';
import { ErrorMessage } from '../components/ErrorMessage';
import { notify } from '../components/Toast';
import { logger } from '../utils/logger';
import api from '../api/axios';

/**
 * 示例 1: 基本错误处理
 */
export function BasicErrorExample() {
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get('/api/v1/data');
      notify.success('数据加载成功');
      console.log(response.data);
    } catch (err) {
      // API 错误已被全局处理器处理
      // 我们只需要在组件中记录错误状态
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">基本错误处理示例</h2>

      <ErrorMessage
        error={error}
        onRetry={handleFetchData}
        showDetails={import.meta.env.DEV}
      />

      <button
        onClick={handleFetchData}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? '加载中...' : '加载数据'}
      </button>
    </div>
  );
}

/**
 * 示例 2: 使用 Toast 通知
 */
export function ToastExample() {
  const handleSuccess = () => {
    notify.success('操作成功完成！');
  };

  const handleError = () => {
    notify.error('操作失败，请重试');
  };

  const handleWarning = () => {
    notify.warning('请注意：此操作不可撤销');
  };

  const handleInfo = () => {
    notify.info('提示：您可以在设置中更改此选项');
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Toast 通知示例</h2>

      <div className="flex gap-2">
        <button
          onClick={handleSuccess}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          成功通知
        </button>

        <button
          onClick={handleError}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          错误通知
        </button>

        <button
          onClick={handleWarning}
          className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
        >
          警告通知
        </button>

        <button
          onClick={handleInfo}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          信息通知
        </button>
      </div>
    </div>
  );
}

/**
 * 示例 3: Promise Toast
 */
export function PromiseToastExample() {
  const simulateAsyncOperation = () => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        Math.random() > 0.5 ? resolve('成功') : reject('失败');
      }, 2000);
    });
  };

  const handlePromiseToast = () => {
    notify.promise(simulateAsyncOperation(), {
      pending: '处理中...',
      success: '操作成功！',
      error: '操作失败！',
    });
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Promise Toast 示例</h2>

      <button
        onClick={handlePromiseToast}
        className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
      >
        执行异步操作
      </button>
    </div>
  );
}

/**
 * 示例 4: 日志记录
 */
export function LoggerExample() {
  const handleDebugLog = () => {
    logger.debug('这是一条调试日志', { data: 'debug data' });
    notify.info('调试日志已记录（仅开发环境可见）');
  };

  const handleInfoLog = () => {
    logger.info('用户执行了某个操作', { action: 'click', button: 'submit' });
    notify.info('信息日志已记录');
  };

  const handleWarningLog = () => {
    logger.warn('检测到潜在问题', { issue: 'deprecated API' });
    notify.warning('警告日志已记录');
  };

  const handleErrorLog = () => {
    logger.error('发生错误', {
      error: 'Something went wrong',
      context: 'user action',
    });
    notify.error('错误日志已记录');
  };

  const handlePerformanceLog = () => {
    logger.performance('API 请求耗时', 1234, 'ms');
    notify.info('性能日志已记录');
  };

  const handleUserActionLog = () => {
    logger.userAction('点击提交按钮', {
      form: 'registration',
      timestamp: Date.now(),
    });
    notify.info('用户行为日志已记录');
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">日志记录示例</h2>

      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={handleDebugLog}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Debug 日志
        </button>

        <button
          onClick={handleInfoLog}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Info 日志
        </button>

        <button
          onClick={handleWarningLog}
          className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
        >
          Warning 日志
        </button>

        <button
          onClick={handleErrorLog}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Error 日志
        </button>

        <button
          onClick={handlePerformanceLog}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Performance 日志
        </button>

        <button
          onClick={handleUserActionLog}
          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          User Action 日志
        </button>
      </div>

      <p className="mt-4 text-sm text-gray-600">
        打开浏览器控制台查看日志输出
      </p>
    </div>
  );
}

/**
 * 示例 5: 表单错误处理
 */
export function FormErrorExample() {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // 模拟表单验证
      if (!formData.email) {
        throw new Error('请输入邮箱地址');
      }

      if (!formData.password) {
        throw new Error('请输入密码');
      }

      // 模拟 API 调用
      await api.post('/api/v1/auth/login', formData);
      notify.success('登录成功');
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      logger.error('登录失败', {
        error: error.message,
        email: formData.email,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">表单错误处理示例</h2>

      <form onSubmit={handleSubmit} className="max-w-md">
        <ErrorMessage error={error} />

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">邮箱</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) =>
              setFormData({ ...formData, email: e.target.value })
            }
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">密码</label>
          <input
            type="password"
            value={formData.password}
            onChange={(e) =>
              setFormData({ ...formData, password: e.target.value })
            }
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '登录中...' : '登录'}
        </button>
      </form>
    </div>
  );
}

/**
 * 主示例组件
 */
export function ErrorHandlingExamples() {
  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">错误处理机制使用示例</h1>

      <div className="space-y-8">
        <div className="border rounded-lg p-4 bg-white shadow">
          <BasicErrorExample />
        </div>

        <div className="border rounded-lg p-4 bg-white shadow">
          <ToastExample />
        </div>

        <div className="border rounded-lg p-4 bg-white shadow">
          <PromiseToastExample />
        </div>

        <div className="border rounded-lg p-4 bg-white shadow">
          <LoggerExample />
        </div>

        <div className="border rounded-lg p-4 bg-white shadow">
          <FormErrorExample />
        </div>
      </div>
    </div>
  );
}
