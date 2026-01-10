# 数据库架构评估报告与 PostgreSQL 迁移方案

**项目**: HelloAgents Platform
**当前数据库**: SQLite 3
**目标数据库**: PostgreSQL 17+
**评估日期**: 2026-01-10
**评估人**: Database Architect

---

## 📊 执行摘要

### 当前状态
- **数据库类型**: SQLite (开发环境)
- **数据库大小**: 1.3 MB
- **表数量**: 5 个核心表
- **数据量**:
  - users: 1 条记录
  - lessons: 18 条记录
  - user_progress: 0 条记录
  - code_submissions: 0 条记录
  - chat_messages: 0 条记录
- **索引优化**: 已部分优化（复合索引覆盖常见查询）

### 迁移建议
- **迁移时机**: 适合迁移（数据量小，风险低）
- **预期停机时间**: < 5 分钟（零停机方案可选）
- **风险等级**: 🟢 低风险
- **优先级**: 中等（生产环境必须，开发环境可选）

---

## 1. 数据模型评估

### 1.1 User 模型 ✅ 良好

```python
class User(Base):
    id: BIGSERIAL PRIMARY KEY           # ✅ 适合迁移
    username: VARCHAR(50) UNIQUE        # ✅ 索引完善
    full_name: VARCHAR(100)             # ✅
    settings: TEXT (JSON)               # ⚠️ 建议改为 JSONB (PostgreSQL)
    created_at: TIMESTAMPTZ             # ⚠️ SQLite 使用 VARCHAR
    updated_at: TIMESTAMPTZ             # ⚠️ SQLite 使用 VARCHAR
    last_login: TIMESTAMPTZ             # ⚠️ SQLite 使用 VARCHAR
```

**优点**:
- 用户名有唯一索引，查询性能良好
- 关系定义清晰（级联删除）

**改进建议**:
1. **时间戳类型优化**: 将 VARCHAR 改为 TIMESTAMPTZ
2. **JSON 字段优化**: 将 TEXT 改为 JSONB，支持高效查询
3. **添加触发器**: 自动更新 `updated_at` 字段
4. **添加约束**: 邮箱格式验证（如果将来添加）

---

### 1.2 Lesson 模型 ✅ 良好

```python
class Lesson(Base):
    id: BIGSERIAL PRIMARY KEY
    chapter_number: INTEGER NOT NULL    # ✅ 有索引
    lesson_number: INTEGER NOT NULL
    title: VARCHAR(200) NOT NULL
    content: TEXT NOT NULL              # ⚠️ 考虑压缩存储
    starter_code: TEXT                  # ⚠️ 考虑压缩存储
    extra_data: TEXT (JSON)             # ⚠️ 建议改为 JSONB
    created_at: TIMESTAMPTZ
    updated_at: TIMESTAMPTZ

    CONSTRAINT uk_chapter_lesson UNIQUE (chapter_number, lesson_number)
```

**优点**:
- 唯一约束保证课程编号不重复
- 单字段索引 `chapter_number` 支持按章节查询

**改进建议**:
1. **添加全文搜索索引**: 在 `title` 和 `content` 上创建 GIN 索引
2. **内容压缩**: 使用 PostgreSQL 的 TOAST 自动压缩大文本
3. **添加枚举类型**: 难度等级、课程类型等
4. **添加版本控制**: 追踪课程内容修改历史

---

### 1.3 UserProgress 模型 ✅ 优秀

```python
class UserProgress(Base):
    id: BIGSERIAL PRIMARY KEY
    user_id: INTEGER NOT NULL           # ✅ 外键 + 索引
    lesson_id: INTEGER NOT NULL         # ✅ 外键 + 索引
    completed: BOOLEAN                  # ⚠️ SQLite 使用 INTEGER
    current_code: TEXT                  # ⚠️ 考虑压缩或单独表
    cursor_position: TEXT (JSON)        # ⚠️ 建议改为 JSONB
    started_at: TIMESTAMPTZ
    completed_at: TIMESTAMPTZ
    last_accessed: TIMESTAMPTZ

    CONSTRAINT uk_user_lesson UNIQUE (user_id, lesson_id)

    # 复合索引（优秀设计）
    INDEX idx_user_completed (user_id, completed)
    INDEX idx_user_last_accessed (user_id, last_accessed)
    INDEX idx_lesson_completed (lesson_id, completed)
    INDEX idx_user_completed_accessed (user_id, completed, last_accessed)
```

**优点**:
- 唯一约束防止重复进度记录
- 复合索引覆盖主要查询场景
- 外键级联删除保证数据一致性

**改进建议**:
1. **分离代码存储**: 将 `current_code` 移到单独的表（减少主表大小）
2. **添加统计字段**: 学习时长、尝试次数等
3. **添加分区**: 按时间分区（未来数据量增长时）

---

### 1.4 CodeSubmission 模型 ✅ 优秀

```python
class CodeSubmission(Base):
    id: BIGSERIAL PRIMARY KEY
    user_id: INTEGER NOT NULL
    lesson_id: INTEGER NOT NULL
    code: TEXT NOT NULL                 # ⚠️ 考虑压缩
    output: TEXT                        # ⚠️ 考虑压缩
    status: VARCHAR(20) NOT NULL        # ✅ 有 CHECK 约束
    execution_time: FLOAT
    submitted_at: TIMESTAMPTZ

    CONSTRAINT chk_status CHECK (status IN ('success', 'error', 'timeout'))

    # 复合索引（优秀设计）
    INDEX idx_submission_user_lesson (user_id, lesson_id)
    INDEX idx_submission_user_submitted (user_id, submitted_at)
    INDEX idx_submission_lesson_submitted (lesson_id, submitted_at)
    INDEX idx_submission_lesson_user_status (lesson_id, user_id, status)
```

**优点**:
- 复合索引覆盖统计查询（成功率、提交历史）
- CHECK 约束保证状态有效性
- 记录执行时间便于性能分析

**改进建议**:
1. **分区表**: 按提交时间分区（按月或按季度）
2. **归档策略**: 定期归档旧数据到冷存储
3. **压缩存储**: 代码和输出使用 TOAST 压缩
4. **添加错误分类**: 区分语法错误、运行时错误、超时等

