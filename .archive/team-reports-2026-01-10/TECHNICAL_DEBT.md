# HelloAgents Platform - 技术债务管理

**最后更新**: 2026-01-09
**负责人**: 技术团队

---

## 📊 技术债务总览

| 状态 | 数量 | 预估工作量 | 说明 |
|------|------|-----------|------|
| 🔴 高优先级 | 1 | 3-5 天 | 需要尽快处理 |
| 🟡 中优先级 | 3 | 5-7 天 | 本月内处理 |
| 🟢 低优先级 | 3 | 4-6 天 | 可延后处理 |
| **总计** | **7** | **12-18 天** | |

---

## 🔴 高优先级技术债务

### TD-1: 提升前端测试覆盖率

**创建日期**: 2026-01-09
**优先级**: 🔴 高
**预估工作量**: 3-5 天
**负责人**: 待分配

#### 问题描述
当前前端测试覆盖率为 59.68%，低于行业标准（70%+）。以下模块缺少测试：

```
缺少测试的关键模块:
├── CodeEditor.tsx: 0% → 目标 70%
├── LearnPage.tsx: 0% → 目标 60%
├── hooks/
│   ├── useChatMessages.ts: 0% → 目标 70%
│   ├── useCodeExecution.ts: 0% → 目标 70%
│   └── useLesson.ts: 0% → 目标 70%
├── services/api.ts: 0% → 目标 80%
└── components/learn/: 0% → 目标 60%
```

#### 影响分析
- **可维护性**: ⬇️ 降低 - 难以安全重构
- **质量保证**: ⬇️ 降低 - 回归风险高
- **开发速度**: ⬇️ 降低 - 手动测试耗时

#### 解决方案

##### 1. 添加 Hooks 单元测试
```typescript
// frontend/src/hooks/__tests__/useChatMessages.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useChatMessages } from '../useChatMessages';
import { chatStorage } from '../../utils/storage';
import { chatWithAI } from '../../services/api';

jest.mock('../../utils/storage');
jest.mock('../../services/api');

describe('useChatMessages', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should load chat history from storage', () => {
    const mockMessages = [
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: 'Hi!' },
    ];

    (chatStorage.get as jest.Mock).mockReturnValue(mockMessages);

    const { result } = renderHook(() => useChatMessages('lesson-1', ''));

    expect(result.current.chatMessages).toEqual(mockMessages);
  });

  it('should send message and receive AI response', async () => {
    (chatWithAI as jest.Mock).mockResolvedValue({
      message: 'AI response',
      success: true,
    });

    const { result } = renderHook(() => useChatMessages('lesson-1', 'code'));

    result.current.setChatInput('Test message');
    await result.current.sendMessage();

    await waitFor(() => {
      expect(result.current.chatMessages).toHaveLength(2);
      expect(result.current.chatMessages[1].content).toBe('AI response');
    });
  });
});
```

##### 2. 添加 API 服务测试
```typescript
// frontend/src/services/__tests__/api.test.ts
import { executeCode, chatWithAI } from '../api';
import { apiClient } from '../../utils/apiClient';

jest.mock('../../utils/apiClient');

describe('api.ts', () => {
  describe('executeCode', () => {
    it('should execute code successfully', async () => {
      const mockResponse = {
        success: true,
        output: 'Hello World',
        execution_time: 0.5,
      };

      (apiClient.post as jest.Mock).mockResolvedValue(mockResponse);

      const result = await executeCode({
        code: 'print("Hello World")',
        language: 'python',
      });

      expect(result).toEqual(mockResponse);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/execute',
        expect.any(Object),
        expect.objectContaining({ timeout: 60000 })
      );
    });

    it('should handle execution failure', async () => {
      const mockError = new Error('Execution failed');
      (apiClient.post as jest.Mock).mockRejectedValue(mockError);

      await expect(
        executeCode({ code: 'invalid code' })
      ).rejects.toThrow('Execution failed');
    });
  });
});
```

