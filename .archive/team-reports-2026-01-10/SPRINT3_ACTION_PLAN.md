# Sprint 3 行动计划和风险缓解措施

**制定日期**: 2026-01-10
**项目经理**: Technical Project Manager
**Sprint 周期**: Sprint 3 (2026-01-05 至 2026-01-19)

---

## 🔴 Critical 问题 - 立即行动

### 问题 1: 生产环境 AI 助手未配置

**优先级**: P0 - CRITICAL
**影响**: 核心功能不可用, 影响所有用户
**发现时间**: 2026-01-09
**当前状态**: 🔴 未解决

#### 问题描述
生产环境后端服务未配置 `DEEPSEEK_API_KEY` 环境变量, 导致 AI 助手功能完全不可用。这是平台的核心功能之一, 严重影响用户体验。

#### 影响范围
- 用户无法使用 AI 助手进行代码辅导
- 无法获得实时问题解答
- 学习体验严重受损
- 可能导致用户流失

#### 解决方案

**责任人**: DevOps Engineer + Backend Lead

**步骤**:

1. **获取 DeepSeek API Key** (10 分钟)
   ```bash
   # 访问 DeepSeek Platform
   # 网址: https://platform.deepseek.com/
   # 注册/登录账号
   # 进入 API Keys 页面: https://platform.deepseek.com/api_keys
   # 创建新的 API Key
   # 复制密钥 (格式: sk-xxxxx...)
   ```

2. **配置 Render 环境变量** (5 分钟)
   ```bash
   # 1. 登录 Render Dashboard
   # 网址: https://dashboard.render.com/

   # 2. 选择 helloagents-platform 服务

   # 3. 进入 Environment 标签

   # 4. 添加环境变量:
   # Key: DEEPSEEK_API_KEY
   # Value: sk-xxxxx... (复制的 API Key)

   # 5. 保存 (Render 将自动重新部署)
   ```

3. **等待自动部署完成** (3-5 分钟)
   ```bash
   # 监控部署状态
   # Render Dashboard 会显示部署进度
   # 等待状态变为 "Live"
   ```

4. **验证 AI 助手功能** (10 分钟)
   ```bash
   # 1. 访问生产环境
   https://helloagents-platform.pages.dev

   # 2. 进入学习页面

   # 3. 切换到 AI 助手标签

   # 4. 发送测试消息:
   "你好, 请介绍一下 Python 的 Agent 开发"

   # 5. 验证是否收到回复

   # 6. 检查后端日志:
   # Render Dashboard → Logs
   # 确认没有 API Key 相关错误
   ```

5. **更新文档** (5 分钟)
   ```bash
   # 更新 README.md
   # 添加环境变量配置说明
   # 更新 FAQ.md
   # 添加 AI 助手配置常见问题
   ```

#### 验收标准
- [ ] DEEPSEEK_API_KEY 已配置到 Render
- [ ] 后端服务已重新部署
- [ ] AI 助手功能正常工作
- [ ] 能够正常发送和接收消息
- [ ] 后端日志无错误
- [ ] 文档已更新

#### 时间估算
- **总计**: 30-40 分钟
- **截止时间**: 2026-01-10 12:00 (今天中午)

#### 风险
- **低风险**: API Key 配置错误 → 重新检查和配置
- **低风险**: 部署失败 → 查看 Render 日志, 回滚如有必要

---

### 问题 2: 后端 API 路由失败

**优先级**: P0 - CRITICAL
**影响**: 前端功能可能无法正常工作
**发现时间**: 2026-01-09 (性能测试)
**当前状态**: 🔴 未解决

#### 问题描述
性能测试发现 `/api/v1/*` 路由全部返回 404, 包括:
- `/api/v1/ping` - 404
- `/api/v1/skills` - 404
- `/api/v1/lessons` - 404
- `/api/v1/execute` - 404

但 `/health` 端点正常返回 200。

#### 影响范围
- 可能影响前端功能 (课程加载, 代码执行, AI 助手)
- 用户无法正常使用平台
- 数据无法正常交互

#### 调查计划

**责任人**: API Architect + Backend Lead

**步骤**:

1. **验证问题存在** (10 分钟)
   ```bash
   # 测试生产环境 API
   BACKEND_URL="https://helloagents-platform.onrender.com"

   # 测试 /health (应该 200)
   curl -i $BACKEND_URL/health

   # 测试 /api/v1/ping (可能 404)
   curl -i $BACKEND_URL/api/v1/ping

   # 测试 /api/v1/lessons (可能 404)
   curl -i $BACKEND_URL/api/v1/lessons

   # 检查响应状态码和错误信息
   ```

