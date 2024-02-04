import sys
import io

def execute_python_code(code: str) -> str:
    # 注意，这是一个不安全的操作，因为用户可以输入任意的Python代码
    # 实际生产中为了安全起见，可以使用docker隔离执行环境

    # 创建一个StringIO对象来捕获输出
    output = io.StringIO()

    # 保存当前的stdout，以便之后可以恢复它
    old_stdout = sys.stdout

    # 重定向stdout到StringIO对象
    sys.stdout = output

    try:
        exec(code)
    finally:
        # 恢复原来的stdout
        sys.stdout = old_stdout

    # 获取从StringIO对象中捕获的输出
    captured_output = output.getvalue()
    return captured_output