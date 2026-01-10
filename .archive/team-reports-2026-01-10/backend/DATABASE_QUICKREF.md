# 数据库快速参考指南

**项目**: HelloAgents Platform
**受众**: 开发团队、运维团队
**更新日期**: 2026-01-10

---

## 📋 目录

1. [环境配置](#环境配置)
2. [常用命令](#常用命令)
3. [迁移操作](#迁移操作)
4. [备份恢复](#备份恢复)
5. [性能监控](#性能监控)
6. [故障排查](#故障排查)
7. [优化建议](#优化建议)

---

## 环境配置

### SQLite（开发环境）

```bash
# 无需额外配置，开箱即用
cd backend
python -m app.database  # 初始化数据库

# 数据库位置
backend/helloagents.db

# 查看数据库
sqlite3 backend/helloagents.db
sqlite> .schema
sqlite> .tables
sqlite> SELECT COUNT(*) FROM users;
```

### PostgreSQL（生产环境）

```bash
# 1. 安装 PostgreSQL 17
# macOS
brew install postgresql@17

# Ubuntu
sudo apt install postgresql-17 postgresql-contrib-17

# 2. 创建数据库
sudo -u postgres psql
CREATE DATABASE helloagents_prod ENCODING 'UTF8';
CREATE USER helloagents_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE helloagents_prod TO helloagents_user;

# PostgreSQL 15+
\c helloagents_prod
GRANT ALL ON SCHEMA public TO helloagents_user;

# 3. 配置环境变量
export DATABASE_URL="postgresql://helloagents_user:password@localhost:5432/helloagents_prod"
export PG_PASSWORD="your_secure_password"

# 4. 验证连接
psql -h localhost -p 5432 -U helloagents_user -d helloagents_prod -c '\l'
```

---

## 常用命令

### SQLite 命令

```bash
# 连接数据库
sqlite3 backend/helloagents.db

# 查看表结构
.schema users
.schema --indent lessons

# 查看表数据
SELECT * FROM users;
SELECT * FROM lessons LIMIT 10;

# 导出数据
.mode csv
.headers on
.output users.csv
SELECT * FROM users;

# 备份数据库
.backup backup.db

# 导出 SQL
.dump > backup.sql

# 分析性能
EXPLAIN QUERY PLAN SELECT * FROM user_progress WHERE user_id = 1;

# 优化数据库
VACUUM;
ANALYZE;

# 查看数据库大小
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

# 退出
.quit
```

### PostgreSQL 命令

```bash
# 连接数据库
psql -h localhost -p 5432 -U helloagents_user -d helloagents_prod

# 查看表结构
\d users
\d+ user_progress

# 查看所有表
\dt

# 查看索引
\di

# 查看表大小
\dt+ users

# 查看数据库大小
\l+

# 查询数据
SELECT * FROM users;
SELECT * FROM lessons LIMIT 10;

# 导出数据
\copy users TO 'users.csv' CSV HEADER;

# 执行 SQL 文件
\i script.sql

# 查看连接
SELECT * FROM pg_stat_activity;

# 杀死连接
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = 12345;

# 分析查询性能
EXPLAIN ANALYZE SELECT * FROM user_progress WHERE user_id = 1;

# 优化数据库
VACUUM ANALYZE;

# 退出
\q
```

---

## 迁移操作

### 完整迁移流程

```bash
# 1. 设置环境变量
export PG_HOST="localhost"
export PG_PORT="5432"
export PG_DB="helloagents_prod"
export PG_USER="helloagents_user"
export PG_PASSWORD="your_password"

# 2. 执行迁移脚本
cd backend/scripts
chmod +x migrate_to_postgresql.sh
./migrate_to_postgresql.sh

# 3. 验证迁移结果
psql -h localhost -U helloagents_user -d helloagents_prod

SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL SELECT 'lessons', COUNT(*) FROM lessons
UNION ALL SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL SELECT 'code_submissions', COUNT(*) FROM code_submissions
UNION ALL SELECT 'chat_messages', COUNT(*) FROM chat_messages;

# 4. 更新应用配置
echo "DATABASE_URL=postgresql://helloagents_user:password@localhost:5432/helloagents_prod" >> ../.env

# 5. 重启应用
cd ../..
systemctl restart helloagents  # 或者你的启动命令
```

### 手动迁移步骤

```bash
# 1. 导出 SQLite 数据
sqlite3 backend/helloagents.db <<EOF
.headers on
.mode csv
.output users.csv
SELECT * FROM users;
EOF

# 2. 创建 PostgreSQL 表
psql -U helloagents_user -d helloagents_prod -f scripts/create_tables_postgresql.sql

# 3. 导入数据
psql -U helloagents_user -d helloagents_prod <<EOF
\COPY users FROM 'users.csv' WITH CSV HEADER;
EOF

# 4. 创建索引
psql -U helloagents_user -d helloagents_prod -f scripts/create_indexes_postgresql.sql
```

---

## 备份恢复

### 自动备份设置

```bash
# 1. 配置 cron 任务（每天凌晨 3:00 备份）
crontab -e

# 添加以下行
0 3 * * * /path/to/backend/scripts/backup_postgresql.sh >> /var/log/db_backup.log 2>&1

# 2. 配置环境变量
export PG_PASSWORD="your_password"
export BACKUP_DIR="/var/backups/postgresql"
export RETENTION_DAYS=30
export S3_BUCKET="s3://your-bucket/backups"
export ENABLE_S3_SYNC="true"

# 3. 手动执行备份
cd backend/scripts
chmod +x backup_postgresql.sh
./backup_postgresql.sh
```

### 手动备份

```bash
# PostgreSQL 备份

# 1. 自定义格式（推荐，支持并行恢复）
pg_dump -U helloagents_user -d helloagents_prod \
    -Fc -Z 9 \
    -f backup_$(date +%Y%m%d).dump

# 2. SQL 格式（可读）
pg_dump -U helloagents_user -d helloagents_prod \
    --clean --if-exists \
    -f backup_$(date +%Y%m%d).sql

# 3. 仅备份表结构
pg_dump -U helloagents_user -d helloagents_prod \
    --schema-only \
    -f schema_only.sql

# SQLite 备份
sqlite3 backend/helloagents.db ".backup backup_$(date +%Y%m%d).db"
```

### 恢复数据

```bash
# PostgreSQL 恢复

# 1. 从自定义格式恢复（并行恢复，快速）
pg_restore -U helloagents_user -d helloagents_prod \
    -j 4 \
    --clean --if-exists \
    backup.dump

# 2. 从 SQL 文件恢复
psql -U helloagents_user -d postgres < backup.sql

# 3. 恢复单个表
pg_restore -U helloagents_user -d helloagents_prod \
    -t users \
    backup.dump

# SQLite 恢复
cp backup.db backend/helloagents.db
```

---

## 性能监控

### 运行监控脚本

```bash
# 完整监控报告
psql -U helloagents_user -d helloagents_prod -f scripts/monitor_postgresql.sql

# 输出到文件
psql -U helloagents_user -d helloagents_prod \
    -f scripts/monitor_postgresql.sql \
    > monitoring_report_$(date +%Y%m%d).txt
```

### 关键指标

```sql
-- 1. 缓存命中率（应该 > 90%）
SELECT
    ROUND(100.0 * sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2) as cache_hit_ratio
FROM pg_statio_user_tables;

-- 2. 活跃连接数
SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';

-- 3. 数据库大小
SELECT pg_size_pretty(pg_database_size(current_database()));

-- 4. 慢查询（平均 > 100ms）
SELECT
    calls,
    ROUND(mean_exec_time::numeric, 2) as avg_ms,
    LEFT(query, 100) as query_preview
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 5. 表大小 Top 5
SELECT
    schemaname||'.'||tablename as table_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 5;

-- 6. 未使用的索引
SELECT
    schemaname, tablename, indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND schemaname = 'public';
```

### 性能优化命令

```sql
-- 更新统计信息
ANALYZE;

-- 清理死元组
VACUUM ANALYZE;

-- 完全清理（锁表）
VACUUM FULL;

-- 重建索引
REINDEX INDEX idx_users_username;
REINDEX TABLE users;

-- 查看查询计划
EXPLAIN ANALYZE SELECT * FROM user_progress WHERE user_id = 1;
```

---

## 故障排查

### 连接问题

```bash
# 1. 测试连接
psql -h localhost -U helloagents_user -d helloagents_prod -c '\l'

# 2. 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 3. 查看日志
sudo tail -f /var/log/postgresql/postgresql-17-main.log

# 4. 检查连接数
psql -U postgres -c "SELECT COUNT(*) FROM pg_stat_activity;"

# 5. 杀死僵尸连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND state_change < now() - interval '1 hour';
```

### 性能问题

```sql
-- 1. 查找长时间运行的查询
SELECT
    pid,
    usename,
    ROUND(EXTRACT(EPOCH FROM (now() - query_start))::numeric, 2) as duration_seconds,
    state,
    LEFT(query, 100) as query_preview
FROM pg_stat_activity
WHERE state = 'active' AND query_start < now() - interval '5 seconds'
ORDER BY query_start;

-- 2. 杀死慢查询
SELECT pg_cancel_backend(pid);  -- 温和取消
SELECT pg_terminate_backend(pid);  -- 强制终止

-- 3. 查看锁等待
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### 磁盘空间问题

```bash
# 1. 查看磁盘使用
df -h /var/lib/postgresql

# 2. 查看数据库大小
psql -U postgres -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database ORDER BY pg_database_size(datname) DESC;"

# 3. 清理日志
sudo find /var/log/postgresql -name "*.log" -mtime +7 -delete

# 4. 清理临时文件
psql -U postgres -c "SELECT pg_stat_reset();"

# 5. VACUUM FULL（释放磁盘空间）
psql -U helloagents_user -d helloagents_prod -c "VACUUM FULL;"
```

---

## 优化建议

### 查询优化

```sql
-- 1. 使用 EXPLAIN ANALYZE 分析查询
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT u.*, up.*
FROM users u
JOIN user_progress up ON u.id = up.user_id
WHERE u.id = 1;

-- 2. 添加索引（如果查询使用全表扫描）
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);

-- 3. 使用 CTE 提高可读性
WITH active_users AS (
    SELECT id, username FROM users WHERE last_login > now() - interval '30 days'
)
SELECT au.*, COUNT(up.id) as progress_count
FROM active_users au
LEFT JOIN user_progress up ON au.id = up.user_id
GROUP BY au.id, au.username;

-- 4. 避免 SELECT *，只选择需要的字段
SELECT id, username, email FROM users WHERE id = 1;

-- 5. 使用批量操作
INSERT INTO users (username, email) VALUES
    ('user1', 'user1@example.com'),
    ('user2', 'user2@example.com'),
    ('user3', 'user3@example.com');
```

### 索引优化

```sql
-- 1. 查找缺失的索引（根据查询模式）
-- 分析慢查询日志，添加复合索引

-- 2. 删除未使用的索引
SELECT
    schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND schemaname = 'public';

DROP INDEX IF EXISTS idx_unused_index;

-- 3. 重建碎片化的索引
REINDEX INDEX CONCURRENTLY idx_users_username;

-- 4. 使用部分索引（减少索引大小）
CREATE INDEX idx_active_users ON users(last_login)
WHERE last_login > now() - interval '30 days';
```

### 连接池配置

```python
# backend/app/database.py

# 推荐配置（100 并发用户）
engine = create_engine(
    DATABASE_URL,
    pool_size=20,              # 基础连接数
    max_overflow=40,           # 最大额外连接数
    pool_recycle=3600,         # 1 小时回收连接
    pool_pre_ping=True,        # 连接健康检查
    pool_timeout=30,           # 30 秒超时
)
```

### PostgreSQL 配置优化

```ini
# /etc/postgresql/17/main/postgresql.conf

# 内存配置（16GB RAM 服务器）
shared_buffers = 4GB              # 25% of RAM
effective_cache_size = 12GB       # 75% of RAM
maintenance_work_mem = 1GB
work_mem = 50MB

# 连接配置
max_connections = 200

# 检查点配置
checkpoint_completion_target = 0.9
wal_buffers = 16MB
max_wal_size = 2GB
min_wal_size = 1GB

# 查询规划
random_page_cost = 1.1            # SSD 磁盘
effective_io_concurrency = 200    # SSD 磁盘

# 日志配置
log_min_duration_statement = 1000  # 记录 > 1 秒的查询
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'ddl'             # 记录 DDL 操作

# 自动 VACUUM
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
```

---

## 常见问题 (FAQ)

### Q1: 如何切换数据库？

```bash
# 切换到 PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"
systemctl restart helloagents

# 切换回 SQLite（移除环境变量）
unset DATABASE_URL
systemctl restart helloagents
```

### Q2: 如何查看应用使用的数据库？

```python
# backend/app/database.py
from app.database import IS_POSTGRES, DATABASE_URL

print(f"Database Type: {'PostgreSQL' if IS_POSTGRES else 'SQLite'}")
print(f"Database URL: {DATABASE_URL}")
```

### Q3: 如何优化慢查询？

```sql
-- 1. 启用 pg_stat_statements
CREATE EXTENSION pg_stat_statements;

-- 2. 查看慢查询
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- 3. 分析查询计划
EXPLAIN ANALYZE <your_slow_query>;

-- 4. 添加索引
CREATE INDEX idx_name ON table_name(column_name);
```

### Q4: 如何恢复误删除的数据？

```bash
# 从最近的备份恢复
pg_restore -U user -d db \
    -t users \
    /var/backups/postgresql/latest/full_backup.dump

# 或者使用 PITR（如果启用了 WAL 归档）
# 参考: DATABASE_ARCHITECTURE_REPORT.md 第 5.3 节
```

---

## 联系方式

- **数据库架构师**: database-team@helloagents.com
- **DevOps**: devops@helloagents.com
- **技术支持**: support@helloagents.com

---

**最后更新**: 2026-01-10
**下次审查**: 2026-02-10