##### 3. 添加组件快照测试
```typescript
// frontend/src/components/__tests__/CodeEditor.test.tsx
import { render } from '@testing-library/react';
import { CodeEditor } from '../CodeEditor';

describe('CodeEditor', () => {
  it('should render with default props', () => {
    const { container } = render(<CodeEditor value="" />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it('should match snapshot', () => {
    const { container } = render(
      <CodeEditor value="print('Hello')" language="python" />
    );
    expect(container).toMatchSnapshot();
  });

  it('should call onChange when code changes', () => {
    const handleChange = jest.fn();
    render(<CodeEditor value="" onChange={handleChange} />);
    // 测试代码变更
  });
});
```

#### 完成标准
- [ ] useChatMessages 测试覆盖率 > 70%
- [ ] useCodeExecution 测试覆盖率 > 70%
- [ ] useLesson 测试覆盖率 > 70%
- [ ] services/api.ts 测试覆盖率 > 80%
- [ ] CodeEditor 测试覆盖率 > 70%
- [ ] LearnPage 测试覆盖率 > 60%
- [ ] 所有测试通过
- [ ] CI/CD 集成测试覆盖率检查

#### 时间表
- **Week 1**: Hooks 单元测试（3 天）
- **Week 2**: API 和组件测试（2 天）

---

## 🟡 中优先级技术债务

### TD-2: 添加性能监控和指标收集

**创建日期**: 2026-01-09
**优先级**: 🟡 中
**预估工作量**: 2-3 天
**负责人**: 待分配

#### 问题描述
当前缺少系统化的性能监控，难以发现和定位性能瓶颈。

#### 解决方案

##### 1. 前端性能监控
```typescript
// frontend/src/utils/performance.ts
import { logger } from './logger';

export class PerformanceMonitor {
  private marks: Map<string, number> = new Map();

  /**
   * 开始性能测量
   */
  start(name: string): void {
    this.marks.set(name, performance.now());
  }

  /**
   * 结束性能测量
   */
  end(name: string): number {
    const startTime = this.marks.get(name);
    if (!startTime) {
      logger.warn(`Performance mark "${name}" not found`);
      return 0;
    }

    const duration = performance.now() - startTime;
    this.marks.delete(name);

    logger.performance(name, duration);

    // 发送到监控服务
    this.sendMetric(name, duration);

    return duration;
  }

  /**
   * 测量函数执行时间
   */
  measure<T>(name: string, fn: () => T): T {
    this.start(name);
    const result = fn();
    this.end(name);
    return result;
  }

  /**
   * 测量异步函数执行时间
   */
  async measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    this.start(name);
    try {
      return await fn();
    } finally {
      this.end(name);
    }
  }

  private sendMetric(name: string, duration: number): void {
    // TODO: 发送到监控服务（如 DataDog, New Relic）
    if (window.gtag) {
      window.gtag('event', 'performance', {
        event_category: 'Performance',
        event_label: name,
        value: Math.round(duration),
      });
    }
  }
}

export const performanceMonitor = new PerformanceMonitor();
```

##### 2. React 性能分析
```typescript
// frontend/src/components/PerformanceProfiler.tsx
import { Profiler, ProfilerOnRenderCallback } from 'react';
import { logger } from '../utils/logger';

const onRenderCallback: ProfilerOnRenderCallback = (
  id,
  phase,
  actualDuration,
  baseDuration,
  startTime,
  commitTime
) => {
  logger.performance(`React.${id}.${phase}`, actualDuration, 'ms');

  // 记录慢渲染
  if (actualDuration > 100) {
    logger.warn(`Slow render detected: ${id}`, {
      phase,
      actualDuration,
      baseDuration,
    });
  }
};

export function PerformanceProfiler({
  id,
  children
}: {
  id: string;
  children: React.ReactNode;
}) {
  return (
    <Profiler id={id} onRender={onRenderCallback}>
      {children}
    </Profiler>
  );
}
```