2. **检查前端 API 调用** (15 分钟)
   ```bash
   # 1. 查看前端实际使用的 API 路径
   cd frontend/src
   grep -r "api/v1" . --include="*.ts" --include="*.tsx"

   # 2. 检查 API 基础 URL 配置
   cat src/config.ts  # 或 .env 文件

   # 3. 验证前端是否能正常工作
   # 打开浏览器开发者工具 → Network
   # 访问: https://helloagents-platform.pages.dev
   # 观察 API 请求和响应
   ```

3. **检查后端路由配置** (20 分钟)
   ```bash
   # 1. 查看 main.py 路由注册
   cat backend/app/main.py

   # 查找:
   # - app.include_router(...) 调用
   # - API v1 路由是否正确注册
   # - 路由前缀是否正确

   # 2. 查看 routers/__init__.py
   cat backend/app/routers/__init__.py

   # 3. 查看各个路由文件
   ls -la backend/app/routers/
   cat backend/app/routers/chat.py
   cat backend/app/routers/progress.py
   # 检查路由装饰器: @router.get("/lessons") 等
   ```

4. **检查 Render 配置** (15 分钟)
   ```bash
   # 1. 登录 Render Dashboard
   # 2. 检查 Web Service 配置:
   #    - Start Command: 是否正确 (python run.py 或 uvicorn ...)
   #    - Root Directory: 是否指向 backend/
   #    - Environment: Python 版本
   #    - Build Command: 是否正确安装依赖

   # 3. 查看最近的部署日志
   # Render Dashboard → Logs → Deploy Logs
   # 查找路由注册相关日志

   # 4. 查看运行时日志
   # Render Dashboard → Logs → Runtime Logs
   # 查找 404 错误日志
   ```

5. **检查 CORS 配置** (10 分钟)
   ```bash
   # 查看 CORS 中间件配置
   cat backend/app/main.py

   # 查找 CORSMiddleware 配置:
   # - allow_origins: 是否包含前端域名
   # - allow_methods: 是否包含 GET, POST
   # - allow_headers: 是否包含 Content-Type
   ```

#### 可能原因和解决方案

**原因 1: 路由未正确注册**
```python
# 问题: main.py 中可能遗漏了路由注册

# 解决方案: 检查并添加路由注册
# backend/app/main.py

from app.routers import chat, progress, submissions, users

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(progress.router, prefix="/api/v1", tags=["progress"])
app.include_router(submissions.router, prefix="/api/v1", tags=["submissions"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
```

**原因 2: Render Root Directory 配置错误**
```bash
# 问题: Render 可能在错误的目录启动应用

# 解决方案:
# 1. Render Dashboard → Settings → Root Directory
# 2. 确保设置为: backend
# 3. 确保 Start Command: python run.py 或 uvicorn app.main:app
```

**原因 3: API 版本中间件问题**
```python
# 问题: version_middleware 可能阻止了请求

# 解决方案: 检查中间件配置
# backend/app/middleware/version_middleware.py

# 确保中间件正确处理 /api/v1 路径
# 可能需要临时禁用进行测试
```

**原因 4: FastAPI 路由路径冲突**
```python
# 问题: 可能存在路由路径冲突

# 解决方案: 检查所有路由定义
# 确保没有重复的路径
# 确保路由顺序正确 (具体路径在前, 通配路径在后)
```

#### 调试流程

```bash
# Step 1: 本地复现问题
cd backend
python run.py

# 在另一个终端测试:
curl http://localhost:8000/api/v1/ping
curl http://localhost:8000/api/v1/lessons

# Step 2: 如果本地正常, 问题在部署配置
# 检查 Render 配置和环境变量

# Step 3: 如果本地也有问题, 问题在代码
# 检查路由注册和中间件配置

# Step 4: 修复后测试
# 本地测试 → Git Push → Render 自动部署 → 验证生产环境
```

#### 验收标准
- [ ] 所有 `/api/v1/*` 端点返回正确状态码 (200 或 404)
- [ ] 前端功能正常工作 (课程加载, 代码执行, AI 助手)
- [ ] 后端日志无路由错误
- [ ] 性能测试通过

#### 时间估算
- **调查**: 1-2 小时
- **修复**: 1-2 小时
- **测试和验证**: 0.5-1 小时
- **总计**: 2.5-5 小时
- **截止时间**: 2026-01-10 18:00 (今天下班前)

#### 风险
- **中等风险**: 需要代码修改 → 可能引入新 bug, 需要仔细测试
- **低风险**: 仅配置问题 → 修复简单, 风险低

