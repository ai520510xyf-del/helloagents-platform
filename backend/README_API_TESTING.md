# 后端API测试和诊断工具使用指南

本目录包含用于测试和诊断HelloAgents Platform后端API的工具和脚本。

---

## 📁 工具清单

| 工具 | 文件 | 用途 |
|-----|------|------|
| API路由测试 | `test_api_routes.py` | 快速测试所有关键API端点 |
| API诊断工具 | `diagnose_api.py` | 全面诊断API路由、冲突、中间件 |
| API快速参考 | `API_QUICK_REFERENCE.md` | API端点速查表 |
| 详细分析报告 | `API_ROUTES_FIX_REPORT.md` | 完整的路由分析和建议 |

---

## 🚀 快速开始

### 方式1: API路由测试 (推荐)

最简单快速的测试方式:

```bash
cd /Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/backend
python test_api_routes.py
```

**输出示例**:
```
============================================================
HelloAgents Platform - API 路由测试
============================================================

=== 所有注册路由 ===
GET        /
GET        /api/chat
POST       /api/execute
...

=== 健康检查端点 ===
GET /: 200
GET /health: 200
GET /health/ready: 200
GET /health/live: 200

=== API v1 端点 ===
GET /api/v1/lessons: 200
  - 返回课程数量: 8
...

✅ API 路由测试完成
============================================================
```

### 方式2: 综合诊断 (详细)

生成完整的诊断报告:

```bash
cd /Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/backend
python diagnose_api.py
```

**生成文件**:
- `api_diagnostic_report.json` - JSON格式的详细报告

**报告内容**:
- 所有注册路由列表
- 路由冲突检测
- 中间件顺序分析
- API端点测试结果
- 诊断摘要

---

## 📋 测试覆盖

### 健康检查端点 (4个)

- `GET /` - 根端点
- `GET /health` - 完整健康检查
- `GET /health/ready` - 就绪检查
- `GET /health/live` - 存活检查

### API v1 端点 (8个)

**课程管理**:
- `GET /api/v1/lessons` - 获取课程列表
- `GET /api/v1/lessons/` - 获取课程列表 (带斜杠)
- `GET /api/v1/lessons/{id}` - 获取课程详情

**代码执行**:
- `POST /api/v1/code/execute` - 执行代码
- `POST /api/v1/code/hint` - 获取AI提示

**AI助手**:
- `POST /api/v1/chat` - AI聊天

**沙箱管理**:
- `GET /api/v1/sandbox/pool/stats` - 容器池统计

### 向后兼容端点 (6个)

- `GET /api/lessons` - 旧版课程列表
- `GET /api/lessons/{id}` - 旧版课程详情
- `POST /api/execute` - 旧版代码执行
- `POST /api/chat` - 旧版AI聊天
- `POST /api/hint` - 旧版AI提示
- `GET /api/sandbox/pool/stats` - 旧版容器统计

### 其他端点 (2个)

- `GET /api/users/current` - 获取当前用户
- `GET /api/version` - API版本信息

---

## 🔍 诊断功能

### 1. 路由注册分析

列出所有注册的路由,按标签分组:

```
[lessons] - 4 个端点
  GET        /api/lessons
  GET        /api/lessons/{lesson_id}
  GET        /api/v1/lessons
  GET        /api/v1/lessons/{lesson_id}

[code] - 4 个端点
  POST       /api/execute
  POST       /api/hint
  POST       /api/v1/code/execute
  POST       /api/v1/code/hint
...
```

### 2. 路由冲突检测

检查是否有多个路由注册到同一路径和方法:

```
✅ 未发现路由冲突
```

或

```
⚠️  发现 1 个路由冲突:
路径: /api/test
方法: GET
冲突的路由:
  - get_test_v1 (GET) [test]
  - get_test_v2 (GET) [test]
```

### 3. 中间件顺序检查

显示中间件执行顺序 (从下往上):

```
1. CORSMiddleware
2. LoggingMiddleware
3. PerformanceMonitoringMiddleware
4. ErrorLoggingMiddleware
5. APIVersionMiddleware
6. ErrorHandlerMiddleware
```

### 4. 端点功能测试

实际调用每个端点并验证响应:

```
✅ 获取课程列表 (v1)
   GET /api/v1/lessons -> 200
   返回字段: success, lessons

❌ AI 聊天 (v1)
   POST /api/v1/chat -> 500
   错误: DEEPSEEK_API_KEY environment variable is not set
```

---

## 📊 诊断报告格式

