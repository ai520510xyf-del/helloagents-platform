# API 使用示例

完整的 HelloAgents API v1 使用示例和代码片段。

## 目录

1. [基础请求](#基础请求)
2. [代码执行](#代码执行)
3. [AI 功能](#ai-功能)
4. [课程管理](#课程管理)
5. [系统监控](#系统监控)
6. [错误处理](#错误处理)
7. [完整示例](#完整示例)

---

## 基础请求

### 查看 API 版本信息

```bash
curl http://localhost:8000/api/version
```

响应:

```json
{
  "current_version": "v1",
  "supported_versions": ["v1"],
  "deprecated_versions": [],
  "latest_version": "v1",
  "version_info": {
    "v1": {
      "status": "stable",
      "release_date": "2026-01-08",
      "deprecation_date": null,
      "end_of_life_date": null,
      "description": "Initial stable release with code execution, lessons, sandbox monitoring, and AI chat features."
    }
  }
}
```

### 健康检查

```bash
curl -i http://localhost:8000/health
```

注意响应头:

```http
HTTP/1.1 200 OK
X-API-Version: v1
X-Supported-Versions: v1
Content-Type: application/json
```

---

## 代码执行

### 基础代码执行

```bash
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")\nprint(2 + 2)",
    "language": "python",
    "timeout": 30
  }'
```

响应:

```json
{
  "success": true,
  "output": "Hello, World!\n4\n",
  "error": null,
  "execution_time": 0.023
}
```

### 错误处理示例

```bash
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(undefined_variable)",
    "language": "python"
  }'
```

响应:

```json
{
  "success": false,
  "output": "",
  "error": "NameError: name 'undefined_variable' is not defined",
  "execution_time": 0.012
}
```

### JavaScript 客户端

```javascript
async function executeCode(code) {
  const response = await fetch('/api/v1/code/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      code,
      language: 'python',
      timeout: 30
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return await response.json();
}

// 使用
try {
  const result = await executeCode('print("Hello")');
  console.log(result.output); // "Hello\n"
} catch (error) {
  console.error('执行失败:', error);
}
```

---

## AI 功能

### AI 智能提示

```bash
curl -X POST http://localhost:8000/api/v1/code/hint \
  -H "Content-Type: application/json" \
  -d '{
    "code": "class ReActAgent:\n    def __init__(self",
    "cursor_line": 2,
    "cursor_column": 20,
    "language": "python"
  }'
```

响应:

```json
{
  "current_context": "ReActAgent.__init__() 初始化方法",
  "hint": "你正在编写 ReAct Agent 的初始化方法。需要接收 llm_client 和 tool_executor 两个参数...",
  "reference_code": "def __init__(self, llm_client, tool_executor):\n    self.llm_client = llm_client\n    ...",
  "key_concepts": [
    "llm_client: LLM 客户端，负责推理和决策",
    "tool_executor: 工具执行器，负责执行具体操作"
  ]
}
```

### AI 聊天助手

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "什么是 ReAct Agent?",
    "conversation_history": [],
    "lesson_id": "1",
    "code": "class Agent: pass"
  }'
```

响应:

```json
{
  "message": "ReAct (Reasoning + Acting) 是一种结合推理和行动的 Agent 范式...",
  "success": true
}
```

### TypeScript 聊天客户端

```typescript
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

class ChatClient {
  private history: ChatMessage[] = [];

  async sendMessage(message: string, lessonId?: string, code?: string) {
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_history: this.history,
        lesson_id: lessonId,
        code
      })
    });

    const result = await response.json();

    if (result.success) {
      // 更新历史
      this.history.push({ role: 'user', content: message });
      this.history.push({ role: 'assistant', content: result.message });

      // 只保留最近10轮对话
      if (this.history.length > 20) {
        this.history = this.history.slice(-20);
      }
    }

    return result;
  }

  clearHistory() {
    this.history = [];
  }
}

// 使用
const chat = new ChatClient();
const response = await chat.sendMessage('如何实现 ReAct Agent?', '1');
console.log(response.message);
```

---

## 课程管理

### 获取课程列表

```bash
curl http://localhost:8000/api/v1/lessons
```

响应:

```json
{
  "success": true,
  "lessons": [
    {
      "id": "1",
      "title": "第1章 - ReAct Agent 基础",
      "description": "...",
      "order": 1
    }
  ]
}
```

### 获取课程详情

```bash
curl http://localhost:8000/api/v1/lessons/1
```

响应:

```json
{
  "lesson_id": "1",
  "title": "第1章 - ReAct Agent 基础",
  "content": "# ReAct Agent\n\nReAct 是...",
  "code_template": "class ReActAgent:\n    pass"
}
```

### React Hook 示例

```typescript
import { useState, useEffect } from 'react';

interface Lesson {
  lesson_id: string;
  title: string;
  content: string;
  code_template: string;
}

function useLessons() {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch('/api/v1/lessons')
      .then(res => res.json())
      .then(data => setLessons(data.lessons))
      .catch(err => setError(err))
      .finally(() => setLoading(false));
  }, []);

  return { lessons, loading, error };
}