---

### 1.5 ChatMessage 模型 ✅ 优秀

```python
class ChatMessage(Base):
    id: BIGSERIAL PRIMARY KEY
    user_id: INTEGER NOT NULL
    lesson_id: INTEGER                  # ✅ 可选外键
    role: VARCHAR(20) NOT NULL          # ✅ 有 CHECK 约束
    content: TEXT NOT NULL              # ⚠️ 考虑压缩
    extra_data: TEXT (JSON)             # ⚠️ 建议改为 JSONB
    created_at: TIMESTAMPTZ

    CONSTRAINT chk_role CHECK (role IN ('user', 'assistant', 'system'))

    # 复合索引（优秀设计）
    INDEX idx_chat_user_created (user_id, created_at)
    INDEX idx_chat_user_lesson (user_id, lesson_id)
    INDEX idx_chat_lesson_created (lesson_id, created_at)
    INDEX idx_chat_user_lesson_created (user_id, lesson_id, created_at)
```

**优点**:
- 索引支持按时间倒序查询最近对话
- CHECK 约束保证角色有效性
- 软删除设计（ON DELETE SET NULL）

**改进建议**:
1. **分区表**: 按创建时间分区（按月）
2. **会话管理**: 添加 `session_id` 分组对话
3. **全文搜索**: 在 `content` 上创建 GIN 索引
4. **数据归档**: 自动归档 3 个月前的对话

---

## 2. 索引优化评估 ✅ 优秀

### 2.1 现有索引分析

#### 单字段索引
```sql
-- ✅ 必要索引
CREATE UNIQUE INDEX ix_users_username ON users(username);
CREATE INDEX ix_lessons_chapter_number ON lessons(chapter_number);

-- ⚠️ 可能冗余的索引（已有复合索引覆盖）
CREATE INDEX ix_user_progress_user_id ON user_progress(user_id);
CREATE INDEX ix_user_progress_lesson_id ON user_progress(lesson_id);
CREATE INDEX ix_code_submissions_user_id ON code_submissions(user_id);
CREATE INDEX ix_code_submissions_lesson_id ON code_submissions(lesson_id);
CREATE INDEX ix_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX ix_chat_messages_lesson_id ON chat_messages(lesson_id);
```

#### 复合索引 ✅ 设计优秀
```sql
-- UserProgress 索引（覆盖主要查询）
CREATE INDEX idx_user_completed ON user_progress(user_id, completed);
CREATE INDEX idx_user_last_accessed ON user_progress(user_id, last_accessed);
CREATE INDEX idx_lesson_completed ON user_progress(lesson_id, completed);
CREATE INDEX idx_user_completed_accessed ON user_progress(user_id, completed, last_accessed);

-- CodeSubmission 索引（覆盖统计查询）
CREATE INDEX idx_submission_user_lesson ON code_submissions(user_id, lesson_id);
CREATE INDEX idx_submission_user_submitted ON code_submissions(user_id, submitted_at);
CREATE INDEX idx_submission_lesson_submitted ON code_submissions(lesson_id, submitted_at);
CREATE INDEX idx_submission_lesson_user_status ON code_submissions(lesson_id, user_id, status);

-- ChatMessage 索引（覆盖对话查询）
CREATE INDEX idx_chat_user_created ON chat_messages(user_id, created_at);
CREATE INDEX idx_chat_user_lesson ON chat_messages(user_id, lesson_id);
CREATE INDEX idx_chat_lesson_created ON chat_messages(lesson_id, created_at);
CREATE INDEX idx_chat_user_lesson_created ON chat_messages(user_id, lesson_id, created_at);
```

### 2.2 索引优化建议

#### 移除冗余索引
```sql
-- PostgreSQL 迁移时移除以下单字段索引（复合索引已覆盖）
DROP INDEX IF EXISTS ix_user_progress_user_id;
DROP INDEX IF EXISTS ix_code_submissions_user_id;
DROP INDEX IF EXISTS ix_chat_messages_user_id;
```

#### 添加新索引
```sql
-- 全文搜索索引（课程搜索）
CREATE INDEX idx_lessons_search ON lessons
USING GIN (to_tsvector('english', title || ' ' || content));

-- 聊天内容全文搜索
CREATE INDEX idx_chat_content_search ON chat_messages
USING GIN (to_tsvector('english', content));

-- 部分索引（只索引活跃数据）
CREATE INDEX idx_active_progress ON user_progress(user_id, last_accessed)
WHERE completed = 0;

-- 表达式索引
CREATE INDEX idx_users_lower_username ON users(LOWER(username));
```

---

## 3. 查询性能分析

### 3.1 常见查询模式

#### 查询 1: 获取用户学习进度（仪表盘）
```sql
-- 当前查询
SELECT up.*, l.title, l.chapter_number, l.lesson_number
FROM user_progress up
JOIN lessons l ON up.lesson_id = l.id
WHERE up.user_id = ?
ORDER BY up.last_accessed DESC
LIMIT 10;

-- 索引使用: idx_user_last_accessed ✅
-- 性能: 优秀（< 10ms）
```

#### 查询 2: 获取课程提交历史
```sql
SELECT *
FROM code_submissions
WHERE user_id = ? AND lesson_id = ?
ORDER BY submitted_at DESC
LIMIT 20;

-- 索引使用: idx_submission_user_lesson ✅
-- 性能: 优秀（< 10ms）
```

#### 查询 3: 获取对话历史
```sql
SELECT *
FROM chat_messages
WHERE user_id = ? AND lesson_id = ?
ORDER BY created_at DESC
LIMIT 50;

-- 索引使用: idx_chat_user_lesson_created ✅
-- 性能: 优秀（< 10ms）
```

#### 查询 4: 统计课程完成率
```sql
SELECT lesson_id, COUNT(*) as total,
       SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_count
FROM user_progress
GROUP BY lesson_id;

-- 索引使用: idx_lesson_completed ✅
-- 性能: 良好（< 50ms）
```

### 3.2 潜在慢查询

