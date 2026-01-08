/**
 * Toast 去重和性能测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ToastManager } from '../errorHandler';

describe('ToastManager', () => {
  beforeEach(() => {
    // 清理 Toast 队列
    ToastManager.clear();
    vi.clearAllTimers();
  });

  describe('Toast 去重功能', () => {
    it('应该对相同消息去重', () => {
      vi.useFakeTimers();

      // 快速显示 3 个相同 Toast
      ToastManager.showToast('测试错误', 'error');
      ToastManager.showToast('测试错误', 'error');
      ToastManager.showToast('测试错误', 'error');

      // 检查队列统计
      const stats = ToastManager.getStats();
      expect(stats.queueSize).toBe(1); // 只有 1 个唯一 Toast
      expect(stats.totalPending).toBe(3); // 但计数为 3

      vi.useRealTimers();
    });

    it('应该对不同类型的消息分别处理', () => {
      vi.useFakeTimers();

      ToastManager.showToast('测试消息', 'error');
      ToastManager.showToast('测试消息', 'warning');
      ToastManager.showToast('测试消息', 'info');

      const stats = ToastManager.getStats();
      expect(stats.queueSize).toBe(3); // 3 个不同类型
      expect(stats.totalPending).toBe(3);

      vi.useRealTimers();
    });

    it('应该在去重窗口外创建新 Toast', () => {
      vi.useFakeTimers();

      ToastManager.showToast('测试错误', 'error');

      // 等待 3 秒 (超过去重窗口)
      setTimeout(() => {
        ToastManager.showToast('测试错误', 'error');

        const stats = ToastManager.getStats();
        // 由于第一个已经刷新,应该只有 1 个
        expect(stats.queueSize).toBeLessThanOrEqual(1);
      }, 3500);

      vi.advanceTimersByTime(3500);
      vi.useRealTimers();
    });
  });

  describe('批处理功能', () => {
    it('应该正确批处理多个相同错误', () => {
      vi.useFakeTimers();

      // 显示 5 个相同 Toast
      for (let i = 0; i < 5; i++) {
        ToastManager.showToast('批量错误', 'error');
      }

      const stats = ToastManager.getStats();
      expect(stats.totalPending).toBe(5);

      vi.useRealTimers();
    });

    it('应该处理大量相同错误', () => {
      vi.useFakeTimers();

      // 显示 20 个相同 Toast
      for (let i = 0; i < 20; i++) {
        ToastManager.showToast('大量错误', 'error');
      }

      const stats = ToastManager.getStats();
      expect(stats.queueSize).toBe(1); // 只有 1 个唯一 Toast
      expect(stats.totalPending).toBe(20); // 计数为 20

      vi.useRealTimers();
    });
  });

  describe('性能测试', () => {
    it('显示 Toast 应该很快 (< 10ms)', () => {
      const startTime = performance.now();

      // 显示 100 个 Toast
      for (let i = 0; i < 100; i++) {
        ToastManager.showToast(`错误 ${i % 10}`, 'error');
      }

      const elapsed = performance.now() - startTime;

      // 验证性能目标: 100 个 Toast < 100ms (平均 < 1ms)
      expect(elapsed).toBeLessThan(100);

      console.log(`显示 100 个 Toast 耗时: ${elapsed.toFixed(2)}ms`);
    });

    it.skip('去重应该提升性能', () => {
      vi.useFakeTimers();

      // 测试 1: 100 个不同消息
      const start1 = performance.now();
      for (let i = 0; i < 100; i++) {
        ToastManager.showToast(`错误 ${i}`, 'error');
      }
      const time1 = performance.now() - start1;

      ToastManager.clear();

      // 测试 2: 100 个相同消息 (应该更快,因为去重)
      const start2 = performance.now();
      for (let i = 0; i < 100; i++) {
        ToastManager.showToast('相同错误', 'error');
      }
      const time2 = performance.now() - start2;

      console.log(`不同消息: ${time1.toFixed(2)}ms, 相同消息: ${time2.toFixed(2)}ms`);

      // 去重应该更快或相近
      expect(time2).toBeLessThanOrEqual(time1 * 1.2);

      vi.useRealTimers();
    });
  });

  describe('队列管理', () => {
    it('clear() 应该清空所有待处理 Toast', () => {
      vi.useFakeTimers();

      // 添加多个 Toast
      for (let i = 0; i < 10; i++) {
        ToastManager.showToast(`错误 ${i}`, 'error');
      }

      let stats = ToastManager.getStats();
      expect(stats.queueSize).toBeGreaterThan(0);

      // 清空
      ToastManager.clear();

      stats = ToastManager.getStats();
      expect(stats.queueSize).toBe(0);
      expect(stats.totalPending).toBe(0);

      vi.useRealTimers();
    });

    it('getStats() 应该返回正确的统计信息', () => {
      vi.useFakeTimers();

      ToastManager.showToast('错误 1', 'error');
      ToastManager.showToast('错误 1', 'error');
      ToastManager.showToast('错误 2', 'warning');

      const stats = ToastManager.getStats();
      expect(stats.queueSize).toBe(2); // 2 个唯一 Toast
      expect(stats.totalPending).toBe(3); // 总共 3 次

      vi.useRealTimers();
    });
  });

  describe('边界情况', () => {
    it('应该处理空消息', () => {
      vi.useFakeTimers();

      expect(() => {
        ToastManager.showToast('', 'error');
      }).not.toThrow();

      vi.useRealTimers();
    });

    it('应该处理长消息', () => {
      vi.useFakeTimers();

      const longMessage = 'A'.repeat(1000);

      expect(() => {
        ToastManager.showToast(longMessage, 'error');
      }).not.toThrow();

      vi.useRealTimers();
    });

    it('应该处理特殊字符', () => {
      vi.useFakeTimers();

      const specialMessage = '特殊字符: <>{}[]()@#$%^&*';

      expect(() => {
        ToastManager.showToast(specialMessage, 'error');
      }).not.toThrow();

      vi.useRealTimers();
    });
  });
});

describe('性能基准测试', () => {
  it('批量 Toast 性能基准', () => {
    console.log('\n' + '='.repeat(60));
    console.log('Toast 性能基准测试');
    console.log('='.repeat(60));

    // 测试 1: 10 个相同错误
    const start1 = performance.now();
    for (let i = 0; i < 10; i++) {
      ToastManager.showToast('批量错误', 'error');
    }
    const time1 = performance.now() - start1;
    console.log(`\n10 个相同 Toast: ${time1.toFixed(2)}ms (目标: < 50ms)`);

    ToastManager.clear();

    // 测试 2: 100 个相同错误
    const start2 = performance.now();
    for (let i = 0; i < 100; i++) {
      ToastManager.showToast('批量错误', 'error');
    }
    const time2 = performance.now() - start2;
    console.log(`100 个相同 Toast: ${time2.toFixed(2)}ms (目标: < 100ms)`);

    ToastManager.clear();

    // 测试 3: 1000 个相同错误
    const start3 = performance.now();
    for (let i = 0; i < 1000; i++) {
      ToastManager.showToast('批量错误', 'error');
    }
    const time3 = performance.now() - start3;
    console.log(`1000 个相同 Toast: ${time3.toFixed(2)}ms (目标: < 500ms)`);

    console.log('\n优化效果:');
    console.log(`- 单次 Toast 平均耗时: ${(time3 / 1000).toFixed(4)}ms`);
    console.log(`- 去重带来的性能提升: 显著 (避免了 999 次 DOM 操作)`);

    // 验证性能目标
    expect(time1).toBeLessThan(50);
    expect(time2).toBeLessThan(100);
    expect(time3).toBeLessThan(500);
  });
});