function useLesson(lessonId: string) {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/v1/lessons/${lessonId}`)
      .then(res => res.json())
      .then(data => setLesson(data))
      .finally(() => setLoading(false));
  }, [lessonId]);

  return { lesson, loading };
}

// 使用
function LessonViewer({ lessonId }: { lessonId: string }) {
  const { lesson, loading } = useLesson(lessonId);

  if (loading) return <div>加载中...</div>;
  if (!lesson) return <div>课程不存在</div>;

  return (
    <div>
      <h1>{lesson.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: lesson.content }} />
      <pre><code>{lesson.code_template}</code></pre>
    </div>
  );
}
```

---

## 系统监控

### 沙箱统计

```bash
curl http://localhost:8000/api/v1/sandbox/pool/stats
```

响应:

```json
{
  "pool_enabled": true,
  "available_containers": 5,
  "in_use_containers": 2,
  "total_executions": 1523,
  "timestamp": "2026-01-08T15:30:00.000Z"
}
```

### 监控仪表板示例

```typescript
import { useState, useEffect } from 'react';

interface PoolStats {
  pool_enabled: boolean;
  available_containers?: number;
  in_use_containers?: number;
  total_executions?: number;
  timestamp: string;
}

function SandboxMonitor() {
  const [stats, setStats] = useState<PoolStats | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      const response = await fetch('/api/v1/sandbox/pool/stats');
      const data = await response.json();
      setStats(data);
    };

    // 初始获取
    fetchStats();

    // 每5秒更新一次
    const interval = setInterval(fetchStats, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!stats) return <div>加载中...</div>;

  return (
    <div className="sandbox-stats">
      <h2>沙箱状态</h2>
      <div>
        状态: {stats.pool_enabled ? '✅ 启用' : '❌ 未启用'}
      </div>
      {stats.pool_enabled && (
        <>
          <div>可用容器: {stats.available_containers}</div>
          <div>使用中: {stats.in_use_containers}</div>
          <div>总执行次数: {stats.total_executions}</div>
          <div>
            使用率:
            {(stats.in_use_containers! /
              (stats.available_containers! + stats.in_use_containers!) * 100
            ).toFixed(1)}%
          </div>
        </>
      )}
      <small>更新时间: {new Date(stats.timestamp).toLocaleString()}</small>
    </div>
  );
}
```

---

## 错误处理

### 统一错误格式

所有错误响应遵循统一格式:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "path": "/api/v1/code/execute",
    "timestamp": 1704672000.0,
    "details": {
      "validation_errors": [
        {
          "field": "code",
          "message": "Field required",
          "type": "missing"
        }
      ]
    }
  }
}
```

### TypeScript 错误处理

```typescript
interface APIError {
  error: {
    code: string;
    message: string;
    path: string;
    timestamp: number;
    details?: any;
  };
}

class APIClient {
  private baseURL = '/api/v1';

  async request<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(this.baseURL + path, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error: APIError = await response.json();
      throw new APIException(
        error.error.message,
        error.error.code,
        response.status,
        error.error.details
      );
    }

    return await response.json();
  }

  async executeCode(code: string) {
    return this.request<CodeExecutionResponse>('/code/execute', {
      method: 'POST',
      body: JSON.stringify({ code, language: 'python' }),
    });
  }
}

class APIException extends Error {
  constructor(
    message: string,
    public code: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIException';
  }
}

// 使用
const api = new APIClient();

try {
  const result = await api.executeCode('print("Hello")');
  console.log(result.output);
} catch (error) {
  if (error instanceof APIException) {
    console.error(`API Error [${error.code}]:`, error.message);
    if (error.details) {
      console.error('Details:', error.details);
    }
  } else {
    console.error('Unexpected error:', error);
  }
}
```

---

## 完整示例

### 完整的代码编辑器组件

```typescript
import React, { useState, useEffect } from 'react';

interface CodeEditorProps {
  lessonId: string;
}