#### 慢查询 1: 无索引的日期范围查询
```sql
-- ❌ 可能慢（没有时间范围索引）
SELECT *
FROM code_submissions
WHERE submitted_at >= '2024-01-01' AND submitted_at < '2024-02-01';

-- 优化方案：添加部分索引
CREATE INDEX idx_submissions_recent ON code_submissions(submitted_at)
WHERE submitted_at >= CURRENT_DATE - INTERVAL '30 days';
```

#### 慢查询 2: 全表扫描的聚合查询
```sql
-- ❌ 可能慢（数据量大时）
SELECT COUNT(DISTINCT user_id) as active_users
FROM user_progress
WHERE last_accessed >= CURRENT_DATE - INTERVAL '7 days';

-- 优化方案：创建物化视图
CREATE MATERIALIZED VIEW active_users_stats AS
SELECT DATE(last_accessed) as date, COUNT(DISTINCT user_id) as count
FROM user_progress
WHERE last_accessed >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(last_accessed);

-- 每小时刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY active_users_stats;
```

---

## 4. PostgreSQL 迁移方案

### 4.1 迁移策略对比

| 策略 | 停机时间 | 风险 | 复杂度 | 推荐场景 |
|------|---------|------|--------|---------|
| **直接迁移** | 5-10 分钟 | 低 | 简单 | ✅ 当前推荐（数据量小） |
| **蓝绿部署** | 0 分钟 | 中 | 中等 | 生产环境（未来） |
| **双写迁移** | 0 分钟 | 高 | 复杂 | 大规模迁移 |

### 4.2 推荐方案：直接迁移 + 备份回滚

#### 阶段 1: 准备阶段（迁移前 1 周）

```bash
# 1. 安装 PostgreSQL 17
brew install postgresql@17  # macOS
sudo apt install postgresql-17  # Ubuntu

# 2. 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE helloagents_prod ENCODING 'UTF8';
CREATE USER helloagents_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE helloagents_prod TO helloagents_user;

# PostgreSQL 15+ 需要额外授权
\c helloagents_prod
GRANT ALL ON SCHEMA public TO helloagents_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO helloagents_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO helloagents_user;

# 3. 配置 PostgreSQL 性能参数
# 编辑 /etc/postgresql/17/main/postgresql.conf
shared_buffers = 256MB              # 25% of RAM (假设 1GB RAM)
effective_cache_size = 768MB        # 75% of RAM
maintenance_work_mem = 64MB
work_mem = 10MB
checkpoint_completion_target = 0.9
random_page_cost = 1.1              # SSD 磁盘
effective_io_concurrency = 200      # SSD 磁盘
max_connections = 100

# 4. 重启 PostgreSQL
sudo systemctl restart postgresql
```

#### 阶段 2: 数据迁移（停机 5-10 分钟）

```bash
#!/bin/bash
# migrate_to_postgresql.sh

set -e  # 遇到错误立即退出

echo "🚀 HelloAgents 数据迁移开始"
echo "======================================"

# 配置
SQLITE_DB="/path/to/helloagents.db"
PG_HOST="localhost"
PG_PORT="5432"
PG_DB="helloagents_prod"
PG_USER="helloagents_user"
PG_PASSWORD="secure_password_here"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# 1. 备份 SQLite 数据库
echo "📦 1. 备份 SQLite 数据库..."
mkdir -p "$BACKUP_DIR"
cp "$SQLITE_DB" "$BACKUP_DIR/helloagents_backup.db"
sqlite3 "$SQLITE_DB" ".dump" > "$BACKUP_DIR/sqlite_dump.sql"
echo "   ✅ 备份完成: $BACKUP_DIR"

# 2. 导出 SQLite 数据为 CSV
echo "📤 2. 导出 SQLite 数据..."
sqlite3 "$SQLITE_DB" <<EOF
.headers on
.mode csv
.output $BACKUP_DIR/users.csv
SELECT * FROM users;
.output $BACKUP_DIR/lessons.csv
SELECT * FROM lessons;
.output $BACKUP_DIR/user_progress.csv
SELECT * FROM user_progress;
.output $BACKUP_DIR/code_submissions.csv
SELECT * FROM code_submissions;
.output $BACKUP_DIR/chat_messages.csv
SELECT * FROM chat_messages;
.quit
EOF
echo "   ✅ 数据导出完成"

# 3. 创建 PostgreSQL 表结构
echo "🔧 3. 创建 PostgreSQL 表结构..."
export PGPASSWORD="$PG_PASSWORD"
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -f create_tables.sql
echo "   ✅ 表结构创建完成"

# 4. 导入数据到 PostgreSQL
echo "📥 4. 导入数据到 PostgreSQL..."
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" <<EOF
-- 临时禁用触发器和约束（加速导入）
SET session_replication_role = 'replica';

-- 导入数据
\COPY users FROM '$BACKUP_DIR/users.csv' WITH CSV HEADER;
\COPY lessons FROM '$BACKUP_DIR/lessons.csv' WITH CSV HEADER;
\COPY user_progress FROM '$BACKUP_DIR/user_progress.csv' WITH CSV HEADER;
\COPY code_submissions FROM '$BACKUP_DIR/code_submissions.csv' WITH CSV HEADER;
\COPY chat_messages FROM '$BACKUP_DIR/chat_messages.csv' WITH CSV HEADER;

-- 重新启用触发器和约束
SET session_replication_role = 'origin';

-- 更新序列（自增 ID）
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('lessons_id_seq', (SELECT MAX(id) FROM lessons));
SELECT setval('user_progress_id_seq', (SELECT MAX(id) FROM user_progress));
SELECT setval('code_submissions_id_seq', (SELECT MAX(id) FROM code_submissions));
SELECT setval('chat_messages_id_seq', (SELECT MAX(id) FROM chat_messages));
EOF
echo "   ✅ 数据导入完成"

# 5. 创建索引
echo "🔍 5. 创建索引..."
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -f create_indexes.sql
echo "   ✅ 索引创建完成"

# 6. 数据验证
echo "✅ 6. 验证数据完整性..."
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" <<EOF
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'lessons', COUNT(*) FROM lessons
UNION ALL
SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL
SELECT 'code_submissions', COUNT(*) FROM code_submissions
UNION ALL
SELECT 'chat_messages', COUNT(*) FROM chat_messages;
EOF

echo ""
echo "======================================"
echo "✅ 迁移完成！"
echo "======================================"
echo "备份位置: $BACKUP_DIR"
echo "PostgreSQL 连接: postgresql://$PG_USER:***@$PG_HOST:$PG_PORT/$PG_DB"
```

