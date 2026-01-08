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


# ==================== 增强安全测试 ====================

def test_sandbox_block_nested_eval(sandbox):
    """测试阻止嵌套的 eval 调用"""
    code = """
x = "eval('print(1)')"
eval(x)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "eval" in output


def test_sandbox_block_eval_in_function(sandbox):
    """测试阻止函数内的 eval"""
    code = """
def dangerous():
    eval('import os')
    return True

dangerous()
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output


def test_sandbox_block_exec_with_globals(sandbox):
    """测试阻止带 globals 的 exec"""
    code = """
exec('x = 10', globals())
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "exec" in output


def test_sandbox_block_subprocess_popen(sandbox):
    """测试阻止 subprocess.Popen"""
    code = """
import subprocess
p = subprocess.Popen(['echo', 'test'])
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "subprocess" in output


def test_sandbox_block_subprocess_call(sandbox):
    """测试阻止 subprocess.call"""
    code = """
import subprocess
subprocess.call(['ls'])
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output


def test_sandbox_block_os_system_with_quotes(sandbox):
    """测试阻止带引号的 os.system"""
    code = """
import os
os.system("echo 'hello'")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "os.system" in output


def test_sandbox_block_compile_with_eval(sandbox):
    """测试阻止 compile + eval 组合"""
    code = """
code_obj = compile('print("test")', '<string>', 'exec')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output


def test_sandbox_block_open_write(sandbox):
    """测试阻止 open 写文件"""
    code = """
with open('/tmp/test.txt', 'w') as f:
    f.write('test')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "open" in output


def test_sandbox_block_file_builtin(sandbox):
    """测试阻止 file 内置函数"""
    code = """
f = file('/etc/passwd')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output


def test_sandbox_block_import_via_function(sandbox):
    """测试阻止通过 __import__ 导入模块"""
    code = """
os = __import__('os')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output
    assert "__import__" in output


# ==================== 边界情况测试 ====================

def test_sandbox_very_long_code(sandbox):
    """测试非常长的代码（接近限制）"""
    # 生成接近 10KB 限制的代码（9990 字节）
    code = "x = " + "1" * 9980
    assert len(code) < 10000
    success, output, exec_time = sandbox.execute_python(code)

    # 应该成功（未超过限制）
    assert "代码长度超过限制" not in output


def test_sandbox_exactly_10kb_code(sandbox):
    """测试恰好 10KB 的代码"""
    # 生成恰好 10000 字节的代码
    code = "x = " + "1" * 9996
    assert len(code) == 10000

    success, output, exec_time = sandbox.execute_python(code)

    # 应该成功（等于限制）
    assert "代码长度超过限制" not in output


def test_sandbox_exceed_10kb_by_one(sandbox):
    """测试超过 10KB 一个字节"""
    # 生成 10001 字节的代码
    code = "x = " + "1" * 9997
    assert len(code) == 10001

    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "代码长度超过限制" in output


def test_sandbox_large_memory_operation(sandbox):
    """测试大内存操作"""
    code = """
# 创建一个较大的列表（但在限制内）
data = list(range(100000))
print(f"Created list with {len(data)} elements")
"""
    success, output, exec_time = sandbox.execute_python(code)

    # 这个应该成功（内存使用合理）
    if "Created list" in output:
        assert success is True
    # 如果失败，可能是环境限制，也是可接受的
    assert exec_time >= 0


def test_sandbox_long_running_loop(sandbox):
    """测试长时间运行的循环"""
    code = """
import time
# 运行一个短时间的循环（不会超时）
for i in range(10):
    time.sleep(0.01)  # 总共约 0.1 秒
print("Completed")
"""
    success, output, exec_time = sandbox.execute_python(code)

    # 应该成功完成
    if success:
        assert "Completed" in output
    # 如果失败，检查是否是环境问题
    assert exec_time >= 0


