# 容器池快速入门指南

## 什么是容器池?

容器池是一种性能优化技术,通过预创建和复用 Docker 容器来显著减少代码执行延迟。

**性能提升:**
- 传统方式 (一次性容器): ~1.6秒/次
- 容器池方式: ~0.15秒/次
- **性能提升: 10倍以上**

## 快速启动

### 1. 确保 Docker 运行

```bash
# 检查 Docker 状态
docker ps

# 如果没有运行,启动 Docker
# macOS: 打开 Docker Desktop
# Linux: sudo systemctl start docker
```

### 2. 启动后端服务

```bash
cd backend
python3 -m uvicorn app.main:app --reload
```

容器池会自动初始化 (默认创建 3 个容器)。

### 3. 测试容器池

#### 方法 1: 通过 API 测试

```bash
# 执行代码
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"print(\"Hello from container pool!\")", "language":"python"}'

# 查看容器池状态
curl http://localhost:8000/api/sandbox/pool/stats | python3 -m json.tool
```

#### 方法 2: 运行性能测试

```bash
cd backend
python3 test_pool_performance.py
```

这会对比容器池和一次性容器的性能差异。

## 查看统计信息

### 通过 API

```bash
curl http://localhost:8000/api/sandbox/pool/stats
```

### 响应示例

```json
{
  "pool_enabled": true,
  "pool_id": "a1b2c3d4",
  "available_containers": 2,
  "in_use_containers": 1,
  "total_containers": 3,
  "max_size": 10,
  "min_size": 1,
  "total_created": 3,
  "total_destroyed": 0,
  "total_executions": 15,
  "total_resets": 14,
  "health_check_failures": 0,
  "containers": [
    {
      "id": "abc123",
      "status": "available",
      "created_at": 1704700000.0,
      "last_used_at": 1704700300.0,
      "execution_count": 5,
      "reset_count": 4,
      "health_check_failures": 0
    }
  ]
}
```

## 配置选项

### 基础配置

编辑 `backend/app/sandbox.py` 中的全局沙箱实例:

```python
# 默认配置 (已启用容器池)
sandbox = CodeSandbox(
    use_pool=True,          # 启用容器池
    pool_initial_size=3,    # 初始 3 个容器
    pool_max_size=10        # 最多 10 个容器
)
```

### 自定义配置

```python
# 开发环境配置 (资源有限)
sandbox = CodeSandbox(
    use_pool=True,
    pool_initial_size=2,
    pool_max_size=5,
    timeout=30
)

# 生产环境配置 (高并发)
sandbox = CodeSandbox(
    use_pool=True,
    pool_initial_size=5,
    pool_max_size=20,
    timeout=30
)
```

### 禁用容器池

```python
# 使用一次性容器 (向后兼容)
sandbox = CodeSandbox(
    use_pool=False
)
```

## 监控与维护

### 监控关键指标

1. **可用容器数** (`available_containers`)
   - 正常: > 0
   - 告警: = 0 且请求频繁

2. **使用中容器数** (`in_use_containers`)
   - 正常: < max_size
   - 告警: = max_size (池已满)

3. **健康检查失败** (`health_check_failures`)
   - 正常: 接近 0
   - 告警: > 总检查次数的 5%

4. **总执行次数** (`total_executions`)
   - 用于计算 QPS

### 查看日志

```bash
# 容器池日志位置
tail -f backend/logs/helloagents.log | grep container_pool
```

关键日志事件:
- `container_pool_initialized`: 容器池启动
- `container_acquired`: 获取容器
- `container_returned`: 归还容器
- `container_reset_completed`: 容器重置完成
- `container_marked_unhealthy`: 容器标记为不健康

## 常见问题

### Q1: 容器池没有初始化?

**症状:** 日志显示 "docker_unavailable"

**解决:**
```bash
# 检查 Docker 是否运行
docker ps

# 如果失败,启动 Docker
# macOS: 打开 Docker Desktop
# Linux: sudo systemctl start docker

# 重启后端服务
```

### Q2: 性能没有提升?

**可能原因:**
1. Docker 未运行 (降级到本地执行)
2. 容器池配置太小 (initial_size < 并发数)
3. 首次执行包含容器创建时间

