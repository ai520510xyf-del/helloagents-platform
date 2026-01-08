# API 数据库集成指南

**更新日期**: 2026-01-08
**版本**: v2.0 (数据库集成版)

---

## 概述

HelloAgents API 现已集成 SQLite 数据库，支持持久化存储学习进度、代码提交历史和聊天记录。

### 主要变更

1. ✅ 新增 **4个数据库路由模块**（Users, Progress, Submissions, Chat）
2. ✅ 修改现有端点（`/api/execute`, `/api/chat`）支持数据库保存
3. ✅ 自动数据库初始化（应用启动时）
4. ✅ 默认用户自动创建

---

## 新增 API 端点

### 1. 用户管理 API (`/api/users`)

#### 获取当前用户
```http
GET /api/users/current
```

**响应**:
```json
{
  "id": 1,
  "username": "local_user",
  "full_name": "本地用户",
  "settings": {
    "theme": "dark",
    "editor": {
      "fontSize": 14,
      "tabSize": 4,
      "wordWrap": true
    }
  },
  "created_at": "2026-01-08T02:10:00.823440",
  "last_login": null
}
```

#### 创建/获取用户
```http
POST /api/users/
Content-Type: application/json

{
  "username": "my_user",
  "full_name": "My Name",
  "settings": {
    "theme": "light"
  }
}
```

#### 更新用户
```http
PUT /api/users/{user_id}
Content-Type: application/json

{
  "full_name": "Updated Name",
  "settings": {
    "theme": "dark",
    "editor": {
      "fontSize": 16
    }
  }
}
```

---

### 2. 学习进度 API (`/api/progress`)

#### 创建/更新学习进度
```http
POST /api/progress/
Content-Type: application/json

{
  "user_id": 1,
  "lesson_id": 1,
  "current_code": "print('hello')",
  "cursor_position": {
    "line": 1,
    "column": 15
  }
}
```

#### 获取用户所有进度
```http
GET /api/progress/user/1
```

**响应**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "lesson_id": 1,
    "completed": false,
    "current_code": "print('hello')",
    "cursor_position": {"line": 1, "column": 15},
    "started_at": "2026-01-08T02:15:00",
    "completed_at": null,
    "last_accessed": "2026-01-08T02:20:00"
  }
]
```

#### 获取最近学习的课程
```http
GET /api/progress/user/1/recent?limit=10
```

#### 获取特定课程的进度
```http
GET /api/progress/user/1/lesson/1
```

#### 更新学习进度
```http
PUT /api/progress/user/1/lesson/1
Content-Type: application/json

{
  "completed": true,
  "current_code": "print('completed')"
}
```

#### 标记课程为完成
```http
POST /api/progress/user/1/lesson/1/complete
```

#### 获取学习统计
```http
GET /api/progress/user/1/stats
```

**响应**:
```json
{
  "total_lessons": 16,
  "started_lessons": 5,
  "completed_lessons": 2,
  "completion_rate": 12.5
}
```

---

### 3. 代码提交记录 API (`/api/submissions`)

#### 创建代码提交
```http
POST /api/submissions/
Content-Type: application/json

{
  "user_id": 1,
  "lesson_id": 1,
  "code": "print('hello world')",
  "output": "hello world\n",
  "status": "success",
  "execution_time": 0.023
}
```

**status 可选值**: `success`, `error`, `timeout`

#### 获取用户所有提交
```http
GET /api/submissions/user/1?limit=50
```

#### 获取特定课程的提交历史
```http
GET /api/submissions/user/1/lesson/1?limit=20
```

#### 获取提交统计
```http
GET /api/submissions/user/1/stats
```

**响应**:
```json
{
  "total_submissions": 45,
  "success_count": 38,
  "error_count": 6,
  "timeout_count": 1,
  "success_rate": 84.4,
  "average_execution_time": 0.156
}
```

---

### 4. 聊天消息 API (`/api/chat-history`)

#### 保存聊天消息
```http
POST /api/chat-history/
Content-Type: application/json

{
  "user_id": 1,
  "lesson_id": 1,
  "role": "user",
  "content": "什么是 ReAct Agent？",
  "metadata": {}
}
```

**role 可选值**: `user`, `assistant`, `system`

#### 获取用户所有聊天
```http
GET /api/chat-history/user/1?limit=100
```

#### 获取特定课程的聊天历史
```http
GET /api/chat-history/user/1/lesson/1?limit=50
```

#### 删除课程聊天历史
```http
DELETE /api/chat-history/user/1/lesson/1
```

#### 获取聊天统计
```http
GET /api/chat-history/user/1/stats
```

**响应**:
```json
{
  "total_messages": 120,
  "user_messages": 60,
  "assistant_messages": 60,
  "conversation_count": 60
}
```

---

## 修改的现有 API

### 1. 代码执行 API（增强版）

```http
POST /api/execute?user_id=1&lesson_id=1
Content-Type: application/json

{
  "code": "print('hello')",
  "language": "python",
  "timeout": 30
}
```

**变更**:
- ✅ 新增可选参数：`user_id`, `lesson_id`（查询参数）
- ✅ 如果提供 user_id 和 lesson_id，自动保存到 `code_submissions` 表
- ✅ 响应格式不变，向后兼容

**示例**:
```bash
# 不保存到数据库
curl -X POST "http://localhost:8000/api/execute" \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello\")"}'

# 保存到数据库
curl -X POST "http://localhost:8000/api/execute?user_id=1&lesson_id=1" \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello\")"}'
```

### 2. AI 聊天 API（增强版）

```http
POST /api/chat?user_id=1
Content-Type: application/json