#### 完成标准
- [ ] 实现 PerformanceMonitor 工具类
- [ ] 集成 React Profiler
- [ ] 关键路径添加性能监控
- [ ] 配置监控服务（如 DataDog）
- [ ] 设置性能告警阈值

---

### TD-3: 完善后端日志上报接口

**创建日期**: 2026-01-09
**优先级**: 🟡 中
**预估工作量**: 1-2 天
**负责人**: 待分配

#### 问题描述
前端日志当前只记录到浏览器 console，缺少统一的日志上报机制。

#### 解决方案

##### 后端日志接收 API
```python
# backend/app/routers/logs.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/logs", tags=["logs"])

class LogEntry(BaseModel):
    level: str  # debug, info, warn, error
    message: str
    timestamp: str
    data: Optional[dict] = None
    user_agent: Optional[str] = None
    url: Optional[str] = None

@router.post("/")
async def receive_logs(logs: List[LogEntry]):
    """接收前端日志"""
    for log in logs:
        # 记录到结构化日志
        logger.log(
            log.level,
            f"Frontend: {log.message}",
            extra={
                "timestamp": log.timestamp,
                "data": log.data,
                "user_agent": log.user_agent,
                "url": log.url,
            }
        )

    return {"success": True, "received": len(logs)}
```

##### 前端日志批量上报
```typescript
// frontend/src/utils/logger.ts
class LogBuffer {
  private buffer: LogEntry[] = [];
  private flushInterval: number = 5000; // 5秒
  private maxBufferSize: number = 50;

  constructor() {
    // 定期刷新
    setInterval(() => this.flush(), this.flushInterval);

    // 页面卸载时刷新
    window.addEventListener('beforeunload', () => this.flush());
  }

  add(entry: LogEntry): void {
    this.buffer.push(entry);

    if (this.buffer.length >= this.maxBufferSize) {
      this.flush();
    }
  }

  async flush(): Promise<void> {
    if (this.buffer.length === 0) return;

    const logs = [...this.buffer];
    this.buffer = [];

    try {
      await apiClient.post('/api/logs', logs);
    } catch (error) {
      console.error('Failed to send logs:', error);
      // 失败的日志重新加入缓冲区
      this.buffer.unshift(...logs);
    }
  }
}
```

#### 完成标准
- [ ] 实现日志接收 API
- [ ] 实现日志批量上报
- [ ] 配置日志过滤规则
- [ ] 添加日志查询界面（可选）

---

### TD-4: 添加 API 速率限制

**创建日期**: 2026-01-09
**优先级**: 🟡 中
**预估工作量**: 1-2 天
**负责人**: 待分配

#### 问题描述
API 端点缺少速率限制，存在被恶意滥用的风险。

#### 解决方案

```python
# backend/app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# 在 main.py 中应用
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 在路由中使用
@router.post("/api/execute")
@limiter.limit("10/minute")  # 每分钟最多 10 次
async def execute_code(request: Request, ...):
    ...

@router.post("/api/chat")
@limiter.limit("20/minute")  # 每分钟最多 20 次
async def chat(request: Request, ...):
    ...
```

#### 完成标准
- [ ] 安装并配置 slowapi
- [ ] 为关键 API 添加速率限制
- [ ] 配置合理的限制阈值
- [ ] 添加速率限制文档

---

## 🟢 低优先级技术债务

### TD-5: 拆分 ContainerPool 类

**创建日期**: 2026-01-09
**优先级**: 🟢 低
**预估工作量**: 2-3 天
**负责人**: 待分配

#### 问题描述
`container_pool.py` 文件过长（1196 行），包含多个职责。

#### 解决方案

```
拆分为多个模块:
backend/app/container_pool/
├── __init__.py
├── pool.py              # 容器池主类
├── health_check.py      # 健康检查逻辑
├── lifecycle.py         # 容器生命周期管理
├── reset.py             # 容器重置逻辑
├── config.py            # 配置常量
└── metadata.py          # 元数据定义
```

