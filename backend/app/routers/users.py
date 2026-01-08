"""
用户管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json

from ..database import get_db
from ..models.user import User

router = APIRouter(prefix="/api/users", tags=["users"])


# Pydantic 模型
class UserCreate(BaseModel):
    username: str
    full_name: Optional[str] = None
    settings: Optional[dict] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    settings: Optional[dict] = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    settings: dict
    created_at: str
    last_login: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    创建本地用户

    如果用户已存在，返回 400 错误
    """
    # 检查用户是否存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # 创建新用户
    db_user = User(
        username=user.username,
        full_name=user.full_name,
        settings=json.dumps(user.settings or {})
    )
    db.add(db_user)
    db.commit()
    # refresh 在测试环境中可能有问题，直接返回对象
    # db_user 已经在 session 中，所有属性都已加载

    return db_user.to_dict()


@router.get("/current", response_model=UserResponse)
def get_current_user(db: Session = Depends(get_db)):
    """
    获取当前用户

    本地模式：返回第一个用户，如果不存在则创建默认用户
    """
    user = db.query(User).first()

    if not user:
        # 创建默认用户
        user = User(
            username="local_user",
            full_name="本地用户",
            settings=json.dumps({
                "theme": "dark",
                "editor": {
                    "fontSize": 14,
                    "tabSize": 4,
                    "wordWrap": True
                }
            })
        )
        db.add(user)
        db.commit()
        # refresh 在测试环境中可能有问题，直接返回对象

    return user.to_dict()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.full_name is not None:
        user.full_name = user_update.full_name

    if user_update.settings is not None:
        user.settings = json.dumps(user_update.settings)

    from datetime import datetime
    user.updated_at = datetime.utcnow().isoformat()

    db.commit()
    # refresh 在测试环境中可能有问题，直接返回对象

    return user.to_dict()


@router.post("/{user_id}/login")
def record_login(user_id: int, db: Session = Depends(get_db)):
    """记录用户登录时间"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from datetime import datetime
    user.last_login = datetime.utcnow().isoformat()
    db.commit()

    return {"success": True, "last_login": user.last_login}
