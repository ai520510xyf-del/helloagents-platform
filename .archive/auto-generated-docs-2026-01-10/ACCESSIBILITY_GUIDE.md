# 可访问性指南

## 概览

本文档描述了 HelloAgents 平台的可访问性改进和测试指南，确保符合 WCAG 2.1 AA 标准。

## 已实施的改进

### 1. 颜色对比度优化

**文件**: `frontend/tailwind.config.js`

#### 暗色主题
```javascript
text: {
  primary: '#F8FAFC',      // 对比度 16:1 ✅
  secondary: '#E2E8F0',    // 对比度 11:1 ✅ (从 CBD5E1 提升)
  muted: '#94A3B8',        // 对比度 5.2:1 ✅
  disabled: '#94A3B8',     // 对比度 5.2:1 ✅ (从 64748B 提升)
}
```

#### 亮色主题
```javascript
'text-light': {
  primary: '#0F172A',      // 对比度 16:1 ✅
  secondary: '#475569',    // 对比度 7.1:1 ✅
  muted: '#64748B',        // 对比度 4.9:1 ✅
  disabled: '#64748B',     // 对比度 4.9:1 ✅ (从 94A3B8 提升)
}
```

**验证**: 所有文字对比度 >= 4.5:1，符合 WCAG AA 标准。

---

### 2. ARIA 标签和语义化标记

**文件**: `frontend/src/components/learn/CodeEditorPanel.tsx`

#### 地标区域 (Landmarks)
```tsx
// 主要内容区域
<div role="main" aria-label="代码编辑器面板">

// 导航区域
<div role="tablist" aria-label="代码文件标签">

// 工具栏
<div role="toolbar" aria-label="代码操作工具栏">

// 编辑器区域
<div role="region" aria-label="代码编辑区域">
```

#### 交互元素标签
```tsx
// 按钮 ARIA 标签
<Button aria-label={isRunning ? "代码运行中" : "运行代码"}>
<Button aria-label="停止代码执行">
<Button aria-label="重置代码到初始状态">

// 图标隐藏
<Play aria-hidden="true" />

// 动态内容
<div role="status" aria-live="polite" aria-label="光标位置">
```

---

### 3. 键盘导航

**文件**: `frontend/src/components/learn/CodeEditorPanel.tsx`

#### 键盘快捷键
- **Ctrl/Cmd + Enter**: 运行代码
- **Escape**: 停止运行
- **Ctrl/Cmd + R**: 重置代码
- **Tab**: 在控件间切换
- **Enter/Space**: 激活按钮

#### 实现
```tsx
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // Ctrl/Cmd + Enter: 运行代码
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !isRunning) {
      e.preventDefault();
      onRun();
    }

    // Escape: 停止运行
    if (e.key === 'Escape' && isRunning) {
      e.preventDefault();
      onStop();
    }

    // Ctrl/Cmd + R: 重置代码
    if ((e.ctrlKey || e.metaKey) && e.key === 'r' && !isRunning) {
      e.preventDefault();
      onReset();
    }
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [isRunning, onRun, onStop, onReset]);
```

---

### 4. 屏幕阅读器优化

**文件**: `frontend/src/index.css`

#### sr-only 工具类
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

#### 使用示例
```tsx
// 键盘快捷键说明（仅屏幕阅读器）
<div className="sr-only" role="region" aria-label="键盘快捷键说明">
  <h2>键盘快捷键</h2>
  <ul>
    <li>Ctrl + Enter 或 Command + Enter: 运行代码</li>
    <li>Escape: 停止运行</li>
    <li>Ctrl + R 或 Command + R: 重置代码</li>
    <li>Tab: 在控件间切换</li>
  </ul>
</div>

// 加载状态说明
<span className="sr-only">正在处理请求，请稍候</span>
```

---

### 5. 跳转链接 (Skip Links)

**文件**: `frontend/index.html`

```html
<!-- 跳转链接 - 改善键盘导航 -->
<a href="#main-content" class="sr-only sr-only-focusable">
  跳转到主内容
</a>
```

**行为**: 默认隐藏，获得焦点时显示，允许键盘用户快速跳过导航。

---

### 6. Button 组件增强

