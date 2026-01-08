"""
HelloAgents 负载测试脚本 (Locust)

模拟真实用户行为，测试系统在不同负载下的表现

运行方法:
  # 启动 Web UI (推荐)
  locust -f locustfile.py --host=http://localhost:8000

  # 无头模式（命令行）
  locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 5m

  # 生成报告
  locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 5m --html=report.html --csv=results

参数说明:
  -u, --users: 模拟用户数
  -r, --spawn-rate: 每秒生成用户数
  -t, --run-time: 运行时长
  --host: 目标服务器地址
"""

from locust import HttpUser, task, between, SequentialTaskSet
from faker import Faker
import random
import json

fake = Faker()


class LearningBehavior(SequentialTaskSet):
    """
    顺序学习行为模式

    模拟学生的完整学习流程:
    1. 获取课程列表
    2. 选择课程
    3. 查看课程详情
    4. 编写代码
    5. 执行代码
    6. 保存进度
    """

    def on_start(self):
        """用户开始学习前的初始化"""
        self.user_id = random.randint(1, 1000)
        self.current_lesson_id = None

    @task
    def browse_lessons(self):
        """浏览课程列表"""
        with self.client.get(
            "/api/v1/lessons",
            name="GET /api/v1/lessons (浏览课程)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                lessons = response.json()
                if lessons:
                    # 选择一个课程
                    self.current_lesson_id = random.choice(lessons)['id']
                    response.success()
                else:
                    response.failure("没有课程数据")
            else:
                response.failure(f"状态码: {response.status_code}")

    @task
    def view_lesson_detail(self):
        """查看课程详情"""
        if not self.current_lesson_id:
            self.current_lesson_id = random.randint(1, 20)

        with self.client.get(
            f"/api/v1/lessons/{self.current_lesson_id}",
            name="GET /api/v1/lessons/{id} (课程详情)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.failure("课程不存在")
            else:
                response.failure(f"状态码: {response.status_code}")

    @task
    def write_and_execute_code(self):
        """编写并执行代码"""
        # 模拟不同复杂度的代码
        code_samples = [
            # 简单代码
            "print('Hello, World!')",
            "x = 1 + 2\nprint(x)",

            # 中等复杂度
            """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

print(factorial(5))
""",

            # 较复杂
            """
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n-1):
        a, b = b, a + b
    return b

for i in range(10):
    print(fibonacci(i))
""",
        ]

        code = random.choice(code_samples)

        with self.client.post(
            "/api/v1/code/execute",
            json={
                "code": code,
                "language": "python",
                "timeout": 30
            },
            name="POST /api/v1/code/execute (执行代码)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    response.success()
                else:
                    # 代码执行失败不算系统错误
                    response.success()
            else:
                response.failure(f"状态码: {response.status_code}")

    @task
    def save_progress(self):
        """保存学习进度"""
        if not self.current_lesson_id:
            return

        with self.client.post(
            "/api/v1/progress",
            json={
                "user_id": self.user_id,
                "lesson_id": self.current_lesson_id,
                "completed": random.choice([0, 1]),
                "current_code": "print('progress saved')"
            },
            name="POST /api/v1/progress (保存进度)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"状态码: {response.status_code}")

    @task
    def get_progress(self):
        """查询学习进度"""
        with self.client.get(
            f"/api/v1/progress?user_id={self.user_id}",
            name="GET /api/v1/progress (查询进度)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"状态码: {response.status_code}")


class CodeExecutionUser(HttpUser):
    """
    代码执行用户

    专注于代码执行功能的负载测试
    """
    wait_time = between(2, 5)  # 用户操作间隔 2-5 秒
    weight = 3  # 权重：70% 的流量

    @task(5)
    def execute_simple_code(self):
        """执行简单代码（高频）"""
        self.client.post(
            "/api/v1/code/execute",
            json={
                "code": "print('Hello, World!')",
                "language": "python"
            },
            name="执行简单代码"
        )

    @task(3)
    def execute_medium_code(self):
        """执行中等复杂度代码"""
        code = """
def sum_list(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = sum_list([1, 2, 3, 4, 5])
print(f"Sum: {result}")
"""
        self.client.post(
            "/api/v1/code/execute",
            json={
                "code": code,
                "language": "python"
            },
            name="执行中等代码"
        )

    @task(1)
    def execute_complex_code(self):
        """执行复杂代码（低频）"""
        code = """
class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

calc = Calculator()
print(calc.add(10, 20))
print(calc.multiply(5, 6))
print("History:", calc.history)
"""
        self.client.post(
            "/api/v1/code/execute",
            json={
                "code": code,
                "language": "python"
            },
            name="执行复杂代码"
        )

    @task(2)
    def get_ai_hint(self):
        """获取 AI 提示"""
        self.client.post(
            "/api/v1/code/hint",
            json={
                "code": "def __init__(self, llm_client, tool_executor):\n    ",
                "cursor_line": 1,
                "cursor_column": 4,
                "language": "python"
            },
            name="获取 AI 提示"
        )


class BrowsingUser(HttpUser):
    """
    浏览用户

    主要浏览课程内容，偶尔执行代码
    """
    wait_time = between(3, 8)  # 浏览间隔较长
    weight = 1  # 权重：30% 的流量

    @task(5)
    def browse_lessons(self):
        """浏览课程列表"""
        self.client.get("/api/v1/lessons", name="浏览课程")

    @task(3)
    def view_lesson_detail(self):
        """查看课程详情"""
        lesson_id = random.randint(1, 20)
        self.client.get(f"/api/v1/lessons/{lesson_id}", name="课程详情")

    @task(1)
    def try_code_execution(self):
        """偶尔执行代码"""
        self.client.post(
            "/api/v1/code/execute",
            json={
                "code": "print('试试看')",
                "language": "python"
            },
            name="尝试执行代码"
        )


class LearningUser(HttpUser):
    """
    学习用户

    按照完整的学习流程进行操作
    """
    tasks = [LearningBehavior]
    wait_time = between(1, 3)
    weight = 2  # 权重：占比适中


class StressTestUser(HttpUser):
    """
    压力测试用户

    用于压力测试，高频执行代码
    """
    wait_time = between(0.5, 1)  # 高频操作

    @task
    def stress_execute(self):
        """高频代码执行"""
        self.client.post(
            "/api/v1/code/execute",
            json={
                "code": f"print({random.randint(1, 1000)})",
                "language": "python"
            },
            name="压力测试执行"
        )


# ============================================
# 自定义事件监听器
# ============================================

from locust import events

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时触发"""
    print("\n" + "="*60)
    print("HelloAgents 负载测试开始")
    print(f"目标服务器: {environment.host}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时触发"""
    print("\n" + "="*60)
    print("HelloAgents 负载测试完成")
    print("="*60 + "\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """每次请求后触发（用于自定义监控）"""
    # 检测慢请求
    if response_time > 1000:  # > 1s
        print(f"⚠️  慢请求: {name} - {response_time:.0f}ms")


# ============================================
# 使用示例
# ============================================

"""
负载测试场景示例:

1. 基准测试 (10 用户，持续 2 分钟)
   locust -f locustfile.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 2m

2. 负载测试 (100 用户，持续 5 分钟)
   locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 5m

3. 压力测试 (500 用户，快速增长)
   locust -f locustfile.py --host=http://localhost:8000 --headless -u 500 -r 50 -t 10m

4. 峰值测试 (1000 用户突发)
   locust -f locustfile.py --host=http://localhost:8000 --headless -u 1000 -r 200 -t 2m

5. 耐久测试 (50 用户，持续 1 小时)
   locust -f locustfile.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 1h

6. 使用 Web UI (推荐)
   locust -f locustfile.py --host=http://localhost:8000
   然后访问: http://localhost:8089

性能目标:
  - 响应时间 (P95): < 500ms
  - 吞吐量: > 100 RPS
  - 错误率: < 1%
  - 并发容器池: 支持 100 并发执行
"""
