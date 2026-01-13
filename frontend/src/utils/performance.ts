/**
 * Web Vitals 性能监控工具
 *
 * 监控关键性能指标：
 * - LCP (Largest Contentful Paint): < 2.5s
 * - FID (First Input Delay): < 100ms
 * - CLS (Cumulative Layout Shift): < 0.1
 * - INP (Interaction to Next Paint): < 200ms
 * - TTFB (Time to First Byte): < 800ms
 * - FCP (First Contentful Paint): < 1.8s
 */

import type { Metric } from 'web-vitals';

// 性能指标类型
export interface PerformanceMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
  navigationType: string;
  timestamp: number;
}

// 性能阈值配置
const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 },
  FID: { good: 100, poor: 300 },
  CLS: { good: 0.1, poor: 0.25 },
  INP: { good: 200, poor: 500 },
  TTFB: { good: 800, poor: 1800 },
  FCP: { good: 1800, poor: 3000 },
} as const;

// 评级函数（保留以供未来使用）
// @ts-ignore - 保留此函数供未来使用
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getRating(metricName: keyof typeof THRESHOLDS, value: number): 'good' | 'needs-improvement' | 'poor' {
  const threshold = THRESHOLDS[metricName];
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

// 格式化指标
function formatMetric(metric: Metric): PerformanceMetric {
  return {
    name: metric.name,
    value: metric.value,
    rating: metric.rating as 'good' | 'needs-improvement' | 'poor',
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
    timestamp: Date.now(),
  };
}

// 发送到分析服务
function sendToAnalytics(metric: PerformanceMetric) {
  const body = JSON.stringify(metric);

  // 尝试使用 sendBeacon (页面卸载时也能发送)
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/performance', body);
  } else {
    // 降级到 fetch with keepalive
    fetch('/api/analytics/performance', {
      body,
      method: 'POST',
      keepalive: true,
      headers: {
        'Content-Type': 'application/json',
      },
    }).catch((error) => {
      console.warn('Failed to send performance metric:', error);
    });
  }
}

// 控制台输出（开发环境）
function logMetric(metric: PerformanceMetric) {
  const emoji = metric.rating === 'good' ? '✅' : metric.rating === 'needs-improvement' ? '⚠️' : '❌';
  const color = metric.rating === 'good' ? 'color: #0cce6b' : metric.rating === 'needs-improvement' ? 'color: #ffa400' : 'color: #ff4e42';

  console.groupCollapsed(`${emoji} ${metric.name}: ${metric.value.toFixed(2)}ms`);
  console.log('%cRating:', color, metric.rating);
  console.log('Value:', metric.value.toFixed(2));
  console.log('Delta:', metric.delta.toFixed(2));
  console.log('ID:', metric.id);
  console.log('Navigation Type:', metric.navigationType);
  console.groupEnd();
}

// 初始化性能监控
export async function initPerformanceMonitoring() {
  // 使用静态导入以避免代码分割问题
  const { onCLS, onLCP, onINP, onTTFB, onFCP } = await import(/* webpackIgnore: true */ 'web-vitals/attribution');

  const handleMetric = (metric: Metric) => {
    const formattedMetric = formatMetric(metric);

    // 开发环境输出到控制台
    if (import.meta.env.DEV) {
      logMetric(formattedMetric);
    }

    // 发送到分析服务（生产环境）
    if (import.meta.env.PROD) {
      sendToAnalytics(formattedMetric);
    }

    // 触发自定义事件，允许其他模块监听
    window.dispatchEvent(
      new CustomEvent('web-vitals-metric', {
        detail: formattedMetric,
      })
    );
  };

  // 监控所有核心 Web Vitals
  onCLS(handleMetric);
  onLCP(handleMetric);
  onINP(handleMetric);
  onTTFB(handleMetric);
  onFCP(handleMetric);

  console.log('🚀 Web Vitals monitoring initialized');
}

// 性能标记工具
export class PerformanceMarker {
  private marks: Map<string, number> = new Map();

  /**
   * 标记开始时间
   */
  start(name: string) {
    this.marks.set(`${name}-start`, performance.now());
    performance.mark(`${name}-start`);
  }

  /**
   * 标记结束时间并计算耗时
   */
  end(name: string): number {
    const endTime = performance.now();
    performance.mark(`${name}-end`);

    const startTime = this.marks.get(`${name}-start`);
    if (!startTime) {
      console.warn(`No start mark found for "${name}"`);
      return 0;
    }

    const duration = endTime - startTime;

    // 创建性能测量
    try {
      performance.measure(name, `${name}-start`, `${name}-end`);
    } catch (error) {
      console.warn(`Failed to measure "${name}":`, error);
    }

    // 清理标记
    this.marks.delete(`${name}-start`);

    if (import.meta.env.DEV) {
      console.log(`⏱️ ${name}: ${duration.toFixed(2)}ms`);
    }

    return duration;
  }

