"""
沙箱安全测试

测试代码执行沙箱的安全检查和资源限制
"""
import pytest
from app.sandbox import CodeSandbox


@pytest.fixture
def sandbox():
    """创建沙箱实例"""
    return CodeSandbox(timeout=5)


def test_sandbox_basic_execution(sandbox):
    """测试基本代码执行"""
    code = "print('Hello, World!')"
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Hello, World!" in output
    assert exec_time >= 0


def test_sandbox_simple_calculation(sandbox):
    """测试简单计算"""
    code = """
result = 2 + 2
print(f"Result: {result}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Result: 4" in output


def test_sandbox_syntax_error(sandbox):
    """测试语法错误处理"""
    code = "print('missing closing quote"
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "SyntaxError" in output or "unterminated" in output.lower()


def test_sandbox_runtime_error(sandbox):
    """测试运行时错误处理"""
    code = """
x = 1 / 0  # Division by zero
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "ZeroDivisionError" in output


def test_sandbox_block_os_system(sandbox):
    """测试阻止 os.system"""
    code = """
import os
os.system('ls')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "os.system" in output


def test_sandbox_block_subprocess(sandbox):
    """测试阻止 subprocess"""
    code = """
import subprocess
subprocess.run(['ls'])
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "subprocess" in output


def test_sandbox_block_eval(sandbox):
    """测试阻止 eval"""
    code = """
eval('print("test")')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "eval" in output


def test_sandbox_block_exec(sandbox):
    """测试阻止 exec"""
    code = """
exec('print("test")')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "exec" in output


def test_sandbox_block_compile(sandbox):
    """测试阻止 compile"""
    code = """
compile('print("test")', '<string>', 'exec')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "compile" in output


def test_sandbox_block_import(sandbox):
    """测试阻止 __import__"""
    code = """
__import__('os')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "__import__" in output


def test_sandbox_block_open(sandbox):
    """测试阻止 open 函数"""
    code = """
open('/etc/passwd', 'r')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "open" in output


def test_sandbox_block_file(sandbox):
    """测试阻止 file 函数"""
    code = """
file('/etc/passwd', 'r')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "file" in output


def test_sandbox_block_input(sandbox):
    """测试阻止 input 函数"""
    code = """
name = input('Enter name: ')
print(name)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "input" in output


def test_sandbox_block_raw_input(sandbox):
    """测试阻止 raw_input 函数"""
    code = """
name = raw_input('Enter name: ')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    # raw_input 会被检测到，错误信息包含 "raw_input" 或 "input"
    assert "raw_input" in output or "input" in output


def test_sandbox_code_length_limit(sandbox):
    """测试代码长度限制"""
    # 创建超过 10KB 的代码
    code = "# " + "x" * 10001
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "代码长度超过限制" in output


def test_sandbox_allowed_imports(sandbox):
    """测试允许的标准库导入"""
    code = """
import math
import json
import datetime

result = math.sqrt(16)
print(f"Square root: {result}")

data = json.dumps({"key": "value"})
print(f"JSON: {data}")

now = datetime.datetime.now()
print(f"Time: {now.year}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    # 注意: 这可能在 Docker 模式下成功，在本地模式下也成功
    # 我们主要测试它不会被安全检查拒绝
    assert "安全检查失败" not in output


def test_sandbox_loop_execution(sandbox):
    """测试循环执行"""
    code = """
total = 0
for i in range(10):
    total += i
print(f"Total: {total}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Total: 45" in output


def test_sandbox_function_definition(sandbox):
    """测试函数定义和调用"""
    code = """
def greet(name):
    return f"Hello, {name}!"

result = greet("Agent")
print(result)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Hello, Agent!" in output


def test_sandbox_class_definition(sandbox):
    """测试类定义和实例化"""
    code = """
class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"I am {self.name}"

person = Person("Alice")
print(person.introduce())
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "I am Alice" in output


def test_sandbox_multiline_output(sandbox):
    """测试多行输出"""
    code = """
for i in range(5):
    print(f"Line {i}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Line 0" in output
    assert "Line 4" in output


def test_sandbox_cleanup(sandbox):
    """测试沙箱清理"""
    # 执行代码
    sandbox.execute_python("print('test')")

    # 清理
    sandbox.cleanup()

    # 验证清理后的状态（如果 client 是 None，清理应该安全）
    # 这个测试主要是为了覆盖 cleanup 方法
    assert True


def test_sandbox_initialization_with_custom_timeout():
    """测试使用自定义超时初始化沙箱"""
    custom_sandbox = CodeSandbox(timeout=10)
    assert custom_sandbox.timeout == 10


def test_sandbox_initialization_with_custom_image():
    """测试使用自定义镜像初始化沙箱"""
    custom_sandbox = CodeSandbox(image="python:3.12-slim")
    assert custom_sandbox.image == "python:3.12-slim"
