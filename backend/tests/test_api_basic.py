"""
测试基础 API 端点
"""
import pytest


def test_root_endpoint(client):
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_get_all_lessons(client):
    """测试获取所有课程列表"""
    response = client.get("/api/lessons")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "lessons" in data


def test_get_lesson_content(client, sample_lesson):
    """测试获取课程内容"""
    # 使用实际存在的课程 ID
    response = client.get("/api/lessons/1")
    assert response.status_code == 200
    data = response.json()
    assert "lesson_id" in data
    assert "title" in data
    assert "content" in data


def test_get_nonexistent_lesson(client):
    """测试获取不存在的课程"""
    response = client.get("/api/lessons/9999")
    assert response.status_code == 404


def test_execute_code_success(client):
    """测试成功执行代码"""
    response = client.post("/api/execute", json={
        "code": "print('Hello, World!')",
        "language": "python",
        "timeout": 30
    })
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "output" in data
    assert "execution_time" in data


def test_execute_code_with_error(client):
    """测试执行有错误的代码"""
    response = client.post("/api/execute", json={
        "code": "print(undefined_variable)",
        "language": "python",
        "timeout": 30
    })
    assert response.status_code == 200
    data = response.json()
    # 可能成功但有错误信息，或者 success=False
    assert "output" in data or "error" in data
