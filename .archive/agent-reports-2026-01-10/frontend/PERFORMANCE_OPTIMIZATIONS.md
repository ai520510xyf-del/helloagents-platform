# HelloAgents Platform - 性能优化实施指南

本文档详细说明了如何实施性能报告中提出的优化建议。

---

## ✅ 已完成的优化

### 1. HTML 关键性能优化

**文件**: `index.html`

**优化内容**:
- ✅ 添加 DNS 预解析和预连接到后端 API
- ✅ 内联关键 CSS 减少渲染阻塞
- ✅ 优化字体加载策略 (`font-display: swap`)
- ✅ 添加加载骨架屏改善感知性能

**预期效果**: 减少首屏加载时间 200-400ms

---

### 2. HTTP Headers 缓存策略优化

**文件**: `public/_headers`

**优化内容**:
- ✅ 静态资源长期缓存 (1年, immutable)
- ✅ HTML 文件不缓存，始终验证
- ✅ 安全 Headers 增强
- ✅ CSP 策略配置

**预期效果**:
- 二次访问加载时间减少 80%+
- 减少服务器请求压力
- 提升安全性

---

## 🚀 待实施的高优先级优化

### 优化 #1: Monaco Editor 懒加载

**目标**: 减少首屏包大小 3.6MB，改善 LCP 2-3秒

#### 步骤 1: 创建懒加载组件包装器

```typescript
// src/components/CodeEditor/LazyCodeEditor.tsx
import { lazy, Suspense } from 'react';
import CodeEditorSkeleton from './CodeEditorSkeleton';

// 懒加载 Monaco Editor
const MonacoEditor = lazy(() => import('@monaco-editor/react'));

interface LazyCodeEditorProps {
  value: string;
  language: string;
  onChange?: (value: string | undefined) => void;
  height?: string;
  theme?: string;
  readOnly?: boolean;
}

export default function LazyCodeEditor(props: LazyCodeEditorProps) {
  return (
    <Suspense fallback={<CodeEditorSkeleton />}>
      <MonacoEditor {...props} />
    </Suspense>
  );
}
```

#### 步骤 2: 创建加载骨架屏

```typescript
// src/components/CodeEditor/CodeEditorSkeleton.tsx
import { Card } from '@/components/ui/Card';

export default function CodeEditorSkeleton() {
  return (
    <Card className="w-full h-[500px] animate-pulse">
      <div className="p-4 space-y-3">
        {/* 工具栏骨架 */}
        <div className="flex items-center justify-between border-b pb-2">
          <div className="flex gap-2">
            <div className="w-20 h-6 bg-gray-300 rounded"></div>
            <div className="w-20 h-6 bg-gray-300 rounded"></div>
          </div>
          <div className="w-16 h-6 bg-gray-300 rounded"></div>
        </div>

        {/* 代码行骨架 */}
        <div className="space-y-2">
          <div className="w-3/4 h-4 bg-gray-200 rounded"></div>
          <div className="w-full h-4 bg-gray-200 rounded"></div>
          <div className="w-5/6 h-4 bg-gray-200 rounded"></div>
          <div className="w-2/3 h-4 bg-gray-200 rounded"></div>
          <div className="w-full h-4 bg-gray-200 rounded"></div>
        </div>

        {/* 加载提示 */}
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center gap-2 text-gray-500">
            <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
            <span>正在加载代码编辑器...</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
```

#### 步骤 3: 更新使用代码编辑器的组件

```typescript
// src/pages/PlaygroundPage.tsx
import LazyCodeEditor from '@/components/CodeEditor/LazyCodeEditor';

export default function PlaygroundPage() {
  const [code, setCode] = useState('// 开始编写代码...\n');
  const [language, setLanguage] = useState('javascript');

  return (
    <div className="playground-container">
      {/* 只在需要时加载编辑器 */}
      <LazyCodeEditor
        value={code}
        language={language}
        onChange={(value) => setCode(value || '')}
        height="600px"
        theme="vs-dark"
      />
    </div>
  );
}
```

#### 步骤 4: 配置 Monaco Editor Worker 按需加载

