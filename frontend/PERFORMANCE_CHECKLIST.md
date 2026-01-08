# 前端性能优化检查清单

快速参考指南，用于日常开发中的性能检查。

---

## 开发阶段

### 组件开发
- [ ] 高频渲染的组件使用 `React.memo`
- [ ] 回调函数使用 `useCallback` 稳定引用
- [ ] 昂贵计算使用 `useMemo` 缓存结果
- [ ] 避免在 render 中创建新对象/数组
- [ ] 使用 `key` 优化列表渲染

### 代码导入
- [ ] 按需导入，避免 `import *`
- [ ] 大型组件使用 `lazy()` 懒加载
- [ ] 第三方库优先使用 ES Module 版本
- [ ] 避免导入整个库 (如 lodash)

### 资源加载
- [ ] 图片使用懒加载
- [ ] 大文件异步加载
- [ ] 非关键资源延迟加载
- [ ] 使用现代图片格式 (WebP, AVIF)

---

## 构建阶段

### 打包配置
- [ ] 启用代码分割 (manualChunks)
- [ ] 启用 Gzip/Brotli 压缩
- [ ] 启用 Tree shaking
- [ ] 生产环境移除 console
- [ ] 关闭生产环境 sourcemap

### Bundle 分析
- [ ] 运行 `npm run build`
- [ ] 查看 `dist/stats.html`
- [ ] 检查主包大小 < 200KB
- [ ] 检查第三方库大小
- [ ] 识别重复依赖

---

## 测试阶段

### 性能测试
- [ ] 运行 Lighthouse 测试 (目标 > 90)
- [ ] 检查 Web Vitals 指标
  - LCP < 2.5s
  - FID < 100ms
  - CLS < 0.1
- [ ] 检查首屏加载时间 < 2s
- [ ] 检查交互响应时间 < 100ms

### 功能测试
- [ ] 运行 `npm run test`
- [ ] 运行 `npx tsc --noEmit`
- [ ] 手动测试关键功能
- [ ] 检查无性能回归

---

## 监控阶段

### 开发环境
- [ ] 查看控制台 Web Vitals 输出
- [ ] 监控长任务警告 (> 50ms)
- [ ] 监控大资源警告 (> 100KB)
- [ ] 使用 React DevTools Profiler

### 生产环境
- [ ] 配置 Web Vitals 上报
- [ ] 设置性能监控告警
- [ ] 定期查看性能报告
- [ ] 监控性能回归

---

## 常见性能陷阱

### ❌ 避免
```typescript
// ❌ 在 render 中创建新函数
<Button onClick={() => handleClick(id)} />

// ❌ 在 render 中创建新对象
<Component style={{ color: 'red' }} />

// ❌ 没有依赖数组
useEffect(() => { }, []);  // 缺少依赖

// ❌ 导入整个库
import * as _ from 'lodash';
```

### ✅ 推荐
```typescript
// ✅ 使用 useCallback
const handleClick = useCallback(() => { }, []);
<Button onClick={handleClick} />

// ✅ 提取到组件外
const buttonStyle = { color: 'red' };
<Component style={buttonStyle} />

// ✅ 正确的依赖数组
useEffect(() => { }, [dep1, dep2]);

// ✅ 按需导入
import { debounce } from 'lodash-es';
```

---

## 快速命令

```bash
# 开发
npm run dev

# 构建
npm run build

# 预览
npm run preview

# 测试
npm run test

# 类型检查
npx tsc --noEmit

# Bundle 分析
npm run build && open dist/stats.html

# 查看 Bundle 大小
ls -lh dist/assets/js/
```

---

## 性能指标速查

| 指标 | 好 | 需改进 | 差 |
|------|-----|--------|-----|
| LCP | < 2.5s | 2.5-4s | > 4s |
| FID | < 100ms | 100-300ms | > 300ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |
| FCP | < 1.8s | 1.8-3s | > 3s |
| TTFB | < 600ms | 600ms-1.8s | > 1.8s |
| INP | < 200ms | 200-500ms | > 500ms |

---

## 紧急优化流程

### 当 Lighthouse 评分 < 70
1. 检查 Bundle 大小 (查看 stats.html)
2. 检查是否有未压缩的资源
3. 检查是否有阻塞渲染的脚本
4. 检查是否缺少代码分割

### 当页面卡顿
1. 使用 React DevTools Profiler
2. 检查是否有频繁重渲染
3. 检查是否有长任务 (> 50ms)
4. 检查是否有内存泄漏

### 当 Bundle 过大 (> 500KB)
1. 查看 dist/stats.html 分析
2. 识别最大的依赖
3. 考虑替换或懒加载
4. 检查是否有重复依赖

---

**更新日期**: 2026-01-08
**维护者**: Frontend Performance Engineer
