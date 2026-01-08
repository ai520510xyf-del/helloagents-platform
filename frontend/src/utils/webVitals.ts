/**
 * Web Vitals 性能监控
 *
 * 监控关键性能指标：
 * - LCP (Largest Contentful Paint): 最大内容绘制时间 < 2.5s
 * - FID (First Input Delay): 首次输入延迟 < 100ms
 * - CLS (Cumulative Layout Shift): 累计布局偏移 < 0.1
 * - FCP (First Contentful Paint): 首次内容绘制 < 1.8s
 * - TTFB (Time to First Byte): 首字节时间 < 600ms
 * - INP (Interaction to Next Paint): 交互到下次绘制 < 200ms
 */

import { onCLS, onLCP, onFCP, onTTFB, onINP, type Metric } from 'web-vitals';

// 性能数据上报接口
interface PerformanceData {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
  navigationType: string;
  timestamp: number;
  url: string;
  userAgent: string;
}

/**
 * 发送性能指标到分析服务
 */
function sendToAnalytics(metric: Metric) {
  const data: PerformanceData = {
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
    timestamp: Date.now(),
    url: window.location.href,
    userAgent: navigator.userAgent,
  };

  // 开发环境：控制台输出
  if (import.meta.env.DEV) {
    console.log('📊 Web Vitals:', {
      metric: metric.name,
      value: `${Math.round(metric.value)}ms`,
      rating: metric.rating,
      delta: `${Math.round(metric.delta)}ms`,
    });
  }

  // 生产环境：发送到分析服务
  // 使用 sendBeacon 确保数据即使在页面卸载时也能发送
  if (import.meta.env.PROD) {
    const endpoint = '/api/analytics/web-vitals';

    if (navigator.sendBeacon) {
      // 优先使用 sendBeacon (更可靠)
      const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
      navigator.sendBeacon(endpoint, blob);
    } else {
      // 降级到 fetch (keepalive 确保请求完成)
      fetch(endpoint, {
        body: JSON.stringify(data),
        method: 'POST',
        keepalive: true,
        headers: {
          'Content-Type': 'application/json',
        },
      }).catch(err => {
        console.error('Failed to send performance data:', err);
      });
    }
  }
}

/**
 * 初始化 Web Vitals 监控
 */
export function initWebVitals() {
  // 监控 LCP - 最大内容绘制时间
  // 好: < 2.5s, 需要改进: 2.5s-4s, 差: > 4s
  onLCP(sendToAnalytics);

  // 监控 CLS - 累计布局偏移
  // 好: < 0.1, 需要改进: 0.1-0.25, 差: > 0.25
  onCLS(sendToAnalytics);

  // 监控 FCP - 首次内容绘制
  // 好: < 1.8s, 需要改进: 1.8s-3s, 差: > 3s
  onFCP(sendToAnalytics);

  // 监控 TTFB - 首字节时间
  // 好: < 600ms, 需要改进: 600ms-1.8s, 差: > 1.8s
  onTTFB(sendToAnalytics);

  // 监控 INP - 交互到下次绘制 (替代 FID 的新指标)
  // 好: < 200ms, 需要改进: 200ms-500ms, 差: > 500ms
  onINP(sendToAnalytics);
}

/**
 * 获取性能摘要
 */
export function getPerformanceSummary() {
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  const paint = performance.getEntriesByType('paint');

  const fcp = paint.find(entry => entry.name === 'first-contentful-paint');
  const lcp = paint.find(entry => entry.name === 'largest-contentful-paint');

  return {
    // 导航时间
    dns: Math.round(navigation.domainLookupEnd - navigation.domainLookupStart),
    tcp: Math.round(navigation.connectEnd - navigation.connectStart),
    ttfb: Math.round(navigation.responseStart - navigation.requestStart),
    download: Math.round(navigation.responseEnd - navigation.responseStart),
    domInteractive: Math.round(navigation.domInteractive - navigation.fetchStart),
    domComplete: Math.round(navigation.domComplete - navigation.fetchStart),
    loadComplete: Math.round(navigation.loadEventEnd - navigation.fetchStart),

    // 渲染时间
    fcp: fcp ? Math.round(fcp.startTime) : 0,
    lcp: lcp ? Math.round(lcp.startTime) : 0,

    // 资源统计
    resources: performance.getEntriesByType('resource').length,
  };
}

/**
 * 自定义性能标记
 */
export function markPerformance(name: string) {
  if (performance.mark) {
    performance.mark(name);
  }
}

/**
 * 测量两个标记之间的时间
 */
export function measurePerformance(name: string, startMark: string, endMark: string) {
  if (performance.measure) {
    try {
      performance.measure(name, startMark, endMark);
      const measure = performance.getEntriesByName(name)[0];
      console.log(`⏱️ ${name}: ${Math.round(measure.duration)}ms`);
      return measure.duration;
    } catch (error) {
      console.error('Failed to measure performance:', error);
      return 0;
    }
  }
  return 0;
}

/**
 * 清除性能标记和测量
 */
export function clearPerformanceMarks() {
  if (performance.clearMarks) {
    performance.clearMarks();
  }
  if (performance.clearMeasures) {
    performance.clearMeasures();
  }
}

/**
 * 监控资源加载性能
 */
export function monitorResourceLoading() {
  const resourceObserver = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      const resource = entry as PerformanceResourceTiming;

      // 只监控大于 100KB 的资源
      if (resource.transferSize > 102400) {
        console.warn('⚠️ Large resource detected:', {
          name: resource.name,
          size: `${Math.round(resource.transferSize / 1024)}KB`,
          duration: `${Math.round(resource.duration)}ms`,
          type: resource.initiatorType,
        });
      }
    }
  });

  resourceObserver.observe({ entryTypes: ['resource'] });

  return () => resourceObserver.disconnect();
}

/**
 * 监控长任务 (阻塞主线程 > 50ms)
 */
export function monitorLongTasks() {
  if ('PerformanceObserver' in window && PerformanceObserver.supportedEntryTypes?.includes('longtask')) {
    const longTaskObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.warn('⚠️ Long task detected:', {
          duration: `${Math.round(entry.duration)}ms`,
          startTime: `${Math.round(entry.startTime)}ms`,
        });
      }
    });

    longTaskObserver.observe({ entryTypes: ['longtask'] });

    return () => longTaskObserver.disconnect();
  }

  console.warn('Long task monitoring not supported');
  return () => {};
}
