"""tools_register.py
工具的注册
遍历tools_manage包里有效的工具
"""
# 内置库
import importlib
from pathlib import Path
# 自己的模块
from qq_message_monitor import QQMessageMonitor

# API工具的参数
tools = []
# 工具映射，工具名映射对应的函数地址
tools_map = {}

def tools_register(qq_message_monitor: QQMessageMonitor):
    # 遍历工具目录的所有文件(条目：文件夹和文件)
    # for entry in Path(tools_manage.package_path).iterdir():
    for entry in Path(__file__).parent.iterdir():
        # 遍历的条目是文件且不是__init__.py和base_tool.py文件，当然也不能是自己
        if entry.is_file() and entry.name not in ("__init__.py", "base_tool.py", "tools_register.py"):
            # 动态导入模块
            tools_manage_module = importlib.import_module(f"tools_manage.{entry.stem}")
            # 模块名转类名(必须是没有.py后缀的文件本体名),分割后每个单词大写且拼接
            class_name = "".join(word.capitalize() for word in entry.stem.split("_"))
            # 工具类
            tool_object = getattr(tools_manage_module, class_name)
            # 创建对象
            to = tool_object(qq_message_monitor)        # 以前是不用传递对象进去的
            # 并调用dict方法拿到构建的字典，把工具参数传递进去
            tools.append(to.dict())
            # 构建函数名(字符串)和函数调用的地址映射
            tools_map[entry.stem] = to.execute # 防止闭包陷阱不加()


# # 遍历工具目录的所有文件(条目：文件夹和文件)
# # for entry in Path(tools_manage.package_path).iterdir():
# for entry in Path(__file__).parent.iterdir():
#     # 遍历的条目是文件且不是__init__.py和base_tool.py文件，当然也不能是自己
#     if entry.is_file() and entry.name not in ("__init__.py", "base_tool.py", "tools_register.py"):
#         # 动态导入模块
#         tools_manage_module = importlib.import_module(f"tools_manage.{entry.stem}")
#         # 模块名转类名(必须是没有.py后缀的文件本体名),分割后每个单词大写且拼接
#         class_name = "".join(word.capitalize() for word in entry.stem.split("_"))
#         # 工具类
#         tool_object = getattr(tools_manage_module, class_name)
#         # 创建对象
#         to = tool_object()
#         # 并调用dict方法拿到构建的字典，把工具参数传递进去
#         tools.append(to.dict())
#         # 构建函数名(字符串)和函数调用的地址映射
#         tools_map[entry.stem] = to.execute # 防止闭包陷阱不加()