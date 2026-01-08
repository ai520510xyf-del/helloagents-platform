# 前端性能优化文档

## 概述

本文档记录了 HelloAgents 平台前端的性能优化措施和最佳实践。

## 性能目标

- **首屏加载时间**: < 2s
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **Bundle Size (gzipped)**: < 300KB (主包)

## 已实施的优化措施

### 1. 代码分割与懒加载

#### 路由级别代码分割
```typescript
// src/App.tsx
import { lazy, Suspense } from 'react';

// 懒加载 LearnPage
const LearnPage = lazy(() =>
  import('./pages/LearnPage').then(module => ({
    default: module.LearnPage,
  }))
);

// 使用 Suspense 提供加载状态
<Suspense fallback={<PageLoading theme="dark" />}>
  <LearnPage />
</Suspense>
```

**效果**:
- 减少初始 Bundle 大小
- 加快首屏加载速度
- 按需加载页面组件

#### Vite 手动分块配置
```typescript
// vite.config.ts
manualChunks: {
  'react-vendor': ['react', 'react-dom'],           // ~150KB
  'monaco-editor': ['monaco-editor', '@monaco-editor/react'], // ~800KB
  'markdown': ['react-markdown', 'remark-gfm', 'rehype-raw'],
  'ui-vendor': ['lucide-react', 'react-resizable-panels', 'react-toastify'],
  'utils': ['axios', 'zustand', 'socket.io-client'],
}
```

**效果**:
- 将大型第三方库独立打包
- 利用浏览器缓存
- 支持并行下载

---

### 2. React 组件性能优化

#### React.memo 防止不必要的重渲染
```typescript
// NavigationBar, CourseMenu, CodeEditorPanel 都已优化

export const NavigationBar = memo(function NavigationBar({ ... }) {
  // 组件内容
}, (prevProps, nextProps) => {
  // 自定义比较函数
  return (
    prevProps.progress === nextProps.progress &&
    prevProps.theme === nextProps.theme &&
    prevProps.currentLesson.id === nextProps.currentLesson.id
  );
});
```

**优化的组件**:
- ✅ `NavigationBar`: 仅在 progress/theme/lesson 变化时更新
- ✅ `CourseMenu`: 仅在 currentLesson.id/theme 变化时更新
- ✅ `CodeEditorPanel`: 仅在 code/theme/isRunning 等关键属性变化时更新

#### useCallback 和 useMemo 优化
```typescript
// LearnPage.tsx

// 稳定回调函数引用
const toggleTheme = useCallback(() => {
  setTheme(prev => prev === 'dark' ? 'light' : 'dark');
}, []);

const handleLessonChange = useCallback(async (lessonId: string) => {
  // ...
}, [changeLesson, clearOutput]);

const handleRunCode = useCallback(() => {
  runCode(code);
}, [code, runCode]);

// 缓存计算结果
const progress = useMemo(() => calculateProgress(), []);
```

**效果**:
- 避免子组件因父组件重渲染而重新渲染
- 减少函数重新创建
- 缓存昂贵的计算结果

---

### 3. 打包构建优化

#### 压缩配置
```typescript
// vite.config.ts
build: {
  // Gzip 压缩
  compression({ algorithm: 'gzip', ext: '.gz' }),

  // Brotli 压缩 (更高压缩率)
  compression({ algorithm: 'brotliCompress', ext: '.br' }),

  // Terser 压缩
  minify: 'terser',
  terserOptions: {
    compress: {
      drop_console: true,       // 移除 console
      drop_debugger: true,      // 移除 debugger
      pure_funcs: ['console.log', 'console.info'],
    },
  },
}
```

**效果**:
- Gzip 压缩率: ~70%
- Brotli 压缩率: ~75%
- 生产环境自动移除 console 和 debugger

#### Bundle 分析
```bash
# 构建时生成分析报告
npm run build

# 查看报告
open dist/stats.html
```

**报告内容**:
- 各模块大小分布
- Gzip/Brotli 压缩后大小
- 依赖关系树状图

---

### 4. Web Vitals 性能监控

#### 监控的指标
```typescript
// src/utils/webVitals.ts

// 核心指标
- LCP (Largest Contentful Paint)     目标: < 2.5s
- FID (First Input Delay)            目标: < 100ms
- CLS (Cumulative Layout Shift)      目标: < 0.1
- FCP (First Contentful Paint)       目标: < 1.8s
- TTFB (Time to First Byte)          目标: < 600ms
- INP (Interaction to Next Paint)    目标: < 200ms
```

#### 使用方式
```typescript
// main.tsx 自动初始化
import { initWebVitals } from './utils/webVitals';

initWebVitals();
```

**功能**:
- ✅ 开发环境：控制台输出性能数据
- ✅ 生产环境：上报到分析服务 (使用 sendBeacon)
- ✅ 监控长任务 (> 50ms)
- ✅ 监控大资源 (> 100KB)

---

### 5. 资源优化

#### 依赖预构建
```typescript
// vite.config.ts
optimizeDeps: {
  include: ['react', 'react-dom', 'axios', 'zustand'],
  exclude: ['monaco-editor'], // Monaco 已优化，无需预构建
}
```