**解决:**
- 确保 Docker 运行
- 增加 `initial_size`
- 排除首次执行计算平均时间

### Q3: 容器池占用内存过多?

**原因:** 每个容器 ~128MB,10 个容器约 1.3GB

**解决:**
```python
# 减少最大容器数
sandbox = CodeSandbox(
    use_pool=True,
    max_size=5  # 降低到 5 个
)
```

### Q4: 容器获取超时?

**症状:** 日志显示 "container_acquisition_timeout"

**原因:** 所有容器都在使用中,池已满

**解决:**
```python
# 增加最大容器数
sandbox = CodeSandbox(
    use_pool=True,
    max_size=20  # 增加到 20 个
)
```

## 高级用法

### 编程式使用

```python
from app.sandbox import CodeSandbox

# 创建自定义沙箱
my_sandbox = CodeSandbox(
    use_pool=True,
    pool_initial_size=5,
    pool_max_size=15,
    image="python:3.11-slim",
    timeout=60
)

# 执行代码
success, output, exec_time = my_sandbox.execute_python("""
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)

print(factorial(10))
""")

print(f"成功: {success}")
print(f"输出: {output}")
print(f"耗时: {exec_time * 1000:.2f}ms")

# 获取统计
stats = my_sandbox.pool.get_stats()
print(f"总执行次数: {stats['total_executions']}")

# 清理
my_sandbox.cleanup()
```

### 自定义容器镜像

```python
# 使用自定义镜像 (包含预装库)
sandbox = CodeSandbox(
    use_pool=True,
    image="my-python-image:latest",  # 自定义镜像
    pool_initial_size=3
)
```

### 调整超时和限制

```python
# 调整执行超时
sandbox = CodeSandbox(
    use_pool=True,
    timeout=60  # 60 秒超时
)
```

## 性能优化建议

### 1. 预热容器池

```python
# 应用启动时立即创建足够的容器
sandbox = CodeSandbox(
    use_pool=True,
    pool_initial_size=10,  # 预创建 10 个
    pool_max_size=20
)
```

### 2. 监控并调整

```bash
# 定期检查统计信息
watch -n 5 "curl -s http://localhost:8000/api/sandbox/pool/stats | python3 -m json.tool"
```

根据 `in_use_containers` 的平均值调整 `initial_size`。

### 3. 使用自定义镜像

预装常用库可以减少首次导入时间:

```dockerfile
FROM python:3.11-slim

# 预装常用库
RUN pip install numpy pandas matplotlib requests

# 其他配置...
```

### 4. 调整健康检查频率

```python
from app.container_pool import ContainerPool

pool = ContainerPool(
    initial_size=3,
    max_size=10,
    health_check_interval=60,  # 降低到 60 秒 (减少开销)
    idle_timeout=600  # 增加到 10 分钟 (减少重建)
)
```

## 故障排查

### 启用详细日志

```python
# 在 backend/.env 中设置
LOG_LEVEL=DEBUG
```

### 检查容器状态

```bash
# 查看容器池创建的容器
docker ps -a --filter "label=helloagents.pool_id"

# 检查容器日志
docker logs <container_id>
```

### 手动清理

```bash
# 停止所有容器池容器
docker ps -a --filter "label=helloagents.pool_id" -q | xargs docker stop

# 删除所有容器池容器
docker ps -a --filter "label=helloagents.pool_id" -q | xargs docker rm
```

## 下一步

- 阅读完整的实现文档: `CONTAINER_POOL_IMPLEMENTATION.md`
- 查看架构设计: `reports/容器池架构设计_2026-01-08.md`
- 运行性能测试: `python3 test_pool_performance.py`
- 探索统计 API: `/api/sandbox/pool/stats`

## 支持

如有问题,请查看:
1. 完整实现文档: `CONTAINER_POOL_IMPLEMENTATION.md`
2. 日志文件: `backend/logs/helloagents.log`
3. 测试代码: `backend/tests/test_sandbox.py`

---

**快速入门完成!** 🎉

现在你已经了解如何使用容器池来加速代码执行。
