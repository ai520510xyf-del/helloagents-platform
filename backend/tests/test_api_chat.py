"""
Chat API 测试

测试聊天消息管理相关的 API 端点
"""
import pytest
import json


def test_create_chat_message(client, sample_user, sample_lesson):
    """测试创建聊天消息"""
    response = client.post(
        "/api/chat-history/",
        json={
            "user_id": sample_user.id,
            "lesson_id": sample_lesson.id,
            "role": "user",
            "content": "Hello, I need help with this lesson",
            "metadata": {"context": "lesson_1"}
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == sample_user.id
    assert data["lesson_id"] == sample_lesson.id
    assert data["role"] == "user"
    assert data["content"] == "Hello, I need help with this lesson"
    assert "id" in data
    assert "created_at" in data


def test_create_message_invalid_role(client, sample_user):
    """测试创建消息时使用无效的角色"""
    response = client.post(
        "/api/chat-history/",
        json={
            "user_id": sample_user.id,
            "role": "invalid_role",
            "content": "Test message"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "Invalid role" in data["error"]["message"]


def test_create_message_without_lesson(client, sample_user):
    """测试创建消息时不指定课程"""
    response = client.post(
        "/api/chat-history/",
        json={
            "user_id": sample_user.id,
            "role": "assistant",
            "content": "I can help you with that"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["lesson_id"] is None


def test_get_user_messages(client, sample_user, sample_lesson):
    """测试获取用户的所有聊天消息"""
    # 创建多条消息
    for i in range(3):
        client.post(
            "/api/chat-history/",
            json={
                "user_id": sample_user.id,
                "lesson_id": sample_lesson.id,
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i}"
            }
        )

    # 获取消息
    response = client.get(f"/api/chat-history/user/{sample_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(msg["user_id"] == sample_user.id for msg in data)


def test_get_user_messages_with_limit(client, sample_user):
    """测试获取用户消息时使用限制数量"""
    # 创建5条消息
    for i in range(5):
        client.post(
            "/api/chat-history/",
            json={
                "user_id": sample_user.id,
                "role": "user",
                "content": f"Message {i}"
            }
        )

    # 限制返回2条
    response = client.get(f"/api/chat-history/user/{sample_user.id}?limit=2")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_lesson_messages(client, sample_user, sample_lesson):
    """测试获取特定课程的聊天历史"""
    # 创建课程相关消息
    client.post(
        "/api/chat-history/",
        json={
            "user_id": sample_user.id,
            "lesson_id": sample_lesson.id,
            "role": "user",
            "content": "Question about this lesson"
        }
    )

    client.post(
        "/api/chat-history/",
        json={
            "user_id": sample_user.id,
            "lesson_id": sample_lesson.id,
            "role": "assistant",
            "content": "Here's the answer"
        }
    )

    # 获取课程消息
    response = client.get(
        f"/api/chat-history/user/{sample_user.id}/lesson/{sample_lesson.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(msg["lesson_id"] == sample_lesson.id for msg in data)


def test_delete_lesson_messages(client, sample_user, sample_lesson):
    """测试删除特定课程的聊天历史"""
    # 创建消息
    for i in range(3):
        client.post(
            "/api/chat-history/",
            json={
                "user_id": sample_user.id,
                "lesson_id": sample_lesson.id,
                "role": "user",
                "content": f"Message {i}"
            }
        )

    # 删除消息
    response = client.delete(
        f"/api/chat-history/user/{sample_user.id}/lesson/{sample_lesson.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["deleted_count"] == 3

    # 验证消息已被删除
    get_response = client.get(
        f"/api/chat-history/user/{sample_user.id}/lesson/{sample_lesson.id}"
    )
    assert len(get_response.json()) == 0


def test_get_chat_stats(client, sample_user, sample_lesson):
    """测试获取聊天统计信息"""
    # 创建不同角色的消息
    messages = [
        {"role": "user", "content": "Question 1"},
        {"role": "assistant", "content": "Answer 1"},
        {"role": "user", "content": "Question 2"},
        {"role": "assistant", "content": "Answer 2"},
        {"role": "system", "content": "System message"},
    ]

    for msg in messages:
        client.post(
            "/api/chat-history/",
            json={
                "user_id": sample_user.id,
                "lesson_id": sample_lesson.id,
                **msg
            }
        )

    # 获取统计
    response = client.get(f"/api/chat-history/user/{sample_user.id}/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total_messages"] == 5
    assert data["user_messages"] == 2
    assert data["assistant_messages"] == 2
    assert data["conversation_count"] == 2


def test_get_chat_stats_no_messages(client, sample_user):
    """测试获取没有消息的用户的统计信息"""
    response = client.get(f"/api/chat-history/user/{sample_user.id}/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total_messages"] == 0
    assert data["user_messages"] == 0
    assert data["assistant_messages"] == 0
    assert data["conversation_count"] == 0
