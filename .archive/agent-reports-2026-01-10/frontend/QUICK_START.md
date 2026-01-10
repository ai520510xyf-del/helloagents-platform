# 🚀 HelloAgents Platform - 优化快速上手指南

> 本指南帮助开发者快速了解和使用本次优化的新功能和组件

---

## 📦 新增组件使用指南

### 1. Toast 通知系统

**位置**: `src/components/ui/Toast.tsx` + `src/hooks/useToast.ts`

#### 基础使用

```tsx
import { useToast } from '../hooks/useToast';
import { ToastContainer } from '../components/ui/Toast';

function MyComponent() {
  const { success, error, warning, info, toasts } = useToast();

  const handleSuccess = () => {
    success('操作成功！', 3000);
  };

  const handleError = () => {
    error('操作失败，请重试', 5000);
  };

  return (
    <div>
      <button onClick={handleSuccess}>成功通知</button>
      <button onClick={handleError}>错误通知</button>

      {/* 添加 ToastContainer */}
      <ToastContainer toasts={toasts} position="top-right" />
    </div>
  );
}
```

#### API

```typescript
// Hook返回值
interface UseToastReturn {
  toasts: ToastProps[];           // 当前所有toast
  success: (msg: string, duration?: number) => string;
  error: (msg: string, duration?: number) => string;
  warning: (msg: string, duration?: number) => string;
  info: (msg: string, duration?: number) => string;
  removeToast: (id: string) => void;
}

// 位置选项
type Position =
  | 'top-right'    // 右上角（默认）
  | 'top-left'     // 左上角
  | 'bottom-right' // 右下角
  | 'bottom-left'  // 左下角
  | 'top-center'   // 顶部居中
  | 'bottom-center'; // 底部居中
```

---

### 2. 加载指示器组件

**位置**: `src/components/ui/LoadingSpinner.tsx`

#### A. LoadingSpinner - 旋转加载器

```tsx
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

// 基础使用
<LoadingSpinner size="md" variant="primary" />

// 带标签
<LoadingSpinner size="lg" variant="white" label="加载中..." />

// 在按钮中
<button disabled>
  <LoadingSpinner size="sm" variant="white" />
  <span>提交中...</span>
</button>
```

**Props**:
- `size`: `'xs' | 'sm' | 'md' | 'lg' | 'xl'`
- `variant`: `'primary' | 'white' | 'current'`
- `label`: 可选文字标签

#### B. LoadingOverlay - 全屏加载遮罩

```tsx
import { LoadingOverlay } from '../components/ui/LoadingSpinner';

<LoadingOverlay
  show={isLoading}
  message="正在加载课程..."
  theme="dark"
/>
```

#### C. Skeleton - 骨架屏占位

```tsx
import { Skeleton } from '../components/ui/LoadingSpinner';

// 矩形骨架
<Skeleton width="100%" height="20px" />

// 圆形骨架
<Skeleton width="40px" height="40px" circle />

// 自定义样式
<Skeleton className="mb-2" width="200px" height="16px" />
```

#### D. PulseLoader - 脉冲加载点

```tsx
import { PulseLoader } from '../components/ui/LoadingSpinner';

<PulseLoader count={3} size="md" />
```

#### E. ProgressBar - 进度条

```tsx
import { ProgressBar } from '../components/ui/LoadingSpinner';

<ProgressBar
  value={75}
  max={100}
  showLabel
  variant="success"
  size="md"
/>
```

**Props**:
- `value`: 当前值
- `max`: 最大值（默认100）
- `showLabel`: 是否显示百分比
- `variant`: `'primary' | 'success' | 'warning' | 'error'`
- `size`: `'sm' | 'md' | 'lg'`

---

## 🎨 增强的样式系统

### 新增Tailwind类

#### 动画类

```tsx
// 淡入动画
<div className="animate-fade-in">内容</div>

// 滑入动画
<div className="animate-slide-in">内容</div>
<div className="animate-slide-up">内容</div>
<div className="animate-slide-down">内容</div>

// 缩放动画
<div className="animate-scale-in">内容</div>

// 微妙弹跳
<div className="animate-bounce-subtle">图标</div>

// 发光脉冲
<div className="animate-pulse-glow">按钮</div>

// 闪烁效果
<div className="animate-shimmer">加载中</div>
```

#### 骨架屏类

```tsx
// 深色主题自动适配
<div className="skeleton h-4 w-32 rounded" />
```

#### Tab过渡类

```tsx
// 在切换的内容上使用
<div className="tab-transition">
  {/* 内容 */}
</div>
```

#### 触摸反馈类

```tsx
// 按钮按压反馈
<button className="touch-feedback">点击我</button>

// 涟漪效果（需要额外JS）
<button className="ripple-effect">点击我</button>
```

---

## 🎨 优化的颜色系统

### 主题颜色变体

```tsx
// Primary颜色
bg-primary          // 默认 #3B82F6
bg-primary-light    // 浅色 #60A5FA
bg-primary-dark     // 深色 #2563EB

// 状态颜色
bg-success          // 成功 #10B981
bg-success-light    // 浅色 #34D399
bg-success-dark     // 深色 #059669

bg-warning          // 警告 #F59E0B
bg-error            // 错误 #EF4444
bg-info             // 信息 #3B82F6
bg-ai               // AI色 #A855F7
```

### 文字颜色 (优化对比度)

```tsx
// 暗黑主题
text-text-primary    // #F8FAFC (提升对比度)
text-text-secondary  // #CBD5E1 (更清晰)
text-text-muted      // #94A3B8
text-text-disabled   // #64748B

// 亮色主题
dark:text-text-light-primary    // #0F172A
dark:text-text-light-secondary  // #475569
```

---

## 📱 移动端优化要点

### 1. 触摸区域