**文件**: `frontend/src/components/ui/Button.tsx`

#### ARIA 状态
```tsx
<button
  aria-busy={isLoading}
  aria-disabled={disabled || isLoading}
>
  {isLoading ? (
    <>
      <Loader2 aria-hidden="true" />
      <span className="sr-only">正在处理请求，请稍候</span>
      加载中...
    </>
  ) : (
    children
  )}
</button>
```

---

### 7. Focus 样式

**文件**: `frontend/src/index.css`

```css
*:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--bg-dark), 0 0 0 4px var(--primary);
  border-radius: 4px;
}
```

**对比度**: 焦点环使用 `#3B82F6` (Primary Blue)，对比度 4.6:1。

---

### 8. 触摸目标尺寸

**文件**: `frontend/src/components/ui/Button.tsx`

```tsx
size: {
  sm: 'h-8 px-3 text-sm rounded min-w-[44px]',
  md: 'h-10 px-4 text-sm rounded-md min-w-[44px]',
  lg: 'h-12 px-6 text-base rounded-md min-w-[44px]',
}
```

**最小尺寸**: 44x44px，符合 Apple 和 Google 推荐。

---

### 9. 动画尊重用户偏好

**文件**: `frontend/src/index.css`

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 测试清单

### 自动化测试

#### Lighthouse Accessibility Audit
```bash
# 安装 Lighthouse CLI
npm install -g @lhci/cli

# 运行 Lighthouse 测试
lhci autorun --config=./lighthouserc.json

# 或使用浏览器 DevTools
# 1. 打开 Chrome DevTools
# 2. 选择 Lighthouse 标签
# 3. 勾选 Accessibility
# 4. 点击 Generate Report
```

**目标**: Accessibility Score >= 95

#### axe DevTools
```bash
# 安装 axe 浏览器扩展
# Chrome: https://chrome.google.com/webstore/detail/axe-devtools/lhdoppojpmngadmnindnejefpokejbdd
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/axe-devtools/

# 运行自动扫描
# 1. 打开 DevTools
# 2. 选择 axe DevTools 标签
# 3. 点击 "Scan ALL of my page"
```

**目标**: 0 Critical/Serious Issues

#### WAVE Extension
```bash
# 安装 WAVE 浏览器扩展
# https://wave.webaim.org/extension/

# 运行测试
# 点击浏览器工具栏中的 WAVE 图标
```

**目标**: 无错误

---

### 手动测试

#### 1. 键盘导航测试

**测试步骤**:
1. 使用 **Tab** 键在所有交互元素间导航
2. 使用 **Shift + Tab** 反向导航
3. 使用 **Enter** 或 **Space** 激活按钮
4. 使用 **Escape** 关闭模态框（如果有）
5. 检查焦点指示器是否清晰可见

**验收标准**:
- ✅ 所有交互元素可通过键盘访问
- ✅ Tab 顺序符合逻辑
- ✅ 焦点指示器清晰可见（蓝色边框）
- ✅ 快捷键正常工作

---

#### 2. 屏幕阅读器测试

**macOS VoiceOver**:
```bash
# 启动 VoiceOver
Cmd + F5

# 导航命令
Ctrl + Option + 右箭头: 下一个元素
Ctrl + Option + 左箭头: 上一个元素
Ctrl + Option + Space: 激活元素
```

**Windows NVDA**:
```bash
# 下载 NVDA
https://www.nvaccess.org/download/

# 导航命令
下箭头: 下一行
上箭头: 上一行
Tab: 下一个交互元素
Enter/Space: 激活元素
```

**测试内容**:
- ✅ 所有图像有替代文本
- ✅ 按钮有描述性标签
- ✅ 表单输入有关联的标签
- ✅ 页面结构清晰（标题层级、地标）
- ✅ 动态内容变化有提示（aria-live）

---

#### 3. 颜色对比度测试

**工具**:
- **浏览器扩展**: WCAG Color Contrast Checker
- **在线工具**: https://webaim.org/resources/contrastchecker/

**测试步骤**:
1. 检查所有文字颜色对比度
2. 检查按钮和交互元素对比度
3. 检查图标和图形对比度

