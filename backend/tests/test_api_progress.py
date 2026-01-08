"""
测试学习进度 API
"""
import pytest


def test_create_progress(client, sample_user, sample_lesson):
    """测试创建学习进度"""
    response = client.post("/api/progress/", json={
        "user_id": sample_user.id,
        "lesson_id": sample_lesson.id,
        "current_code": "print('test')",
        "cursor_position": {"line": 1, "column": 1}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == sample_user.id
    assert data["lesson_id"] == sample_lesson.id
    assert data["completed"] == 0


def test_update_progress(client, sample_progress):
    """测试更新学习进度"""
    response = client.put(
        f"/api/progress/user/{sample_progress.user_id}/lesson/{sample_progress.lesson_id}",
        json={
            "current_code": "print('updated')",
            "completed": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_code"] == "print('updated')"
    assert data["completed"] == 1


def test_complete_lesson(client, sample_progress):
    """测试标记课程完成"""
    response = client.post(
        f"/api/progress/user/{sample_progress.user_id}/lesson/{sample_progress.lesson_id}/complete"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] == 1
    assert data["completed_at"] is not None


def test_get_user_progress(client, sample_progress):
    """测试获取用户所有进度"""
    response = client.get(f"/api/progress/user/{sample_progress.user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_recent_progress(client, sample_progress):
    """测试获取最近学习的课程"""
    response = client.get(f"/api/progress/user/{sample_progress.user_id}/recent?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_progress_stats(client, sample_progress):
    """测试获取学习统计"""
    response = client.get(f"/api/progress/user/{sample_progress.user_id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_lessons" in data
    assert "started_lessons" in data
    assert "completed_lessons" in data
    assert "completion_rate" in data


def test_get_specific_lesson_progress(client, sample_progress):
    """测试获取特定课程进度"""
    response = client.get(
        f"/api/progress/user/{sample_progress.user_id}/lesson/{sample_progress.lesson_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == sample_progress.user_id
    assert data["lesson_id"] == sample_progress.lesson_id


def test_get_nonexistent_progress(client, sample_user):
    """测试获取不存在的进度"""
    response = client.get(f"/api/progress/user/{sample_user.id}/lesson/9999")
    assert response.status_code == 404