```typescript
// src/components/CodeEditor/monaco-setup.ts
import * as monaco from 'monaco-editor';

// 配置 Worker
self.MonacoEnvironment = {
  getWorker(_, label) {
    switch (label) {
      case 'json':
        return new Worker(
          new URL('monaco-editor/esm/vs/language/json/json.worker', import.meta.url),
          { type: 'module' }
        );
      case 'css':
      case 'scss':
      case 'less':
        return new Worker(
          new URL('monaco-editor/esm/vs/language/css/css.worker', import.meta.url),
          { type: 'module' }
        );
      case 'html':
      case 'handlebars':
      case 'razor':
        return new Worker(
          new URL('monaco-editor/esm/vs/language/html/html.worker', import.meta.url),
          { type: 'module' }
        );
      case 'typescript':
      case 'javascript':
        return new Worker(
          new URL('monaco-editor/esm/vs/language/typescript/ts.worker', import.meta.url),
          { type: 'module' }
        );
      default:
        return new Worker(
          new URL('monaco-editor/esm/vs/editor/editor.worker', import.meta.url),
          { type: 'module' }
        );
    }
  },
};

// 只注册实际使用的语言
const SUPPORTED_LANGUAGES = [
  'javascript',
  'typescript',
  'python',
  'java',
  'cpp',
  'csharp',
  'go',
  'rust',
];

export function setupMonaco() {
  SUPPORTED_LANGUAGES.forEach((lang) => {
    monaco.languages.register({ id: lang });
  });
}
```

#### 测试验证

```bash
# 1. 构建项目
npm run build

# 2. 检查Bundle大小
ls -lh dist/assets/js/ | grep monaco

# 3. 预览应用
npm run preview

# 4. 运行 Lighthouse 测试
lighthouse http://localhost:4173 --view
```

**预期结果**:
- ✅ Monaco Editor 不再阻塞首屏加载
- ✅ 首屏包大小从 3.8MB 减少到 ~200KB
- ✅ LCP 改善 2-3 秒
- ✅ TTI 改善 2-4 秒

---

### 优化 #2: 路由级代码分割

**目标**: 减少主包大小 40-60%，按需加载路由组件

#### 步骤 1: 使用 React.lazy 懒加载路由组件

```typescript
// src/App.tsx
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PageLoadingSpinner from './components/ui/PageLoadingSpinner';

// 懒加载页面组件
const HomePage = lazy(() => import('./pages/HomePage'));
const LearnPage = lazy(() => import('./pages/LearnPage'));
const PlaygroundPage = lazy(() => import('./pages/PlaygroundPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const SkillDetailPage = lazy(() => import('./pages/SkillDetailPage'));

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoadingSpinner />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/learn" element={<LearnPage />} />
          <Route path="/playground" element={<PlaygroundPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/skills/:skillId" element={<SkillDetailPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

#### 步骤 2: 创建页面加载指示器

```typescript
// src/components/ui/PageLoadingSpinner.tsx
export default function PageLoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 to-indigo-700">
      <div className="text-center">
        {/* 动画 Logo */}
        <div className="mb-6 animate-bounce">
          <svg
            className="w-16 h-16 mx-auto text-white"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm1 11H9v-2h2v2zm0-4H9V5h2v4z" />
          </svg>
        </div>

        {/* 加载文本 */}
        <p className="text-white text-lg font-medium">
          正在加载页面...
        </p>

        {/* 加载进度条 */}
        <div className="mt-4 w-48 h-1 mx-auto bg-white/30 rounded-full overflow-hidden">
          <div className="h-full bg-white rounded-full animate-loading-bar"></div>
        </div>
      </div>
    </div>
  );
}
```

#### 步骤 3: 添加 CSS 动画

```css
/* src/index.css */
@keyframes loading-bar {
  0% {
    width: 0%;
    margin-left: 0%;
  }
  50% {
    width: 50%;
    margin-left: 25%;
  }
  100% {
    width: 0%;
    margin-left: 100%;
  }
}

.animate-loading-bar {
  animation: loading-bar 1.5s ease-in-out infinite;
}
```

#### 步骤 4: 优化 Vite 配置

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // 分离 vendor 包
          if (id.includes('node_modules')) {
            // React 相关
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor';
            }
            // Monaco Editor
            if (id.includes('monaco-editor') || id.includes('@monaco-editor')) {
              return 'monaco-editor';
            }
            // UI 组件库
            if (id.includes('lucide-react') || id.includes('react-resizable-panels')) {
              return 'ui-vendor';
            }
            // Markdown
            if (id.includes('react-markdown') || id.includes('remark') || id.includes('rehype')) {
              return 'markdown';
            }
            // 其他第三方库
            return 'vendor';
          }

          // 按路由分割代码
          if (id.includes('src/pages/')) {
            const page = id.split('src/pages/')[1].split('/')[0];
            return `page-${page}`;
          }
        },
      },
    },
  },
});
```

**预期结果**:
- ✅ 初始包大小减少到 80-100KB
- ✅ 后续路由按需加载 (10-30KB each)
- ✅ FCP 改善 0.5-1 秒
- ✅ 更快的路由切换

