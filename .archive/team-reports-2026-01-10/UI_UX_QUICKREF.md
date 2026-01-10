# UI/UX 优化快速参考

**作用**: UI/UX 工程师的每日工作速查手册

---

## 目录

- [快速诊断](#快速诊断)
- [优先级清单](#优先级清单)
- [设计 Token](#设计-token)
- [可访问性检查](#可访问性检查)
- [常用命令](#常用命令)
- [代码片段](#代码片段)

---

## 快速诊断

### 1. 颜色对比度检查

```bash
# 使用 Chrome DevTools
1. 打开开发者工具 (F12)
2. Elements > Styles > 点击颜色
3. 查看 "Contrast ratio" 信息

# 目标: WCAG AA
- 正文文字: ≥ 4.5:1
- 大文本 (18px+): ≥ 3:1
- UI 组件: ≥ 3:1
```

**快速修复**:
```css
/* ❌ 对比度不足 */
color: #94A3B8; /* 3.8:1 - 不通过 */

/* ✅ 提升对比度 */
color: #CBD5E1; /* 5.2:1 - 通过 */
```

---

### 2. 键盘导航测试

```bash
# 测试流程 (5分钟)
1. 按 Tab 键 - 焦点应该按逻辑顺序移动
2. 按 Enter/Space - 激活按钮和链接
3. 按 Escape - 关闭弹窗/清空输入
4. 按 方向键 - 在列表/菜单中导航

# 焦点可见性检查
- 焦点指示器清晰可见 (ring-2 ring-primary)
- 对比度 ≥ 3:1
- 不被遮挡
```

**快速修复**:
```typescript
// ❌ 缺少焦点样式
<button className="...">按钮</button>

// ✅ 添加焦点样式
<button className="... focus:ring-2 focus:ring-primary focus:outline-none">
  按钮
</button>
```

---

### 3. 移动端触摸目标

```bash
# 检查清单
- 按钮最小尺寸: 44x44 px
- 触摸目标间距: ≥ 8px
- 触摸反馈: active:scale-95
- 防止双击缩放: touch-action: manipulation
```

**快速修复**:
```typescript
// ❌ 触摸目标过小
<Button size="sm">按钮</Button>  // 32px

// ✅ 移动端增大
<Button size="sm" className="md:h-8 h-10">按钮</Button>  // 移动端 40px, 桌面 32px
```

---

## 优先级清单

### P0 - 立即修复（本周）

- [ ] **颜色对比度**: `text-text-muted` 改为 `#CBD5E1`（对比度 5.2:1）
- [ ] **ARIA 标签**: 所有图标按钮添加 `aria-label`
- [ ] **键盘导航**: AI 输入框支持 Escape 清空
- [ ] **焦点管理**: 所有交互元素添加焦点样式
- [ ] **Skip Links**: 添加页面跳转链接

### P1 - 重要优化（本月）

- [ ] **Onboarding**: 首次访问显示欢迎引导
- [ ] **AI 输入优化**: Textarea + 字数限制 + 移动端适配
- [ ] **代码复制**: AI 消息代码块添加复制按钮
- [ ] **空状态设计**: AI 助手快速问题建议
- [ ] **错误处理**: 友好的错误提示 + 重试机制

### P2 - 体验优化（下个月）

- [ ] **打字机效果**: AI 回复流式显示
- [ ] **进度庆祝**: 完成课程显示成就动画
- [ ] **微交互**: 按钮涟漪效果、平滑过渡
- [ ] **骨架屏**: 加载状态优化
- [ ] **长按菜单**: 移动端上下文菜单

---

## 设计 Token

### 颜色（复制即用）

```typescript
// 暗黑主题
const darkTheme = {
  bg: {
    dark: '#0F172A',        // 主背景
    surface: '#1E293B',     // 卡片/面板
    elevated: '#334155',    // 悬浮/弹窗
    hover: '#475569',       // 悬停状态
  },
  text: {
    primary: '#F8FAFC',     // 标题/正文 (对比度 16:1)
    secondary: '#CBD5E1',   // 辅助文字 (对比度 9.3:1)
    muted: '#94A3B8',       // 灰色文字 (对比度 5.2:1)
  },
  border: {
    DEFAULT: '#334155',
    light: '#475569',
  },
  primary: '#3B82F6',       // 主色
  success: '#10B981',       // 成功
  warning: '#F59E0B',       // 警告
  error: '#EF4444',         // 错误
  ai: '#A855F7',            // AI 助手
};

// 亮色主题
const lightTheme = {
  bg: {
    light: '#FFFFFF',
    surface: '#F8FAFC',
    elevated: '#F1F5F9',
    hover: '#E2E8F0',
  },
  text: {
    primary: '#0F172A',     // (对比度 16:1)
    secondary: '#475569',   // (对比度 7.1:1)
    muted: '#64748B',       // (对比度 4.9:1)
  },
  border: {
    DEFAULT: '#E2E8F0',
    dark: '#CBD5E1',
  },
  // 其他颜色同上
};
```

---

### 间距（4px 网格）

```typescript
// Tailwind 类名速查
p-1   // 4px
p-2   // 8px
p-3   // 12px
p-4   // 16px (默认)
p-6   // 24px
p-8   // 32px

// 组件内间距
Button: p-2 px-3      // 8px 12px
Card: p-6             // 24px
Input: py-2 px-3      // 8px 12px

// 组件间间距
space-y-2  // 8px (列表项)
space-y-4  // 16px (段落)
space-y-6  // 24px (区域)
```

---

### 排版

```typescript
// 标题
h1: 'text-2xl font-bold leading-tight'        // 24px
h2: 'text-xl font-semibold leading-tight'     // 20px
h3: 'text-lg font-semibold leading-snug'      // 18px

// 正文
body: 'text-base leading-relaxed'             // 16px
bodySmall: 'text-sm leading-relaxed'          // 14px
caption: 'text-xs leading-normal'             // 12px

// 代码
code: 'font-mono text-sm'                     // 14px
codeInline: 'font-mono text-sm px-1.5 py-0.5 rounded'
```

---

## 可访问性检查

### 5分钟快速检查

```bash
1. ✅ 颜色对比度
   - 使用 Chrome DevTools 检查对比度
   - 正文 ≥ 4.5:1, 大文本 ≥ 3:1

2. ✅ 键盘导航
   - Tab 导航所有交互元素
   - Enter/Space 激活按钮
   - Escape 关闭弹窗

3. ✅ ARIA 标签
   - 图标按钮有 aria-label
   - 表单输入有 label 或 aria-label
   - 动态内容有 aria-live

4. ✅ 焦点可见
   - 焦点指示器清晰 (ring-2 ring-primary)
   - 不被其他元素遮挡

5. ✅ 移动端触摸
   - 按钮最小 44x44 px
   - 触摸目标间距 ≥ 8px
```

---

### ARIA 属性速查

```typescript
// 按钮
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
<span id="search-hint" className="sr-only">输入关键词</span>

// 动态内容
<div role="status" aria-live="polite" aria-atomic="true">
  {isLoading ? '加载中...' : '加载完成'}
</div>

// 导航
<nav role="navigation" aria-label="课程目录">
  {/* 内容 */}
</nav>

// 地标区域
<main role="main" id="main-content">
<aside role="complementary" aria-label="AI 助手">
<section role="log" aria-label="聊天历史">
```

---

## 常用命令

### 可访问性审计

```bash
# Lighthouse
npm run audit:a11y

# axe DevTools (浏览器扩展)
# 1. 安装 axe DevTools 扩展
# 2. F12 > axe DevTools > Scan
# 3. 修复 Critical 和 Serious 问题

# 手动测试
# VoiceOver (macOS): Cmd+F5
# NVDA (Windows): 下载并安装
```

---

### 性能测试

```bash
# Lighthouse Performance
npm run audit:performance

# 实时性能监控
npm run dev
# 打开 Chrome DevTools > Performance
# 录制 3 秒交互
# 检查 FPS (应 ≥ 60)
```

---

## 代码片段

### 1. 可访问的按钮

```typescript
import { Button } from '@/components/ui/Button';
import { Play } from 'lucide-react';

<Button
  variant="primary"
  size="md"
  onClick={handleRun}
  disabled={isRunning}
  aria-label={isRunning ? '代码正在运行' : '运行代码'}
  className="min-w-[44px]"  // 确保触摸目标
>
  <Play className="h-4 w-4 mr-1.5" />
  运行
</Button>
```

---

### 2. 可访问的输入框

```typescript
<div className="flex flex-col gap-1">
  <label htmlFor="chat-input" className="text-sm font-medium">
    AI 助手输入
  </label>
  <input
    id="chat-input"
    type="text"
    value={input}
    onChange={(e) => setInput(e.target.value)}
    placeholder="输入你的问题..."
    aria-describedby="chat-hint"
    aria-invalid={hasError ? 'true' : 'false'}
    className="px-3 py-2 border rounded focus:ring-2 focus:ring-primary"
  />
  <span id="chat-hint" className="text-xs text-text-muted">
    按 Enter 发送，Shift+Enter 换行
  </span>
</div>
```

---

### 3. 状态公告（屏幕阅读器）

```typescript
function LiveAnnouncer({ message }: { message: string }) {
  return (
    <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
      {message}
    </div>
  );
}

// 使用
<LiveAnnouncer message={isRunning ? '代码正在运行' : '代码执行完毕'} />
```

---

### 4. 键盘导航

```typescript
const handleKeyDown = (e: React.KeyboardEvent) => {
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault();
      // 下移焦点
      break;
    case 'ArrowUp':
      e.preventDefault();
      // 上移焦点
      break;
    case 'Enter':
    case ' ':
      e.preventDefault();
      // 激活元素
      break;
    case 'Escape':
      // 关闭/清空
      break;
  }
};

<div onKeyDown={handleKeyDown}>
  {/* 内容 */}
</div>
```

---

### 5. Skip Links

```typescript
function SkipLinks() {
  return (
    <nav aria-label="快捷导航" className="sr-only focus-within:not-sr-only">
      <a
        href="#main-content"
        className="
          fixed top-4 left-4 z-50 px-4 py-2 rounded
          bg-primary text-white font-medium
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary
        "
      >
        跳转到主内容
      </a>
    </nav>
  );
}
```

---

### 6. 响应式按钮尺寸

```typescript
// 移动端 40px，桌面 32px
<Button
  size="sm"
  className="h-10 md:h-8 min-w-[44px]"
>
  按钮
</Button>

// 或使用 CVA
const buttonVariants = cva('...', {
  variants: {
    size: {
      sm: 'h-10 md:h-8 px-3 text-sm rounded',
      md: 'h-12 md:h-10 px-4 text-sm rounded-md',
    },
  },
});
```

---

## 常见问题速查

### Q1: 如何检查颜色对比度？

```bash
# 方法 1: Chrome DevTools
1. 检查元素 (F12)
2. Elements > Styles > 点击颜色选择器
3. 查看 "Contrast ratio"

# 方法 2: 在线工具
https://webaim.org/resources/contrastchecker/

# 方法 3: Figma 插件
安装 Stark 插件
```

---

### Q2: 如何测试屏幕阅读器？

```bash
# macOS
1. 按 Cmd+F5 开启 VoiceOver
2. 使用 VO+A 阅读全部内容
3. 使用 Tab 导航交互元素
4. 使用 VO+Right Arrow 逐项阅读

# Windows
1. 下载并安装 NVDA
2. Ctrl+NVDA+Down Arrow 阅读全部
3. 使用 Tab 导航
4. 使用 Down Arrow 逐项阅读
```

---

### Q3: 如何优化移动端触摸体验？

```typescript
// 1. 增大触摸目标
className="min-h-[44px] min-w-[44px]"

// 2. 触摸反馈
className="active:scale-95 touch-manipulation"

// 3. 防止意外缩放
className="touch-action-manipulation"

// 4. 移动端字号 ≥ 16px (避免 iOS 缩放)
<input className="text-base" />  // 16px
```

---

### Q4: 如何添加加载状态？

```typescript
import { Loader2 } from 'lucide-react';

<Button isLoading={isLoading} disabled={isLoading}>
  {isLoading ? (
    <>
      <Loader2 className="h-4 w-4 animate-spin mr-1.5" />
      加载中...
    </>
  ) : (
    '提交'
  )}
</Button>
```

---

### Q5: 如何实现暗黑模式切换？

```typescript
// 1. 使用 Tailwind dark: 前缀
<div className="bg-white dark:bg-bg-dark text-gray-900 dark:text-text-primary">

// 2. 添加 dark class 到 <html>
useEffect(() => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}, [theme]);
```

---

## 工具推荐

### 必备工具

1. **axe DevTools** (Chrome 扩展) - 可访问性审计
2. **WAVE** (Chrome 扩展) - 可访问性评估
3. **Lighthouse** (Chrome 内置) - 综合性能审计
4. **React DevTools** - 组件性能分析

### Figma 插件

1. **Stark** - 颜色对比度检查
2. **A11y Annotation Kit** - 可访问性标注
3. **Content Reel** - 快速填充内容

### VS Code 扩展

1. **ESLint** - 代码规范
2. **Tailwind CSS IntelliSense** - Tailwind 自动补全
3. **axe Accessibility Linter** - 可访问性检查

---

## 学习资源

### 必读文档

- [WCAG 2.1 快速参考](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN 可访问性](https://developer.mozilla.org/zh-CN/docs/Web/Accessibility)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)

### 实用工具

- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Accessible Colors](https://accessible-colors.com/)
- [Who Can Use](https://whocanuse.com/)

---

**维护**: UI/UX Engineering Team
**更新**: 2026-01-10
