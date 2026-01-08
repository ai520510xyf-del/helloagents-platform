/**
 * useCodeExecution Hook
 * 管理代码执行状态
 */

import { useState } from 'react';
import { executeCode } from '../services/api';

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
      setOutput(`> python ReAct.py\n\n❌ 连接后端失败\n\n${error instanceof Error ? error.message : '未知错误'}\n\n请确保后端服务正在运行 (http://localhost:8000)`);
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
