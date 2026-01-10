# Database Scripts Guide

**项目**: HelloAgents Platform
**目录**: backend/scripts/
**维护者**: Database Architect

---

## 📂 脚本清单

| 脚本 | 描述 | 使用场景 |
|------|------|---------|
| `migrate_to_postgresql.sh` | SQLite → PostgreSQL 迁移 | 生产环境部署 |
| `backup_postgresql.sh` | PostgreSQL 自动备份 | 定时任务（cron） |
| `monitor_postgresql.sql` | 性能监控查询 | 日常运维监控 |
| `create_tables_postgresql.sql` | PostgreSQL 表结构 | 手动建表 |
| `create_indexes_postgresql.sql` | PostgreSQL 索引 | 手动创建索引 |

---

## 🚀 快速开始

### 1. PostgreSQL 迁移

#### 准备工作

```bash
# 1. 安装 PostgreSQL 17
# macOS
brew install postgresql@17

# Ubuntu
sudo apt install postgresql-17 postgresql-contrib-17

# 2. 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE helloagents_prod ENCODING 'UTF8';
CREATE USER helloagents_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE helloagents_prod TO helloagents_user;

# PostgreSQL 15+
\c helloagents_prod
GRANT ALL ON SCHEMA public TO helloagents_user;
\q

# 3. 设置环境变量
export PG_HOST="localhost"
export PG_PORT="5432"
export PG_DB="helloagents_prod"
export PG_USER="helloagents_user"
export PG_PASSWORD="your_password"
```

#### 执行迁移

```bash
# 进入脚本目录
cd backend/scripts

# 运行迁移脚本
./migrate_to_postgresql.sh

# 查看迁移日志
cat ../backups/[最新日期]/migration.log

# 查看迁移报告
cat ../backups/[最新日期]/MIGRATION_REPORT.md
```

#### 验证迁移

```bash
# 连接到 PostgreSQL
psql -h localhost -U helloagents_user -d helloagents_prod

# 验证表和数据
\dt
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM lessons;
\q

# 更新应用配置
echo "DATABASE_URL=postgresql://helloagents_user:password@localhost:5432/helloagents_prod" >> ../.env

# 重启应用
cd ../..
systemctl restart helloagents  # 或者你的启动命令
```

---

### 2. 自动备份设置

#### 配置 Cron 任务

```bash
# 1. 编辑 crontab
crontab -e

# 2. 添加每日备份任务（凌晨 3:00）
0 3 * * * /path/to/backend/scripts/backup_postgresql.sh >> /var/log/db_backup.log 2>&1

# 3. 保存退出
# 验证 crontab
crontab -l
```

#### 手动执行备份

```bash
# 设置环境变量
export PG_PASSWORD="your_password"
export BACKUP_DIR="/var/backups/postgresql"
export RETENTION_DAYS=30

# 可选: S3 同步
export ENABLE_S3_SYNC=true
export S3_BUCKET="s3://your-bucket/helloagents"

# 可选: 通知
export SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK"
export EMAIL_TO="admin@helloagents.com"

# 执行备份
cd backend/scripts
./backup_postgresql.sh

# 查看备份
ls -lh /var/backups/postgresql/
```

#### 恢复数据

```bash
# 方法 1: 从自定义格式恢复（推荐）
pg_restore -h localhost -U helloagents_user -d helloagents_prod \
    -j 4 \
    --clean --if-exists \
    /var/backups/postgresql/20260110_030000/full_backup.dump

# 方法 2: 从 SQL 文件恢复
gunzip -c /var/backups/postgresql/20260110_030000/schema_and_data.sql.gz | \
    psql -h localhost -U helloagents_user -d postgres

# 方法 3: 恢复单个表
pg_restore -h localhost -U helloagents_user -d helloagents_prod \
    -t users \
    /var/backups/postgresql/20260110_030000/full_backup.dump
```

---

### 3. 性能监控

#### 运行完整监控报告

```bash
# 连接到数据库并运行监控脚本
psql -h localhost -U helloagents_user -d helloagents_prod \
    -f scripts/monitor_postgresql.sql

# 输出到文件
psql -h localhost -U helloagents_user -d helloagents_prod \
    -f scripts/monitor_postgresql.sql \
    > monitoring_report_$(date +%Y%m%d).txt
```

#### 监控特定指标

```bash
# 1. 数据库大小
psql -U helloagents_user -d helloagents_prod -c "SELECT pg_size_pretty(pg_database_size(current_database()));"

# 2. 表大小
psql -U helloagents_user -d helloagents_prod -c "\dt+"

# 3. 活跃连接
psql -U helloagents_user -d helloagents_prod -c "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';"

# 4. 缓存命中率
psql -U helloagents_user -d helloagents_prod -c "
SELECT ROUND(100.0 * sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2) as cache_hit_ratio
FROM pg_statio_user_tables;
"

# 5. 慢查询（需要 pg_stat_statements 扩展）
psql -U helloagents_user -d helloagents_prod -c "
SELECT calls, ROUND(mean_exec_time::numeric, 2) as avg_ms, LEFT(query, 100) as query_preview
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"
```