{
  "message": "什么是 ReAct Agent？",
  "conversation_history": [],
  "lesson_id": "1",
  "code": "print('hello')"
}
```

**变更**:
- ✅ 新增可选参数：`user_id`（查询参数）
- ✅ 如果提供 user_id，自动保存用户消息和助手回复到 `chat_messages` 表
- ✅ 响应格式不变，向后兼容

**示例**:
```bash
# 不保存到数据库
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是 ReAct？", "conversation_history": []}'

# 保存到数据库
curl -X POST "http://localhost:8000/api/chat?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是 ReAct？", "lesson_id": "1"}'
```

---

## 数据库架构

### 表结构

```
users                 # 用户配置
├── id (PK)
├── username (UNIQUE)
├── full_name
├── settings (JSON)
├── created_at
├── updated_at
└── last_login

lessons               # 课程内容
├── id (PK)
├── chapter_number
├── lesson_number
├── title
├── content (Markdown)
├── starter_code
├── extra_data (JSON)
└── UNIQUE(chapter_number, lesson_number)

user_progress         # 学习进度
├── id (PK)
├── user_id (FK → users)
├── lesson_id (FK → lessons)
├── completed
├── current_code
├── cursor_position (JSON)
├── started_at
├── completed_at
├── last_accessed
└── UNIQUE(user_id, lesson_id)

code_submissions      # 代码提交历史
├── id (PK)
├── user_id (FK → users)
├── lesson_id (FK → lessons)
├── code
├── output
├── status (success/error/timeout)
├── execution_time
└── submitted_at

chat_messages         # AI 对话记录
├── id (PK)
├── user_id (FK → users)
├── lesson_id (FK → lessons)
├── role (user/assistant/system)
├── content
├── extra_data (JSON)
└── created_at
```

### 数据库文件

- **位置**: `backend/helloagents.db`
- **类型**: SQLite 3
- **ORM**: SQLAlchemy 2.0+
- **初始化**: 应用启动时自动创建表

---

## 前端集成建议

### 1. 获取当前用户
```typescript
// 应用启动时获取用户
async function initUser() {
  const response = await fetch('http://localhost:8000/api/users/current');
  const user = await response.json();
  return user;
}
```

### 2. 保存代码执行记录
```typescript
// 执行代码时传递 user_id 和 lesson_id
async function executeCode(code: string, userId: number, lessonId: number) {
  const response = await fetch(
    `http://localhost:8000/api/execute?user_id=${userId}&lesson_id=${lessonId}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    }
  );
  return await response.json();
}
```

### 3. 保存聊天记录
```typescript
// AI 聊天时传递 user_id
async function chatWithAI(message: string, userId: number, lessonId?: string) {
  const response = await fetch(
    `http://localhost:8000/api/chat?user_id=${userId}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        lesson_id: lessonId,
        conversation_history: []
      })
    }
  );
  return await response.json();
}
```

### 4. 自动保存学习进度
```typescript
// 切换课程或代码变更时更新进度
async function updateProgress(
  userId: number,
  lessonId: number,
  code: string,
  cursorPosition: { line: number; column: number }
) {
  const response = await fetch('http://localhost:8000/api/progress/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      lesson_id: lessonId,
      current_code: code,
      cursor_position: cursorPosition
    })
  });
  return await response.json();
}
```

### 5. 获取学习统计
```typescript
// 显示学习进度仪表板
async function getStats(userId: number) {
  const [progressStats, submissionStats, chatStats] = await Promise.all([
    fetch(`http://localhost:8000/api/progress/user/${userId}/stats`).then(r => r.json()),
    fetch(`http://localhost:8000/api/submissions/user/${userId}/stats`).then(r => r.json()),
    fetch(`http://localhost:8000/api/chat-history/user/${userId}/stats`).then(r => r.json())
  ]);

  return {
    progress: progressStats,
    submissions: submissionStats,
    chat: chatStats
  };
}
```

---

## 向后兼容性

所有修改的 API 端点都保持向后兼容：

| 端点 | 行为 | 兼容性 |
|------|------|--------|
| `/api/execute` | 不传 user_id/lesson_id → 不保存数据库 | ✅ 完全兼容 |
| `/api/chat` | 不传 user_id → 不保存聊天记录 | ✅ 完全兼容 |
| `/api/lessons` | 保持不变 | ✅ 完全兼容 |
| `/api/hint` | 保持不变 | ✅ 完全兼容 |

---

## 测试指南

### 1. 测试数据库连接
```bash
curl http://localhost:8000/health
# 期望：{"status": "healthy", "timestamp": "..."}
```

### 2. 测试用户创建
```bash
curl -X GET http://localhost:8000/api/users/current
# 期望：自动创建 local_user
```

### 3. 测试学习进度
```bash
curl -X POST http://localhost:8000/api/progress/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "lesson_id": 1, "current_code": "print(\"test\")"}'
```

### 4. 测试代码执行（带保存）
```bash
curl -X POST "http://localhost:8000/api/execute?user_id=1&lesson_id=1" \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello world\")"}'
```

### 5. 查看所有提交
```bash
curl http://localhost:8000/api/submissions/user/1
```

---

## API 文档

完整的交互式 API 文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 常见问题

### Q1: 数据库文件在哪里？
**A**: `backend/helloagents.db`（应用启动时自动创建）

### Q2: 如何重置数据库？
**A**: 删除 `helloagents.db` 文件，重启应用即可自动重建

### Q3: 如何导入课程内容？
**A**: 使用 `/api/lessons` 端点或直接插入 `lessons` 表

### Q4: 多个用户如何处理？
**A**: 本地单用户模式，`local_user` 自动创建。如需多用户，使用 `/api/users/` 创建

### Q5: 数据如何备份？
**A**: 复制 `helloagents.db` 文件即可

---

**更新日期**: 2026-01-08
**文档维护**: Backend Lead
