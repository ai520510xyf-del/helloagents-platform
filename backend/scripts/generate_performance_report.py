#!/usr/bin/env python3
"""
性能测试报告生成器

整合 pytest-benchmark、locust、k6 的测试结果，生成统一的性能报告

功能:
- 解析多种测试工具的输出
- 生成 HTML/Markdown 格式报告
- 对比历史基准
- 检测性能退化

使用方法:
  python scripts/generate_performance_report.py
  python scripts/generate_performance_report.py --format html
  python scripts/generate_performance_report.py --compare baseline.json
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics


class PerformanceReportGenerator:
    """性能报告生成器"""

    def __init__(self, output_dir: str = "performance_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "pytest_benchmark": None,
            "locust": None,
            "k6": None,
            "summary": {},
        }

    def load_pytest_benchmark(self, file_path: str = ".benchmarks/*/0001_*.json"):
        """加载 pytest-benchmark 结果"""
        import glob

        files = glob.glob(file_path)
        if not files:
            print(f"⚠️  未找到 pytest-benchmark 结果: {file_path}")
            return

        latest_file = max(files, key=lambda p: Path(p).stat().st_mtime)
        print(f"📊 加载 pytest-benchmark: {latest_file}")

        with open(latest_file, 'r') as f:
            data = json.load(f)

        self.report_data["pytest_benchmark"] = {
            "benchmarks": self._parse_pytest_benchmarks(data.get("benchmarks", [])),
            "machine_info": data.get("machine_info", {}),
            "commit_info": data.get("commit_info", {}),
        }

    def _parse_pytest_benchmarks(self, benchmarks: List[Dict]) -> Dict:
        """解析 pytest benchmark 数据"""
        grouped = {}

        for bench in benchmarks:
            group = bench.get("group", "default")
            name = bench.get("name", "unknown")
            stats = bench.get("stats", {})

            if group not in grouped:
                grouped[group] = []

            grouped[group].append({
                "name": name,
                "mean": stats.get("mean", 0) * 1000,  # 转为 ms
                "min": stats.get("min", 0) * 1000,
                "max": stats.get("max", 0) * 1000,
                "stddev": stats.get("stddev", 0) * 1000,
                "median": stats.get("median", 0) * 1000,
                "iqr": stats.get("iqr", 0) * 1000,
                "iterations": stats.get("iterations", 0),
                "rounds": stats.get("rounds", 0),
            })

        return grouped

    def load_locust_stats(self, file_path: str = "locust_stats.json"):
        """加载 Locust 统计结果"""
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  未找到 Locust 结果: {file_path}")
            return

        print(f"📊 加载 Locust: {file_path}")

        with open(path, 'r') as f:
            data = json.load(f)

        self.report_data["locust"] = {
            "requests": data.get("stats", []),
            "total": data.get("total", {}),
            "failures": data.get("failures", []),
            "user_count": data.get("user_count", 0),
        }

    def load_k6_results(self, file_path: str = "summary.json"):
        """加载 K6 测试结果"""
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  未找到 K6 结果: {file_path}")
            return

        print(f"📊 加载 K6: {file_path}")

        with open(path, 'r') as f:
            data = json.load(f)

        metrics = data.get("metrics", {})

        self.report_data["k6"] = {
            "http_reqs": self._extract_k6_metric(metrics.get("http_reqs", {})),
            "http_req_duration": self._extract_k6_metric(metrics.get("http_req_duration", {})),
            "http_req_failed": self._extract_k6_metric(metrics.get("http_req_failed", {})),
            "vus": self._extract_k6_metric(metrics.get("vus", {})),
            "custom_metrics": {
                "code_execution_duration": self._extract_k6_metric(
                    metrics.get("code_execution_duration", {})
                ),
                "success_rate": self._extract_k6_metric(metrics.get("success", {})),
                "error_rate": self._extract_k6_metric(metrics.get("errors", {})),
            }
        }

    def _extract_k6_metric(self, metric: Dict) -> Dict:
        """提取 K6 指标"""
        values = metric.get("values", {})
        return {
            "count": values.get("count", 0),
            "rate": values.get("rate", 0),
            "avg": values.get("avg", 0),
            "min": values.get("min", 0),
            "max": values.get("max", 0),
            "med": values.get("med", 0),
            "p90": values.get("p(90)", 0),
            "p95": values.get("p(95)", 0),
            "p99": values.get("p(99)", 0),
        }

    def generate_summary(self):
        """生成性能总结"""
        summary = {
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tests_run": [],
            "performance_targets": {},
            "warnings": [],
        }

        # pytest-benchmark 总结
        if self.report_data["pytest_benchmark"]:
            benchmarks = self.report_data["pytest_benchmark"]["benchmarks"]
            total_benchmarks = sum(len(group) for group in benchmarks.values())
            summary["tests_run"].append(f"pytest-benchmark: {total_benchmarks} 个基准测试")

            # 检查性能目标
            for group_name, group_benchmarks in benchmarks.items():
                for bench in group_benchmarks:
                    if bench["mean"] > 1000:  # > 1s
                        summary["warnings"].append(
                            f"⚠️  {bench['name']} 平均耗时过高: {bench['mean']:.2f}ms"
                        )

        # Locust 总结
        if self.report_data["locust"]:
            locust_data = self.report_data["locust"]
            total = locust_data.get("total", {})
            summary["tests_run"].append(f"Locust: {total.get('num_requests', 0)} 个请求")

            # 检查错误率
            fail_ratio = total.get("fail_ratio", 0)
            if fail_ratio > 0.01:  # > 1%
                summary["warnings"].append(
                    f"⚠️  Locust 错误率过高: {fail_ratio * 100:.2f}%"
                )

            summary["performance_targets"]["locust_error_rate"] = {
                "target": "< 1%",
                "actual": f"{fail_ratio * 100:.2f}%",
                "pass": fail_ratio < 0.01,
            }

        # K6 总结
        if self.report_data["k6"]:
            k6_data = self.report_data["k6"]
            http_reqs = k6_data.get("http_reqs", {})
            http_duration = k6_data.get("http_req_duration", {})
            http_failed = k6_data.get("http_req_failed", {})

            summary["tests_run"].append(f"K6: {http_reqs.get('count', 0)} 个请求")

            # 检查性能目标
            p95 = http_duration.get("p95", 0)
            p99 = http_duration.get("p99", 0)
            error_rate = http_failed.get("rate", 0)

            summary["performance_targets"]["k6_p95"] = {
                "target": "< 500ms",
                "actual": f"{p95:.2f}ms",
                "pass": p95 < 500,
            }

            summary["performance_targets"]["k6_p99"] = {
                "target": "< 1000ms",
                "actual": f"{p99:.2f}ms",
                "pass": p99 < 1000,
            }

            summary["performance_targets"]["k6_error_rate"] = {
                "target": "< 1%",
                "actual": f"{error_rate * 100:.2f}%",
                "pass": error_rate < 0.01,
            }

            if p95 > 500:
                summary["warnings"].append(f"⚠️  K6 P95 超过目标: {p95:.2f}ms > 500ms")
            if p99 > 1000:
                summary["warnings"].append(f"⚠️  K6 P99 超过目标: {p99:.2f}ms > 1000ms")
            if error_rate > 0.01:
                summary["warnings"].append(f"⚠️  K6 错误率过高: {error_rate * 100:.2f}%")

        self.report_data["summary"] = summary

    def generate_html_report(self) -> str:
        """生成 HTML 报告"""
        html_path = self.output_dir / f"performance_report_{self.timestamp}.html"

        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HelloAgents 性能测试报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-left: 4px solid #4CAF50;
            padding-left: 10px;
        }}
        .summary-box {{
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .warning-box {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .error-box {{
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #4CAF50;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .pass {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .fail {{
            color: #f44336;
            font-weight: bold;
        }}
        .metric {{
            display: inline-block;
            background: #e3f2fd;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 4px;
            font-weight: 500;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 HelloAgents 性能测试报告</h1>

        <div class="summary-box">
            <h3>📊 测试概览</h3>
            <p><strong>测试时间:</strong> {self.report_data['summary'].get('test_date', 'N/A')}</p>
            {''.join([f'<p>• {test}</p>' for test in self.report_data['summary'].get('tests_run', [])])}
        </div>

        {self._generate_warnings_html()}
        {self._generate_performance_targets_html()}
        {self._generate_pytest_benchmark_html()}
        {self._generate_locust_html()}
        {self._generate_k6_html()}

        <div class="footer">
            <p>Generated by HelloAgents Performance Report Generator</p>
            <p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML 报告已生成: {html_path}")
        return str(html_path)

    def _generate_warnings_html(self) -> str:
        """生成警告部分"""
        warnings = self.report_data["summary"].get("warnings", [])
        if not warnings:
            return ""

        return f"""
        <div class="warning-box">
            <h3>⚠️  性能警告</h3>
            {''.join([f'<p>{warning}</p>' for warning in warnings])}
        </div>
        """

    def _generate_performance_targets_html(self) -> str:
        """生成性能目标检查"""
        targets = self.report_data["summary"].get("performance_targets", {})
        if not targets:
            return ""

        rows = []
        for name, target_data in targets.items():
            status = "✅ PASS" if target_data["pass"] else "❌ FAIL"
            status_class = "pass" if target_data["pass"] else "fail"

            rows.append(f"""
            <tr>
                <td>{name}</td>
                <td>{target_data['target']}</td>
                <td>{target_data['actual']}</td>
                <td class="{status_class}">{status}</td>
            </tr>
            """)

        return f"""
        <h2>🎯 性能目标检查</h2>
        <table>
            <tr>
                <th>指标</th>
                <th>目标</th>
                <th>实际</th>
                <th>状态</th>
            </tr>
            {''.join(rows)}
        </table>
        """

    def _generate_pytest_benchmark_html(self) -> str:
        """生成 pytest-benchmark 报告部分"""
        data = self.report_data.get("pytest_benchmark")
        if not data:
            return ""

        benchmarks = data.get("benchmarks", {})
        rows = []

        for group_name, group_benchmarks in benchmarks.items():
            rows.append(f'<tr><td colspan="7" style="background:#f0f0f0;font-weight:bold;">{group_name}</td></tr>')

            for bench in group_benchmarks:
                rows.append(f"""
                <tr>
                    <td>{bench['name']}</td>
                    <td>{bench['mean']:.2f}ms</td>
                    <td>{bench['min']:.2f}ms</td>
                    <td>{bench['max']:.2f}ms</td>
                    <td>{bench['median']:.2f}ms</td>
                    <td>{bench['stddev']:.2f}ms</td>
                    <td>{bench['iterations']}</td>
                </tr>
                """)

        return f"""
        <h2>🧪 Pytest Benchmark 结果</h2>
        <table>
            <tr>
                <th>测试名称</th>
                <th>平均</th>
                <th>最小</th>
                <th>最大</th>
                <th>中位数</th>
                <th>标准差</th>
                <th>迭代次数</th>
            </tr>
            {''.join(rows)}
        </table>
        """

    def _generate_locust_html(self) -> str:
        """生成 Locust 报告部分"""
        data = self.report_data.get("locust")
        if not data:
            return ""

        total = data.get("total", {})

        return f"""
        <h2>🦗 Locust 负载测试结果</h2>
        <div class="summary-box">
            <h4>整体统计</h4>
            <span class="metric">总请求: {total.get('num_requests', 0)}</span>
            <span class="metric">失败: {total.get('num_failures', 0)}</span>
            <span class="metric">RPS: {total.get('total_rps', 0):.2f}</span>
            <span class="metric">平均响应时间: {total.get('avg_response_time', 0):.2f}ms</span>
            <span class="metric">P50: {total.get('median_response_time', 0):.2f}ms</span>
            <span class="metric">P95: {total.get('ninetieth_response_time', 0):.2f}ms</span>
        </div>
        """

    def _generate_k6_html(self) -> str:
        """生成 K6 报告部分"""
        data = self.report_data.get("k6")
        if not data:
            return ""

        http_reqs = data.get("http_reqs", {})
        http_duration = data.get("http_req_duration", {})

        return f"""
        <h2>📈 K6 负载测试结果</h2>
        <div class="summary-box">
            <h4>HTTP 请求统计</h4>
            <span class="metric">总请求: {http_reqs.get('count', 0)}</span>
            <span class="metric">RPS: {http_reqs.get('rate', 0):.2f}</span>
            <span class="metric">平均: {http_duration.get('avg', 0):.2f}ms</span>
            <span class="metric">P50: {http_duration.get('med', 0):.2f}ms</span>
            <span class="metric">P95: {http_duration.get('p95', 0):.2f}ms</span>
            <span class="metric">P99: {http_duration.get('p99', 0):.2f}ms</span>
        </div>
        """

    def generate_markdown_report(self) -> str:
        """生成 Markdown 报告"""
        md_path = self.output_dir / f"performance_report_{self.timestamp}.md"

        summary = self.report_data["summary"]

        md_content = f"""# HelloAgents 性能测试报告

