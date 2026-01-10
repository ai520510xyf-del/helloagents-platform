# 🚀 Clean Architecture 快速参考

HelloAgents Platform 后端架构速查表

---

## 📂 目录结构速览

```
app/
├── 🔵 domain/              # 领域层：核心业务逻辑
│   ├── entities/           # 领域实体
│   ├── repositories/       # 仓储接口
│   └── services/           # 领域服务
│
├── 🟢 application/         # 应用层：用例协调
│   ├── use_cases/          # 业务用例
│   └── dto/                # 数据传输对象
│
├── 🟡 infrastructure/      # 基础设施层：技术实现
│   ├── repositories/       # 仓储实现
│   └── external_services/  # 外部服务
│
└── 🟣 api/v2/              # API 层：接口暴露
    └── routes/             # 路由端点
```

---

## 🎯 核心概念速查

### 1. Entity（实体）

**用途**: 封装业务逻辑和不变量

```python
@dataclass
class UserEntity:
    username: str
    full_name: Optional[str] = None

    def __post_init__(self):
        if not self.username:
            raise ValueError("Username cannot be empty")

    def update_profile(self, full_name: str):
        self.full_name = full_name
        self.updated_at = datetime.utcnow()
```

**位置**: `app/domain/entities/`

---

### 2. Repository Interface（仓储接口）

**用途**: 定义数据访问的抽象方法

```python
class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        pass
```

**位置**: `app/domain/repositories/`

---

### 3. Repository Implementation（仓储实现）

**用途**: 实现数据访问逻辑（SQLAlchemy/MongoDB/Redis）

```python
class UserRepositoryImpl(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: UserEntity) -> UserEntity:
        db_user = User(username=user.username)
        self.session.add(db_user)
        self.session.commit()
        return self._to_entity(db_user)
```

**位置**: `app/infrastructure/repositories/`

---

### 4. Use Case（用例）

**用途**: 编排业务流程，协调多个领域对象

```python
class UserManagementUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def create_user(self, request: UserCreateDTO) -> UserResponseDTO:
        # 1. 验证
        if self.user_repository.exists(request.username):
            raise ConflictError("用户名已存在")

        # 2. 创建实体
        user = UserEntity(username=request.username)

        # 3. 保存
        created = self.user_repository.create(user)

        # 4. 返回 DTO
        return UserResponseDTO.from_entity(created)
```

**位置**: `app/application/use_cases/`

---

### 5. DTO（数据传输对象）

**用途**: API 层和应用层之间的数据传输

```python
class UserCreateDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

class UserResponseDTO(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    created_at: str
```

**位置**: `app/application/dto/`

---

### 6. API Route（API 路由）

**用途**: 接收 HTTP 请求，调用用例，返回响应

```python
@router.post("")
def create_user(
    request: UserCreateDTO,
    use_case: UserManagementUseCase = Depends(get_user_management_use_case)
):
    return use_case.create_user(request)
```

**位置**: `app/api/v2/routes/`

---

### 7. Container（依赖注入容器）

**用途**: 管理服务的创建和依赖关系

```python
# 注册服务
container.register_factory('user_repository', lambda: UserRepositoryImpl(...))
container.register_factory('user_use_case', lambda: UserManagementUseCase(...))

# 获取服务
user_repo = container.get('user_repository')
```

**位置**: `app/container.py`

---

## 🔄 数据流向

```
HTTP Request
    ↓
🟣 API Route (接收请求，验证参数)
    ↓
🟢 Use Case (编排业务流程)
    ↓
🔵 Entity (业务逻辑)
    ↓
🔵 Repository Interface (定义接口)
    ↓
🟡 Repository Implementation (数据访问)
    ↓
🟡 ORM Model (数据库映射)
    ↓
Database
```

---

## 🧪 测试策略

### 单元测试（Use Case）

```python
def test_create_user_use_case():
    # Mock 依赖
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

### 集成测试（Repository）

```python
def test_user_repository_impl(db_session):
    # 真实数据库
    repo = UserRepositoryImpl(db_session)
    user = UserEntity(username="alice")

    # 测试
    created = repo.create(user)
    assert created.id is not None
```

### E2E 测试（API）

```python
def test_create_user_api(client):
    response = client.post("/api/v2/users", json={"username": "alice"})
    assert response.status_code == 201
    assert response.json()['username'] == "alice"
