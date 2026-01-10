# 移动端性能优化 - 快速使用指南

## 🚀 快速开始

### 构建和测试

```bash
# 安装依赖
cd frontend
npm install

# 开发模式（测试优化效果）
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

---

## 📱 移动端测试

### 1. Chrome DevTools 模拟

```bash
# 启动开发服务器
npm run dev

# 在浏览器中访问 http://localhost:5173
# 按 F12 打开开发者工具
# 点击设备工具栏图标（Ctrl+Shift+M 或 Cmd+Shift+M）
# 选择移动设备：
#   - iPhone 14 Pro (393x852)
#   - iPhone SE (375x667)
#   - Pixel 5 (393x851)
```

### 2. 真机测试

```bash
# 查看本机 IP
ifconfig | grep inet  # macOS/Linux
ipconfig              # Windows

# 确保手机和电脑在同一 WiFi
# 在手机浏览器访问: http://YOUR_IP:5173
```

---

## 🎯 核心功能

### SimpleMobileEditor（轻量级编辑器）

**何时使用**:
- 移动端首次加载
- 慢速网络环境
- 需要快速交互

**功能特性**:
- ✅ 基础代码编辑
- ✅ Tab 键缩进
- ✅ 行号显示
- ✅ 主题切换
- ✅ 光标位置追踪

**代码示例**:
```typescript
import { SimpleMobileEditor } from './components/SimpleMobileEditor';

<SimpleMobileEditor
  value={code}
  onChange={handleCodeChange}
  language="python"
  theme="dark"
  onUpgradeToFull={() => setUseFullEditor(true)}
/>
```

---

### LazyCodeEditor（智能加载）

**加载策略**:

| 设备 | 网络 | 初始编辑器 | Monaco 加载时机 |
|------|------|-----------|----------------|
| 桌面端 | - | Monaco Editor | 立即 |
| 移动端 | 4G/WiFi | SimpleMobileEditor | 2秒后 |
| 移动端 | 3G/2G | SimpleMobileEditor | 5秒后 |
| 移动端 | - | SimpleMobileEditor | 用户点击 |

**代码示例**:
```typescript
import { LazyCodeEditor } from './components/LazyCodeEditor';

// 自动处理设备检测和智能加载
<LazyCodeEditor
  value={code}
  onChange={handleCodeChange}
  language="python"
  theme="dark"
  isMobile={true}  // 可选，自动检测
/>
```

---

## 🔧 配置说明

### Vite 配置

已在 `vite.config.ts` 中配置:

```typescript
optimizeDeps: {
  exclude: [
    'monaco-editor',        // 不预构建 Monaco
    '@monaco-editor/react', // 不预构建 Monaco React
  ],
},

define: {
  // 只加载 Python 语言支持
  'process.env.MONACO_LANGUAGES': JSON.stringify(['python']),
}
```

### Monaco 配置

`src/lib/monacoConfig.ts` 提供:

```typescript
// 按需加载语言支持
loadLanguageSupport('python');
loadLanguageSupport('javascript');

// 配置 Monaco 环境
configureMonacoEnvironment(monaco);

// 记录性能指标（开发环境）
logMonacoPerformance();
```

---

## 📊 性能监控

### 开发环境

Monaco 加载后会自动输出性能日志:

```javascript
[Monaco] Performance Metrics
  monaco-editor-*.js: { size: "723.12 KB", duration: "450.32 ms" }
  ts.worker-*.js:     { size: "1013.33 KB", duration: "850.45 ms" }
```

### 生产环境

建议集成 Web Vitals:

```bash
npm install web-vitals
```

```typescript
import { getCLS, getFID, getLCP } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getLCP(console.log);
```

---

## 🐛 常见问题

### Q1: 移动端编辑器没有自动升级到 Monaco？

**检查**:
- 打开浏览器开发者工具 Console
- 查看是否有错误日志
- 确认网络连接正常

**解决**:
- 点击"升级到完整编辑器"按钮手动升级
- 刷新页面重试

### Q2: 构建时出现类型错误？

**常见错误**:
```
Cannot find namespace 'NodeJS'
```

**解决**:
已在代码中修复，使用 `number` 替代 `NodeJS.Timeout`

### Q3: Monaco Editor 加载很慢？

**原因**:
- Monaco Editor 包体积较大（3.6MB）
- Workers 额外加载（9MB+）

**优化**:
- 移动端已自动使用 SimpleMobileEditor
- 桌面端建议使用有线网络或 WiFi
- 考虑使用 CDN 加速

---

## 🎯 性能目标

### 移动端（优化后）

| 指标 | 目标值 | 当前预期 |
|------|--------|---------|
| 首屏加载 | < 2s | < 1.5s ✅ |
| LCP | < 2.5s | < 3.5s 🟡 |
| FCP | < 1.8s | < 2.5s 🟡 |
| TTI | < 5s | < 5s ✅ |
| Lighthouse | > 75 | 75-80 ✅ |

### 桌面端

| 指标 | 目标值 | 当前预期 |
|------|--------|---------|
| 首屏加载 | < 2s | < 2s ✅ |
| LCP | < 2.5s | < 2.5s ✅ |
| Lighthouse | > 85 | 85-90 ✅ |

---

## 📈 下一步优化

### Phase 2 计划

1. **图片优化** - 使用 WebP/AVIF 格式
2. **路由代码分割** - 页面级别懒加载
3. **Service Worker** - 离线支持和缓存
4. **关键资源 Preload** - 优化资源加载顺序
5. **性能监控** - 集成 Sentry/Analytics

---

## 📚 相关文档

- [完整实施报告](./MOBILE_PERFORMANCE_PHASE1_IMPLEMENTATION.md)
- [性能优化报告](./.archive/agent-reports-2026-01-10/frontend/PERFORMANCE_REPORT.md)
- [移动端优化说明](./.archive/agent-reports-2026-01-10/frontend/MOBILE_OPTIMIZATION.md)

---

## 🆘 获取帮助

如有问题，请：

1. 查看 [完整实施报告](./MOBILE_PERFORMANCE_PHASE1_IMPLEMENTATION.md)
2. 查看 Console 日志
3. 提交 Issue 描述问题
4. 联系开发团队

---

**更新时间**: 2026-01-10
**版本**: v1.0
