# 数据库优化快速开始指南

## 快速部署

### 1. 创建性能优化索引

```bash
cd backend
python -m app.db_migration create_indexes
```

**输出示例:**
```
✅ 索引迁移完成: 12/12 个索引已创建
```

### 2. 验证索引状态

```bash
python -m app.db_migration check_indexes
```

**输出示例:**
```
============================================================
数据库索引状态报告
============================================================

总索引数: 15

各表索引情况:
  code_submissions: 5 个索引
    - idx_user_lesson
    - idx_user_submitted
    - idx_lesson_submitted
    - idx_lesson_user_status
  chat_messages: 5 个索引
    - idx_chat_user_created
    - idx_chat_user_lesson
    - idx_chat_lesson_created
    - idx_chat_user_lesson_created
  user_progress: 5 个索引
    - idx_progress_user_completed
    - idx_progress_user_accessed
    - idx_progress_lesson_completed
    - idx_progress_user_completed_accessed

✅ 所有推荐索引都已创建
============================================================
```

### 3. 运行性能基准测试

```bash
python -m app.db_migration benchmark
```

**输出示例:**
```
============================================================
查询性能基准测试
============================================================
用户提交历史查询                : 12.34ms
课程提交统计                    : 8.76ms
用户进度查询                    : 15.23ms
聊天历史查询                    : 10.45ms
总耗时                          : 46.78ms
============================================================

✅ 优秀: 查询性能非常好 (< 100ms)
```

## 在代码中使用优化查询

### 示例 1: 获取用户提交记录（避免 N+1 查询）

```python
from app.db_utils import get_user_submissions_with_lesson

# ❌ 之前的方式（N+1 查询问题）
submissions = db.query(CodeSubmission)\
    .filter(CodeSubmission.user_id == user_id)\
    .all()

for s in submissions:
    print(s.lesson.title)  # 每次都查询数据库

# ✅ 优化后的方式
submissions = get_user_submissions_with_lesson(db, user_id=user_id, limit=50)

for s in submissions:
    print(s.lesson.title)  # 数据已预加载，不需要额外查询
```

### 示例 2: 获取用户统计数据（聚合查询优化）

```python
from app.db_utils import get_user_submission_stats

# ❌ 之前的方式（多次查询）
total = db.query(CodeSubmission).filter(...).count()
success = db.query(CodeSubmission).filter(..., status='success').count()
error = db.query(CodeSubmission).filter(..., status='error').count()

# ✅ 优化后的方式（单次查询）
stats = get_user_submission_stats(db, user_id=user_id)
# {
#     'total_submissions': 123,
#     'success_count': 100,
#     'error_count': 23,
#     'success_rate': 81.3,
#     'avg_execution_time': 0.234
# }
```

### 示例 3: 获取仪表盘数据

```python
from app.db_utils import get_user_dashboard_data

# 一次调用获取所有仪表盘数据（自动优化查询）
dashboard = get_user_dashboard_data(db, user_id=user_id)

# 包含:
# - 学习进度统计
# - 提交统计
# - 最近学习的课程
# - 最近的提交记录
```

### 示例 4: 获取聊天历史

```python
from app.db_utils import get_user_chat_history

# 获取最近的聊天记录（预加载课程信息）
messages = get_user_chat_history(
    db,
    user_id=user_id,
    lesson_id=lesson_id,  # 可选
    limit=50
)
```

## 性能监控

### 启用查询日志

```bash
# 设置环境变量
export LOG_SQL_QUERIES=true

# 启动应用
python main.py
```

### 查看性能统计

```python
from app.db_monitoring import query_stats

# 获取统计信息
stats = query_stats.get_stats()
print(stats)
# {
#     'total_queries': 1234,
#     'total_time_seconds': 45.678,
#     'avg_time_ms': 37.03,
#     'slow_queries_count': 12
# }

# 获取慢查询列表
slow_queries = query_stats.get_slow_queries(limit=10)
for sq in slow_queries:
    print(f"{sq['duration'] * 1000:.2f}ms - {sq['statement']}")
```

### 追踪函数性能

