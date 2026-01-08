#!/usr/bin/env python3
"""
性能测试环境验证脚本

验证所有性能测试文件和依赖是否正确安装
"""

import sys
import os
from pathlib import Path
import importlib.util

# 颜色输出
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def log_success(msg):
    print(f"{GREEN}✅ {msg}{NC}")


def log_error(msg):
    print(f"{RED}❌ {msg}{NC}")


def log_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{NC}")


def log_info(msg):
    print(f"{BLUE}ℹ️  {msg}{NC}")


def check_python_dependencies():
    """检查 Python 依赖"""
    print("\n" + "="*60)
    print("检查 Python 依赖")
    print("="*60)

    required_packages = {
        'pytest': 'pytest',
        'pytest-benchmark': 'pytest_benchmark',
        'locust': 'locust',
        'faker': 'faker',
        'fastapi': 'fastapi',
        'docker': 'docker',
    }

    all_ok = True

    for package_name, import_name in required_packages.items():
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            log_success(f"{package_name} 已安装")
        else:
            log_error(f"{package_name} 未安装")
            all_ok = False

    if not all_ok:
        log_warning("请运行: pip install -r requirements.txt")

    return all_ok


def check_test_files():
    """检查测试文件"""
    print("\n" + "="*60)
    print("检查测试文件")
    print("="*60)

    test_files = [
        'tests/test_performance_benchmarks.py',
        'tests/test_api_performance.py',
        'locustfile.py',
        'load-test-k6.js',
    ]

    all_ok = True

    for test_file in test_files:
        path = Path(test_file)
        if path.exists():
            size = path.stat().st_size
            log_success(f"{test_file} ({size} bytes)")
        else:
            log_error(f"{test_file} 不存在")
            all_ok = False

    return all_ok


def check_scripts():
    """检查脚本文件"""
    print("\n" + "="*60)
    print("检查脚本文件")
    print("="*60)

    scripts = [
        'scripts/generate_performance_report.py',
        'scripts/run_performance_tests.sh',
    ]

    all_ok = True

    for script in scripts:
        path = Path(script)
        if path.exists():
            is_executable = os.access(path, os.X_OK)
            if is_executable:
                log_success(f"{script} (可执行)")
            else:
                log_warning(f"{script} (不可执行，请运行: chmod +x {script})")
                all_ok = False
        else:
            log_error(f"{script} 不存在")
            all_ok = False

    return all_ok


def check_documentation():
    """检查文档"""
    print("\n" + "="*60)
    print("检查文档")
    print("="*60)

    docs = [
        'PERFORMANCE_TESTING.md',
        'PERFORMANCE_TEST_SUMMARY.md',
    ]

    all_ok = True

    for doc in docs:
        path = Path(doc)
        if path.exists():
            size = path.stat().st_size
            log_success(f"{doc} ({size} bytes)")
        else:
            log_error(f"{doc} 不存在")
            all_ok = False

    return all_ok


def check_external_tools():
    """检查外部工具"""
    print("\n" + "="*60)
    print("检查外部工具")
    print("="*60)

    import subprocess

    # 检查 Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            log_success(f"Docker: {result.stdout.strip()}")
        else:
            log_error("Docker 未正确安装")
    except FileNotFoundError:
        log_warning("Docker 未安装 (部分测试需要 Docker)")

    # 检查 K6
    try:
        result = subprocess.run(['k6', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            log_success(f"K6: {result.stdout.strip()}")
        else:
            log_warning("K6 未正确安装")
    except FileNotFoundError:
        log_warning("K6 未安装 (可选，安装: brew install k6)")


def run_syntax_check():
    """运行语法检查"""
    print("\n" + "="*60)
    print("运行 Python 语法检查")
    print("="*60)

    python_files = [
        'tests/test_performance_benchmarks.py',
        'tests/test_api_performance.py',
        'locustfile.py',
        'scripts/generate_performance_report.py',
    ]

    all_ok = True

    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                compile(f.read(), py_file, 'exec')
            log_success(f"{py_file} 语法正确")
        except SyntaxError as e:
            log_error(f"{py_file} 语法错误: {e}")
            all_ok = False
        except FileNotFoundError:
            log_error(f"{py_file} 文件不存在")
            all_ok = False

    return all_ok


def count_tests():
    """统计测试数量"""
    print("\n" + "="*60)
    print("统计测试数量")
    print("="*60)

    import subprocess

    try:
        # 统计 pytest 测试
        result = subprocess.run(
            ['pytest', '--collect-only', '-q', 'tests/test_performance_benchmarks.py'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # 找到包含测试数量的行
            for line in lines:
                if 'test' in line.lower():
                    log_info(f"test_performance_benchmarks.py: {line}")
                    break
        else:
            log_warning("无法统计测试数量")

        result = subprocess.run(
            ['pytest', '--collect-only', '-q', 'tests/test_api_performance.py'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'test' in line.lower():
                    log_info(f"test_api_performance.py: {line}")
                    break

    except Exception as e:
        log_warning(f"统计测试时出错: {e}")


def print_summary(results):
    """打印总结"""
    print("\n" + "="*60)
    print("验证总结")
    print("="*60)

    all_passed = all(results.values())

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")

    if all_passed:
        print(f"\n{GREEN}🎉 所有检查通过! 性能测试环境已就绪.{NC}")
        print(f"\n{BLUE}快速开始:{NC}")
        print(f"  ./scripts/run_performance_tests.sh quick")
    else:
        print(f"\n{RED}⚠️  部分检查失败，请根据上述提示修复问题.{NC}")
        sys.exit(1)


def main():
    """主函数"""
    print("\n" + "="*60)
    print("HelloAgents 性能测试环境验证")
    print("="*60)

    results = {
        "Python 依赖": check_python_dependencies(),
        "测试文件": check_test_files(),
        "脚本文件": check_scripts(),
        "文档文件": check_documentation(),
        "语法检查": run_syntax_check(),
    }

    check_external_tools()
    count_tests()

    print_summary(results)


if __name__ == "__main__":
    main()
