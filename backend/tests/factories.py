"""
测试数据工厂函数
使用 Faker 生成测试数据
"""
import random
import string
from datetime import datetime, timedelta
from typing import Optional

# 简化的 faker 替代方案（如果需要更强大的功能，可以安装 faker 库）
# 对于基本测试，这些简单的生成器已经足够


class SimpleFaker:
    """简单的测试数据生成器"""

    @staticmethod
    def username(prefix: str = "user") -> str:
        """生成用户名"""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}_{suffix}"

    @staticmethod
    def full_name() -> str:
        """生成全名"""
        first_names = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @staticmethod
    def email(username: Optional[str] = None) -> str:
        """生成邮箱"""
        if not username:
            username = SimpleFaker.username()
        domains = ["example.com", "test.com", "demo.com"]
        return f"{username}@{random.choice(domains)}"

    @staticmethod
    def sentence(words: int = 6) -> str:
        """生成句子"""
        word_list = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
                     "cat", "mouse", "bird", "fish", "code", "test", "data", "function"]
        return ' '.join(random.choices(word_list, k=words)).capitalize() + '.'

    @staticmethod
    def paragraph(sentences: int = 3) -> str:
        """生成段落"""
        return ' '.join([SimpleFaker.sentence() for _ in range(sentences)])

    @staticmethod
    def code(lines: int = 3) -> str:
        """生成代码片段"""
        code_samples = [
            "def hello():",
            "    print('Hello, World!')",
            "x = 42",
            "y = x + 10",
            "for i in range(10):",
            "    print(i)",
            "if x > 0:",
            "    return True",
        ]
        return '\n'.join(random.sample(code_samples, min(lines, len(code_samples))))

    @staticmethod
    def date_recent(days: int = 30) -> datetime:
        """生成最近的日期"""
        return datetime.utcnow() - timedelta(days=random.randint(0, days))

    @staticmethod
    def integer(min_val: int = 1, max_val: int = 1000) -> int:
        """生成整数"""
        return random.randint(min_val, max_val)

    @staticmethod
    def float_number(min_val: float = 0.0, max_val: float = 10.0, decimals: int = 3) -> float:
        """生成浮点数"""
        value = random.uniform(min_val, max_val)
        return round(value, decimals)

    @staticmethod
    def choice(choices: list):
        """从列表中随机选择"""
        return random.choice(choices)


faker = SimpleFaker()


def create_user_data(db_session, **overrides):
    """
    创建用户测试数据
    """
    from app.models.user import User
    import json

    default_data = {
        "username": faker.username(),
        "full_name": faker.full_name(),
        "settings": json.dumps({
            "theme": faker.choice(["light", "dark"]),
            "editor": {
                "fontSize": faker.choice([12, 14, 16, 18]),
                "tabSize": faker.choice([2, 4]),
            }
        })
    }

    data = {**default_data, **overrides}

    user = User(**data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_lesson_data(db_session, **overrides):
    """
    创建课程测试数据
    """
    from app.models.lesson import Lesson

    default_data = {
        "chapter_number": faker.integer(1, 5),
        "lesson_number": faker.integer(1, 10),
        "title": faker.sentence(),
        "content": f"# {faker.sentence()}\n\n{faker.paragraph()}",
        "starter_code": faker.code(),
        "extra_data": f'{{"difficulty": "{faker.choice(["easy", "medium", "hard"])}"}}',
    }

    data = {**default_data, **overrides}

    lesson = Lesson(**data)
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)

    return lesson


def create_progress_data(db_session, user_id: int = None, lesson_id: int = None, **overrides):
    """
    创建学习进度测试数据
    """
    from app.models.user_progress import UserProgress

    # 如果没有提供 user_id 或 lesson_id，自动创建
    if user_id is None:
        user = create_user_data(db_session)
        user_id = user.id

    if lesson_id is None:
        lesson = create_lesson_data(db_session)
        lesson_id = lesson.id

    default_data = {
        "user_id": user_id,
        "lesson_id": lesson_id,
        "completed": faker.choice([0, 1]),
        "current_code": faker.code(),
    }

    data = {**default_data, **overrides}

    progress = UserProgress(**data)
    db_session.add(progress)
    db_session.commit()
    db_session.refresh(progress)

    return progress