---

### 问题 3: 移动端性能极差

**优先级**: P0 - CRITICAL
**影响**: 90% 移动用户可能流失
**发现时间**: 2026-01-09 (性能测试)
**当前状态**: 🔴 待优化

#### 问题描述
移动端 Lighthouse 性能评分仅 50/100, 关键指标严重超标:
- **LCP**: 9.0s (目标 <2.5s) - 慢 3.6 倍
- **FCP**: 7.4s (目标 <1.8s) - 慢 4.1 倍
- **TTI**: 20.2s (目标 <3.8s) - 慢 5.3 倍

用户需要等待 9 秒才能看到主要内容, 20 秒才能交互, 这是完全不可接受的。

#### 影响范围
- 移动端用户体验极差
- 可能导致 90% 移动用户流失
- 影响 SEO 排名 (Core Web Vitals)
- 品牌形象受损

#### 优化计划

**责任人**: Frontend Performance + Frontend Lead

**阶段 1: P0 优化 (本周完成)**

##### 1.1 Monaco Editor 懒加载 (预计节省 2-3秒)

**问题**: Monaco Editor 3.6MB + Workers 9MB = 12.6MB 阻塞首屏加载

**解决方案**:

```typescript
// 1. 创建 LazyCodeEditor 组件
// frontend/src/components/LazyCodeEditor.tsx

import { lazy, Suspense } from 'react';
import { CodeEditorSkeleton } from './CodeEditorSkeleton';

const MonacoEditor = lazy(() => import('@monaco-editor/react'));

export function LazyCodeEditor(props: CodeEditorProps) {
  return (
    <Suspense fallback={<CodeEditorSkeleton />}>
      <MonacoEditor {...props} />
    </Suspense>
  );
}

// 2. 创建加载骨架屏
// frontend/src/components/CodeEditorSkeleton.tsx

export function CodeEditorSkeleton() {
  return (
    <div className="h-full bg-gray-100 dark:bg-gray-800 animate-pulse">
      <div className="p-4 space-y-3">
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4"></div>
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/2"></div>
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-5/6"></div>
      </div>
    </div>
  );
}

// 3. 替换现有 CodeEditor
// frontend/src/pages/LearnPage.tsx

import { LazyCodeEditor } from '../components/LazyCodeEditor';

// 将 <CodeEditor /> 替换为 <LazyCodeEditor />
```

**工作量**: 2 天
**责任人**: Frontend Lead
**预期效果**: LCP -2.0s, FCP -1.5s

---

##### 1.2 路由代码分割 (预计节省 0.5-1秒)

**问题**: 主包 191KB 包含所有页面代码

**解决方案**:

```typescript
// frontend/src/App.tsx

import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { PageLoadingSpinner } from './components/PageLoadingSpinner';

// 懒加载路由组件
const LearnPage = lazy(() => import('./pages/LearnPage'));
const HomePage = lazy(() => import('./pages/HomePage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoadingSpinner />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/learn" element={<LearnPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

**工作量**: 1 天
**责任人**: Frontend Lead
**预期效果**: FCP -0.5s, 主包 191KB → 80KB

---

##### 1.3 关键资源 Preload (预计节省 0.5秒)

**问题**: 关键资源未预加载, 浏览器发现较晚

**解决方案**:

```html
<!-- frontend/index.html -->

<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Preconnect to API -->
  <link rel="preconnect" href="https://helloagents-platform.onrender.com">
  <link rel="dns-prefetch" href="https://helloagents-platform.onrender.com">

  <!-- Preload 关键资源 -->
  <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/index.js" as="script">
  <link rel="preload" href="/assets/index.css" as="style">

  <!-- 关键 CSS 内联 -->
  <style>
    /* 首屏关键 CSS */
    body { margin: 0; font-family: Inter, sans-serif; }
    .loading { /* loading 样式 */ }
  </style>

  <title>HelloAgents Platform</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