export function CodeEditor({ lessonId }: CodeEditorProps) {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [executing, setExecuting] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  // 加载课程模板
  useEffect(() => {
    fetch(`/api/v1/lessons/${lessonId}`)
      .then(res => res.json())
      .then(data => setCode(data.code_template));
  }, [lessonId]);

  // 执行代码
  const executeCode = async () => {
    setExecuting(true);
    setOutput('执行中...');

    try {
      const response = await fetch('/api/v1/code/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language: 'python' }),
      });

      const result = await response.json();

      if (result.success) {
        setOutput(result.output || '(无输出)');
      } else {
        setOutput(`错误:\n${result.error}`);
      }
    } catch (error) {
      setOutput(`请求失败: ${error}`);
    } finally {
      setExecuting(false);
    }
  };

  // 发送聊天消息
  const sendMessage = async () => {
    if (!chatMessage.trim()) return;

    const userMessage = chatMessage;
    setChatMessage('');

    // 添加用户消息到历史
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          conversation_history: chatHistory,
          lesson_id: lessonId,
          code,
        }),
      });

      const result = await response.json();

      if (result.success) {
        setChatHistory(prev => [
          ...prev,
          { role: 'assistant', content: result.message },
        ]);
      }
    } catch (error) {
      console.error('聊天失败:', error);
    }
  };

  return (
    <div className="code-editor">
      <div className="editor-panel">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="code-input"
          placeholder="在这里编写代码..."
        />
        <button onClick={executeCode} disabled={executing}>
          {executing ? '执行中...' : '运行代码'}
        </button>
      </div>

      <div className="output-panel">
        <h3>输出</h3>
        <pre>{output}</pre>
      </div>

      <div className={`chat-panel ${chatOpen ? 'open' : ''}`}>
        <button onClick={() => setChatOpen(!chatOpen)}>
          {chatOpen ? '关闭' : '打开'} AI 助手
        </button>

        {chatOpen && (
          <>
            <div className="chat-history">
              {chatHistory.map((msg, i) => (
                <div key={i} className={`message ${msg.role}`}>
                  <strong>{msg.role === 'user' ? '你' : 'AI'}:</strong>
                  <p>{msg.content}</p>
                </div>
              ))}
            </div>

            <div className="chat-input">
              <input
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="向 AI 助手提问..."
              />
              <button onClick={sendMessage}>发送</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
```

### Python 客户端

```python
import requests
from typing import Optional, List, Dict

class HelloAgentsClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_v1 = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def get_version(self) -> Dict:
        """获取 API 版本信息"""
        response = self.session.get(f"{self.base_url}/api/version")
        response.raise_for_status()
        return response.json()

    def execute_code(self, code: str, language: str = "python",
                    timeout: int = 30) -> Dict:
        """执行代码"""
        response = self.session.post(
            f"{self.api_v1}/code/execute",
            json={
                "code": code,
                "language": language,
                "timeout": timeout
            }
        )
        response.raise_for_status()
        return response.json()

    def get_hint(self, code: str, cursor_line: int,
                cursor_column: int, language: str = "python") -> Dict:
        """获取 AI 提示"""
        response = self.session.post(
            f"{self.api_v1}/code/hint",
            json={
                "code": code,
                "cursor_line": cursor_line,
                "cursor_column": cursor_column,
                "language": language
            }
        )
        response.raise_for_status()
        return response.json()

    def chat(self, message: str, conversation_history: Optional[List] = None,
            lesson_id: Optional[str] = None, code: Optional[str] = None) -> Dict:
        """与 AI 助手聊天"""
        response = self.session.post(
            f"{self.api_v1}/chat",
            json={
                "message": message,
                "conversation_history": conversation_history or [],
                "lesson_id": lesson_id,
                "code": code
            }
        )
        response.raise_for_status()
        return response.json()

    def get_lessons(self) -> Dict:
        """获取课程列表"""
        response = self.session.get(f"{self.api_v1}/lessons")
        response.raise_for_status()
        return response.json()

    def get_lesson(self, lesson_id: str) -> Dict:
        """获取课程详情"""
        response = self.session.get(f"{self.api_v1}/lessons/{lesson_id}")
        response.raise_for_status()
        return response.json()

    def get_sandbox_stats(self) -> Dict:
        """获取沙箱统计"""
        response = self.session.get(f"{self.api_v1}/sandbox/pool/stats")
        response.raise_for_status()
        return response.json()


# 使用示例
if __name__ == "__main__":
    client = HelloAgentsClient()

    # 获取版本信息
    version = client.get_version()
    print(f"API Version: {version['current_version']}")

    # 执行代码
    result = client.execute_code('print("Hello, World!")')
    print(f"Output: {result['output']}")

    # 获取课程列表
    lessons = client.get_lessons()
    print(f"Total lessons: {len(lessons['lessons'])}")

    # 与 AI 聊天
    chat_result = client.chat("什么是 ReAct Agent?")
    print(f"AI: {chat_result['message']}")

    # 获取沙箱统计
    stats = client.get_sandbox_stats()
    if stats['pool_enabled']:
        print(f"Available containers: {stats['available_containers']}")
```

---

更多示例请参考:
- [API 完整文档](./API_VERSIONING.md)
- [快速参考](./QUICK_START.md)
- [Swagger UI](http://localhost:8000/api/v1/docs)