所有交互元素最小 **44×44px**（自动应用）

### 2. 虚拟键盘处理

```tsx
// input字段自动16px，防止iOS缩放
<input type="text" className="..." />

// 监听键盘显示
useEffect(() => {
  const handleFocus = () => document.body.classList.add('keyboard-visible');
  const handleBlur = () => document.body.classList.remove('keyboard-visible');

  // 添加事件监听...
}, []);
```

### 3. Monaco编辑器移动端配置

```tsx
<CodeEditor
  value={code}
  onChange={onChange}
  language="python"
  theme={theme}
  isMobile={true}  // 启用移动端优化
/>
```

**自动优化项**:
- ✅ 禁用小地图
- ✅ 自动换行
- ✅ 简化滚动条
- ✅ 关闭快速建议
- ✅ 禁用右键菜单
- ✅ 平滑滚动

---

## 🔧 响应式断点

```typescript
// 使用 useResponsiveLayout Hook
const { layoutType, isMobile, isTablet, isDesktop } = useResponsiveLayout();

// 断点定义
mobile: < 768px
tablet: 768px - 1024px
desktop: > 1024px
```

### Tailwind响应式前缀

```tsx
// 移动优先
<div className="text-sm md:text-base lg:text-lg">
  响应式文字
</div>

<div className="px-3 md:px-6 lg:px-12">
  响应式间距
</div>

<div className="hidden md:block">
  平板及以上显示
</div>
```

---

## ✨ 增强的Button组件

### 新特性

```tsx
import { Button } from '../components/ui/Button';

// 基础使用
<Button variant="primary" size="md">
  点击我
</Button>

// 加载状态
<Button isLoading>提交中...</Button>

// 禁用状态
<Button disabled>不可用</Button>

// 变体
<Button variant="primary">主按钮</Button>
<Button variant="secondary">次要按钮</Button>
<Button variant="cta">行动号召</Button>
<Button variant="destructive">危险操作</Button>
<Button variant="ghost">幽灵按钮</Button>
<Button variant="success">成功按钮</Button>
```

**自动优化**:
- ✅ 按压反馈 (`active:scale-95`)
- ✅ 阴影效果 (`hover:shadow-md`)
- ✅ 触摸优化 (`touch-manipulation`)
- ✅ 最小触摸区域 (`min-w-[44px]`)
- ✅ 平滑过渡 (`transition-all duration-200`)

---

## 🎯 TerminalOutput组件增强

### 新特性

**自动错误检测**:
```tsx
<TerminalOutput
  output={output}
  isRunning={isRunning}
  theme={theme}
  onClear={clearOutput}
/>
```

**自动识别**:
- ✅ 错误输出（红色高亮）
- ✅ 成功执行（绿色徽章）
- ✅ 运行状态（黄色脉冲）

---

## 📐 新增间距

```tsx
// 新增间距档位
gap-18    // 4.5rem (72px)
w-88      // 22rem (352px)
h-128     // 32rem (512px)
```

---

## 🔤 新增字体大小

```tsx
text-2xs  // 0.625rem (10px) - 用于徽章、标签
```

---

## 🧪 测试建议

### 移动端测试清单

- [ ] iPhone SE (375×667) - 小屏幕边界
- [ ] iPhone 12 (390×844) - 标准尺寸
- [ ] iPhone 14 Pro Max (430×932) - 大屏幕
- [ ] iPad Mini (768×1024) - 平板布局
- [ ] iPad Pro (1024×1366) - 大平板
- [ ] Android设备 - 实机测试

### 交互测试清单

- [ ] 按钮点击反馈明显
- [ ] Tab切换动画流畅
- [ ] 主题切换无闪烁
- [ ] Toast通知正常显示
- [ ] 加载状态清晰可见
- [ ] Monaco编辑器流畅

### 样式测试清单

- [ ] 暗黑主题完整
- [ ] 亮色主题完整
- [ ] 文字对比度充足
- [ ] 响应式布局正常
- [ ] 滚动条主题正确

---

## 🐛 常见问题

### Q: Toast不显示？

**A**: 确保添加了 `<ToastContainer>`：
```tsx
<ToastContainer toasts={toasts} position="top-right" />
```

### Q: 移动端编辑器卡顿？

**A**: 确保传入 `isMobile={true}`：
```tsx
<CodeEditor isMobile={true} />
```

### Q: 动画不流畅？

**A**: 检查是否启用了 `prefers-reduced-motion`：
```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}
```

### Q: 主题切换有问题？

**A**: 确保正确应用了 `dark` 类到 `<html>` 元素：
```tsx
useEffect(() => {
  document.documentElement.classList.toggle('dark', theme === 'dark');
}, [theme]);
```

---

## 📚 参考资源

- **完整优化报告**: `OPTIMIZATION_REPORT.md`
- **组件源码**: `src/components/ui/`
- **Hooks**: `src/hooks/`
- **样式配置**: `tailwind.config.js`
- **全局样式**: `src/index.css`

---

## 🤝 贡献指南

### 添加新组件

1. 创建组件文件: `src/components/ui/YourComponent.tsx`
2. 遵循现有命名和结构
3. 添加TypeScript类型定义
4. 使用Tailwind类名
5. 支持暗黑/亮色主题
6. 添加无障碍属性

### 样式规范

- ✅ 使用Tailwind utility类
- ✅ 使用主题颜色变量
- ✅ 支持响应式断点
- ✅ 添加平滑过渡
- ✅ 触摸优化

### 性能要求

- ✅ 使用 `memo` 优化组件
- ✅ 使用 `useMemo` 缓存计算
- ✅ 使用 `useCallback` 稳定函数
- ✅ 避免不必要的re-render

---

**更新时间**: 2026-01-09
**版本**: v1.0

*Happy Coding! 🚀*