#### 完成标准
- [ ] 拆分为多个模块
- [ ] 保持向后兼容
- [ ] 更新测试
- [ ] 更新文档

---

### TD-6: 添加 Swagger UI

**创建日期**: 2026-01-09
**优先级**: 🟢 低
**预估工作量**: 1 天
**负责人**: 待分配

#### 问题描述
API 文档需要手动维护，缺少交互式文档界面。

#### 解决方案

FastAPI 内置 Swagger UI，只需启用：

```python
# backend/run.py
app = FastAPI(
    title="HelloAgents API",
    description="AI Agent 学习平台 API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)
```

访问 `http://localhost:8000/docs` 查看 API 文档。

#### 完成标准
- [ ] 启用 Swagger UI
- [ ] 完善 API 描述和示例
- [ ] 添加认证配置（如需要）
- [ ] 更新 README

---

### TD-7: 实现前端日志上报

**创建日期**: 2026-01-09
**优先级**: 🟢 低
**预估工作量**: 1-2 天
**负责人**: 待分配

#### 问题描述
当前日志只记录到浏览器 console，生产环境难以追踪问题。

#### 解决方案
参见 TD-3 的前端部分。

#### 完成标准
- [ ] 实现日志批量上报
- [ ] 配置日志级别过滤
- [ ] 添加用户上下文信息
- [ ] 测试日志上报功能

---

## 📅 技术债务偿还计划

### Sprint 1 (本周)
- [x] ✅ 重构 API 客户端和 Storage 管理器（已完成）
- [ ] 🎯 TD-1: 提升测试覆盖率（进行中）

### Sprint 2 (本月)
- [ ] TD-2: 添加性能监控
- [ ] TD-3: 完善日志上报
- [ ] TD-4: 添加 API 速率限制

### Sprint 3 (下月)
- [ ] TD-5: 拆分 ContainerPool 类
- [ ] TD-6: 添加 Swagger UI
- [ ] TD-7: 实现前端日志上报

---

## 📊 技术债务趋势

```
技术债务趋势图:

债务数量
    ▲
  8 │     ●
  7 │   ●
  6 │ ●
  5 │
  4 │           ○ (预期)
  3 │               ○
  2 │                   ○
  1 │________________________▶
     Dec  Jan  Feb  Mar  时间

  ● 实际债务
  ○ 计划债务
```

### 历史记录

| 日期 | 债务数量 | 已偿还 | 新增 | 说明 |
|------|---------|--------|------|------|
| 2026-01-09 | 7 | 2 | 7 | 初次审查，重构 API 和 Storage |

---

## 🎯 最佳实践

### 技术债务管理原则

1. **及时记录**: 发现债务立即记录
2. **优先级明确**: 根据影响和紧急程度评估
3. **定期审查**: 每月审查和更新
4. **逐步偿还**: 每个 Sprint 偿还 1-2 个
5. **预防为主**: Code Review 时防止新债务

### 债务评估标准

#### 优先级评分矩阵

| 影响 / 紧急度 | 低 | 中 | 高 |
|-------------|---|---|---|
| **高** | 🟡 中 | 🔴 高 | 🔴 紧急 |
| **中** | 🟢 低 | 🟡 中 | 🔴 高 |
| **低** | 🟢 低 | 🟢 低 | 🟡 中 |

#### 影响维度
- 安全性
- 性能
- 可维护性
- 用户体验
- 开发效率

#### 紧急度维度
- 立即（本周）
- 短期（本月）
- 中期（本季度）
- 长期（下季度）

---

## 📝 更新日志

### 2026-01-09
- 初始版本
- 记录 7 个技术债务
- 完成 API 客户端和 Storage 重构

---

**文档维护**: 请在每次 Sprint 结束后更新此文档