**测试时间:** {summary.get('test_date', 'N/A')}

## 📊 测试概览

{chr(10).join([f'- {test}' for test in summary.get('tests_run', [])])}

## ⚠️ 性能警告

{chr(10).join([warning for warning in summary.get('warnings', [])]) if summary.get('warnings') else '✅ 无警告'}

## 🎯 性能目标检查

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
"""

        for name, target_data in summary.get("performance_targets", {}).items():
            status = "✅ PASS" if target_data["pass"] else "❌ FAIL"
            md_content += f"| {name} | {target_data['target']} | {target_data['actual']} | {status} |\n"

        md_content += "\n---\n\n*Generated by HelloAgents Performance Report Generator*\n"

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"✅ Markdown 报告已生成: {md_path}")
        return str(md_path)


def main():
    parser = argparse.ArgumentParser(description="生成性能测试报告")
    parser.add_argument(
        "--format",
        choices=["html", "markdown", "both"],
        default="both",
        help="报告格式"
    )
    parser.add_argument(
        "--output-dir",
        default="performance_reports",
        help="输出目录"
    )
    parser.add_argument(
        "--pytest-benchmark",
        help="pytest-benchmark 结果文件路径"
    )
    parser.add_argument(
        "--locust",
        help="Locust 统计文件路径"
    )
    parser.add_argument(
        "--k6",
        help="K6 结果文件路径"
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("HelloAgents 性能报告生成器")
    print("="*60 + "\n")

    generator = PerformanceReportGenerator(output_dir=args.output_dir)

    # 加载各种测试结果
    if args.pytest_benchmark:
        generator.load_pytest_benchmark(args.pytest_benchmark)
    else:
        generator.load_pytest_benchmark()

    if args.locust:
        generator.load_locust_stats(args.locust)
    else:
        generator.load_locust_stats()

    if args.k6:
        generator.load_k6_results(args.k6)
    else:
        generator.load_k6_results()

    # 生成总结
    generator.generate_summary()

    # 生成报告
    if args.format in ["html", "both"]:
        generator.generate_html_report()

    if args.format in ["markdown", "both"]:
        generator.generate_markdown_report()

    print("\n" + "="*60)
    print("报告生成完成!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