  /**
   * 获取标记的耗时（不清理标记）
   */
  getDuration(name: string): number {
    const startTime = this.marks.get(`${name}-start`);
    if (!startTime) {
      return 0;
    }
    return performance.now() - startTime;
  }

  /**
   * 清除所有标记
   */
  clear() {
    this.marks.clear();
    performance.clearMarks();
    performance.clearMeasures();
  }
}

// 导出单例
export const performanceMarker = new PerformanceMarker();

/**
 * 资源加载性能分析
 */
export function analyzeResourcePerformance() {
  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

  const analysis = {
    scripts: [] as { name: string; duration: number; size: number }[],
    stylesheets: [] as { name: string; duration: number; size: number }[],
    images: [] as { name: string; duration: number; size: number }[],
    fonts: [] as { name: string; duration: number; size: number }[],
    totalScriptSize: 0,
    totalStylesheetSize: 0,
    totalImageSize: 0,
    totalFontSize: 0,
  };

  resources.forEach((resource) => {
    const duration = resource.responseEnd - resource.startTime;
    const size = resource.transferSize || 0;
    const name = resource.name.split('/').pop() || resource.name;

    const resourceInfo = { name, duration, size };

    if (resource.initiatorType === 'script' || resource.name.endsWith('.js')) {
      analysis.scripts.push(resourceInfo);
      analysis.totalScriptSize += size;
    } else if (resource.initiatorType === 'link' || resource.name.endsWith('.css')) {
      analysis.stylesheets.push(resourceInfo);
      analysis.totalStylesheetSize += size;
    } else if (resource.initiatorType === 'img' || /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(resource.name)) {
      analysis.images.push(resourceInfo);
      analysis.totalImageSize += size;
    } else if (resource.initiatorType === 'css' && /\.(woff|woff2|ttf|otf|eot)$/i.test(resource.name)) {
      analysis.fonts.push(resourceInfo);
      analysis.totalFontSize += size;
    }
  });

  // 按大小排序
  analysis.scripts.sort((a, b) => b.size - a.size);
  analysis.stylesheets.sort((a, b) => b.size - a.size);
  analysis.images.sort((a, b) => b.size - a.size);
  analysis.fonts.sort((a, b) => b.size - a.size);

  return analysis;
}

/**
 * 打印性能报告
 */
export function printPerformanceReport() {
  console.group('📊 Performance Report');

  // Navigation Timing
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  if (navigation) {
    console.group('⏱️ Navigation Timing');
    console.log('DNS Lookup:', (navigation.domainLookupEnd - navigation.domainLookupStart).toFixed(2), 'ms');
    console.log('TCP Connection:', (navigation.connectEnd - navigation.connectStart).toFixed(2), 'ms');
    console.log('Request:', (navigation.responseStart - navigation.requestStart).toFixed(2), 'ms');
    console.log('Response:', (navigation.responseEnd - navigation.responseStart).toFixed(2), 'ms');
    console.log('DOM Processing:', (navigation.domComplete - navigation.domInteractive).toFixed(2), 'ms');
    console.log('Load Complete:', (navigation.loadEventEnd - navigation.loadEventStart).toFixed(2), 'ms');
    console.groupEnd();
  }

  // Resource Analysis
  const resourceAnalysis = analyzeResourcePerformance();
  console.group('📦 Resource Analysis');
  console.log('Scripts:', resourceAnalysis.scripts.length, 'files,', (resourceAnalysis.totalScriptSize / 1024).toFixed(2), 'KB');
  console.log('Stylesheets:', resourceAnalysis.stylesheets.length, 'files,', (resourceAnalysis.totalStylesheetSize / 1024).toFixed(2), 'KB');
  console.log('Images:', resourceAnalysis.images.length, 'files,', (resourceAnalysis.totalImageSize / 1024).toFixed(2), 'KB');
  console.log('Fonts:', resourceAnalysis.fonts.length, 'files,', (resourceAnalysis.totalFontSize / 1024).toFixed(2), 'KB');

  if (resourceAnalysis.scripts.length > 0) {
    console.group('Top 5 Largest Scripts:');
    resourceAnalysis.scripts.slice(0, 5).forEach((script, index) => {
      console.log(`${index + 1}.`, script.name, '-', (script.size / 1024).toFixed(2), 'KB');
    });
    console.groupEnd();
  }
  console.groupEnd();

  console.groupEnd();
}