### JSON报告结构

```json
{
  "timestamp": "2026-01-10T12:00:00",
  "summary": {
    "total_routes": 33,
    "test_cases": 14,
    "passed_tests": 12,
    "failed_tests": 2,
    "route_conflicts": 0,
    "middleware_count": 6
  },
  "routes": [
    {
      "methods": "GET",
      "path": "/api/v1/lessons",
      "name": "get_all_lessons",
      "tags": ["lessons"]
    }
  ],
  "test_results": [
    {
      "method": "GET",
      "path": "/api/v1/lessons",
      "description": "获取课程列表 (v1)",
      "status_code": 200,
      "success": true,
      "error": null
    }
  ],
  "conflicts": [],
  "middleware_stack": [
    "ErrorHandlerMiddleware",
    "APIVersionMiddleware",
    ...
  ]
}
```

---

## 🛠️ 使用场景

### 场景1: 日常开发测试

在开发新功能后,快速验证API:

```bash
python test_api_routes.py
```

### 场景2: 部署前验证

在部署到生产前,全面检查:

```bash
python diagnose_api.py
cat api_diagnostic_report.json | jq '.summary'
```

### 场景3: 故障排查

当遇到路由问题时:

```bash
python diagnose_api.py
# 检查报告中的:
# - route_conflicts (路由冲突)
# - failed_tests (失败的测试)
# - middleware_stack (中间件顺序)
```

### 场景4: 性能分析

配合性能监控:

```bash
# 运行诊断
python diagnose_api.py

# 查看响应时间
# 在日志中查找 performance_monitoring 相关记录
grep "performance_monitoring" logs/app.log
```

---

## 🐛 常见问题排查

### 问题1: ImportError

**错误**:
```
ModuleNotFoundError: No module named 'app'
```

**解决**:
```bash
# 确保在backend目录下运行
cd /Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/backend
python test_api_routes.py
```

### 问题2: 数据库连接失败

**错误**:
```
❌ GET /health/ready: 503
   错误: could not connect to database
```

**解决**:
```bash
# 初始化数据库
python -c "from app.database import init_db; init_db()"
```

### 问题3: AI服务测试失败

**错误**:
```
❌ POST /api/v1/chat -> 500
   错误: DEEPSEEK_API_KEY environment variable is not set
```

**说明**: 这是正常的,AI聊天功能需要配置 DEEPSEEK_API_KEY。如果不测试AI功能,可以忽略这个错误。

**解决**:
```bash
# 设置环境变量
export DEEPSEEK_API_KEY=your_api_key_here
python test_api_routes.py
```

### 问题4: 端口占用

**错误**:
```
Address already in use
```

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

---

## 📈 最佳实践

### 1. 定期运行测试

建议在以下时机运行测试:
- ✅ 每次添加新API端点后
- ✅ 修改路由配置后
- ✅ 部署到生产环境前
- ✅ 每周定期检查

### 2. 保存测试报告

```bash
# 运行诊断并保存报告
python diagnose_api.py > api_test_$(date +%Y%m%d).log

# 检查报告
cat api_test_20260110.log
```

### 3. 集成到CI/CD

在 `.github/workflows/` 中添加:

```yaml
- name: Test API Routes
  run: |
    cd backend
    python test_api_routes.py
```

### 4. 监控生产环境

```bash
# 定期测试生产API
curl https://helloagents-platform.onrender.com/health

# 保存健康检查日志
curl https://helloagents-platform.onrender.com/health > health_$(date +%Y%m%d_%H%M%S).json
```

---

## 📚 相关文档

- [API快速参考](./API_QUICK_REFERENCE.md) - API端点速查表
- [API路由分析报告](./API_ROUTES_FIX_REPORT.md) - 详细分析和建议
- [前端API迁移指南](../FRONTEND_API_MIGRATION_GUIDE.md) - 前端升级指南
- [执行摘要](../BACKEND_API_ANALYSIS_SUMMARY.md) - 分析总结

---

## 🤝 贡献

如果发现问题或有改进建议:

1. 创建 GitHub Issue
2. 描述问题和复现步骤
3. 附上诊断报告 (`api_diagnostic_report.json`)

---

## 📞 支持

如有问题,请联系:
- **后端团队**: Senior Backend Developer
- **文档**: 查看上述相关文档
- **紧急问题**: 创建 GitHub Issue 并标记为 `priority:high`

---

**最后更新**: 2026-01-10
**工具版本**: 1.0.0
**维护者**: Senior Backend Developer