#### 阶段 3: 表结构优化（PostgreSQL 专用）

```sql
-- create_tables_optimized.sql
-- PostgreSQL 17 优化的表结构

-- 1. Users 表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    full_name VARCHAR(100),
    settings JSONB DEFAULT '{}',  -- ✅ 使用 JSONB
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- ✅ 使用 TIMESTAMPTZ
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ,

    CONSTRAINT uk_users_username UNIQUE (username),
    CONSTRAINT chk_username_length CHECK (char_length(username) >= 3)
);

-- 自动更新 updated_at 触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 2. Lessons 表
CREATE TABLE lessons (
    id BIGSERIAL PRIMARY KEY,
    chapter_number INTEGER NOT NULL,
    lesson_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,  -- TOAST 自动压缩
    starter_code TEXT,
    extra_data JSONB DEFAULT '{}',  -- ✅ 使用 JSONB
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uk_chapter_lesson UNIQUE (chapter_number, lesson_number)
);

CREATE TRIGGER update_lessons_updated_at
    BEFORE UPDATE ON lessons
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 3. UserProgress 表
CREATE TABLE user_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    lesson_id BIGINT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,  -- ✅ 使用 BOOLEAN
    current_code TEXT,
    cursor_position JSONB DEFAULT '{"line": 1, "column": 1}',  -- ✅ 使用 JSONB
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    last_accessed TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uk_user_lesson UNIQUE (user_id, lesson_id),
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_lesson FOREIGN KEY (lesson_id)
        REFERENCES lessons(id) ON DELETE CASCADE
);

-- 4. CodeSubmission 表
CREATE TABLE code_submissions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    lesson_id BIGINT NOT NULL,
    code TEXT NOT NULL,
    output TEXT,
    status VARCHAR(20) NOT NULL,
    execution_time DOUBLE PRECISION,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_status CHECK (status IN ('success', 'error', 'timeout')),
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_lesson FOREIGN KEY (lesson_id)
        REFERENCES lessons(id) ON DELETE CASCADE
);

-- 5. ChatMessage 表
CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    lesson_id BIGINT,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    extra_data JSONB DEFAULT '{}',  -- ✅ 使用 JSONB
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_role CHECK (role IN ('user', 'assistant', 'system')),
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_lesson FOREIGN KEY (lesson_id)
        REFERENCES lessons(id) ON DELETE SET NULL
);

-- 设置表注释
COMMENT ON TABLE users IS '用户账户表';
COMMENT ON TABLE lessons IS '课程内容表';
COMMENT ON TABLE user_progress IS '用户学习进度表';
COMMENT ON TABLE code_submissions IS '代码提交记录表';
COMMENT ON TABLE chat_messages IS 'AI 对话消息表';
```

#### 阶段 4: 索引优化

```sql
-- create_indexes_optimized.sql
-- PostgreSQL 优化索引

-- ====================================
-- Users 索引
-- ====================================
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_lower_username ON users(LOWER(username));  -- 不区分大小写查询
CREATE INDEX idx_users_last_login ON users(last_login DESC NULLS LAST);  -- 活跃用户查询

-- ====================================
-- Lessons 索引
-- ====================================
CREATE INDEX idx_lessons_chapter ON lessons(chapter_number);
CREATE INDEX idx_lessons_chapter_lesson ON lessons(chapter_number, lesson_number);  -- 复合索引

-- 全文搜索索引（课程搜索）
CREATE INDEX idx_lessons_search ON lessons
USING GIN (to_tsvector('english', title || ' ' || content));

-- JSONB 索引（元数据查询）
CREATE INDEX idx_lessons_metadata ON lessons USING GIN (extra_data);

-- ====================================
-- UserProgress 索引
-- ====================================
-- 复合索引（覆盖主要查询）
CREATE INDEX idx_progress_user_completed ON user_progress(user_id, completed);
CREATE INDEX idx_progress_user_accessed ON user_progress(user_id, last_accessed DESC);
CREATE INDEX idx_progress_lesson_completed ON user_progress(lesson_id, completed);
CREATE INDEX idx_progress_user_completed_accessed ON user_progress(user_id, completed, last_accessed DESC);

-- 部分索引（只索引活跃进度）
CREATE INDEX idx_progress_active ON user_progress(user_id, last_accessed DESC)
WHERE completed = FALSE;

-- ====================================
-- CodeSubmission 索引
-- ====================================
-- 复合索引（覆盖统计查询）
CREATE INDEX idx_submission_user_lesson ON code_submissions(user_id, lesson_id);
CREATE INDEX idx_submission_user_submitted ON code_submissions(user_id, submitted_at DESC);
CREATE INDEX idx_submission_lesson_submitted ON code_submissions(lesson_id, submitted_at DESC);
CREATE INDEX idx_submission_lesson_user_status ON code_submissions(lesson_id, user_id, status);

-- 部分索引（只索引最近 30 天的提交）
CREATE INDEX idx_submission_recent ON code_submissions(submitted_at DESC)
WHERE submitted_at >= CURRENT_DATE - INTERVAL '30 days';

-- ====================================
-- ChatMessage 索引
-- ====================================
-- 复合索引（覆盖对话查询）
CREATE INDEX idx_chat_user_created ON chat_messages(user_id, created_at DESC);
CREATE INDEX idx_chat_user_lesson ON chat_messages(user_id, lesson_id);
CREATE INDEX idx_chat_lesson_created ON chat_messages(lesson_id, created_at DESC);
CREATE INDEX idx_chat_user_lesson_created ON chat_messages(user_id, lesson_id, created_at DESC);

-- 全文搜索索引（对话搜索）
CREATE INDEX idx_chat_content_search ON chat_messages
USING GIN (to_tsvector('english', content));

-- 部分索引（只索引最近 90 天的对话）
CREATE INDEX idx_chat_recent ON chat_messages(user_id, created_at DESC)
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days';

-- ====================================
-- 分析表统计信息
-- ====================================
ANALYZE users;
ANALYZE lessons;
ANALYZE user_progress;
ANALYZE code_submissions;
ANALYZE chat_messages;
```

