"""
User Domain Entity

用户领域实体：封装用户相关的业务逻辑和不变量
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import json


@dataclass
class UserEntity:
    """
    用户领域实体

    职责：
    - 封装用户核心业务逻辑
    - 维护用户状态的一致性
    - 提供用户相关的业务操作
    """

    id: Optional[int] = None
    username: str = ""
    full_name: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    def __post_init__(self):
        """初始化后验证"""
        if not self.username:
            raise ValueError("Username cannot be empty")

        if self.created_at is None:
            self.created_at = datetime.utcnow()

        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    def update_profile(self, full_name: Optional[str] = None, settings: Optional[Dict] = None):
        """
        更新用户配置

        Args:
            full_name: 全名
            settings: 用户设置
        """
        if full_name is not None:
            self.full_name = full_name

        if settings is not None:
            self.settings.update(settings)

        self.updated_at = datetime.utcnow()

    def record_login(self):
        """记录登录时间"""
        self.last_login = datetime.utcnow()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        获取用户设置

        Args:
            key: 设置键
            default: 默认值

        Returns:
            设置值
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """
        设置用户配置

        Args:
            key: 设置键
            value: 设置值
        """
        self.settings[key] = value
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'settings': self.settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserEntity':
        """从字典创建实体"""
        # 处理日期字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])

        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])

        if 'last_login' in data and isinstance(data['last_login'], str):
            data['last_login'] = datetime.fromisoformat(data['last_login'])

        # 处理 settings
        if 'settings' in data and isinstance(data['settings'], str):
            data['settings'] = json.loads(data['settings'])

        return cls(**data)
