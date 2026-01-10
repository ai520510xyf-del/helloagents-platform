# 架构迁移指南

从原有架构迁移到 Clean Architecture 的实用指南

---

## 📋 目录

1. [迁移概述](#迁移概述)
2. [目录结构变化](#目录结构变化)
3. [逐步迁移步骤](#逐步迁移步骤)
4. [代码示例对比](#代码示例对比)
5. [测试策略](#测试策略)
6. [常见问题](#常见问题)

---

## 🎯 迁移概述

### 为什么要迁移？

✅ **更清晰的架构**: 分层明确，职责清晰
✅ **更好的测试性**: 业务逻辑独立，易于测试
✅ **更强的可维护性**: 代码复用，易于扩展
✅ **更低的耦合度**: 依赖倒置，灵活替换

### 迁移策略

采用 **渐进式迁移** 策略，确保系统平稳过渡：

1. 保留原有 API v1（向后兼容）
2. 创建新架构 API v2（逐步迁移）
3. 两套系统并行运行
4. 逐步切换流量到 v2
5. 最终废弃 v1

---

## 📁 目录结构变化

### 原有结构

```
app/
├── models/              # ORM 模型
├── routers/             # API 路由（混杂业务逻辑）
├── api/v1/              # API v1
├── database.py          # 数据库配置
├── sandbox.py           # 沙箱
└── main.py              # 入口
```

### 新架构结构

```
app/
├── domain/              # 🆕 领域层（核心业务逻辑）
│   ├── entities/        # 领域实体
│   ├── repositories/    # 仓储接口
│   ├── services/        # 领域服务
│   └── value_objects/   # 值对象
│
├── application/         # 🆕 应用层（用例协调）
│   ├── use_cases/       # 业务用例
│   └── dto/             # 数据传输对象
│
├── infrastructure/      # 🆕 基础设施层（技术实现）
│   ├── repositories/    # 仓储实现
│   └── external_services/ # 外部服务
│
├── api/
│   ├── v1/              # API v1（保持兼容）
│   └── v2/              # 🆕 API v2（新架构）
│
├── models/              # ORM 模型（仅用于持久化）
├── container.py         # 🆕 依赖注入容器
├── database.py
└── main.py
```

---

## 🚀 逐步迁移步骤

### Step 1: 创建领域实体

**原有代码** (`models/user.py`):
```python
# ORM 模型直接暴露给上层
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    full_name = Column(String(100))
```

**新架构代码** (`domain/entities/user_entity.py`):
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserEntity:
    """领域实体：封装业务逻辑和不变量"""
    id: Optional[int] = None
    username: str = ""
    full_name: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def update_profile(self, full_name: str, settings: Dict):
        """业务方法：更新配置"""
        self.full_name = full_name
        self.settings.update(settings)
        self.updated_at = datetime.utcnow()
```

**迁移操作**:
```bash
# 1. 创建领域实体文件
mkdir -p app/domain/entities
touch app/domain/entities/user_entity.py

# 2. 实现实体类
# 参考: backend/app/domain/entities/user_entity.py
```

---

### Step 2: 定义仓储接口

**新架构代码** (`domain/repositories/user_repository.py`):
```python
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    """仓储接口：定义数据访问的抽象方法"""

    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def update(self, user: UserEntity) -> UserEntity:
        pass
```

**迁移操作**:
```bash
# 创建仓储接口
mkdir -p app/domain/repositories
touch app/domain/repositories/user_repository.py
```

---

### Step 3: 实现仓储

**新架构代码** (`infrastructure/repositories/user_repository_impl.py`):
```python
from app.domain.repositories.user_repository import IUserRepository
from app.domain.entities.user_entity import UserEntity
from app.models.user import User  # ORM 模型

class UserRepositoryImpl(IUserRepository):
    """仓储实现：使用 SQLAlchemy"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, user: UserEntity) -> UserEntity:
        # 实体 → ORM
        db_user = User(
            username=user.username,
            full_name=user.full_name
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

        # ORM → 实体
        return self._to_entity(db_user)

    def _to_entity(self, db_user: User) -> UserEntity:
        return UserEntity.from_dict(db_user.to_dict())
```

**迁移操作**:
```bash
# 创建仓储实现
mkdir -p app/infrastructure/repositories
touch app/infrastructure/repositories/user_repository_impl.py
```

---

### Step 4: 创建业务用例

**原有代码** (`routers/users.py`):
```python
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 业务逻辑混杂在路由中
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User exists")

    db_user = User(username=user.username, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user.to_dict()
```

**新架构代码** (`application/use_cases/user_management_use_case.py`):
```python
class UserManagementUseCase:
    """用户管理用例：编排业务流程"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def create_user(self, request: UserCreateDTO) -> UserResponseDTO:
        # 1. 检查用户是否存在
        if self.user_repository.exists(request.username):
            raise ConflictError(f"用户名 '{request.username}' 已存在")

        # 2. 创建实体
        user = UserEntity(
            username=request.username,
            full_name=request.full_name
        )

        # 3. 保存到仓储
        created_user = self.user_repository.create(user)

        # 4. 返回 DTO
        return self._to_response_dto(created_user)
```

**新路由代码** (`api/v2/routes/users.py`):
```python
@router.post("")
def create_user(
    request: UserCreateDTO,
    use_case: UserManagementUseCase = Depends(get_user_management_use_case)
):
    """路由只负责请求/响应转换，业务逻辑在 Use Case 中"""
    return use_case.create_user(request)
```

**迁移操作**:
```bash
# 1. 创建用例
mkdir -p app/application/use_cases
touch app/application/use_cases/user_management_use_case.py

# 2. 创建 DTO
mkdir -p app/application/dto
touch app/application/dto/user_dto.py

# 3. 创建 v2 路由
mkdir -p app/api/v2/routes
touch app/api/v2/routes/users.py
```

---

### Step 5: 设置依赖注入

**新架构代码** (`container.py`):
```python
class Container:
    """依赖注入容器"""

    def __init__(self):
        self._services = {}
        self._register_services()

    def _register_services(self):
        # 注册仓储
        self._factories['user_repository'] = lambda: UserRepositoryImpl(
            session=self.get('db_session')
        )

        # 注册用例
        self._factories['user_management_use_case'] = lambda: UserManagementUseCase(
            user_repository=self.get('user_repository')
        )

# 创建全局容器
container = Container()

# FastAPI 依赖注入辅助函数
def get_user_management_use_case(session: Session) -> UserManagementUseCase:
    user_repository = UserRepositoryImpl(session)
    return UserManagementUseCase(user_repository)
```

**迁移操作**:
```bash
# 创建容器
touch app/container.py
```

---

### Step 6: 注册 v2 路由

**`main.py` 修改**:
```python
from app.api.v2 import api_router as api_v2_router

# 注册 v2 路由
app.include_router(api_v2_router, prefix="/api/v2")

# 保留 v1 路由（向后兼容）
app.include_router(api_v1_router, prefix="/api/v1")
```

---

## 📊 代码示例对比

### 示例 1: 创建用户

#### 原有架构（v1）

```python
# routers/users.py
@router.post("/api/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # ❌ 业务逻辑直接写在路由中
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User exists")

    # ❌ 直接操作 ORM 模型
    db_user = User(username=user.username, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # ❌ 返回 ORM 模型字典
    return db_user.to_dict()
```

**问题**:
- 业务逻辑和数据访问混杂
- 难以测试（需要数据库）
- 难以复用（绑定到路由）
- ORM 模型直接暴露

#### 新架构（v2）

**领域实体**:
```python
# domain/entities/user_entity.py
@dataclass
class UserEntity:
    username: str
    full_name: Optional[str] = None

    def __post_init__(self):
        if not self.username:
            raise ValueError("Username cannot be empty")
```

**仓储接口**:
```python
# domain/repositories/user_repository.py
class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def exists(self, username: str) -> bool:
        pass
```

**业务用例**:
```python
# application/use_cases/user_management_use_case.py
class UserManagementUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def create_user(self, request: UserCreateDTO) -> UserResponseDTO:
        # ✅ 清晰的业务流程
        if self.user_repository.exists(request.username):
            raise ConflictError(f"用户名已存在")

        user = UserEntity(username=request.username, full_name=request.full_name)
        created_user = self.user_repository.create(user)

        return self._to_response_dto(created_user)
```

**API 路由**:
```python
# api/v2/routes/users.py
@router.post("")
def create_user(
    request: UserCreateDTO,
    use_case: UserManagementUseCase = Depends(get_user_management_use_case)
):
    # ✅ 路由只负责请求/响应转换
    return use_case.create_user(request)
```

**优势**:
- ✅ 业务逻辑独立（Use Case）
- ✅ 易于测试（可以 Mock Repository）
- ✅ 可复用（Use Case 可在多处使用）
- ✅ 类型安全（Pydantic DTO）

---

### 示例 2: 执行代码

#### 原有架构（v1）

```python
# main.py
@app.post("/api/execute")
async def execute_code(request: CodeExecutionRequest, db: Session = Depends(get_db)):
    # ❌ 业务逻辑混杂
    # ❌ 直接依赖全局 sandbox
    success, output, execution_time = sandbox.execute_python(request.code)

    # ❌ 保存逻辑混在一起
    if user_id and lesson_id:
        submission = CodeSubmission(...)
        db.add(submission)
        db.commit()

    return CodeExecutionResponse(...)
```

#### 新架构（v2）

**领域实体**:
```python
# domain/entities/code_execution_entity.py
@dataclass
class CodeExecutionEntity:
    code: str
    language: str = "python"
    timeout: int = 30

    def validate(self):
        """验证代码请求"""
        if len(self.code) > 10000:
            raise ValueError("Code length exceeds limit")

    def check_security(self):
        """检查代码安全性"""
        dangerous_patterns = [('os.system', '禁止使用 os.system'), ...]
        for pattern, message in dangerous_patterns:
            if pattern in self.code:
                raise ValueError(f"Security check failed: {message}")
```

**领域服务接口**:
```python
# domain/services/code_execution_service.py
class ICodeExecutionService(ABC):
    @abstractmethod
    def execute(self, execution: CodeExecutionEntity) -> Tuple[bool, str, float]:
        pass
```

**业务用例**:
```python
# application/use_cases/execute_code_use_case.py
class ExecuteCodeUseCase:
    def __init__(self, execution_service: ICodeExecutionService):
        self.execution_service = execution_service

    def execute(self, request: CodeExecutionRequestDTO) -> CodeExecutionResponseDTO:
        # ✅ 清晰的业务流程
        # 1. 创建实体
        execution = CodeExecutionEntity(
            code=request.code,
            language=request.language,
            timeout=request.timeout
        )

        # 2. 验证安全性
        execution.check_security()

        # 3. 执行代码
        success, output, exec_time = self.execution_service.execute(execution)

        # 4. 返回响应
        return CodeExecutionResponseDTO(
            success=success,
            output=output,
            execution_time=exec_time
        )
```

**API 路由**:
```python
# api/v2/routes/code_execution.py
@router.post("/execute")
def execute_code(
    request: CodeExecutionRequestDTO,
    use_case: ExecuteCodeUseCase = Depends(get_execute_code_use_case)
):
    return use_case.execute(request)
```

---

## 🧪 测试策略

### 原有架构测试难度 ❌

```python
# 需要真实数据库
def test_create_user():
    db = TestingSessionLocal()  # 需要测试数据库
    user = UserCreate(username="test")
    result = create_user(user, db)  # 直接调用路由函数
    assert result['username'] == "test"
```

**问题**:
- 需要真实数据库
- 测试耦合度高
- 测试速度慢

### 新架构测试简单 ✅

#### 测试领域实体

```python
def test_user_entity_validation():
    # 纯业务逻辑测试，无需数据库
    with pytest.raises(ValueError):
        UserEntity(username="")  # 用户名不能为空
```

#### 测试用例（Mock Repository）

```python
def test_create_user_use_case():
    # Mock 仓储
    mock_repo = Mock(spec=IUserRepository)
    mock_repo.exists.return_value = False
    mock_repo.create.return_value = UserEntity(id=1, username="alice")

    # 测试用例
    use_case = UserManagementUseCase(mock_repo)
    result = use_case.create_user(UserCreateDTO(username="alice"))

    # 断言
    assert result.id == 1
    mock_repo.create.assert_called_once()
```

#### 测试 API 路由

```python
def test_create_user_api(client):
    # 使用 FastAPI TestClient
    response = client.post("/api/v2/users", json={"username": "alice"})
    assert response.status_code == 201
    assert response.json()['username'] == "alice"
```

---

## ❓ 常见问题

### Q1: 迁移会影响现有 API 吗？

**A**: 不会。我们采用渐进式迁移：
- API v1 保持不变（向后兼容）
- 新功能使用 API v2
- 逐步弃用 v1

### Q2: 需要修改现有 ORM 模型吗？

**A**: 不需要。ORM 模型保持不变，仅用于持久化：
- 领域实体封装业务逻辑
- ORM 模型仅用于数据库映射
- Repository 负责实体 ↔ ORM 转换

### Q3: 依赖注入会影响性能吗？

**A**: 影响极小：
- 容器在应用启动时初始化
- 服务解析开销可忽略（微秒级）
- 带来的架构优势远大于性能开销

### Q4: 如何测试新架构？

**A**: 分层测试：
- **单元测试**: 测试 Entity、Use Case（Mock Repository）
- **集成测试**: 测试 Repository 实现（真实数据库）
- **E2E 测试**: 测试 API 端点（TestClient）

### Q5: 迁移需要多长时间？

**A**: 渐进式迁移，按模块进行：
- **单个端点**: 1-2天
- **完整模块**: 1-2周
- **全部迁移**: 1-2个月

### Q6: 如何保证迁移质量？

**A**: 质量保证措施：
- ✅ 完善的单元测试
- ✅ 自动化集成测试
- ✅ Code Review
- ✅ 灰度发布
- ✅ 监控告警

---

## 🔗 相关资源

- [架构审查报告](./ARCHITECTURE_REVIEW_REPORT.md)
- [API v2 文档](http://localhost:8000/api/v2/docs)
- [Clean Architecture 介绍](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [DDD 实践指南](https://www.domainlanguage.com/ddd/)

---

## 📞 获取帮助

如有问题，请联系:
- **团队 Slack**: #backend-architecture
- **技术负责人**: backend-lead@example.com
- **文档**: [内部文档](./docs/)

---

**最后更新**: 2026-01-09