```

**工作量**: 0.5 天
**责任人**: Frontend Performance
**预期效果**: LCP -0.5s

---

**阶段 1 总结**:
- **总工作量**: 3.5 天
- **预期效果**:
  - LCP: 9.0s → 6.0s (-33%)
  - FCP: 7.4s → 5.4s (-27%)
  - Bundle: 191KB → 80KB (-58%)
- **截止日期**: 2026-01-13

---

**阶段 2: P1 优化 (下周完成)**

##### 2.1 Tree Shaking 优化 (预计节省 1.26秒)

```javascript
// vite.config.ts

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@headlessui/react', 'lucide-react'],
          'monaco': ['@monaco-editor/react', 'monaco-editor'],
        },
      },
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 移除 console.log
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info'],
      },
    },
  },
});
```

**工作量**: 1 天
**预期效果**: TTI -1.26s

---

##### 2.2 图片优化 (预计节省 1.6秒)

```bash
# 1. 转换图片为 WebP 格式
npm install -D @squoosh/cli
npx @squoosh/cli --webp auto public/images/*.{png,jpg}

# 2. 添加响应式图片
<img
  src="/images/hero.webp"
  srcset="
    /images/hero-320w.webp 320w,
    /images/hero-640w.webp 640w,
    /images/hero-1280w.webp 1280w
  "
  sizes="(max-width: 640px) 320px, (max-width: 1024px) 640px, 1280px"
  alt="Hero"
  loading="lazy"
/>
```

**工作量**: 0.5 天
**预期效果**: LCP -1.6s

---

##### 2.3 缓存策略优化

```javascript
// frontend/public/_headers (Cloudflare Pages)

# 静态资源长期缓存
/assets/*
  Cache-Control: public, max-age=31536000, immutable

# HTML 文件不缓存
/*.html
  Cache-Control: public, max-age=0, must-revalidate

# 字体文件
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
```

**工作量**: 0.5 天
**预期效果**: 二次访问加载时间 -80%

---

**阶段 2 总结**:
- **总工作量**: 2 天
- **预期效果**:
  - TTI: 6.0s → 4.7s (-22%)
  - 图片加载: -1.6s
  - 二次访问: 几乎瞬时
- **截止日期**: 2026-01-16

---

#### 最终预期效果

| 指标 | 当前 | 阶段1 | 阶段2 | 目标 | 达标 |
|------|------|-------|-------|------|------|
| **Lighthouse** | 50 | 65 | 75-80 | 75+ | ✅ |
| **LCP** | 9.0s | 6.0s | 3.5-4.0s | <4.0s | ✅ |
| **FCP** | 7.4s | 5.4s | 2.5-3.0s | <3.0s | ✅ |
| **TTI** | 20.2s | 18.9s | 5.0-6.0s | <6.0s | ✅ |

#### 验收标准
- [ ] 移动端 Lighthouse ≥ 75
- [ ] LCP < 4.0s
- [ ] FCP < 3.0s
- [ ] TTI < 6.0s
- [ ] 用户体验显著改善

#### 时间估算
- **阶段 1 (P0)**: 3.5 天 (2026-01-13)
- **阶段 2 (P1)**: 2 天 (2026-01-16)
- **总计**: 5.5 天

---

## 🟡 High 优先级 - 本周内解决

### 问题 4: Docker 沙箱未完成安全审计

**优先级**: P1 - HIGH
**影响**: 安全风险未知
**责任人**: Security Auditor

#### 审计计划

**阶段 1: 代码审查** (2 天)
- [ ] 审查 Docker 容器配置 (网络, 文件系统, capabilities)
- [ ] 审查资源限制 (CPU, 内存, 进程数)
- [ ] 审查代码执行流程
- [ ] 审查输入验证和清理

**阶段 2: 渗透测试** (2 天)
- [ ] 尝试容器逃逸
- [ ] 尝试资源耗尽攻击
- [ ] 尝试注入恶意代码
- [ ] 尝试网络访问

**阶段 3: 漏洞修复** (1 天)
- [ ] 修复发现的安全问题
- [ ] 强化安全配置
- [ ] 更新文档

**阶段 4: 安全报告** (0.5 天)
- [ ] 编写安全审计报告
- [ ] 总结发现和修复
- [ ] 提供安全建议

**截止日期**: 2026-01-16

---

### 问题 5: 测试覆盖率不足

**优先级**: P1 - MEDIUM
**影响**: 代码质量风险
**责任人**: QA Lead + 开发团队

#### 提升计划

**目标**: 前端 70%+, 后端 85%+

**前端 (当前 59.68% → 目标 70%+)**:

```typescript
// 1. CodeEditor 测试 (0% → 70%)
// frontend/src/components/CodeEditor.test.tsx

describe('CodeEditor', () => {
  it('should render editor', () => {
    render(<CodeEditor value="" onChange={() => {}} />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('should call onChange when value changes', () => {
    const onChange = vi.fn();
    render(<CodeEditor value="" onChange={onChange} />);
    // 模拟用户输入
    // 验证 onChange 被调用
  });
});

// 2. Hooks 测试
// frontend/src/hooks/useLesson.test.ts

describe('useLesson', () => {
  it('should load lesson data', async () => {
    const { result } = renderHook(() => useLesson(1));
    await waitFor(() => {
      expect(result.current.lesson).toBeDefined();
    });
  });
});

// 3. API 服务测试
// frontend/src/services/api.test.ts

describe('api', () => {
  it('should execute code successfully', async () => {
    // Mock apiClient
    const result = await executeCode({ code: 'print("hello")' });
    expect(result.success).toBe(true);
  });
});
```

**工作量**: 3-5 天
**截止日期**: 2026-01-17

---

## 📊 进度跟踪表

| 任务 | 责任人 | 优先级 | 状态 | 开始日期 | 截止日期 | 进度 |
|------|--------|--------|------|----------|----------|------|
| **配置 AI 助手** | DevOps | P0 | 🔴 待开始 | 2026-01-10 | 2026-01-10 | 0% |
| **修复 API 路由** | API Architect | P0 | 🔴 待开始 | 2026-01-10 | 2026-01-10 | 0% |
| **Monaco 懒加载** | Frontend Lead | P0 | 🟡 待开始 | 2026-01-10 | 2026-01-12 | 0% |
| **路由代码分割** | Frontend Lead | P0 | 🟡 待开始 | 2026-01-12 | 2026-01-13 | 0% |
| **关键资源 Preload** | Frontend Perf | P0 | 🟡 待开始 | 2026-01-12 | 2026-01-13 | 0% |
| **Tree Shaking** | Frontend Perf | P1 | 🟡 待开始 | 2026-01-13 | 2026-01-14 | 0% |
| **图片优化** | Frontend Perf | P1 | 🟡 待开始 | 2026-01-14 | 2026-01-15 | 0% |
| **缓存策略** | Frontend Perf | P1 | 🟡 待开始 | 2026-01-15 | 2026-01-16 | 0% |
| **安全审计** | Security | P1 | 🟡 待开始 | 2026-01-11 | 2026-01-16 | 0% |
| **测试覆盖率** | QA + Dev | P1 | 🟡 待开始 | 2026-01-11 | 2026-01-17 | 0% |

---

## 📅 每日站会议题

### 2026-01-10 (今天)
- 🔴 **CRITICAL**: AI 助手配置进展?
- 🔴 **CRITICAL**: API 路由调查结果?
- 🟡 Monaco 懒加载准备工作?
- 障碍: 需要什么支持?

### 2026-01-11 (明天)
- AI 助手验证结果?
- API 路由修复完成?
- Monaco 懒加载进展?
- 安全审计开始?

### 2026-01-13 (周一)
- P0 优化进展汇总
- 遇到的技术难点?
- 需要调整计划吗?

### 2026-01-16 (周四)
- P1 优化进展汇总
- 安全审计结果?
- Sprint 3 收尾工作

---

## 🎯 成功指标

### 本周必达目标 (2026-01-16)
- [ ] AI 助手功能正常 (100%)
- [ ] API 路由问题修复 (100%)
- [ ] 移动端 LCP < 6.0s (第一阶段优化)
- [ ] 安全审计完成

### Sprint 3 整体目标 (2026-01-19)
- [ ] 移动端 LCP < 4.0s
- [ ] Lighthouse (移动) ≥ 75
- [ ] 测试覆盖率 ≥ 70%
- [ ] 所有 P0/P1 问题解决

---

## 📞 升级机制

### 问题升级标准

**Level 1: 团队内部** (< 1 天)
- 技术问题
- 小的障碍
- 由团队成员或 Tech Lead 解决

**Level 2: PM 介入** (1-3 天)
- 跨团队协调
- 资源冲突
- PM 协调相关方解决

**Level 3: 管理层升级** (> 3 天)
- 重大风险
- 资源短缺
- 战略调整
- 升级给管理层决策

### 当前升级项

**Level 2 (PM 介入)**:
- API 路由问题 (需要调查和协调)
- 移动端性能优化 (需要资源协调)

**Level 3 (管理层升级)**:
- 暂无

---

## ✅ 验收和交付

### Sprint 3 最终验收

**日期**: 2026-01-19
**参与者**: PM + 团队 + 干系人

**验收清单**:
- [ ] 所有 P0 任务 100% 完成
- [ ] 所有 P1 任务 90%+ 完成
- [ ] 代码质量 A 级
- [ ] 测试覆盖率 70%+
- [ ] Lighthouse (移动) ≥ 75
- [ ] 文档完整更新
- [ ] 生产环境稳定运行

---

**文档编制**: Technical Project Manager
**最后更新**: 2026-01-10
**版本**: v1.0