```

---

## 📋 代码检查清单

### 创建新功能时

- [ ] ✅ Entity：是否定义了领域实体？
- [ ] ✅ Repository Interface：是否定义了仓储接口？
- [ ] ✅ Repository Implementation：是否实现了仓储？
- [ ] ✅ Use Case：是否创建了用例？
- [ ] ✅ DTO：是否定义了请求/响应 DTO？
- [ ] ✅ API Route：是否创建了路由端点？
- [ ] ✅ Container：是否注册了依赖？
- [ ] ✅ Tests：是否编写了单元测试？
- [ ] ✅ Docs：是否更新了 API 文档？

---

## 🎨 命名约定

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| **Entity** | `{Name}Entity` | `UserEntity`, `OrderEntity` |
| **Repository Interface** | `I{Name}Repository` | `IUserRepository` |
| **Repository Implementation** | `{Name}RepositoryImpl` | `UserRepositoryImpl` |
| **Use Case** | `{Action}{Name}UseCase` | `CreateUserUseCase` |
| **DTO** | `{Name}{Create\|Update\|Response}DTO` | `UserCreateDTO` |
| **Service** | `I{Name}Service` | `ICodeExecutionService` |

---

## 🚀 快速开始

### 1. 创建新实体

```bash
touch app/domain/entities/order_entity.py
```

```python
@dataclass
class OrderEntity:
    id: Optional[int] = None
    user_id: int = 0
    total: float = 0.0
    created_at: Optional[datetime] = None

    def calculate_tax(self, rate: float) -> float:
        return self.total * rate
```

### 2. 定义仓储接口

```bash
touch app/domain/repositories/order_repository.py
```

```python
class IOrderRepository(ABC):
    @abstractmethod
    def create(self, order: OrderEntity) -> OrderEntity:
        pass
```

### 3. 实现仓储

```bash
touch app/infrastructure/repositories/order_repository_impl.py
```

```python
class OrderRepositoryImpl(IOrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, order: OrderEntity) -> OrderEntity:
        # SQLAlchemy 实现
        ...
```

### 4. 创建用例

```bash
touch app/application/use_cases/create_order_use_case.py
```

```python
class CreateOrderUseCase:
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository

    def execute(self, request: CreateOrderDTO) -> OrderResponseDTO:
        order = OrderEntity(user_id=request.user_id, total=request.total)
        created = self.order_repository.create(order)
        return OrderResponseDTO.from_entity(created)
```

### 5. 创建路由

```bash
touch app/api/v2/routes/orders.py
```

```python
@router.post("/orders")
def create_order(
    request: CreateOrderDTO,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case)
):
    return use_case.execute(request)
```

### 6. 注册依赖

```python
# app/container.py
container.register_factory('order_repository', lambda: OrderRepositoryImpl(...))
container.register_factory('create_order_use_case', lambda: CreateOrderUseCase(...))
```

---

## 🔍 常用命令

### 运行 API

```bash
cd backend
uvicorn app.main:app --reload
```

### 访问文档

```
http://localhost:8000/api/v2/docs
```

### 运行测试

```bash
pytest tests/ -v
```

### 代码格式化

```bash
black app/
isort app/
```

### 类型检查

```bash
mypy app/
```

---

## 📚 相关文档

- 📖 [架构审查报告](./ARCHITECTURE_REVIEW_REPORT.md) - 详细分析
- 📖 [迁移指南](./MIGRATION_GUIDE.md) - 迁移步骤
- 📖 [重构总结](./ARCHITECTURE_REFACTORING_SUMMARY.md) - 重构概览
- 📖 [API 文档](http://localhost:8000/api/v2/docs) - 交互式文档

---

## 💡 最佳实践

### ✅ DO（推荐）

- ✅ Entity 包含业务逻辑
- ✅ Repository 只负责数据访问
- ✅ Use Case 编排业务流程
- ✅ API 路由只做请求/响应转换
- ✅ 使用依赖注入
- ✅ 编写单元测试

### ❌ DON'T（避免）

- ❌ Entity 直接访问数据库
- ❌ Repository 包含业务逻辑
- ❌ API 路由直接操作数据库
- ❌ Use Case 包含 HTTP 逻辑
- ❌ 全局变量
- ❌ 紧耦合

---

## 🆘 故障排查

### 问题：找不到服务

```python
KeyError: Service 'xxx' not registered
```

**解决**: 检查 `container.py` 是否注册了服务

### 问题：循环依赖

```python
ImportError: cannot import name 'xxx' from partially initialized module
```

**解决**: 使用延迟导入或依赖注入

### 问题：测试失败

```python
AssertionError: Mock not called
```

**解决**: 检查 Mock 配置和断言

---

**快速参考版本**: 1.0.0
**最后更新**: 2026-01-09