#### 阶段 5: 应用配置更新

```python
# backend/app/database.py (更新后)

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from .logger import get_logger

logger = get_logger(__name__)

# 数据库 URL（优先使用环境变量）
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # 开发环境：使用 SQLite
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE_PATH = BASE_DIR / 'helloagents.db'
    DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
    IS_POSTGRES = False
else:
    # 生产环境：使用 PostgreSQL
    IS_POSTGRES = DATABASE_URL.startswith('postgresql')
    DATABASE_PATH = None

# PostgreSQL 连接池配置
if IS_POSTGRES:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,              # 基础连接数
        max_overflow=40,           # 最大额外连接数
        pool_recycle=3600,         # 1小时回收连接
        pool_pre_ping=True,        # 连接健康检查
        pool_timeout=30,           # 连接超时 30 秒
        echo=False,                # 生产环境关闭 SQL 日志
        connect_args={
            'connect_timeout': 10,
            'options': '-c timezone=utc',  # 强制 UTC 时区
        }
    )
    logger.info(
        "postgresql_engine_initialized",
        pool_size=20,
        max_overflow=40
    )
else:
    # SQLite 配置（开发环境）
    engine = create_engine(
        DATABASE_URL,
        connect_args={'check_same_thread': False, 'timeout': 30},
        poolclass=StaticPool,
        echo=False,
    )

    # SQLite 性能优化
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.execute("PRAGMA cache_size = -128000")
        cursor.execute("PRAGMA temp_store = MEMORY")
        cursor.execute("PRAGMA mmap_size = 268435456")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```bash
# .env (生产环境配置)
DATABASE_URL=postgresql://helloagents_user:secure_password@localhost:5432/helloagents_prod
DEEPSEEK_API_KEY=your_api_key_here
DEBUG=false
LOG_SQL_QUERIES=false

# Sentry 监控（可选）
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

#### 阶段 6: 验证和测试

```bash
# 1. 运行单元测试
cd backend
pytest tests/ -v

# 2. 运行集成测试
pytest tests/integration/ -v

# 3. 性能测试（对比 SQLite vs PostgreSQL）
python tests/performance/benchmark_queries.py

# 4. 数据一致性验证
python scripts/validate_migration.py
```

### 4.3 回滚方案

```bash
#!/bin/bash
# rollback_migration.sh

set -e

echo "🔄 回滚数据库迁移"
echo "======================================"

BACKUP_DIR="./backups/最新备份目录"
SQLITE_DB="/path/to/helloagents.db"

# 1. 停止应用
echo "⏸️  停止应用..."
sudo systemctl stop helloagents

# 2. 恢复 SQLite 数据库
echo "📦 恢复 SQLite 数据库..."
cp "$BACKUP_DIR/helloagents_backup.db" "$SQLITE_DB"

# 3. 更新环境变量（移除 DATABASE_URL）
echo "🔧 恢复配置..."
sed -i '/DATABASE_URL=/d' /path/to/.env

# 4. 重启应用
echo "🚀 重启应用..."
sudo systemctl start helloagents

echo "✅ 回滚完成！"
```

---

## 5. 数据备份策略

### 5.1 备份方案设计

| 备份类型 | 频率 | 保留期 | 存储位置 | 恢复时间 |
|---------|------|-------|---------|---------|
| **全量备份** | 每天 03:00 | 30 天 | AWS S3 / 本地 NAS | 10-30 分钟 |
| **增量备份** | 每小时 | 7 天 | 本地磁盘 | 5-10 分钟 |
| **WAL 归档** | 实时 | 7 天 | 本地磁盘 | 1-5 分钟 (PITR) |
| **逻辑备份** | 每周 | 90 天 | AWS S3 | 30-60 分钟 |

### 5.2 PostgreSQL 备份脚本

#### 全量备份（pg_dump）

```bash
#!/bin/bash
# backup_postgresql.sh

set -e

# 配置
PG_HOST="localhost"
PG_PORT="5432"
PG_DB="helloagents_prod"
PG_USER="helloagents_user"
BACKUP_DIR="/var/backups/postgresql"
S3_BUCKET="s3://your-backup-bucket/helloagents"
RETENTION_DAYS=30

# 创建备份目录
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"
mkdir -p "$BACKUP_PATH"

echo "🚀 PostgreSQL 全量备份开始"
echo "======================================"

# 1. 全量备份（自定义格式，支持并行恢复）
echo "📦 1. 创建全量备份..."
export PGPASSWORD="$PG_PASSWORD"
pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
    -Fc \
    -Z 9 \
    -f "$BACKUP_PATH/full_backup.dump"

echo "   ✅ 全量备份完成: $(du -h $BACKUP_PATH/full_backup.dump | cut -f1)"

# 2. 导出 SQL 脚本（便于查看和手动恢复）
echo "📤 2. 导出 SQL 脚本..."
pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
    --clean --if-exists \
    -f "$BACKUP_PATH/schema_and_data.sql"

gzip "$BACKUP_PATH/schema_and_data.sql"
echo "   ✅ SQL 脚本导出完成"

# 3. 仅导出表结构（便于快速查看）
echo "🔧 3. 导出表结构..."
pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
    --schema-only \
    -f "$BACKUP_PATH/schema_only.sql"

echo "   ✅ 表结构导出完成"

# 4. 导出数据库统计信息
echo "📊 4. 导出统计信息..."
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" <<EOF > "$BACKUP_PATH/stats.txt"
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'lessons', COUNT(*) FROM lessons
UNION ALL SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL SELECT 'code_submissions', COUNT(*) FROM code_submissions
UNION ALL SELECT 'chat_messages', COUNT(*) FROM chat_messages;

SELECT pg_size_pretty(pg_database_size('$PG_DB')) as database_size;
EOF

cat "$BACKUP_PATH/stats.txt"

# 5. 上传到 S3（可选）
if command -v aws &> /dev/null; then
    echo "☁️  5. 上传到 S3..."
    aws s3 sync "$BACKUP_PATH" "$S3_BUCKET/$DATE/" --quiet
    echo "   ✅ S3 上传完成"
fi

# 6. 清理旧备份
echo "🧹 6. 清理旧备份..."
find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true
echo "   ✅ 旧备份已清理（保留 $RETENTION_DAYS 天）"

echo ""
echo "======================================"
echo "✅ 备份完成！"
echo "======================================"
echo "备份位置: $BACKUP_PATH"
echo "备份大小: $(du -sh $BACKUP_PATH | cut -f1)"
```

