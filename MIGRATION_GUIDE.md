# localStorage 数据迁移指南

## 功能说明

如果您之前使用过 HelloAgents 学习平台，您的学习数据可能保存在浏览器的 localStorage 中。现在我们提供了数据迁移功能，可以将这些数据迁移到数据库中，更加安全可靠。

## 自动检测与提示

当您打开学习页面时，系统会自动检测 localStorage 中是否存在以下数据：
- `helloagents_lesson_code_*` - 课程代码
- `helloagents_lesson_chat_*` - AI 对话历史
- `helloagents_last_lesson_id` - 最后学习的课程
- `helloagents_theme` - 主题设置

如果检测到旧数据，会自动弹出迁移提示对话框。

## 迁移流程

### 1. 查看数据预览
迁移提示会显示您有多少数据需要迁移：
- **学习进度**：已学习的课程数量
- **代码记录**：保存的代码份数
- **聊天历史**：AI 对话记录数

### 2. 执行迁移
点击"立即迁移"按钮，系统会：
1. 收集 localStorage 中的所有学习数据
2. 发送到后端 API (`/api/migrate/`)
3. 后端解析并保存到数据库
4. 迁移成功后自动清理 localStorage

### 3. 查看结果
迁移完成后，会显示详细的统计信息：
- ✅ 学习进度：X 个
- ✅ 代码提交：X 份
- ✅ 聊天记录：X 条

点击"完成"后页面会自动刷新，从数据库加载数据。

## 注意事项

### 数据安全
- 迁移过程中，原始数据仍保留在 localStorage 中
- 只有在迁移**完全成功**后，才会清理 localStorage
- 如果迁移失败，您的数据不会丢失

### 可选操作
- 您可以点击"稍后再说"跳过迁移
- 不迁移也可以继续使用，数据将继续保存在 localStorage 中
- 下次打开页面时，仍然会显示迁移提示

### 隐藏提示
如果您不想看到迁移提示，可以：
1. 点击右上角的 × 关闭按钮
2. 系统会记录您的选择（`helloagents_migration_dismissed`）
3. 下次打开页面时不会再显示提示

## 手动迁移（开发者）

如果需要手动触发迁移，可以在浏览器控制台执行：

```javascript
import { performMigration } from './utils/migrationHelper';

// 执行迁移
const result = await performMigration();
console.log(result);
```

## API 端点

### POST /api/migrate/
迁移 localStorage 数据到数据库

**请求体**：
```json
{
  "username": "local_user",
  "progress_list": [
    {
      "chapter": 1,
      "lesson": 1,
      "completed": true,
      "code": "print('Hello')"
    }
  ],
  "last_code": {
    "1-1": "print('completed')"
  },
  "chat_history": [
    {
      "lesson_key": "1-1",
      "messages": [
        {"role": "user", "content": "什么是 ReAct？"},
        {"role": "assistant", "content": "ReAct 是..."}
      ]
    }
  ]
}
```

**响应**：
```json
{
  "success": true,
  "message": "成功迁移数据：2 个进度，1 个代码提交，2 条聊天记录",
  "user_id": 1,
  "migrated_progress": 2,
  "migrated_submissions": 1,
  "migrated_chat_messages": 2
}
```

## 故障排查

### 迁移失败
如果迁移失败，请检查：
1. **后端服务是否运行**：http://localhost:8000/health
2. **网络连接是否正常**
3. **浏览器控制台**是否有错误信息

### 数据丢失
如果您担心数据丢失：
1. 在迁移前，可以导出 localStorage 数据：
   ```javascript
   // 在浏览器控制台执行
   const backup = {};
   for (let i = 0; i < localStorage.length; i++) {
     const key = localStorage.key(i);
     if (key.startsWith('helloagents_')) {
       backup[key] = localStorage.getItem(key);
     }
   }
   console.log(JSON.stringify(backup));
   // 复制输出的 JSON 保存到文件
   ```

2. 如需恢复：
   ```javascript
   const backup = {...}; // 粘贴备份的 JSON
   for (const [key, value] of Object.entries(backup)) {
     localStorage.setItem(key, value);
   }
   ```

## 技术细节

### 实现文件
- **前端组件**：`frontend/src/components/MigrationPrompt.tsx`
- **工具函数**：`frontend/src/utils/migrationHelper.ts`
- **后端 API**：`backend/app/routers/migrate.py`

### 数据映射
localStorage 数据如何映射到数据库：

| localStorage Key | 数据库表 | 说明 |
|-----------------|---------|------|
| `helloagents_lesson_code_*` | `code_submissions` | 代码提交记录 |
| `helloagents_lesson_chat_*` | `chat_messages` | AI 聊天记录 |
| `helloagents_progress` | `user_progress` | 学习进度 |
| `helloagents_theme` | `users.settings` | 用户设置 |

---

**版本**：1.0.0
**更新日期**：2026-01-08