#### 定时监控（Cron）

```bash
# 每周一早上 9:00 生成监控报告
crontab -e

# 添加以下行
0 9 * * 1 psql -U helloagents_user -d helloagents_prod -f /path/to/scripts/monitor_postgresql.sql > /var/log/db_monitoring_$(date +\%Y\%m\%d).txt
```

---

## 🔧 常见操作

### 数据库管理

```bash
# 查看所有数据库
psql -U postgres -l

# 创建新数据库
createdb -U postgres helloagents_test

# 删除数据库
dropdb -U postgres helloagents_test

# 重命名数据库
psql -U postgres -c "ALTER DATABASE helloagents_prod RENAME TO helloagents_prod_old;"

# 查看数据库配置
psql -U postgres -c "SHOW ALL;"
```

### 用户管理

```bash
# 创建用户
psql -U postgres -c "CREATE USER newuser WITH PASSWORD 'password';"

# 授权
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE helloagents_prod TO newuser;"

# 修改密码
psql -U postgres -c "ALTER USER helloagents_user PASSWORD 'new_password';"

# 删除用户
psql -U postgres -c "DROP USER olduser;"
```

### 性能优化

```bash
# 1. 更新统计信息
psql -U helloagents_user -d helloagents_prod -c "ANALYZE;"

# 2. 清理死元组
psql -U helloagents_user -d helloagents_prod -c "VACUUM ANALYZE;"

# 3. 完全清理（锁表，慎用）
psql -U helloagents_user -d helloagents_prod -c "VACUUM FULL;"

# 4. 重建索引
psql -U helloagents_user -d helloagents_prod -c "REINDEX TABLE users;"

# 5. 查看查询计划
psql -U helloagents_user -d helloagents_prod -c "
EXPLAIN ANALYZE SELECT * FROM user_progress WHERE user_id = 1;
"
```

---

## 🐛 故障排查

### 连接问题

```bash
# 测试连接
psql -h localhost -U helloagents_user -d helloagents_prod -c '\l'

# 查看 PostgreSQL 状态
sudo systemctl status postgresql

# 重启 PostgreSQL
sudo systemctl restart postgresql

# 查看日志
sudo tail -f /var/log/postgresql/postgresql-17-main.log

# 查看连接数
psql -U postgres -c "SELECT COUNT(*) FROM pg_stat_activity;"

# 杀死僵尸连接
psql -U postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND state_change < now() - interval '1 hour';
"
```

### 性能问题

```bash
# 1. 查找长时间运行的查询
psql -U helloagents_user -d helloagents_prod -c "
SELECT pid, usename, ROUND(EXTRACT(EPOCH FROM (now() - query_start))::numeric, 2) as duration_seconds, state, LEFT(query, 100) as query_preview
FROM pg_stat_activity
WHERE state = 'active' AND query_start < now() - interval '5 seconds'
ORDER BY query_start;
"

# 2. 杀死慢查询
psql -U postgres -c "SELECT pg_cancel_backend(12345);"  # 温和取消
psql -U postgres -c "SELECT pg_terminate_backend(12345);"  # 强制终止

# 3. 查看锁等待
psql -U helloagents_user -d helloagents_prod -f scripts/check_locks.sql
```

### 磁盘空间问题

```bash
# 查看磁盘使用
df -h /var/lib/postgresql

# 查看数据库大小
psql -U postgres -c "
SELECT datname, pg_size_pretty(pg_database_size(datname))
FROM pg_database
ORDER BY pg_database_size(datname) DESC;
"

# 清理日志
sudo find /var/log/postgresql -name "*.log" -mtime +7 -delete

# VACUUM FULL（释放磁盘空间）
psql -U helloagents_user -d helloagents_prod -c "VACUUM FULL;"
```

---

## 📚 相关文档

- **DATABASE_ARCHITECTURE_REPORT.md** - 完整架构评估和迁移方案
- **DATABASE_QUICKREF.md** - 常用命令快速参考
- **DB_ARCHITECT_DELIVERABLES.md** - 交付物总结

---

## 🔒 安全提示

1. **密码管理**
   - 使用强密码（16+ 字符）
   - 定期更换密码（90 天）
   - 不要在脚本中硬编码密码
   - 使用环境变量或密钥管理工具

2. **访问控制**
   - 限制数据库访问 IP（pg_hba.conf）
   - 使用最小权限原则
   - 定期审查用户权限

3. **备份安全**
   - 加密备份文件
   - 安全存储备份（S3 加密）
   - 定期测试恢复流程

4. **日志审计**
   - 记录所有数据库操作
   - 监控异常访问
   - 定期审查日志

---

## 📞 支持

- **紧急问题**: database-team@helloagents.com
- **一般咨询**: Slack #database 频道
- **文档**: 查看 DATABASE_QUICKREF.md

---

**最后更新**: 2026-01-10
**维护者**: Database Architect