#### CSS 代码分割
```typescript
build: {
  cssCodeSplit: true,  // 启用 CSS 代码分割
}
```

**效果**:
- 按需加载 CSS
- 减少初始加载大小
- 提高缓存效率

---

## 性能测试

### 本地测试

#### 1. Lighthouse 测试
```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 使用 Chrome DevTools > Lighthouse 运行测试
```

**目标评分**:
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

#### 2. Bundle 大小分析
```bash
npm run build

# 查看 dist/ 目录
ls -lh dist/assets/js/

# 查看可视化报告
open dist/stats.html
```

#### 3. 开发环境监控
```bash
npm run dev

# 打开浏览器控制台，查看 Web Vitals 输出
# 示例输出:
# 📊 Web Vitals: { metric: 'LCP', value: '1234ms', rating: 'good' }
```

---

## 性能优化检查清单

### 代码层面
- [x] 路由级别懒加载
- [x] 使用 React.memo 避免不必要的重渲染
- [x] 使用 useCallback 稳定回调函数
- [x] 使用 useMemo 缓存计算结果
- [ ] 图片懒加载 (future)
- [ ] 虚拟滚动 (如果有长列表)

### 构建层面
- [x] 代码分割 (手动 chunks)
- [x] Gzip/Brotli 压缩
- [x] Tree shaking
- [x] 移除生产环境 console
- [x] CSS 代码分割
- [x] 关闭生产环境 sourcemap

### 监控层面
- [x] Web Vitals 监控
- [x] 长任务监控
- [x] 资源加载监控
- [x] Bundle 大小分析

---

## 最佳实践

### 1. 组件开发
```typescript
// ✅ 好的做法
export const MyComponent = memo(function MyComponent({ data }) {
  const handleClick = useCallback(() => {
    // 处理点击
  }, []);

  const expensiveValue = useMemo(() => {
    return computeExpensiveValue(data);
  }, [data]);

  return <div onClick={handleClick}>{expensiveValue}</div>;
});

// ❌ 不好的做法
export function MyComponent({ data }) {
  // 每次渲染都创建新函数
  const handleClick = () => { };

  // 每次渲染都重新计算
  const expensiveValue = computeExpensiveValue(data);

  return <div onClick={handleClick}>{expensiveValue}</div>;
}
```

### 2. 导入优化
```typescript
// ✅ 好的做法 - 按需导入
import { useState, useCallback } from 'react';
import { Play, Stop } from 'lucide-react';

// ❌ 不好的做法 - 导入整个库
import * as React from 'react';
import * as Icons from 'lucide-react';
```

### 3. 懒加载
```typescript
// ✅ 好的做法 - 使用 lazy 和 Suspense
const HeavyComponent = lazy(() => import('./HeavyComponent'));

<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>

// ❌ 不好的做法 - 直接导入
import HeavyComponent from './HeavyComponent';
```

---

## 性能预算

### Bundle 大小限制
- **主包 (main)**: < 200KB (gzipped)
- **React Vendor**: < 150KB (gzipped)
- **Monaco Editor**: < 500KB (gzipped)
- **其他 Vendor**: < 100KB (gzipped)

### 运行时性能
- **首屏渲染**: < 2s
- **交互响应**: < 100ms
- **页面切换**: < 500ms

---

## 持续优化

### 定期检查
1. **每周**: 运行 Lighthouse 审计
2. **每次发布**: 检查 Bundle 大小变化
3. **每月**: 分析 Web Vitals 数据

### 性能回归监控
```bash
# 构建前记录 Bundle 大小
npm run build
du -sh dist/

# 对比变化
# 如果增长超过 10%，需要调查原因
```

### 工具推荐
- **Chrome DevTools**: Performance, Coverage, Network
- **Lighthouse**: 性能评分和建议
- **webpack-bundle-analyzer**: Bundle 可视化 (已集成)
- **web-vitals**: 性能监控库 (已集成)

---

## 问题排查

### Q: 首屏加载时间过长
**检查项**:
1. Bundle 大小是否超标
2. 是否有阻塞渲染的资源
3. 网络请求是否过多
4. 是否缺少代码分割

### Q: 页面卡顿
**检查项**:
1. 是否有长任务 (> 50ms)
2. 组件是否频繁重渲染
3. 是否有昂贵的计算未缓存
4. 是否有内存泄漏

### Q: Bundle 体积过大
**检查项**:
1. 查看 `dist/stats.html` 分析报告
2. 检查是否有重复依赖
3. 是否可以移除未使用的库
4. 是否可以替换为更小的库

---

## 相关文档

- [Vite 性能优化](https://vitejs.dev/guide/performance.html)
- [React 性能优化](https://react.dev/learn/render-and-commit)
- [Web Vitals](https://web.dev/vitals/)
- [Core Web Vitals](https://web.dev/articles/vitals)

---

## 更新日志

### 2026-01-08
- ✅ 实现路由懒加载
- ✅ 优化 Vite 配置 (代码分割、压缩)
- ✅ 创建 Loading 组件
- ✅ 优化 React 组件 (memo、useCallback、useMemo)
- ✅ 实现 Web Vitals 监控
- ✅ 创建性能优化文档

---

**维护者**: Frontend Performance Engineer
**最后更新**: 2026-01-08
