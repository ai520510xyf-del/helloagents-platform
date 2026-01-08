"""
测试数据迁移 API
"""
import pytest


def test_migration_example_endpoint(client):
    """测试迁移示例端点"""
    response = client.get("/api/migrate/example")
    assert response.status_code == 200
    data = response.json()
    assert "example_request" in data
    assert "description" in data


def test_migrate_empty_data(client):
    """测试迁移空数据"""
    response = client.post("/api/migrate/", json={
        "username": "empty_user",
        "progress_list": [],
        "last_code": {},
        "chat_history": []
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["migrated_progress"] == 0


def test_migrate_progress_only(client, sample_lesson):
    """测试仅迁移学习进度"""
    response = client.post("/api/migrate/", json={
        "username": "progress_user",
        "progress_list": [
            {
                "chapter": sample_lesson.chapter_number,
                "lesson": sample_lesson.lesson_number,
                "completed": True,
                "code": "print('test')"
            }
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["migrated_progress"] > 0


def test_migrate_with_chat_history(client, sample_lesson):
    """测试迁移聊天历史"""
    response = client.post("/api/migrate/", json={
        "username": "chat_user",
        "chat_history": [
            {
                "lesson_key": f"{sample_lesson.chapter_number}-{sample_lesson.lesson_number}",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"}
                ]
            }
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["migrated_chat_messages"] > 0


def test_migrate_complete_data(client, sample_lesson):
    """测试迁移完整数据"""
    response = client.post("/api/migrate/", json={
        "username": "complete_user",
        "progress_list": [
            {
                "chapter": sample_lesson.chapter_number,
                "lesson": sample_lesson.lesson_number,
                "completed": False
            }
        ],
        "last_code": {
            f"{sample_lesson.chapter_number}-{sample_lesson.lesson_number}": "print('code')"
        },
        "chat_history": [
            {
                "lesson_key": f"{sample_lesson.chapter_number}-{sample_lesson.lesson_number}",
                "messages": [
                    {"role": "user", "content": "Test"}
                ]
            }
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["migrated_progress"] > 0
    assert data["migrated_submissions"] > 0
    assert data["migrated_chat_messages"] > 0


def test_migrate_creates_user_if_not_exists(client):
    """测试迁移时自动创建不存在的用户"""
    response = client.post("/api/migrate/", json={
        "username": "new_migrated_user",
        "progress_list": []
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user_id"] > 0

    # 验证用户已创建
    user_response = client.get(f"/api/users/{data['user_id']}")
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data["username"] == "new_migrated_user"


def test_migrate_with_invalid_lesson_key(client):
    """测试使用无效课程键迁移"""
    response = client.post("/api/migrate/", json={
        "username": "invalid_user",
        "progress_list": [
            {
                "chapter": 999,
                "lesson": 999,
                "completed": False
            }
        ]
    })
    # 应该创建占位符课程或跳过
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
