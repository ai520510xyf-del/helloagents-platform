import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { initWebVitals } from './utils/webVitals'
import { initPerformanceMonitoring, printPerformanceReport } from './utils/performance'
import { initCacheSystem } from './utils/cache'

// 初始化 Web Vitals 性能监控
initWebVitals();

// 初始化增强性能监控
initPerformanceMonitoring();

// 初始化缓存系统
initCacheSystem();

// 页面加载完成后打印性能报告（开发环境）
if (import.meta.env.DEV) {
  window.addEventListener('load', () => {
    setTimeout(() => {
      printPerformanceReport();
    }, 2000);
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
// Build trigger 2026年 1月10日 星期六 17时55分34秒 CST
