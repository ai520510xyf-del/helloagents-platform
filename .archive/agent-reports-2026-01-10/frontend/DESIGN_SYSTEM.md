# HelloAgents 设计系统

## 目录

1. [设计原则](#设计原则)
2. [颜色系统](#颜色系统)
3. [排版系统](#排版系统)
4. [间距系统](#间距系统)
5. [组件库](#组件库)
6. [动画系统](#动画系统)
7. [可访问性规范](#可访问性规范)

---

## 设计原则

### 1. Minimalism（极简主义）
- 去除不必要的装饰
- 专注核心功能
- 清晰的视觉层级

### 2. Consistency（一致性）
- 统一的视觉语言
- 可预测的交互模式
- 复用设计模式

### 3. Accessibility First（可访问性优先）
- WCAG 2.1 AA 标准
- 键盘导航友好
- 屏幕阅读器支持

### 4. Performance（性能）
- 快速加载
- 流畅动画（60fps）
- 渐进式增强

---

## 颜色系统

### 主色调（Primary）
用于主要操作、链接、重点强调

```css
--primary-50: #EFF6FF;
--primary-100: #DBEAFE;
--primary-500: #3B82F6;  /* 默认 */
--primary-600: #2563EB;
--primary-700: #1D4ED8;
```

**使用场景**:
- 主按钮背景
- 链接文字
- 选中状态
- 进度条

**对比度检查**:
- `#3B82F6` on `#FFFFFF`: 4.6:1 ✅
- `#3B82F6` on `#0F172A`: 3.6:1 ⚠️（需要边框或阴影增强）

---

### 暗黑主题（Dark Theme - 默认）

#### 背景色
```css
--bg-dark: #0F172A;        /* 主背景 - Slate 900 */
--bg-surface: #1E293B;     /* 卡片/面板 - Slate 800 */
--bg-elevated: #334155;    /* 悬浮/弹窗 - Slate 700 */
--bg-hover: #475569;       /* 悬停状态 - Slate 600 */
```

#### 文字色
```css
--text-primary: #F8FAFC;    /* 标题/正文 - Slate 50, 对比度 16:1 ✅ */
--text-secondary: #E2E8F0;  /* 辅助文字 - Slate 200, 对比度 11:1 ✅ */
--text-muted: #94A3B8;      /* 灰色文字 - Slate 400, 对比度 5.2:1 ✅ */
--text-disabled: #64748B;   /* 禁用状态 - Slate 500, 对比度 3.8:1 ⚠️ */
```

#### 边框色
```css
--border: #334155;          /* 默认边框 - Slate 700 */
--border-light: #475569;    /* 浅色边框 - Slate 600 */
--border-strong: #64748B;   /* 强边框 - Slate 500 */
```

---

### 亮色主题（Light Theme）

#### 背景色
```css
--bg-light: #FFFFFF;
--bg-light-surface: #F8FAFC;    /* Slate 50 */
--bg-light-elevated: #F1F5F9;   /* Slate 100 */
--bg-light-hover: #E2E8F0;      /* Slate 200 */
```

#### 文字色
```css
--text-light-primary: #0F172A;    /* Slate 900, 对比度 16:1 ✅ */
--text-light-secondary: #475569;  /* Slate 600, 对比度 7.1:1 ✅ */
--text-light-muted: #64748B;      /* Slate 500, 对比度 4.9:1 ✅ */
--text-light-disabled: #94A3B8;   /* Slate 400, 对比度 3.2:1 ⚠️ */
```

---

### 语义化颜色（Semantic Colors）

#### 成功（Success）
```css
--success: #10B981;       /* Green 500 */
--success-light: #34D399; /* Green 400 */
--success-dark: #059669;  /* Green 600 */
```
**使用场景**: 成功提示、完成状态、正向反馈

#### 警告（Warning）
```css
--warning: #F59E0B;       /* Amber 500 */
--warning-light: #FBBF24; /* Amber 400 */
--warning-dark: #D97706;  /* Amber 600 */
```
**使用场景**: 警告提示、需要注意的信息

#### 错误（Error）
```css
--error: #EF4444;         /* Red 500 */
--error-light: #F87171;   /* Red 400 */
--error-dark: #DC2626;    /* Red 600 */
```
**使用场景**: 错误提示、危险操作、失败状态

#### 信息（Info）
```css
--info: #3B82F6;          /* Blue 500 */
--info-light: #60A5FA;    /* Blue 400 */
--info-dark: #2563EB;     /* Blue 600 */
```
**使用场景**: 信息提示、说明文字

#### AI 助手（AI）
```css
--ai: #A855F7;            /* Purple 500 */
--ai-light: #C084FC;      /* Purple 400 */
--ai-dark: #9333EA;       /* Purple 600 */
```
**使用场景**: AI 助手相关元素

---

## 排版系统

### 字体家族

```css
/* UI 字体 */
--font-sans: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;

/* 代码字体 */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

**字体加载策略**:
- 使用 `font-display: swap` 避免 FOIT
- Google Fonts CDN 或自托管
- 仅加载需要的字重（400, 500, 600, 700）

---

### 字体尺寸和行高

| Token | 尺寸 | 行高 | 用途 | 示例 |
|-------|------|------|------|------|
| `text-2xs` | 10px | 14px | 超小文字 | 版本号、角标 |
| `text-xs` | 12px | 16px | 小文字 | 提示、说明 |
| `text-sm` | 14px | 20px | 辅助文字 | 按钮文字、标签 |
| `text-base` | 16px | 24px | 正文 | 段落、列表 |
| `text-lg` | 18px | 28px | 小标题 | H3 |
| `text-xl` | 20px | 28px | 中标题 | H2 |
| `text-2xl` | 24px | 32px | 大标题 | H1, 页面标题 |
| `text-3xl` | 30px | 36px | 超大标题 | 封面标题 |

**移动端适配**:
```css
/* 移动端基础字号不小于 16px，避免 iOS 自动缩放 */
@media (max-width: 768px) {
  input, textarea {
    font-size: 16px;
  }
}
```

---

### 字重（Font Weight）

```css
--font-light: 300;        /* 用于大标题 */
--font-normal: 400;       /* 正文 */
--font-medium: 500;       /* 辅助强调 */
--font-semibold: 600;     /* 小标题 */
--font-bold: 700;         /* 大标题 */
```

**使用建议**:
- 正文使用 `400`
- 按钮使用 `500` 或 `600`
- 标题使用 `600` 或 `700`
- 避免使用 `300` 在小字号上（可读性差）

---

### 排版工具类（Tailwind）

```typescript
const typography = {
  // 标题
  h1: 'text-2xl font-bold leading-tight tracking-tight',
  h2: 'text-xl font-semibold leading-tight',
  h3: 'text-lg font-semibold leading-snug',

  // 正文
  body: 'text-base leading-relaxed',
  bodySmall: 'text-sm leading-relaxed',
  caption: 'text-xs leading-normal',

  // 代码
  code: 'font-mono text-sm',
  codeInline: 'font-mono text-sm px-1.5 py-0.5 rounded bg-bg-elevated',
  codeBlock: 'font-mono text-sm p-4 rounded bg-bg-dark overflow-x-auto',
};
```

---

## 间距系统

### 间距比例（基于 4px 网格）

| Token | 值 | rem | 使用场景 |
|-------|----|----|---------|
| `spacing-0` | 0px | 0 | 无间距 |
| `spacing-1` | 4px | 0.25rem | 极小间距 |
| `spacing-2` | 8px | 0.5rem | 小间距 |
| `spacing-3` | 12px | 0.75rem | 中小间距 |
| `spacing-4` | 16px | 1rem | 默认间距 |
| `spacing-5` | 20px | 1.25rem | 中间距 |
| `spacing-6` | 24px | 1.5rem | 中大间距 |
| `spacing-8` | 32px | 2rem | 大间距 |
| `spacing-10` | 40px | 2.5rem | 超大间距 |
| `spacing-12` | 48px | 3rem | 区域间距 |
| `spacing-16` | 64px | 4rem | 页面级间距 |

### 组件内间距

```css
/* 按钮内边距 */
.button-sm { padding: 8px 12px; }   /* py-2 px-3 */
.button-md { padding: 10px 16px; }  /* py-2.5 px-4 */
.button-lg { padding: 12px 24px; }  /* py-3 px-6 */

/* 卡片内边距 */
.card { padding: 16px; }            /* p-4 */
.card-lg { padding: 24px; }         /* p-6 */

/* 输入框内边距 */
.input { padding: 8px 12px; }       /* py-2 px-3 */
```

### 组件间间距

```css
/* 垂直间距 */
.stack-xs { gap: 4px; }    /* space-y-1 */
.stack-sm { gap: 8px; }    /* space-y-2 */
.stack-md { gap: 16px; }   /* space-y-4 */
.stack-lg { gap: 24px; }   /* space-y-6 */

/* 水平间距 */
.inline-xs { gap: 4px; }   /* space-x-1 */
.inline-sm { gap: 8px; }   /* space-x-2 */
.inline-md { gap: 16px; }  /* space-x-4 */
.inline-lg { gap: 24px; }  /* space-x-6 */
```

---

## 组件库

### Button 按钮

#### 变体（Variants）

```typescript
// Primary - 主按钮
<Button variant="primary">
  运行代码
</Button>

// Secondary - 次要按钮
<Button variant="secondary">
  取消
</Button>

// Destructive - 危险操作
<Button variant="destructive">
  删除
</Button>

// Ghost - 幽灵按钮
<Button variant="ghost">
  查看详情
</Button>

// Success - 成功按钮
<Button variant="success">
  确认
</Button>
```

#### 尺寸（Sizes）

```typescript
<Button size="sm">小按钮</Button>
<Button size="md">中按钮</Button>
<Button size="lg">大按钮</Button>
```

| 尺寸 | 高度 | 内边距 | 字号 | 最小宽度 |
|------|------|--------|------|----------|
| `sm` | 32px | 8px 12px | 14px | 44px |
| `md` | 40px | 10px 16px | 14px | 44px |
| `lg` | 48px | 12px 24px | 16px | 44px |

**移动端优化**: 最小触摸目标 44x44px

#### 状态

```typescript
// 加载状态
<Button isLoading>
  提交中...
</Button>

// 禁用状态
<Button disabled>
  不可用
</Button>

// 带图标
<Button>
  <Play className="h-4 w-4 mr-1.5" />
  运行
</Button>
```

---

### Input 输入框

```typescript
<input
  type="text"
  placeholder="请输入..."
  aria-label="输入框描述"
  className={`
    px-3 py-2 border rounded text-sm
    focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20
    transition-all
    ${theme === 'dark'
      ? 'bg-bg-elevated border-border text-text-primary placeholder-text-muted'
      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'
    }
    disabled:opacity-50 disabled:cursor-not-allowed
  `}
/>
```

**可访问性要求**:
- 必须有 `aria-label` 或关联的 `<label>`
- 错误状态添加 `aria-invalid="true"` 和 `aria-describedby`
- 移动端字号 ≥ 16px（避免 iOS 缩放）

---

### Card 卡片

```typescript
<div className={`
  rounded-lg border p-6
  ${theme === 'dark'
    ? 'bg-bg-surface border-border'
    : 'bg-white border-gray-200'
  }
  hover:shadow-lg transition-shadow
`}>
  {/* 卡片内容 */}
</div>
```

---

### Toast 提示

```typescript
// 成功提示
<Toast variant="success">
  <Check className="h-4 w-4 mr-2" />
  保存成功！
</Toast>

// 错误提示
<Toast variant="error">
  <AlertCircle className="h-4 w-4 mr-2" />
  保存失败，请重试
</Toast>

// 信息提示
<Toast variant="info">
  <Info className="h-4 w-4 mr-2" />
  正在保存...
</Toast>
```

**显示位置**: 右上角（桌面）/ 顶部（移动端）
**持续时间**: 3000ms（可配置）
**最大数量**: 3 个

---

## 动画系统

### 动画原则

1. **快速响应**: 界面交互 < 100ms
2. **流畅过渡**: 动画时长 200-300ms
3. **自然缓动**: 使用 `ease-out` 或 `ease-in-out`
4. **尊重用户偏好**: `prefers-reduced-motion`

### 缓动函数（Easing）

```css
--ease-out: cubic-bezier(0.33, 1, 0.68, 1);      /* 默认 */
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);   /* 双向 */
--ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55); /* 弹性 */
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);     /* 平滑 */
```

### 动画时长

```css
--duration-instant: 100ms;    /* 即时反馈（hover） */
--duration-fast: 150ms;       /* 快速（按钮点击） */
--duration-base: 200ms;       /* 默认（过渡） */
--duration-slow: 300ms;       /* 慢速（弹窗） */
--duration-slower: 500ms;     /* 更慢（页面切换） */
```

### 常用动画

#### Fade In（淡入）
```css
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fade-in 0.3s ease-out;
}
```

#### Slide In（滑入）
```css
@keyframes slide-in {
  from {
    transform: translateX(20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-in {
  animation: slide-in 0.3s ease-out;
}
```

#### Scale In（缩放）
```css
@keyframes scale-in {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.scale-in {
  animation: scale-in 0.2s ease-out;
}
```

#### Bounce（弹跳）
```css
@keyframes bounce-subtle {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.bounce-subtle {
  animation: bounce-subtle 2s ease-in-out infinite;
}
```

#### Pulse Glow（脉冲发光）
```css
@keyframes pulse-glow {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
  }
  50% {
    opacity: 0.8;
    box-shadow: 0 0 20px 10px rgba(59, 130, 246, 0);
  }
}

.pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
```

---

## 可访问性规范

### WCAG 2.1 AA 标准

#### 1. 颜色对比度

**正文**: 对比度 ≥ 4.5:1
**大文本**: 对比度 ≥ 3:1（18px+ 或 14px+ 粗体）
**UI 组件**: 对比度 ≥ 3:1

✅ **通过**:
- `#F8FAFC` on `#0F172A`: 16.1:1
- `#E2E8F0` on `#0F172A`: 11.2:1
- `#94A3B8` on `#0F172A`: 5.2:1

⚠️ **注意**:
- `#64748B` on `#0F172A`: 3.8:1（仅用于禁用状态）

---

#### 2. 键盘导航

**Tab 顺序**: 符合逻辑顺序
**焦点可见**: 明显的焦点指示器（ring-2 ring-primary）
**键盘操作**:
- `Tab` / `Shift+Tab`: 移动焦点
- `Enter` / `Space`: 激活按钮
- `Escape`: 关闭弹窗
- `Arrow Keys`: 列表/菜单导航

**焦点样式**:
```css
*:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--bg-dark), 0 0 0 4px var(--primary);
  border-radius: 4px;
}
```

---

#### 3. ARIA 标签

**必须**:
- 所有交互元素必须有可访问名称
- 动态内容使用 `aria-live`
- 表单输入关联 `label` 或 `aria-label`
- 图标按钮必须有 `aria-label`

**示例**:
```typescript
// 图标按钮
<button aria-label="关闭对话框">
  <X className="h-4 w-4" />
</button>

// 输入框
<input
  type="text"
  aria-label="搜索课程"
  aria-describedby="search-hint"
  aria-invalid={hasError ? 'true' : 'false'}
/>
<span id="search-hint" className="sr-only">
  输入关键词搜索课程
</span>

// 动态内容
<div role="status" aria-live="polite" aria-atomic="true">
  {isLoading ? '加载中...' : '加载完成'}
</div>

// 地标区域
<nav role="navigation" aria-label="课程目录">
  {/* 导航内容 */}
</nav>
```

---

#### 4. 触摸目标尺寸

**最小尺寸**: 44x44 px（Apple 和 Google 推荐）
**间距**: 触摸目标之间至少 8px 间距

```typescript
// Button 组件已包含 min-w-[44px] min-h-[44px]
<Button size="sm">按钮</Button>

// 移动端按钮增大
@media (max-width: 768px) {
  .button-sm {
    height: 40px;  /* 桌面 32px, 移动端 40px */
  }
}
```

---

#### 5. 屏幕阅读器优化

**隐藏视觉内容，保留语义**:
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

**Skip Links（跳转链接）**:
```typescript
<a
  href="#main-content"
  className="sr-only sr-only-focusable"
>
  跳转到主内容
</a>
```

---

### 可访问性测试清单

#### 自动化测试
- [ ] Lighthouse Accessibility Score ≥ 90
- [ ] axe DevTools: 0 Critical/Serious Issues
- [ ] WAVE Extension: 无错误

#### 手动测试
- [ ] 纯键盘导航所有功能
- [ ] VoiceOver (macOS) / NVDA (Windows) 测试
- [ ] 高对比度模式测试
- [ ] 缩放至 200% 仍可用
- [ ] 移动端屏幕阅读器测试

---

## 使用指南

### 1. 安装依赖

```bash
npm install tailwindcss class-variance-authority clsx tailwind-merge
```

### 2. 配置 Tailwind

查看 `tailwind.config.js` 获取完整配置。

### 3. 使用设计 Token

```typescript
import { cn } from '@/lib/utils';

// 使用颜色 Token
<div className="bg-bg-surface text-text-primary border-border">
  内容
</div>

// 使用排版 Token
<h1 className="text-2xl font-bold leading-tight">
  标题
</h1>

// 使用间距 Token
<div className="p-6 space-y-4">
  {/* 内容 */}
</div>
```

### 4. 创建新组件

遵循设计系统规范：

```typescript
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const cardVariants = cva(
  'rounded-lg border p-6 transition-shadow',
  {
    variants: {
      theme: {
        dark: 'bg-bg-surface border-border',
        light: 'bg-white border-gray-200',
      },
      hoverable: {
        true: 'hover:shadow-lg cursor-pointer',
        false: '',
      },
    },
    defaultVariants: {
      theme: 'dark',
      hoverable: false,
    },
  }
);

interface CardProps extends VariantProps<typeof cardVariants> {
  children: React.ReactNode;
  className?: string;
}

export function Card({ theme, hoverable, children, className }: CardProps) {
  return (
    <div className={cn(cardVariants({ theme, hoverable }), className)}>
      {children}
    </div>
  );
}
```

---

## 更新日志

### v1.0.0 (2026-01-10)
- 初始设计系统文档
- 定义颜色、排版、间距系统
- 添加组件库规范
- 添加可访问性规范

---

**维护者**: UI/UX Engineering Team
**最后更新**: 2026-01-10