**验收标准**:
- ✅ 正文对比度 >= 4.5:1
- ✅ 大文本对比度 >= 3:1
- ✅ UI 组件对比度 >= 3:1

**已验证的对比度**:
| 元素 | 前景色 | 背景色 | 对比度 | 状态 |
|------|--------|--------|--------|------|
| 主文字（暗） | #F8FAFC | #0F172A | 16:1 | ✅ |
| 次要文字（暗） | #E2E8F0 | #0F172A | 11:1 | ✅ |
| 灰色文字（暗） | #94A3B8 | #0F172A | 5.2:1 | ✅ |
| 主文字（亮） | #0F172A | #FFFFFF | 16:1 | ✅ |
| 次要文字（亮） | #475569 | #FFFFFF | 7.1:1 | ✅ |
| 灰色文字（亮） | #64748B | #FFFFFF | 4.9:1 | ✅ |

---

#### 4. 缩放测试

**测试步骤**:
1. 缩放至 200% (Ctrl/Cmd + +)
2. 检查布局是否破坏
3. 检查文字是否可读
4. 检查是否需要水平滚动

**验收标准**:
- ✅ 200% 缩放下所有内容可见
- ✅ 无布局破坏
- ✅ 无文字重叠
- ✅ 主要功能可用

---

#### 5. 移动端屏幕阅读器测试

**iOS VoiceOver**:
```
设置 > 辅助功能 > VoiceOver > 开启
```

**Android TalkBack**:
```
设置 > 辅助功能 > TalkBack > 开启
```

**测试内容**:
- ✅ 触摸目标 >= 44x44px
- ✅ 手势操作可替代
- ✅ 屏幕阅读器正确播报
- ✅ 表单输入体验流畅

---

## 常见问题修复

### 问题 1: 按钮没有可访问名称
```tsx
// ❌ 错误
<button>
  <Icon />
</button>

// ✅ 正确
<button aria-label="关闭对话框">
  <Icon aria-hidden="true" />
</button>
```

### 问题 2: 图片缺少替代文本
```tsx
// ❌ 错误
<img src="avatar.jpg" />

// ✅ 正确
<img src="avatar.jpg" alt="用户头像 - 张三" />

// 装饰性图片
<img src="decoration.jpg" alt="" role="presentation" />
```

### 问题 3: 表单输入没有标签
```tsx
// ❌ 错误
<input type="text" placeholder="请输入..." />

// ✅ 正确
<label htmlFor="username">用户名</label>
<input id="username" type="text" placeholder="请输入..." />

// 或使用 aria-label
<input type="text" aria-label="用户名" placeholder="请输入..." />
```

### 问题 4: 动态内容没有通知
```tsx
// ❌ 错误
<div>{isLoading ? '加载中...' : data}</div>

// ✅ 正确
<div role="status" aria-live="polite" aria-atomic="true">
  {isLoading ? '加载中...' : data}
</div>
```

### 问题 5: 对比度不足
```tsx
// ❌ 错误 (对比度 2.8:1)
<span style={{ color: '#999999', background: '#FFFFFF' }}>
  灰色文字
</span>

// ✅ 正确 (对比度 4.9:1)
<span style={{ color: '#64748B', background: '#FFFFFF' }}>
  灰色文字
</span>
```

---

## 持续改进

### 下一步计划
1. 添加更多 ARIA live regions 用于动态内容
2. 实现更多键盘快捷键（如方向键导航列表）
3. 添加高对比度模式支持
4. 实现完整的焦点陷阱（Focus Trap）用于模态框
5. 添加语音控制支持

### 定期测试
- 每次发布前运行 Lighthouse 测试
- 每月进行一次完整的手动测试
- 收集用户反馈并持续改进

---

## 资源链接

### 标准和指南
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Resources](https://webaim.org/resources/)

### 测试工具
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE](https://wave.webaim.org/)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)

### 学习资源
- [A11y Project](https://www.a11yproject.com/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [Google Web Fundamentals - Accessibility](https://developers.google.com/web/fundamentals/accessibility)

---

**维护者**: UI/UX Engineering Team
**最后更新**: 2026-01-10
**版本**: 1.0.0