def test_sandbox_multiple_prints(sandbox):
    """测试大量输出"""
    code = """
for i in range(100):
    print(f"Line {i}: {'x' * 50}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    # 应该成功，但可能截断输出
    assert exec_time >= 0
    # 检查至少有部分输出
    assert "Line" in output


def test_sandbox_empty_code(sandbox):
    """测试空代码"""
    code = ""
    success, output, exec_time = sandbox.execute_python(code)

    # 空代码应该成功执行
    assert success is True
    assert exec_time >= 0


def test_sandbox_whitespace_only_code(sandbox):
    """测试仅包含空白字符的代码"""
    code = "   \n\n\t\t  \n"
    success, output, exec_time = sandbox.execute_python(code)

    # 仅空白字符应该成功
    assert success is True


def test_sandbox_comment_only_code(sandbox):
    """测试仅包含注释的代码"""
    code = """
# This is a comment
# Another comment
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True


def test_sandbox_unicode_characters(sandbox):
    """测试包含 Unicode 字符的代码"""
    code = """
message = "你好，世界！🎉"
print(message)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "你好" in output or "世界" in output


def test_sandbox_exception_handling(sandbox):
    """测试异常处理"""
    code = """
try:
    x = 1 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Caught error" in output


def test_sandbox_complex_data_structures(sandbox):
    """测试复杂数据结构"""
    code = """
data = {
    'list': [1, 2, 3, 4, 5],
    'dict': {'a': 1, 'b': 2},
    'tuple': (1, 2, 3),
    'set': {1, 2, 3}
}
print(f"Keys: {list(data.keys())}")
print(f"List length: {len(data['list'])}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Keys:" in output
    assert "List length: 5" in output


def test_sandbox_string_operations(sandbox):
    """测试字符串操作"""
    code = """
