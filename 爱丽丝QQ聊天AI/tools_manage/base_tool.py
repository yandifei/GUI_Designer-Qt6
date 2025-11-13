"""BaseTool.py
基础工具类，通过被继承属性和重写方法具体实现
与接口一致
"""
# 内置库
from typing import Dict
# 第三方库

# 自己的库


class BaseTool:
    """工具基类定义了通用接口，所有具体工具都继承这个基类并实现相应的方法。"""
    def __init__(self, name: str, description: str, parameters: Dict | None, strict: bool = False):
        """
        工具的参数构造
        :param name: 回调函数的名
        :param description: 函数的描述
        :param parameters: 函数的参数
        :param strict: strict 模式，需要设置 base_url="https://api.deepseek.com/beta" 来开启 Beta 功能
        """
        # 回调函数名
        self.name = name
        # 函数的描述
        self.description = description
        # 函数的参数
        self.parameters = parameters
        # strict 模式，需要设置 base_url="https://api.deepseek.com/beta" 来开启 Beta 功能
        self.strict = strict

    def dict(self) -> Dict:
        """将工具转换为API所需的字典格式"""
        tool_dict = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

        if self.strict:
            tool_dict["function"]["strict"] = True

        return tool_dict

    def execute(self, **kwargs) -> str:
        """
        执行工具的具体功能，子类必须重写这个方法
        返回值必须是字符串，不然AI无法解析
        :param kwargs: 当/多个参数
        :return: 字符串，工具调用结果
        """
        raise NotImplementedError("子类必须实现execute方法")