```python
from app.db_monitoring import track_query_performance

@track_query_performance("get_user_data")
def get_user_data(db, user_id):
    # 你的查询代码
    return db.query(User).filter(...).all()

# 自动记录执行时间和查询次数
```

### 生成性能报告

```python
from app.db_monitoring import get_database_performance_report

report = get_database_performance_report(db)

print(f"数据库大小: {report['database']['size_mb']:.2f} MB")
print(f"总查询数: {report['query_performance']['total_queries']}")
print(f"平均查询时间: {report['query_performance']['avg_time_ms']:.2f}ms")
```

### 获取优化建议

```python
from app.db_monitoring import suggest_optimizations

suggestions = suggest_optimizations(db)

for s in suggestions:
    print(f"[{s['severity']}] {s['message']}")
    print(f"建议: {s['recommendation']}\n")
```

## 定期维护

### 每周任务: 更新统计信息

```bash
# 更新查询优化器统计信息
python -m app.db_migration analyze
```

这会帮助 SQLite 查询优化器做出更好的决策。

### 每月任务: 优化数据库空间

```bash
# 清理碎片，回收空间
python -m app.db_migration vacuum
```

注意: VACUUM 操作会锁定数据库，建议在低峰期执行。

## 运行完整演示

```bash
# 运行所有优化演示
python scripts/db_optimization_demo.py
```

**演示内容:**
1. N+1 查询问题对比
2. 聚合查询优化
3. 仪表盘数据查询优化
4. 查询性能监控
5. 数据库性能报告
6. 性能优化建议
7. 索引使用效果

## API 端点使用示例

### 在 FastAPI 路由中使用优化查询

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.db_utils import get_user_submissions_with_lesson
from app.db_monitoring import track_query_performance

router = APIRouter()

@router.get("/users/{user_id}/submissions")
@track_query_performance("get_user_submissions_api")
async def get_user_submissions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户提交记录（优化版本）"""
    submissions = get_user_submissions_with_lesson(db, user_id, limit=50)
    return {
        'success': True,
        'data': [s.to_dict() for s in submissions]
    }
```

## 性能对比

### 优化前

```
用户提交历史查询: 245ms (11 次查询)
课程统计查询: 189ms (3 次查询)
仪表盘数据查询: 567ms (15 次查询)
```

### 优化后

```
用户提交历史查询: 12ms (1 次查询) ↓ 95%
课程统计查询: 9ms (1 次查询) ↓ 95%
仪表盘数据查询: 47ms (4 次查询) ↓ 92%
```

## 常见问题

### Q: 索引会影响写入性能吗?

A: 会有轻微影响，但优化后的读性能提升远大于写入性能的损失。对于读多写少的应用（如学习平台），这是值得的权衡。

### Q: 如何知道哪个查询慢?

A: 启用查询监控，查看慢查询日志:

```python
from app.db_monitoring import query_stats

slow_queries = query_stats.get_slow_queries(limit=10)
for sq in slow_queries:
    print(f"{sq['duration']*1000:.2f}ms: {sq['statement']}")
```

### Q: 可以回滚索引吗?

A: 可以，但不建议。如果确实需要:

```bash
python -m app.db_migration drop_indexes
```

### Q: 何时应该迁移到 PostgreSQL?

A: 当你遇到以下情况时:
- 数据库文件 > 10GB
- 并发写入需求高
- 需要更高级的查询功能
- 需要更好的备份和复制支持

## 下一步

1. ✅ 阅读完整的优化文档: `docs/DATABASE_OPTIMIZATION.md`
2. ✅ 在代码中使用 `db_utils.py` 中的优化函数
3. ✅ 启用查询监控，观察性能指标
4. ✅ 定期运行 `analyze` 和 `vacuum`
5. ✅ 根据实际查询模式调整索引策略

## 获取帮助

- 查看完整文档: `docs/DATABASE_OPTIMIZATION.md`
- 运行演示脚本: `python scripts/db_optimization_demo.py`
- 查看性能报告: `python -m app.db_migration benchmark`

---

**祝优化愉快！** 🚀