---

### 优化 #3: Tree Shaking 和移除未使用代码

**目标**: 减少未使用 JavaScript 1260ms

#### 步骤 1: 优化导入方式

```typescript
// ❌ 不好的做法 - 导入整个库
import * as LucideIcons from 'lucide-react';
import _ from 'lodash';

// ✅ 好的做法 - 只导入需要的
import { Home, Settings, User, Code } from 'lucide-react';
import debounce from 'lodash/debounce';
import throttle from 'lodash/throttle';
```

#### 步骤 2: 配置 Babel 移除 console

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import babel from '@rollup/plugin-babel';

export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 移除 console.log
        drop_debugger: true, // 移除 debugger
        pure_funcs: ['console.log', 'console.info', 'console.debug'],
      },
    },
  },
  plugins: [
    babel({
      babelHelpers: 'bundled',
      presets: [
        ['@babel/preset-env', {
          targets: 'last 2 versions, not dead',
          modules: false,
          useBuiltIns: 'usage',
          corejs: 3,
        }],
      ],
    }),
  ],
});
```

#### 步骤 3: 分析和移除未使用的依赖

```bash
# 使用 depcheck 查找未使用的依赖
npx depcheck

# 使用 webpack-bundle-analyzer 分析包大小
npm run build
# 打开 dist/stats.html 查看可视化分析

# 移除未使用的依赖
npm uninstall <unused-package>
```

#### 步骤 4: 优化 package.json

```json
{
  "dependencies": {
    // 只保留生产环境需要的包
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    // ... 其他必需的依赖
  },
  "devDependencies": {
    // 开发工具移到这里
    "@types/react": "^19.2.5",
    "vite": "^5.4.11",
    // ... 其他开发依赖
  },
  "sideEffects": false // 启用更激进的 Tree Shaking
}
```

**预期结果**:
- ✅ 包大小减少 20-30%
- ✅ 移除未使用代码节省 ~1260ms
- ✅ 更快的解析和执行时间

---

### 优化 #4: 图片优化

**目标**: 节省 1.6 秒加载时间

#### 步骤 1: 安装图片优化插件

```bash
npm install --save-dev vite-plugin-imagemin
```

#### 步骤 2: 配置 Vite

```typescript
// vite.config.ts
import imagemin from 'vite-plugin-imagemin';

export default defineConfig({
  plugins: [
    imagemin({
      gifsicle: { optimizationLevel: 7, interlaced: false },
      optipng: { optimizationLevel: 7 },
      mozjpeg: { quality: 80 },
      pngquant: { quality: [0.8, 0.9], speed: 4 },
      svgo: {
        plugins: [
          { name: 'removeViewBox', active: false },
          { name: 'removeEmptyAttrs', active: false },
        ],
      },
      webp: { quality: 80 },
      avif: { quality: 75 },
    }),
  ],
});
```

#### 步骤 3: 使用响应式图片组件

```typescript
// src/components/ui/ResponsiveImage.tsx
interface ResponsiveImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
}

export default function ResponsiveImage({
  src,
  alt,
  width,
  height,
  className = '',
}: ResponsiveImageProps) {
  const baseSrc = src.replace(/\.[^.]+$/, ''); // 移除扩展名

  return (
    <picture>
      {/* AVIF - 最佳压缩 */}
      <source srcSet={`${baseSrc}.avif`} type="image/avif" />

      {/* WebP - 良好兼容性 */}
      <source srcSet={`${baseSrc}.webp`} type="image/webp" />

      {/* 备用格式 */}
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading="lazy"
        decoding="async"
        className={className}
      />
    </picture>
  );
}
```

#### 步骤 4: 更新所有图片使用

```typescript
// Before
<img src="/logo.png" alt="Logo" />

// After
<ResponsiveImage
  src="/logo.png"
  alt="Logo"
  width={200}
  height={100}
/>
```

**预期结果**:
- ✅ 图片大小减少 50-70%
- ✅ 支持现代图片格式
- ✅ 懒加载优化
- ✅ 节省 ~1.6 秒

---

## 🔄 部署和验证

### 步骤 1: 本地测试

```bash
# 1. 安装依赖
npm install

# 2. 构建项目
npm run build

# 3. 预览构建
npm run preview

# 4. 打开浏览器测试
open http://localhost:4173
```

### 步骤 2: 性能测试

```bash
# 运行 Lighthouse 测试
lighthouse http://localhost:4173 --view

# 运行自定义性能测试
node performance-test.js

