"""
测试用户管理 API
"""
import pytest
import json


def test_get_current_user_auto_create(client):
    """测试获取当前用户（自动创建）"""
    response = client.get("/api/users/current")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "local_user"
    assert data["full_name"] == "本地用户"
    assert "settings" in data


def test_create_user(client):
    """测试创建用户"""
    response = client.post("/api/users/", json={
        "username": "new_user",
        "full_name": "New User",
        "settings": {"theme": "light"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "new_user"
    assert data["full_name"] == "New User"
    assert data["settings"]["theme"] == "light"


def test_create_duplicate_user(client, sample_user):
    """测试创建重复用户"""
    response = client.post("/api/users/", json={
        "username": sample_user.username,
        "full_name": "Duplicate"
    })
    assert response.status_code == 400


def test_get_user_by_id(client, sample_user):
    """测试根据 ID 获取用户"""
    response = client.get(f"/api/users/{sample_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_user.id
    assert data["username"] == sample_user.username


def test_get_nonexistent_user(client):
    """测试获取不存在的用户"""
    response = client.get("/api/users/9999")
    assert response.status_code == 404


def test_update_user(client, sample_user):
    """测试更新用户信息"""
    response = client.put(f"/api/users/{sample_user.id}", json={
        "full_name": "Updated Name",
        "settings": {"theme": "light", "fontSize": 16}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["settings"]["theme"] == "light"


def test_record_login(client, sample_user):
    """测试记录登录时间"""
    response = client.post(f"/api/users/{sample_user.id}/login")
    assert response.status_code == 200
    data = response.json()
    assert data["last_login"] is not None
