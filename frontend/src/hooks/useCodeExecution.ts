/**
 * useCodeExecution Hook
 * 管理代码执行状态
 *
 * 优化：
 * - 更友好的错误提示
 * - 网络错误检测
 * - 用户操作引导
 */

import { useState } from 'react';
import { executeCode } from '../services/api';
import { ApiError } from '../utils/apiClient';

export function useCodeExecution() {
  const [isRunning, setIsRunning] = useState(false);
  const [output, setOutput] = useState('');

  const runCode = async (code: string) => {
    setIsRunning(true);
    setOutput('> python ReAct.py\n\n正在执行代码...\n\n⏳ 连接到执行环境...');

    try {
      const result = await executeCode({
        code,
        language: 'python',
        timeout: 30
      });

      if (result.success) {
        setOutput(`> python ReAct.py\n\n✅ 代码执行成功！\n\n${result.output}\n\n⏱️  执行时间: ${result.execution_time.toFixed(2)}s`);
      } else {
        setOutput(`> python ReAct.py\n\n❌ 执行失败\n\n${result.error}\n\n⏱️  执行时间: ${result.execution_time.toFixed(2)}s`);
      }
    } catch (error) {
      // 详细的错误处理
      let errorMessage = '> python ReAct.py\n\n❌ 执行失败\n\n';

      if (error instanceof ApiError) {
        // API 错误（如 404, 500 等）
        if (error.status === 404) {
          errorMessage += '后端API端点未找到 (404)\n\n';
        } else if (error.status === 500) {
          errorMessage += '后端服务器内部错误 (500)\n\n';
        } else if (error.status === 503) {
          errorMessage += '后端服务不可用 (503)\n\n';
        } else {
          errorMessage += `HTTP错误 (${error.status}): ${error.message}\n\n`;
        }
      } else if (error instanceof TypeError && error.message.includes('fetch')) {
        // 网络连接错误
        errorMessage += '网络连接失败 - Failed to fetch\n\n';
        errorMessage += '可能的原因：\n';
        errorMessage += '1. 后端服务未启动\n';
        errorMessage += '2. 后端地址配置错误\n';
        errorMessage += '3. 网络连接问题\n\n';
      } else {
        // 其他未知错误
        errorMessage += `${error instanceof Error ? error.message : '未知错误'}\n\n`;
      }

      // 添加用户操作指引
      errorMessage += '━━━━━━━━━━━━━━━━━━━━━━\n';
      errorMessage += '📋 解决方案：\n\n';
      errorMessage += '1. 检查后端服务是否运行：\n';
      errorMessage += '   cd backend && uvicorn app.main:app --reload\n\n';
      errorMessage += '2. 确认后端地址：\n';
      errorMessage += '   默认: http://localhost:8000\n\n';
      errorMessage += '3. 查看后端日志确认问题\n\n';
      errorMessage += '💡 提示：您可以继续编写代码，稍后再运行。';

      setOutput(errorMessage);
    } finally {
      setIsRunning(false);
    }
  };

  const stopExecution = () => {
    setIsRunning(false);
    setOutput(prev => prev + '\n\n🛑 执行已停止');
  };

  const clearOutput = () => {
    setOutput('');
  };

  return {
    isRunning,
    output,
    runCode,
    stopExecution,
    clearOutput
  };
}
