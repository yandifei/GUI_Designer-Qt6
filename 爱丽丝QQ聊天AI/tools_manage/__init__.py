# 内置库
import pathlib
# 顶层封装
from .base_tool import BaseTool
from .tools_register import tools, tools_map    # 必定用到的

# 默认属性
__author__ = "yandifei"
__package__ = "tools_manage"

# 包的路径
package_path = pathlib.Path(__file__).parent    # 这种方式更安全也更现代