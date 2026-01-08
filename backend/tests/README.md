# HelloAgents 后端测试指南

## 测试框架

- **测试工具**: pytest 8.3+
- **数据库**: SQLite (内存数据库)
- **HTTP 客户端**: FastAPI TestClient (基于 httpx)
- **覆盖率**: pytest-cov

## 安装测试依赖

```bash
cd backend
pip install -r requirements.txt
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
pytest tests/test_api_basic.py
pytest tests/test_models.py
```

### 运行特定测试函数
```bash
pytest tests/test_api_basic.py::test_health_check
```

### 显示详细输出
```bash
pytest -v
```

### 显示打印输出
```bash
pytest -s
```

### 生成覆盖率报告
```bash
# 终端输出
pytest --cov=app --cov-report=term-missing

# HTML 报告
pytest --cov=app --cov-report=html
# 查看: open htmlcov/index.html
```

### 只运行失败的测试
```bash
pytest --lf
```

### 使用标记过滤测试
```bash
# 只运行 API 测试
pytest -m api

# 排除慢速测试
pytest -m "not slow"
```

## 测试文件结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和 fixtures
├── test_api_basic.py        # 基础 API 测试
├── test_api_users.py        # 用户 API 测试
├── test_api_progress.py     # 学习进度 API 测试
├── test_api_migration.py    # 数据迁移 API 测试
└── test_models.py           # 数据库模型测试
```

## Fixtures

测试中可用的 fixtures（在 `conftest.py` 中定义）：

### `db_session`
- 提供独立的数据库会话
- 每个测试函数自动创建和清理
- 使用内存 SQLite 数据库

```python
def test_something(db_session):
    # 使用 db_session 操作数据库
    pass
```

### `client`
- FastAPI 测试客户端
- 自动配置使用测试数据库
- 支持所有 HTTP 方法

```python
def test_api(client):
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

### `sample_user`
- 创建测试用户
- 自动添加到数据库

```python
def test_with_user(sample_user):
    assert sample_user.username == "test_user"
```

### `sample_lesson`
- 创建测试课程

### `sample_progress`
- 创建测试学习进度
- 自动关联 sample_user 和 sample_lesson

### `sample_submission`
- 创建测试代码提交
- 自动关联 sample_user 和 sample_lesson

### `sample_chat_message`
- 创建测试聊天消息
- 自动关联 sample_user

## 测试数据工厂

✅ **已配置完成** - 使用工厂函数生成测试数据

### 工厂 Fixtures

我们提供了工厂 fixtures 来动态创建测试数据：

```python
def test_with_factories(user_factory, lesson_factory, progress_factory):
    """使用工厂 fixtures 创建多个测试数据"""

    # 创建随机用户
    user1 = user_factory()
    user2 = user_factory()

    # 创建自定义用户
    custom_user = user_factory(
        username="custom_user",
        full_name="Custom User"
    )

    # 创建课程
    lesson = lesson_factory(
        chapter_number=1,
        lesson_number=1,
        title="Test Lesson"
    )

    # 创建学习进度
    progress = progress_factory(
        user_id=user1.id,
        lesson_id=lesson.id,
        completed=1
    )
```

### 可用的工厂 Fixtures

- `user_factory()` - 创建用户
- `lesson_factory()` - 创建课程
- `progress_factory()` - 创建学习进度
- `submission_factory()` - 创建代码提交
- `chat_message_factory()` - 创建聊天消息

### 直接使用工厂函数

除了 fixtures，你也可以直接导入工厂函数：

```python
from tests.factories import (
    create_user_data,
    create_lesson_data,
    create_progress_data,
    create_multiple,
    MockScenarios
)

def test_with_direct_factory(db_session):
    # 创建单个用户
    user = create_user_data(db_session, username="test_user")

    # 批量创建用户
    users = create_multiple(create_user_data, 5, db_session)

    # 使用预设场景
    new_user = MockScenarios.new_user(db_session)
    experienced_user = MockScenarios.experienced_user_with_progress(db_session)
```

### 预设场景

使用 `MockScenarios` 快速创建常见测试场景：

```python
from tests.factories import MockScenarios

def test_scenarios(db_session):
    # 新用户场景
    new_user = MockScenarios.new_user(db_session)
    assert new_user.username == "new_user"

    # 有学习进度的用户
    experienced_user = MockScenarios.experienced_user_with_progress(db_session)
    # 自动创建了 3 个已完成的课程进度

    # 第一课
    first_lesson = MockScenarios.first_lesson(db_session)
    assert first_lesson.chapter_number == 1
    assert first_lesson.lesson_number == 1

    # 成功的代码提交
    success = MockScenarios.successful_submission(db_session)
    assert success.success is True

    # 失败的代码提交
    failure = MockScenarios.failed_submission(db_session)
    assert failure.success is False
```

## 编写测试

### 基本测试示例

```python
def test_example(client):
    """测试描述"""
    # 发送请求
    response = client.get("/api/endpoint")

    # 断言
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "expected_value"
```

### 使用 fixtures 示例

```python
def test_with_fixtures(client, sample_user, sample_lesson):
    """测试使用多个 fixtures"""
    response = client.post("/api/progress/", json={
        "user_id": sample_user.id,
        "lesson_id": sample_lesson.id,
        "current_code": "print('test')"
    })
    assert response.status_code == 200
```

### 测试异常情况

```python
def test_error_case(client):
    """测试错误处理"""
    response = client.get("/api/users/9999")
    assert response.status_code == 404
```

## 最佳实践

1. **测试命名**: 使用 `test_` 前缀，描述性名称
   ```python
   def test_create_user_success(client):
   def test_create_user_duplicate_username(client):
   ```

2. **一个测试一个断言**: 尽量保持测试简单
   ```python
   # 好
   def test_user_creation(client):
       response = client.post("/api/users/", json={...})
       assert response.status_code == 200

   # 避免
   def test_everything(client):
       # 测试多个不相关的功能
   ```

3. **使用 fixtures**: 复用测试数据
   ```python
   @pytest.fixture
   def custom_data(db_session):
       # 创建自定义测试数据
       return data
   ```

4. **清晰的断言**: 使用明确的断言消息
   ```python
   assert user.username == "test", f"Expected 'test', got {user.username}"
   ```

5. **测试隔离**: 每个测试独立，不依赖其他测试

## 持续集成

在 CI/CD 中运行测试：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
```

## 故障排查

### 导入错误
确保 Python 路径正确：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### 数据库错误
检查模型导入是否完整：
```python
# conftest.py 中
from app.models.user import User
from app.models.lesson import Lesson
# ... 导入所有模型
```

### Fixture 未找到
确保 `conftest.py` 在正确位置（tests/ 目录下）

## 参考资料

- [pytest 文档](https://docs.pytest.org/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy 测试指南](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