def create_submission_data(db_session, user_id: int = None, lesson_id: int = None, **overrides):
    """
    创建代码提交测试数据
    """
    from app.models.code_submission import CodeSubmission

    # 如果没有提供 user_id 或 lesson_id，自动创建
    if user_id is None:
        user = create_user_data(db_session)
        user_id = user.id

    if lesson_id is None:
        lesson = create_lesson_data(db_session)
        lesson_id = lesson.id

    status = faker.choice(['success', 'error'])

    default_data = {
        "user_id": user_id,
        "lesson_id": lesson_id,
        "code": faker.code(),
        "status": status,  # 使用 status 而不是 success
        "output": faker.paragraph() if status == 'success' else f"Error: {faker.sentence()}",
        "execution_time": faker.float_number(0.001, 5.0, 3),
    }

    data = {**default_data, **overrides}

    submission = CodeSubmission(**data)
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)

    return submission


def create_chat_message_data(db_session, user_id: int = None, lesson_id: int = None, **overrides):
    """
    创建聊天消息测试数据
    """
    from app.models.chat_message import ChatMessage

    # 如果没有提供 user_id，自动创建
    if user_id is None:
        user = create_user_data(db_session)
        user_id = user.id

    default_data = {
        "user_id": user_id,
        "lesson_id": lesson_id,  # 可以为 None
        "role": faker.choice(['user', 'assistant']),
        "content": faker.sentence(10),
        "extra_data": '{}',
    }

    data = {**default_data, **overrides}

    chat_message = ChatMessage(**data)
    db_session.add(chat_message)
    db_session.commit()
    db_session.refresh(chat_message)

    return chat_message


def create_multiple(factory_func, count: int, db_session, **kwargs):
    """
    批量创建测试数据

    示例:
        users = create_multiple(create_user_data, 5, db_session)
    """
    return [factory_func(db_session, **kwargs) for _ in range(count)]


# 预设场景数据
class MockScenarios:
    """预设的测试场景"""

    @staticmethod
    def new_user(db_session):
        """新用户场景"""
        return create_user_data(
            db_session,
            username="new_user",
            full_name="New User"
        )

    @staticmethod
    def experienced_user_with_progress(db_session):
        """有学习进度的用户"""
        user = create_user_data(
            db_session,
            username="experienced_user",
            full_name="Experienced User"
        )

        # 创建多个已完成的课程
        for i in range(1, 4):
            lesson = create_lesson_data(
                db_session,
                chapter_number=1,
                lesson_number=i,
                title=f"Lesson 1.{i}"
            )
            create_progress_data(
                db_session,
                user_id=user.id,
                lesson_id=lesson.id,
                completed=1
            )

        return user

    @staticmethod
    def first_lesson(db_session):
        """第一课"""
        return create_lesson_data(
            db_session,
            chapter_number=1,
            lesson_number=1,
            title="Introduction to Programming",
            content="# Welcome\n\nLearn the basics of programming."
        )

    @staticmethod
    def successful_submission(db_session, user_id: int = None, lesson_id: int = None):
        """成功的代码提交"""
        return create_submission_data(
            db_session,
            user_id=user_id,
            lesson_id=lesson_id,
            status='success',
            output="Hello, World!",
            execution_time=0.123
        )

    @staticmethod
    def failed_submission(db_session, user_id: int = None, lesson_id: int = None):
        """失败的代码提交"""
        return create_submission_data(
            db_session,
            user_id=user_id,
            lesson_id=lesson_id,
            status='error',
            output="Error: SyntaxError: invalid syntax",
            execution_time=0.001
        )