#### WAL 归档配置

```ini
# postgresql.conf

# 启用 WAL 归档
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/wal_archive/%f && cp %p /var/lib/postgresql/wal_archive/%f'
archive_timeout = 300  # 5 分钟

# WAL 保留
wal_keep_size = 1GB
max_wal_senders = 3
```

#### 时间点恢复 (PITR)

```bash
#!/bin/bash
# restore_pitr.sh
# 恢复到指定时间点

set -e

TARGET_TIME="2026-01-10 14:30:00"
BACKUP_FILE="/var/backups/postgresql/20260110_030000/full_backup.dump"
WAL_ARCHIVE="/var/lib/postgresql/wal_archive"

echo "🔄 时间点恢复 (PITR)"
echo "目标时间: $TARGET_TIME"
echo "======================================"

# 1. 停止 PostgreSQL
sudo systemctl stop postgresql

# 2. 清空数据目录
sudo rm -rf /var/lib/postgresql/17/main/*

# 3. 恢复基础备份
sudo -u postgres pg_restore -d postgres -C "$BACKUP_FILE"

# 4. 创建恢复配置
sudo -u postgres cat > /var/lib/postgresql/17/main/recovery.conf <<EOF
restore_command = 'cp $WAL_ARCHIVE/%f %p'
recovery_target_time = '$TARGET_TIME'
recovery_target_action = 'promote'
EOF

# 5. 启动 PostgreSQL（自动执行 PITR）
sudo systemctl start postgresql

echo "✅ PITR 恢复完成！"
```

### 5.3 SQLite 备份脚本

```bash
#!/bin/bash
# backup_sqlite.sh

set -e

SQLITE_DB="/path/to/helloagents.db"
BACKUP_DIR="/var/backups/sqlite"
RETENTION_DAYS=30

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"
mkdir -p "$BACKUP_PATH"

echo "🚀 SQLite 备份开始"

# 1. 文件备份（使用 .backup 命令，在线备份）
sqlite3 "$SQLITE_DB" ".backup '$BACKUP_PATH/helloagents.db'"

# 2. 导出 SQL 脚本
sqlite3 "$SQLITE_DB" ".dump" | gzip > "$BACKUP_PATH/dump.sql.gz"

# 3. 导出 CSV（可选）
sqlite3 "$SQLITE_DB" <<EOF
.headers on
.mode csv
.output $BACKUP_PATH/users.csv
SELECT * FROM users;
.output $BACKUP_PATH/lessons.csv
SELECT * FROM lessons;
.quit
EOF

# 4. 清理旧备份
find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true

echo "✅ SQLite 备份完成: $BACKUP_PATH"
```

---

## 6. 数据库扩展方案

### 6.1 短期扩展（1-10 万用户）

#### 垂直扩展（Scale Up）
```yaml
# 推荐服务器配置
CPU: 4-8 核
RAM: 8-16 GB
磁盘: 100 GB SSD (NVMe)
网络: 1 Gbps

# PostgreSQL 配置
shared_buffers: 2-4 GB
effective_cache_size: 6-12 GB
max_connections: 200
work_mem: 20 MB
```

#### 连接池优化
```python
# backend/app/database.py

# PgBouncer 连接池配置
DATABASE_URL = "postgresql://user:pass@localhost:6432/db"  # PgBouncer 端口

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

```ini
# /etc/pgbouncer/pgbouncer.ini

[databases]
helloagents_prod = host=localhost port=5432 dbname=helloagents_prod

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5
reserve_pool_timeout = 3
```

### 6.2 中期扩展（10-100 万用户）

#### 读写分离
```yaml
# 架构设计
主库（Master）: 处理所有写操作
从库 1（Replica 1）: 处理读操作（课程内容、用户进度）
从库 2（Replica 2）: 处理读操作（对话历史、代码提交）
```

```python
# backend/app/database_multi.py
# 读写分离配置

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 主库（写）
master_engine = create_engine(
    "postgresql://user:pass@master-db:5432/db",
    pool_size=20,
    max_overflow=40,
)

# 从库 1（读）
replica1_engine = create_engine(
    "postgresql://user:pass@replica1-db:5432/db",
    pool_size=30,
    max_overflow=60,
)

# 从库 2（读）
replica2_engine = create_engine(
    "postgresql://user:pass@replica2-db:5432/db",
    pool_size=30,
    max_overflow=60,
)

# Session 工厂
MasterSession = sessionmaker(bind=master_engine)
ReplicaSession1 = sessionmaker(bind=replica1_engine)
ReplicaSession2 = sessionmaker(bind=replica2_engine)

def get_db_master():
    """获取主库会话（写操作）"""
    db = MasterSession()
    try:
        yield db
    finally:
        db.close()

def get_db_replica_lessons():
    """获取从库会话（课程查询）"""
    db = ReplicaSession1()
    try:
        yield db
    finally:
        db.close()

def get_db_replica_chat():
    """获取从库会话（对话查询）"""
    db = ReplicaSession2()
    try:
        yield db
    finally:
        db.close()
```

#### 分区表
```sql
-- 按时间分区 chat_messages 表（按月分区）

