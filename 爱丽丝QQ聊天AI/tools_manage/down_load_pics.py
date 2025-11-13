"""down_load_pic.py
图片下载
"""
# 自己的库
from tools_manage.base_tool import BaseTool
from qq_message_monitor import QQMessageMonitor


class DownLoadPics(BaseTool):
    def __init__(self, qq_message_monitor: QQMessageMonitor):
        # QQ消息监控者
        self.qq_message_monitor = qq_message_monitor
        self.name = "down_load_pics"
        self.description = "获取预设的女性主题图片，可选：" + "、".join(name for name in self.qq_message_monitor.picture_map.keys())
        self.parameters = {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "description": "快速获取预设的女性主题图片：" + "、".join(name for name in self.qq_message_monitor.picture_map.keys()),
                    "enum": list(self.qq_message_monitor.picture_map.keys())  # 明确列出所有可选值
                },
                "quantity": {
                    "type": "integer",
                    "description": "图片数量：0=确认能力，默认3",
                    "minimum": 0,  # 最小值为0
                    "maximum": 20  # 最大值为20
                }
            },
            "required": ["theme", "quantity"]
        }
        super().__init__(self.name, self.description, self.parameters)

    def execute(self, **kwargs) -> str:
        # 从 kwargs 字典中获取 'theme' 参数的值
        theme = kwargs.get('theme')
        quantity = kwargs.get('quantity')
        # 检查参数有效性
        if not theme or not isinstance(theme, str):
            return "错误：请提供有效的图片主题参数。"
        # 检查主题是否存在
        if theme not in self.qq_message_monitor.picture_map:
            return f"没有找到主题为 '{theme}' 的图片。"
        for i in range(quantity):
            # 只有通过所有检查后才执行下载
            # 下载图片（这里这么做是为了分离消息发送）
            self.qq_message_monitor.send_url_image(self.qq_message_monitor.picture_map[theme])
        return f"已发送{quantity}张{theme}主题的图片"
# """down_load_pic.py
# 图片下载
# """
# import io
# import json
#
# import requests
# from PIL import Image               # 图片格式转换处理(pip install Pillow)
#
# from tools_manage.base_tool import BaseTool
#
#
# class DownLoadPic(BaseTool):
#     def __init__(self):
#         # 这个必须优于get_description存在
#         self.picture_map = dict()  # 图片映射表
#         self.picture_map_read()  # 录入图片映射表数据
#         self.name = "down_load_pic"
#         self.description = self.get_description()
#         self.parameters = {
#             "type": "object",
#             "properties": {
#                 "theme": {
#                     "type": "string",
#                     "description": "选择其中一个图片主题：" + "、".join(name for name in self.picture_map.keys()),
#                 }
#             },
#             "required": ["theme"]
#         }
#         super().__init__(self.name, self.description, self.parameters)
#         # 请求超时时间
#         self.requests_timeout = 10
#         # 请求头构造
#         self.headers = {
#             "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
#             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#             "accept-encoding": "gzip, deflate, br, zstd",
#             "accept-language": "zh-CN,zh;q=0.9",
#         }
#
#     def get_description(self):
#         return "发送一张图片，图片主题：" + "、".join(name for name in self.picture_map.keys())
#
#     def download_image(self,url):
#         """下载图片
#         url : 图片接口
#         https://t.alcy.cc/moe   # 二次元萌图
#         https://v2.xxapi.cn/api/baisi?return=302   # 三次元白丝
#         https://v2.xxapi.cn/api/heisi?return=302   # 三次元黑丝
#         """
#         try:
#             # 请求超过10秒为超时
#             with Image.open(io.BytesIO(requests.get(url, headers=self.headers, timeout=self.requests_timeout).content)) as img:
#                 img.save("网页请求图片.png", "PNG")
#         except Exception as e:
#             self.output_text = f"图片下载失败，出现异常错误:{e}"
#
#     def picture_map_read(self):
#         """图片映射表读取"""
#         try:
#             with open("用户设置/关键词回复/图片映射表.json", "r", encoding="utf-8") as json_file:
#             # with open("../用户设置/关键词回复/图片映射表.json", "r", encoding="utf-8") as json_file:
#                 self.picture_map = json.load(json_file)  # 监测指定的人和关键字
#         except json.JSONDecodeError as e:
#             print(f"\033[91m图片映射表.json 文件的格式错误或json没有任何内容\033[0m")
#             return False
#         return True
#
#     def execute(self, **kwargs) -> str:
#         # 从 kwargs 字典中获取 'theme' 参数的值
#         theme = kwargs.get('theme')
#         # 检查参数有效性
#         if not theme or not isinstance(theme, str):
#             return "错误：请提供有效的图片主题参数。"
#         # 检查主题是否存在
#         if theme not in self.picture_map:
#             return f"没有找到主题为 '{theme}' 的图片。"
#         # 只有通过所有检查后才执行下载
#         self.download_image(self.picture_map[theme])
#         return f"已发送一张{theme}主题的图片"
#
# if __name__ == '__main__':
#     a = DownLoadPic()
#     print(a.picture_map)
#     print(a.description)