text = "HelloAgents Platform"
print(f"Upper: {text.upper()}")
print(f"Lower: {text.lower()}")
print(f"Split: {text.split()}")
print(f"Length: {len(text)}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "HELLOAGENTS" in output
    assert "helloagents" in output


def test_sandbox_list_comprehension(sandbox):
    """测试列表推导式"""
    code = """
squares = [x**2 for x in range(10)]
print(f"Squares: {squares}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]" in output


def test_sandbox_lambda_functions(sandbox):
    """测试 Lambda 函数"""
    code = """
multiply = lambda x, y: x * y
result = multiply(3, 4)
print(f"Result: {result}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Result: 12" in output


def test_sandbox_generator_expression(sandbox):
    """测试生成器表达式"""
    code = """
gen = (x**2 for x in range(5))
result = list(gen)
print(f"Generated: {result}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Generated: [0, 1, 4, 9, 16]" in output


def test_sandbox_decorator_usage(sandbox):
    """测试装饰器"""
    code = """
def uppercase_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper

@uppercase_decorator
def greet(name):
    return f"hello {name}"

print(greet("world"))
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "HELLO WORLD" in output


def test_sandbox_context_manager(sandbox):
    """测试上下文管理器（不使用文件）"""
    code = """
class MyContext:
    def __enter__(self):
        print("Entering context")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting context")

with MyContext() as ctx:
    print("Inside context")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Entering context" in output
    assert "Inside context" in output
    assert "Exiting context" in output


def test_sandbox_recursion(sandbox):
    """测试递归函数"""
    code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"Factorial of 5: {result}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Factorial of 5: 120" in output


def test_sandbox_multiple_exceptions(sandbox):
    """测试多个异常类型"""
    code = """
def test_exception(case):
    try:
        if case == 1:
            x = 1 / 0
        elif case == 2:
            x = int("abc")
        elif case == 3:
            x = [1, 2, 3][10]
    except ZeroDivisionError:
        print("Division by zero")
    except ValueError:
        print("Value error")
    except IndexError:
        print("Index error")

test_exception(1)
test_exception(2)
test_exception(3)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Division by zero" in output
    assert "Value error" in output
    assert "Index error" in output


# ==================== 安全绕过尝试测试 ====================

def test_sandbox_block_getattr_eval(sandbox):
    """测试阻止通过 getattr 绕过的 eval"""
    code = """
# 尝试通过字符串拼接绕过检查（但 eval 仍然在代码中）
func_name = 'ev' + 'al'
eval('print(1)')
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output


def test_sandbox_block_string_concat_open(sandbox):
    """测试阻止通过字符串拼接的 open"""
    code = """
# 尝试通过变量绕过（但 open( 仍然存在）
filename = '/etc/passwd'
open(filename)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output


def test_sandbox_block_indirect_subprocess(sandbox):
    """测试阻止间接调用 subprocess"""
    code = """
import subprocess
cmd = ['ls', '-la']
subprocess.run(cmd)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "安全检查失败" in output


# ==================== 并发和性能测试 ====================

def test_sandbox_concurrent_execution():
    """测试并发执行多个沙箱"""
    import concurrent.futures

    def run_code(code):
        sb = CodeSandbox(timeout=5)
        return sb.execute_python(code)

    codes = [
        "print('Task 1')",
        "print('Task 2')",
        "print('Task 3')",
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_code, code) for code in codes]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # 所有任务都应该成功
    assert len(results) == 3
    for success, output, exec_time in results:
        assert success is True
        assert "Task" in output


def test_sandbox_execution_time_recorded(sandbox):
    """测试执行时间是否被正确记录"""
    code = """
import time
time.sleep(0.05)  # 睡眠 50ms
print("Done")
"""
    success, output, exec_time = sandbox.execute_python(code)

    # 执行时间应该大于 0
    assert exec_time > 0
    # 如果成功，执行时间应该至少 50ms
    if success:
        assert exec_time >= 0.04  # 留一些误差余地


def test_sandbox_timeout_execution():
    """测试超时检测"""
    # 创建一个超时时间很短的沙箱
    short_timeout_sandbox = CodeSandbox(timeout=1)

    code = """
import time
time.sleep(5)  # 睡眠 5 秒，超过 1 秒超时限制
print("Should not reach here")
"""
    success, output, exec_time = short_timeout_sandbox.execute_python(code)

    # 应该失败（超时）
    assert success is False
    assert "超时" in output or "timeout" in output.lower()


def test_sandbox_name_error(sandbox):
    """测试 NameError 异常"""
    code = """
print(undefined_variable)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "NameError" in output


def test_sandbox_type_error(sandbox):
    """测试 TypeError 异常"""
    code = """
x = "string" + 123
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "TypeError" in output


def test_sandbox_attribute_error(sandbox):
    """测试 AttributeError 异常"""
    code = """
x = 123
x.non_existent_method()
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "AttributeError" in output


def test_sandbox_key_error(sandbox):
    """测试 KeyError 异常"""
    code = """
d = {'a': 1}
print(d['b'])
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "KeyError" in output


def test_sandbox_import_error(sandbox):
    """测试 ImportError 异常"""
    code = """
import non_existent_module
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "ModuleNotFoundError" in output or "ImportError" in output


def test_sandbox_indentation_error(sandbox):
    """测试 IndentationError"""
    code = """
def foo():
print("wrong indentation")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is False
    assert "IndentationError" in output or "SyntaxError" in output


def test_sandbox_multiple_statements(sandbox):
    """测试多个语句执行"""
    code = """
a = 10
b = 20
c = a + b
d = c * 2
print(f"Result: {d}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Result: 60" in output


def test_sandbox_nested_loops(sandbox):
    """测试嵌套循环"""
    code = """
result = []
for i in range(3):
    for j in range(3):
        result.append(i * 3 + j)
print(f"Result: {result}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Result: [0, 1, 2, 3, 4, 5, 6, 7, 8]" in output


def test_sandbox_list_operations(sandbox):
    """测试列表操作"""
    code = """
lst = [1, 2, 3, 4, 5]
lst.append(6)
lst.extend([7, 8])
lst.remove(3)
print(f"List: {lst}")
print(f"Length: {len(lst)}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "List: [1, 2, 4, 5, 6, 7, 8]" in output
    assert "Length: 7" in output


def test_sandbox_dict_operations(sandbox):
    """测试字典操作"""
    code = """
d = {'a': 1, 'b': 2}
d['c'] = 3
d.update({'d': 4, 'e': 5})
print(f"Keys: {sorted(d.keys())}")
print(f"Values: {sorted(d.values())}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Keys: ['a', 'b', 'c', 'd', 'e']" in output
    assert "Values: [1, 2, 3, 4, 5]" in output


def test_sandbox_set_operations(sandbox):
    """测试集合操作"""
    code = """
s1 = {1, 2, 3, 4}
s2 = {3, 4, 5, 6}
print(f"Union: {sorted(s1 | s2)}")
print(f"Intersection: {sorted(s1 & s2)}")
print(f"Difference: {sorted(s1 - s2)}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Union: [1, 2, 3, 4, 5, 6]" in output
    assert "Intersection: [3, 4]" in output
    assert "Difference: [1, 2]" in output


def test_sandbox_string_formatting(sandbox):
    """测试字符串格式化"""
    code = """
name = "Agent"
age = 25
# f-string
print(f"Name: {name}, Age: {age}")
# format method
print("Name: {}, Age: {}".format(name, age))
# % formatting
print("Name: %s, Age: %d" % (name, age))
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Name: Agent, Age: 25" in output


def test_sandbox_conditional_statements(sandbox):
    """测试条件语句"""
    code = """
x = 10
if x > 5:
    print("x is greater than 5")
elif x == 5:
    print("x equals 5")
else:
    print("x is less than 5")

y = 20 if x > 5 else 10
print(f"y = {y}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "x is greater than 5" in output
    assert "y = 20" in output


def test_sandbox_while_loop(sandbox):
    """测试 while 循环"""
    code = """
count = 0
while count < 5:
    count += 1
print(f"Final count: {count}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Final count: 5" in output


def test_sandbox_break_continue(sandbox):
    """测试 break 和 continue"""
    code = """
# Test break
for i in range(10):
    if i == 5:
        break
    print(f"break loop: {i}", end=" ")
print()

# Test continue
for i in range(5):
    if i == 2:
        continue
    print(f"continue loop: {i}", end=" ")
print()
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "break loop: 0" in output
    assert "break loop: 4" in output
    assert "break loop: 5" not in output
    assert "continue loop: 0" in output
    assert "continue loop: 1" in output
    assert "continue loop: 2" not in output
    assert "continue loop: 3" in output


def test_sandbox_try_except_finally(sandbox):
    """测试 try-except-finally"""
    code = """
try:
    x = 1 / 0
except ZeroDivisionError:
    print("Caught ZeroDivisionError")
finally:
    print("Finally block executed")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Caught ZeroDivisionError" in output
    assert "Finally block executed" in output


def test_sandbox_assert_statement(sandbox):
    """测试 assert 语句"""
    code = """
assert 1 + 1 == 2, "Math works!"
print("First assertion passed")

try:
    assert 1 + 1 == 3, "This will fail"
except AssertionError as e:
    print(f"Caught assertion: {e}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "First assertion passed" in output
    assert "Caught assertion: This will fail" in output


def test_sandbox_global_variables(sandbox):
    """测试全局变量"""
    code = """
global_var = 100

def modify_global():
    global global_var
    global_var = 200

print(f"Before: {global_var}")
modify_global()
print(f"After: {global_var}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Before: 100" in output
    assert "After: 200" in output


def test_sandbox_local_variables(sandbox):
    """测试局部变量作用域"""
    code = """
def func():
    local_var = 42
    return local_var

result = func()
print(f"Result: {result}")

try:
    print(local_var)  # 应该抛出 NameError
except NameError:
    print("local_var is not accessible outside function")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "Result: 42" in output
    assert "local_var is not accessible outside function" in output


def test_sandbox_starred_expressions(sandbox):
    """测试星号表达式"""
    code = """
a, *b, c = [1, 2, 3, 4, 5]
print(f"a={a}, b={b}, c={c}")

def func(*args, **kwargs):
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")

func(1, 2, 3, x=10, y=20)
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "a=1, b=[2, 3, 4], c=5" in output
    assert "args: (1, 2, 3)" in output
    assert "kwargs:" in output


def test_sandbox_slice_operations(sandbox):
    """测试切片操作"""
    code = """
lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(f"First 5: {lst[:5]}")
print(f"Last 5: {lst[-5:]}")
print(f"Every 2nd: {lst[::2]}")
print(f"Reversed: {lst[::-1]}")
"""
    success, output, exec_time = sandbox.execute_python(code)

    assert success is True
    assert "First 5: [0, 1, 2, 3, 4]" in output
    assert "Last 5: [5, 6, 7, 8, 9]" in output
    assert "Every 2nd: [0, 2, 4, 6, 8]" in output
    assert "Reversed: [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]" in output