# 检查 Bundle 大小
ls -lh dist/assets/js/
```

### 步骤 3: 部署到 Cloudflare Pages

```bash
# 1. 提交更改
git add .
git commit -m "perf: implement P0 performance optimizations"

# 2. 推送到 GitHub
git push origin main

# 3. Cloudflare Pages 自动部署
# 访问: https://helloagents-platform.pages.dev
```

### 步骤 4: 生产环境验证

```bash
# 运行 Lighthouse 对生产环境
lighthouse https://helloagents-platform.pages.dev --view

# 对比优化前后
node performance-test.js

# 检查 Core Web Vitals
# 访问: https://search.google.com/test/mobile-friendly
```

---

## 📊 性能监控

### 实施 Web Vitals 监控

```typescript
// src/utils/web-vitals.ts
import { getCLS, getFID, getLCP, getTTFB, getFCP } from 'web-vitals';

interface AnalyticsPayload {
  name: string;
  value: number;
  rating: string;
  delta: number;
  id: string;
}

function sendToAnalytics(metric: AnalyticsPayload) {
  // 发送到后端分析服务
  const body = JSON.stringify(metric);

  // 使用 sendBeacon 确保数据发送
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/web-vitals', body);
  } else {
    // 备用方案
    fetch('/api/analytics/web-vitals', {
      method: 'POST',
      body,
      headers: { 'Content-Type': 'application/json' },
      keepalive: true,
    });
  }
}

// 在应用启动时初始化
export function initWebVitals() {
  getCLS(sendToAnalytics);
  getFID(sendToAnalytics);
  getLCP(sendToAnalytics);
  getTTFB(sendToAnalytics);
  getFCP(sendToAnalytics);
}
```

### 集成到主应用

```typescript
// src/main.tsx
import { initWebVitals } from './utils/web-vitals';

// 初始化 Web Vitals 监控
if (import.meta.env.PROD) {
  initWebVitals();
}
```

---

## ✅ 验收标准

### 性能指标目标

| 指标 | 当前值 | 目标值 | 验收标准 |
|------|--------|--------|----------|
| Lighthouse Performance (Desktop) | 60 | 85+ | ✅ >= 85 |
| Lighthouse Performance (Mobile) | 50 | 75+ | ✅ >= 75 |
| LCP (Desktop) | 5.6s | < 2.5s | ✅ < 2.5s |
| LCP (Mobile) | 9.0s | < 4.0s | ✅ < 4.0s |
| FCP (Desktop) | 2.8s | < 1.8s | ✅ < 1.8s |
| TTI (Desktop) | 5.7s | < 3.8s | ✅ < 3.8s |
| Initial Bundle | 191KB | < 100KB | ✅ < 100KB |
| CLS | 0 | < 0.1 | ✅ < 0.1 |
| TBT | 0ms/310ms | < 200ms | ✅ < 200ms |

### 功能验收

- [ ] 所有页面正常加载
- [ ] 路由切换流畅
- [ ] Monaco Editor 正常工作
- [ ] 代码执行功能正常
- [ ] 所有图片正常显示
- [ ] 移动端体验良好
- [ ] 离线功能可用（如实施）

---

## 🐛 故障排查

### 问题 1: Monaco Editor 不加载

**症状**: 代码编辑器区域空白或报错

**解决方案**:
1. 检查 Monaco Worker 配置
2. 确保 Vite 配置正确
3. 检查浏览器 Console 错误

```bash
# 清除缓存重新构建
rm -rf node_modules/.vite
npm run build
```

### 问题 2: 路由懒加载失败

**症状**: 页面切换时白屏或报错

**解决方案**:
1. 检查 Suspense 配置
2. 确保 fallback 组件正确
3. 检查动态导入路径

```typescript
// 确保路径正确
const HomePage = lazy(() => import('./pages/HomePage'));
// 不是
const HomePage = lazy(() => import('pages/HomePage'));
```

### 问题 3: 图片不显示

**症状**: 图片 404 或不加载

**解决方案**:
1. 检查图片路径
2. 确保图片在 public/ 目录
3. 检查 _headers 配置

```bash
# 检查图片是否存在
ls -la public/assets/images/
```

---

## 📚 参考资源

### 官方文档

- [Vite Performance Guide](https://vitejs.dev/guide/performance.html)
- [React Code Splitting](https://react.dev/reference/react/lazy)
- [Web.dev Performance](https://web.dev/performance/)
- [Monaco Editor Documentation](https://microsoft.github.io/monaco-editor/)

### 工具

- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [WebPageTest](https://www.webpagetest.org/)
- [Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)

---

**最后更新**: 2026-01-09
**版本**: v1.0
**状态**: ✅ 准备就绪
