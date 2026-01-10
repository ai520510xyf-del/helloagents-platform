"""
后端 API 负载测试脚本

使用 Locust 进行负载测试,模拟真实用户行为:
- 获取课程列表
- 查看课程内容
- 执行代码
- AI 聊天

运行方式:
1. 命令行模式: locust -f tests/load_test.py --host=http://localhost:8000
2. Web UI 模式: locust -f tests/load_test.py --host=http://localhost:8000 --web-port=8089
3. 无头模式: locust -f tests/load_test.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 5m
"""

from locust import HttpUser, task, between, events
import random
import json
from datetime import datetime


class HelloAgentsUser(HttpUser):
    """
    模拟 HelloAgents 平台用户

    行为模式:
    - 访问课程列表 (权重: 30%)
    - 查看课程内容 (权重: 25%)
    - 执行代码 (权重: 20%)
    - 健康检查 (权重: 15%)
    - AI 聊天 (权重: 10%)
    """

    # 用户请求间隔时间 (秒)
    wait_time = between(1, 3)

    # 可用的课程 ID
    lesson_ids = ["1", "2", "3", "4", "5"]

    # 示例 Python 代码
    sample_codes = [
        "print('Hello, World!')",
        "result = 1 + 1\nprint(result)",
        "for i in range(5):\n    print(i)",
        "def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('Agent'))",
    ]

    def on_start(self):
        """用户开始时执行 (模拟用户登录/初始化)"""
        self.lesson_id = random.choice(self.lesson_ids)
        self.user_id = random.randint(1, 1000)

    @task(30)
    def get_lessons(self):
        """获取课程列表"""
        with self.client.get(
            "/api/lessons",
            catch_response=True,
            name="/api/lessons [GET]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "lessons" in data or "success" in data:
                        response.success()
                    else:
                        response.failure(f"Unexpected response format: {data}")
                except json.JSONDecodeError:
                    response.failure("Response is not valid JSON")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(25)
    def get_lesson_content(self):
        """获取单个课程内容"""
        lesson_id = random.choice(self.lesson_ids)

        with self.client.get(
            f"/api/lessons/{lesson_id}",
            catch_response=True,
            name="/api/lessons/{id} [GET]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "lesson_id" in data and "content" in data:
                        response.success()
                    else:
                        response.failure(f"Missing expected fields in response")
                except json.JSONDecodeError:
                    response.failure("Response is not valid JSON")
            elif response.status_code == 404:
                response.success()  # 404 是预期的错误
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(20)
    def execute_code(self):
        """执行 Python 代码"""
        code = random.choice(self.sample_codes)

        with self.client.post(
            "/api/execute",
            json={
                "code": code,
                "language": "python",
                "timeout": 30
            },
            catch_response=True,
            name="/api/execute [POST]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "success" in data and "output" in data:
                        response.success()
                    else:
                        response.failure(f"Missing expected fields")
                except json.JSONDecodeError:
                    response.failure("Response is not valid JSON")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(15)
    def health_check(self):
        """健康检查"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health [GET]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "status" in data:
                        response.success()
                    else:
                        response.failure("Missing 'status' field")
                except json.JSONDecodeError:
                    response.failure("Response is not valid JSON")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(10)
    def chat_with_ai(self):
        """AI 聊天 (需要 DEEPSEEK_API_KEY)"""
        messages = [
            "什么是 ReAct Agent?",
            "如何实现一个简单的 Agent?",
            "Tool Calling 是什么意思?",
            "能给我讲讲 Agent 的历史吗?",
        ]

        with self.client.post(
            "/api/chat",
            json={
                "message": random.choice(messages),
                "conversation_history": [],
                "lesson_id": self.lesson_id,
                "code": None
            },
            catch_response=True,
            name="/api/chat [POST]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "message" in data:
                        response.success()
                    else:
                        response.failure("Missing 'message' field")
                except json.JSONDecodeError:
                    response.failure("Response is not valid JSON")
            else:
                # AI API 可能未配置,忽略错误
                response.success()


class QuickUser(HttpUser):
    """
    快速测试用户 (只测试关键端点)

    用于快速健康检查和基本功能验证
    """

    wait_time = between(0.5, 1)

    @task(50)
    def health(self):
        """健康检查"""
        self.client.get("/health", name="[Quick] /health")

    @task(30)
    def get_lessons(self):
        """获取课程列表"""
        self.client.get("/api/lessons", name="[Quick] /api/lessons")

    @task(20)
    def readiness(self):
        """就绪检查"""
        self.client.get("/health/ready", name="[Quick] /health/ready")


# Locust 事件监听器 - 用于自定义统计
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时执行"""
    print("\n" + "=" * 80)
    print("🚀 HelloAgents Platform - 负载测试开始")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标主机: {environment.host}")
    print("=" * 80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时执行"""
    print("\n" + "=" * 80)
    print("✅ HelloAgents Platform - 负载测试完成")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 获取统计信息
    stats = environment.stats
    print(f"\n总请求数: {stats.num_requests}")
    print(f"失败请求: {stats.num_failures}")
    print(f"失败率: {stats.num_failures / max(stats.num_requests, 1) * 100:.2f}%")
    print(f"平均响应时间: {stats.total.avg_response_time:.2f}ms")
    print(f"P50 响应时间: {stats.total.get_response_time_percentile(0.5):.2f}ms")
    print(f"P95 响应时间: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"P99 响应时间: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"RPS: {stats.total.current_rps:.2f} req/s")

    print("=" * 80 + "\n")


# 性能基准测试场景
class PerformanceBenchmark(HelloAgentsUser):
    """
    性能基准测试场景

    用于建立性能基准:
    - 测量各端点的响应时间
    - 识别性能瓶颈
    - 验证优化效果
    """

    wait_time = between(0.1, 0.5)  # 更快的请求间隔

    @task
    def benchmark_flow(self):
        """完整的用户流程基准测试"""
        # 1. 获取课程列表
        self.client.get("/api/lessons")

        # 2. 查看课程内容
        lesson_id = random.choice(self.lesson_ids)
        self.client.get(f"/api/lessons/{lesson_id}")

        # 3. 执行简单代码
        self.client.post(
            "/api/execute",
            json={
                "code": "print('benchmark test')",
                "language": "python",
                "timeout": 5
            }
        )


if __name__ == "__main__":
    """
    使用说明:

    1. 基本负载测试 (Web UI):
       locust -f tests/load_test.py --host=http://localhost:8000

    2. 无头模式 (100 用户, 每秒启动 10 个, 运行 5 分钟):
       locust -f tests/load_test.py --host=http://localhost:8000 \\
              --headless -u 100 -r 10 -t 5m

    3. 压力测试 (500 用户, 快速启动):
       locust -f tests/load_test.py --host=http://localhost:8000 \\
              --headless -u 500 -r 50 -t 10m

    4. 只测试关键端点 (QuickUser):
       locust -f tests/load_test.py --host=http://localhost:8000 \\
              QuickUser --headless -u 50 -r 10 -t 2m

    5. 性能基准测试:
       locust -f tests/load_test.py --host=http://localhost:8000 \\
              PerformanceBenchmark --headless -u 20 -r 5 -t 3m

    6. 生产环境测试:
       locust -f tests/load_test.py \\
              --host=https://helloagents-platform.onrender.com \\
              --headless -u 50 -r 5 -t 5m

    参数说明:
    - -u, --users: 并发用户数
    - -r, --spawn-rate: 每秒启动的用户数
    - -t, --run-time: 测试运行时间 (如 5m, 1h, 30s)
    - --headless: 无 Web UI 模式
    - --csv: 导出 CSV 结果
    - --html: 导出 HTML 报告
    """
    print(__doc__)
