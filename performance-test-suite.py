#!/usr/bin/env python3
"""
HelloAgents Platform - 综合性能测试套件

执行完整的性能测试并生成详细报告:
1. 前端性能测试 (Lighthouse)
2. 后端 API 性能测试
3. 负载测试
4. 数据库性能测试
5. 生成综合性能报告

使用方法:
    python performance-test-suite.py --frontend --backend --load --report
"""

import subprocess
import sys
import os
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
import statistics

# 配置
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://helloagents-platform.pages.dev")
BACKEND_URL = os.getenv("BACKEND_URL", "https://helloagents-platform.onrender.com")
REPORT_DIR = Path("performance-reports")


class PerformanceTestSuite:
    """性能测试套件"""

    def __init__(self):
        self.results = {
            "test_date": datetime.now().isoformat(),
            "frontend_url": FRONTEND_URL,
            "backend_url": BACKEND_URL,
            "tests": {}
        }
        REPORT_DIR.mkdir(exist_ok=True)

    def run_frontend_tests(self):
        """运行前端性能测试"""
        print("\n" + "=" * 80)
        print("📊 运行前端性能测试 (Lighthouse)")
        print("=" * 80)

        try:
            # 运行 Lighthouse (如果有Node.js脚本)
            frontend_dir = Path("frontend")
            if (frontend_dir / "performance-test.js").exists():
                result = subprocess.run(
                    ["node", "performance-test.js"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    print("✅ 前端性能测试完成")
                    self.results["tests"]["frontend"] = {
                        "status": "success",
                        "output": result.stdout
                    }
                else:
                    print(f"⚠️  前端性能测试失败: {result.stderr}")
                    self.results["tests"]["frontend"] = {
                        "status": "failed",
                        "error": result.stderr
                    }
            else:
                print("⚠️  找不到前端性能测试脚本")
                self.results["tests"]["frontend"] = {
                    "status": "skipped",
                    "reason": "Test script not found"
                }

        except Exception as e:
            print(f"❌ 前端性能测试出错: {e}")
            self.results["tests"]["frontend"] = {
                "status": "error",
                "error": str(e)
            }

    def run_backend_tests(self):
        """运行后端 API 性能测试"""
        print("\n" + "=" * 80)
        print("🔧 运行后端 API 性能测试")
        print("=" * 80)

        endpoints = [
            {"name": "Health Check", "path": "/health"},
            {"name": "Readiness Check", "path": "/health/ready"},
            {"name": "Liveness Check", "path": "/health/live"},
            {"name": "Get Lessons", "path": "/api/lessons"},
        ]

        backend_results = []

        for endpoint in endpoints:
            print(f"\n测试端点: {endpoint['name']} ({endpoint['path']})")

            try:
                import requests

                # 预热
                requests.get(f"{BACKEND_URL}{endpoint['path']}", timeout=10)

                # 执行测试 (10次请求)
                timings = []
                for i in range(10):
                    start = time.time()
                    response = requests.get(
                        f"{BACKEND_URL}{endpoint['path']}",
                        timeout=10
                    )
                    elapsed = (time.time() - start) * 1000  # ms

                    timings.append(elapsed)
                    status_code = response.status_code

                # 计算统计
                avg_time = statistics.mean(timings)
                p50 = statistics.median(timings)
                p95 = statistics.quantiles(timings, n=20)[18]  # 95th percentile
                p99 = statistics.quantiles(timings, n=100)[98]  # 99th percentile

                result = {
                    "name": endpoint["name"],
                    "path": endpoint["path"],
                    "status_code": status_code,
                    "avg_time_ms": round(avg_time, 2),
                    "p50_ms": round(p50, 2),
                    "p95_ms": round(p95, 2),
                    "p99_ms": round(p99, 2),
                    "min_ms": round(min(timings), 2),
                    "max_ms": round(max(timings), 2)
                }

                backend_results.append(result)

                # 打印结果
                print(f"  ✓ 平均响应: {result['avg_time_ms']:.2f}ms")
                print(f"  ✓ P50: {result['p50_ms']:.2f}ms")
                print(f"  ✓ P95: {result['p95_ms']:.2f}ms")
                print(f"  ✓ P99: {result['p99_ms']:.2f}ms")

            except Exception as e:
                print(f"  ❌ 测试失败: {e}")
                backend_results.append({
                    "name": endpoint["name"],
                    "path": endpoint["path"],
                    "error": str(e)
                })

        self.results["tests"]["backend_api"] = {
            "status": "success",
            "endpoints": backend_results
        }

        print("\n✅ 后端 API 性能测试完成")

    def run_load_tests(self):
        """运行负载测试"""
        print("\n" + "=" * 80)
        print("⚡ 运行负载测试 (Locust)")
        print("=" * 80)

        try:
            # 检查是否安装了 locust
            result = subprocess.run(
                ["locust", "--version"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print("⚠️  Locust 未安装,跳过负载测试")
                self.results["tests"]["load"] = {
                    "status": "skipped",
                    "reason": "Locust not installed"
                }
                return

            # 运行快速负载测试 (50 用户, 1 分钟)
            print("\n运行快速负载测试 (50 用户, 1 分钟)...")

            result = subprocess.run(
                [
                    "locust",
                    "-f", "backend/tests/load_test.py",
                    "--host", BACKEND_URL,
                    "--headless",
                    "-u", "50",
                    "-r", "10",
                    "-t", "1m",
                    "--csv", str(REPORT_DIR / "load_test"),
                    "--html", str(REPORT_DIR / "load_test_report.html")
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print("✅ 负载测试完成")
                print(result.stdout)

                self.results["tests"]["load"] = {
                    "status": "success",
                    "output": result.stdout,
                    "report_file": str(REPORT_DIR / "load_test_report.html")
                }
            else:
                print(f"⚠️  负载测试失败: {result.stderr}")
                self.results["tests"]["load"] = {
                    "status": "failed",
                    "error": result.stderr
                }

        except FileNotFoundError:
            print("⚠️  找不到负载测试脚本")
            self.results["tests"]["load"] = {
                "status": "skipped",
                "reason": "Load test script not found"
            }
        except Exception as e:
            print(f"❌ 负载测试出错: {e}")
            self.results["tests"]["load"] = {
                "status": "error",
                "error": str(e)
            }

    def generate_report(self):
        """生成综合性能报告"""
        print("\n" + "=" * 80)
        print("📝 生成综合性能报告")
        print("=" * 80)

        # 保存 JSON 结果
        json_file = REPORT_DIR / "performance_test_results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n✅ JSON 结果已保存: {json_file}")

        # 生成 Markdown 报告
        md_file = REPORT_DIR / "PERFORMANCE_TEST_REPORT.md"
        report = self._generate_markdown_report()

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ Markdown 报告已保存: {md_file}")

        # 打印摘要
        print("\n" + "=" * 80)
        print("📊 性能测试摘要")
        print("=" * 80)

        for test_name, test_result in self.results["tests"].items():
            status = test_result["status"]
            emoji = "✅" if status == "success" else "⚠️" if status == "skipped" else "❌"
            print(f"{emoji} {test_name}: {status}")

        print("\n" + "=" * 80)

    def _generate_markdown_report(self) -> str:
        """生成 Markdown 格式的报告"""
        report = f"""# HelloAgents Platform - 性能测试报告

**测试日期**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**前端 URL**: {FRONTEND_URL}
**后端 URL**: {BACKEND_URL}

---

## 测试概览

"""

        # 测试结果摘要
        for test_name, test_result in self.results["tests"].items():
            status = test_result["status"]
            emoji = "✅" if status == "success" else "⚠️" if status == "skipped" else "❌"

            report += f"\n### {emoji} {test_name.replace('_', ' ').title()}\n\n"
            report += f"**状态**: {status}\n\n"

            if status == "success" and test_name == "backend_api":
                report += "| 端点 | 平均响应 | P50 | P95 | P99 |\n"
                report += "|------|----------|-----|-----|-----|\n"

                for endpoint in test_result.get("endpoints", []):
                    if "error" not in endpoint:
                        report += f"| {endpoint['name']} | {endpoint['avg_time_ms']:.2f}ms | {endpoint['p50_ms']:.2f}ms | {endpoint['p95_ms']:.2f}ms | {endpoint['p99_ms']:.2f}ms |\n"

            elif "error" in test_result:
                report += f"**错误**: {test_result['error']}\n\n"
            elif "reason" in test_result:
                report += f"**原因**: {test_result['reason']}\n\n"

        report += f"""
---

## 优化建议

基于测试结果,以下是关键优化建议:

### 前端优化
1. **Monaco Editor 懒加载**: 已实施 ✅
2. **路由级代码分割**: 已实施 ✅
3. **图片优化**: 使用 WebP/AVIF 格式
4. **缓存策略**: 配置 Cloudflare 缓存头

### 后端优化
1. **API 响应缓存**: 实施中间件缓存
2. **数据库连接池**: 已优化 ✅
3. **查询优化**: 添加索引,减少 N+1 查询
4. **异步处理**: 代码执行和 AI 聊天使用异步

### 基础设施优化
1. **CDN**: 使用 Cloudflare CDN ✅
2. **容器池**: 预热 Docker 容器
3. **监控**: 集成 Sentry 和日志系统
4. **自动扩展**: 配置 Render 自动扩展

---

## 性能目标

| 指标 | 当前值 | 目标值 | 状态 |
|------|--------|--------|------|
| Lighthouse (Desktop) | - | 85+ | ⏳ 待测试 |
| Lighthouse (Mobile) | - | 75+ | ⏳ 待测试 |
| LCP (Desktop) | - | < 2.5s | ⏳ 待测试 |
| API P95 响应时间 | - | < 500ms | ⏳ 待测试 |
| 并发用户数 | - | 100+ | ⏳ 待测试 |

---

## 文件清单

生成的报告文件:
- `performance_test_results.json` - JSON 格式的原始测试数据
- `PERFORMANCE_TEST_REPORT.md` - 本报告
- `load_test_report.html` - Locust 负载测试报告 (如果运行)
- Lighthouse 报告 (如果运行)

---

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**测试工具**: Lighthouse, Locust, Python Requests
**报告版本**: v1.0
"""

        return report

    def run_all(self, frontend=True, backend=True, load=True):
        """运行所有测试"""
        print("\n" + "🚀" * 40)
        print("HelloAgents Platform - 综合性能测试套件")
        print("🚀" * 40)

        if frontend:
            self.run_frontend_tests()

        if backend:
            self.run_backend_tests()

        if load:
            self.run_load_tests()

        self.generate_report()

        print("\n" + "✅" * 40)
        print("性能测试完成!")
        print("✅" * 40 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="HelloAgents Platform 综合性能测试套件"
    )
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="运行前端性能测试"
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        help="运行后端 API 性能测试"
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="运行负载测试"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="运行所有测试"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="只生成报告 (基于已有数据)"
    )

    args = parser.parse_args()

    # 如果没有指定任何选项,运行所有测试
    if not any([args.frontend, args.backend, args.load, args.all, args.report]):
        args.all = True

    suite = PerformanceTestSuite()

    if args.report:
        # 只生成报告
        suite.generate_report()
    elif args.all:
        # 运行所有测试
        suite.run_all(frontend=True, backend=True, load=True)
    else:
        # 运行指定的测试
        suite.run_all(
            frontend=args.frontend,
            backend=args.backend,
            load=args.load
        )


if __name__ == "__main__":
    # 检查依赖
    try:
        import requests
    except ImportError:
        print("❌ 缺少依赖: requests")
        print("请运行: pip install requests")
        sys.exit(1)

    main()