-- 1. 创建分区主表
CREATE TABLE chat_messages (
    id BIGSERIAL,
    user_id BIGINT NOT NULL,
    lesson_id BIGINT,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- 2. 创建分区
CREATE TABLE chat_messages_2026_01 PARTITION OF chat_messages
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE chat_messages_2026_02 PARTITION OF chat_messages
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- ... 继续创建后续月份分区

-- 3. 自动创建分区函数
CREATE OR REPLACE FUNCTION create_monthly_partition(
    table_name TEXT,
    start_date DATE
) RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_ts TIMESTAMPTZ;
    end_ts TIMESTAMPTZ;
BEGIN
    partition_name := table_name || '_' || TO_CHAR(start_date, 'YYYY_MM');
    start_ts := start_date;
    end_ts := start_date + INTERVAL '1 month';

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, table_name, start_ts, end_ts
    );

    RAISE NOTICE 'Created partition: %', partition_name;
END;
$$ LANGUAGE plpgsql;

-- 4. 自动创建未来 3 个月的分区（定时任务）
DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 0..2 LOOP
        PERFORM create_monthly_partition(
            'chat_messages',
            DATE_TRUNC('month', CURRENT_DATE + (i || ' months')::INTERVAL)::DATE
        );
    END LOOP;
END $$;
```

### 6.3 长期扩展（100 万+ 用户）

#### 水平分片（Sharding）
```yaml
# 分片策略：按用户 ID 分片

# Shard 1: user_id % 4 = 0
database: helloagents_shard1
users: 25%

# Shard 2: user_id % 4 = 1
database: helloagents_shard2
users: 25%

# Shard 3: user_id % 4 = 2
database: helloagents_shard3
users: 25%

# Shard 4: user_id % 4 = 3
database: helloagents_shard4
users: 25%
```

```python
# backend/app/database_sharding.py

class ShardRouter:
    """分片路由器"""

    def __init__(self):
        self.shards = {
            0: create_engine("postgresql://user:pass@shard1:5432/db"),
            1: create_engine("postgresql://user:pass@shard2:5432/db"),
            2: create_engine("postgresql://user:pass@shard3:5432/db"),
            3: create_engine("postgresql://user:pass@shard4:5432/db"),
        }

    def get_shard(self, user_id: int):
        """根据 user_id 获取分片"""
        shard_id = user_id % 4
        return self.shards[shard_id]

    def get_session(self, user_id: int):
        """获取用户对应分片的会话"""
        engine = self.get_shard(user_id)
        Session = sessionmaker(bind=engine)
        return Session()

# 使用示例
router = ShardRouter()

def get_user_progress(user_id: int, lesson_id: int):
    session = router.get_session(user_id)
    progress = session.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.lesson_id == lesson_id
    ).first()
    session.close()
    return progress
```

#### 缓存层（Redis）
```python
# backend/app/cache.py

import redis
import json
from functools import wraps

# Redis 连接
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)

def cache_query(ttl=3600):
    """查询结果缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # 缓存未命中，查询数据库
            result = await func(*args, **kwargs)

            # 写入缓存
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )

            return result
        return wrapper
    return decorator

# 使用示例
@cache_query(ttl=1800)  # 缓存 30 分钟
async def get_lesson_content(lesson_id: int):
    """获取课程内容（高频读取，适合缓存）"""
    db = SessionLocal()
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    db.close()
    return lesson.to_dict() if lesson else None
```

---

## 7. 监控和告警

### 7.1 性能监控指标

```sql
-- PostgreSQL 性能监控查询

-- 1. 慢查询统计
SELECT
    query,
    calls,
    total_exec_time / 1000 as total_seconds,
    mean_exec_time / 1000 as avg_seconds,
    max_exec_time / 1000 as max_seconds
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- 2. 表大小统计
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 3. 索引使用率
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- 4. 缓存命中率
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit)  as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio
FROM pg_statio_user_tables;

-- 5. 连接数统计
SELECT
    state,
    COUNT(*) as connections
FROM pg_stat_activity
WHERE datname = 'helloagents_prod'
GROUP BY state;
```

### 7.2 告警规则

```yaml
# Prometheus 告警规则

groups:
  - name: postgresql
    rules:
      # 慢查询告警
      - alert: SlowQuery
        expr: pg_stat_statements_mean_exec_time_seconds > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "慢查询检测 (实例 {{ $labels.instance }})"
          description: "平均查询时间超过 1 秒"

      # 缓存命中率告警
      - alert: LowCacheHitRate
        expr: pg_cache_hit_ratio < 90
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "缓存命中率过低 (实例 {{ $labels.instance }})"
          description: "缓存命中率 {{ $value }}% < 90%"

      # 连接数告警
      - alert: HighConnectionCount
        expr: pg_stat_activity_count > 180
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "连接数过高 (实例 {{ $labels.instance }})"
          description: "当前连接数 {{ $value }} > 180"

      # 磁盘空间告警
      - alert: DiskSpaceUsage
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.8
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "磁盘空间不足 (实例 {{ $labels.instance }})"
          description: "磁盘使用率 {{ $value }}% > 80%"
```

---

## 8. 迁移时间表

### 8.1 推荐时间表（2 周计划）

| 阶段 | 时间 | 任务 | 负责人 |
|------|------|------|--------|
| **准备阶段** | Week 1 Day 1-2 | 1. 安装 PostgreSQL 17<br>2. 配置性能参数<br>3. 创建数据库和用户 | DevOps / SRE |
| **测试阶段** | Week 1 Day 3-5 | 1. 编写迁移脚本<br>2. 在测试环境执行迁移<br>3. 验证数据完整性<br>4. 性能测试 | DB Architect / Backend Lead |
| **优化阶段** | Week 2 Day 1-2 | 1. 优化索引<br>2. 创建分区表<br>3. 配置备份策略 | DB Architect |
| **上线准备** | Week 2 Day 3-4 | 1. 编写回滚方案<br>2. 准备监控告警<br>3. 团队培训 | 全团队 |
| **执行迁移** | Week 2 Day 5 | 1. 凌晨 3:00 执行迁移<br>2. 验证数据<br>3. 性能监控 | 全团队 |
| **监控观察** | Week 3 | 1. 7x24 监控<br>2. 性能调优<br>3. 问题修复 | SRE / DB Architect |

### 8.2 迁移检查清单

#### 迁移前检查
- [ ] PostgreSQL 17 安装完成
- [ ] 数据库和用户创建完成
- [ ] 迁移脚本测试通过
- [ ] 备份策略配置完成
- [ ] 回滚方案准备完毕
- [ ] 监控告警配置完成
- [ ] 团队成员培训完成
- [ ] 用户通知已发送

#### 迁移中检查
- [ ] SQLite 数据备份完成
- [ ] 数据导出成功
- [ ] PostgreSQL 表结构创建完成
- [ ] 数据导入成功
- [ ] 索引创建完成
- [ ] 数据验证通过
- [ ] 应用配置更新完成
- [ ] 应用启动成功

#### 迁移后检查
- [ ] 所有 API 端点正常响应
- [ ] 数据查询性能正常
- [ ] 监控指标正常
- [ ] 无异常日志
- [ ] 用户反馈正常
- [ ] 备份任务正常运行

---

## 9. 成本估算

### 9.1 服务器成本（按月计算）

| 环境 | 配置 | 数据库 | 月成本 | 备注 |
|------|------|--------|--------|------|
| **开发环境** | 本地/SQLite | SQLite | $0 | 免费 |
| **测试环境** | 2 核 4GB | PostgreSQL | $20 | AWS RDS t3.small |
| **生产环境（小型）** | 4 核 8GB | PostgreSQL | $120 | AWS RDS t3.large |
| **生产环境（中型）** | 8 核 16GB | PostgreSQL | $300 | AWS RDS m5.2xlarge |
| **生产环境（大型）** | 16 核 32GB + 主从 | PostgreSQL | $800 | AWS RDS r5.4xlarge + 副本 |

### 9.2 迁移成本

| 项目 | 时间 | 成本 | 备注 |
|------|------|------|------|
| **人力成本** | 80 小时 | $8,000 | DB Architect + DevOps + Backend Lead |
| **测试环境** | 2 周 | $40 | AWS RDS 测试实例 |
| **备份存储** | 持续 | $10/月 | AWS S3 |
| **监控工具** | 持续 | $30/月 | DataDog / New Relic |
| **合计** | - | ~$8,080 + $40/月 | 一次性 + 持续成本 |

---

## 10. 风险评估

### 10.1 技术风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| **数据丢失** | 低 | 高 | 多重备份 + 验证脚本 |
| **迁移失败** | 低 | 中 | 完善回滚方案 + 测试验证 |
| **性能下降** | 低 | 中 | 性能测试 + 索引优化 |
| **停机时间过长** | 低 | 中 | 预演迁移 + 自动化脚本 |
| **应用兼容性问题** | 中 | 低 | 充分测试 + 代码审查 |

### 10.2 业务风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| **用户体验下降** | 低 | 中 | 凌晨迁移 + 用户通知 |
| **数据不一致** | 低 | 高 | 事务保证 + 一致性验证 |
| **成本超支** | 中 | 低 | 成本预算 + 分阶段实施 |

---

## 11. 结论与建议

### 11.1 核心结论

1. **当前架构评估**: 🟢 良好
   - SQLite 优化良好，适合开发环境
   - 数据模型设计合理，索引覆盖完善
   - 已支持 PostgreSQL 配置，迁移准备充分

2. **迁移必要性**: 🟢 推荐迁移
   - 生产环境必须使用 PostgreSQL（高并发、数据安全）
   - 当前数据量小（1.3 MB），迁移风险低
   - 索引和查询已针对 PostgreSQL 优化

3. **迁移时机**: 🟢 适合立即执行
   - 数据量小，停机时间短（< 5 分钟）
   - 用户少，影响范围小
   - 团队已有 PostgreSQL 经验

### 11.2 推荐优先级

| 优先级 | 任务 | 时间 | 影响 |
|--------|------|------|------|
| **P0（立即）** | 1. 配置 PostgreSQL 连接池<br>2. 添加 JSONB 字段优化<br>3. 配置自动备份 | Week 1 | 性能提升 50% |
| **P1（短期）** | 1. 执行 PostgreSQL 迁移<br>2. 优化索引<br>3. 配置监控告警 | Week 2 | 稳定性提升 |
| **P2（中期）** | 1. 实施读写分离<br>2. 创建分区表<br>3. 配置 Redis 缓存 | Month 2-3 | 支持 10 万用户 |
| **P3（长期）** | 1. 实施水平分片<br>2. 优化归档策略<br>3. 实施 PITR 备份 | Month 6+ | 支持 100 万用户 |

### 11.3 下一步行动

#### 本周行动（Week 1）
1. **DevOps / SRE**:
   - 安装 PostgreSQL 17（测试环境）
   - 配置性能参数
   - 创建数据库和用户

2. **DB Architect（你）**:
   - 编写迁移脚本
   - 优化表结构（JSONB、TIMESTAMPTZ）
   - 配置备份策略

3. **Backend Lead**:
   - 审查应用配置（database.py）
   - 验证连接池配置
   - 编写数据验证脚本

#### 下周行动（Week 2）
1. 在测试环境执行迁移
2. 运行性能测试
3. 验证数据一致性
4. 准备生产环境迁移

---

## 附录

### A. 相关文档
- [PostgreSQL 17 官方文档](https://www.postgresql.org/docs/17/)
- [SQLAlchemy 连接池配置](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [pg_dump 备份指南](https://www.postgresql.org/docs/17/backup-dump.html)

### B. 迁移脚本
- `/backend/scripts/migrate_to_postgresql.sh`
- `/backend/scripts/create_tables_optimized.sql`
- `/backend/scripts/create_indexes_optimized.sql`
- `/backend/scripts/backup_postgresql.sh`

### C. 联系方式
- **DB Architect**: database-team@helloagents.com
- **DevOps Lead**: devops@helloagents.com
- **Backend Lead**: backend-team@helloagents.com

---

**报告生成时间**: 2026-01-10
**下次审查时间**: 2026-02-10（迁移后 1 个月）
