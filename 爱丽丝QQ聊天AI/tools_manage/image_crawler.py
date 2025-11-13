"""image_crawler.py
图片搜索，使用requests联网后通过某个图片搜索引擎来搜索图片，可能没有搜索结果
"""
import io
import random
import re
# 第三方库
import requests
from PIL import Image
from requests import Timeout

# 自己的库
from tools_manage.base_tool import BaseTool
from qq_message_monitor import QQMessageMonitor

class ImageCrawler(BaseTool):
    def __init__(self, qq_message_monitor: QQMessageMonitor):
        # QQ消息监控者
        self.qq_message_monitor = qq_message_monitor
        self.name = "image_crawler"
        self.description = "搜索任意主题的网络图片"
        self.parameters = {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "description": "搜索网络图片，适用于帅哥、风景、动物、大奶等任意主题"
                },
                "quantity": {
                    "type": "integer",
                    "description": "图片数量",
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
            return "错误：请提供有效的图片关键词参数。"
        if not isinstance(quantity, int):
            return "错误：请提供有效的图片数量参数"

        # 请求失败的次数
        request_fail_num: int = 0

        def get(url: str):  # 网络请求
            return requests.get(url,headers=self.qq_message_monitor.headers,
                                    timeout=self.qq_message_monitor.requests_timeout)
        # 在特定网址上使用关键词搜索图片
        response = get(fr"https://www.yeitu.com/index.php?m=sch&c=index&a=init&typeid=&siteid=1&q={theme}")
        # 正则查找元素看看是否有该图片的资料
        if re.search(r'<ul class="list_box">\s*未找到搜索结果\s*</ul>', response.text):
            return f"关键词`{theme}`未找到搜索结果"
        # 拿到所有搜索结果的链接
        all_search_link = re.findall(r'<h5><a href="(.*?)" target="_blank">', response.text)
        # 有效的搜索链接
        search_link: str
        # 遍历网址
        for i in range(len(all_search_link)):
            # 选取其中的一个随机链接
            search_link = random.choice(all_search_link)
            # 构建请求
            response = get(fr"{search_link}")
            # 判断这是一个有效的网址（不是进去没图片）
            if not re.findall("<h5>提示信息</h5>", response.text):
                break
        else:
            return "这个关键词搜索到的所有链接中的内容都为空"

        try:
            # 最大图片数
            max_pic_num = re.search(r'\.\.<a.*?>(?P<page_num>\d+)</a>', response.text).group("page_num")
        except AttributeError:
            # 就只有一张图片，所以检索不到图片
            max_pic_num = 1

        # 下载并发送图片(仅仅发送当前页面集合的最大数量且不得超过目标数量)
        for i in range(min(quantity, max_pic_num)):
            # 拼接需要爬取图片的源网址，然后爬取pic_url的图片地址数据
            response = get(search_link + f"_{i}")
            # 图片地址
            pic_url = re.search(fr'<img alt=".*?" src="(.*?)".>', response.text).group(1)
            try:
                # 网络请求拿到图片二进制数据后Image转换数据格式为png
                with Image.open(io.BytesIO(get(fr"{pic_url}").content)) as img:
                    img.save("./logs/下载缓存/爬虫图片.png", "PNG")
                # 设置剪切板内容为图片
                self.qq_message_monitor.copy_pic("./logs/下载缓存/爬虫图片.png")  # 处理图片并复制到剪切板
                self.qq_message_monitor.ctrl_v()  # 模拟粘贴操作并发送
            except Timeout:
                print(f"第{i}张图片请求超时")
                request_fail_num += 1 # 失败次数
            except Exception as e:
                # 设置剪切板内容出现异常
                print(f"图片无法发送，出现异常错误:{e}")
                request_fail_num += 1 # 失败次数

            self.qq_message_monitor.send_image("./logs/下载缓存/爬虫图片.png")

        # 当前界面连20张都不够
        if quantity > max_pic_num:
            return f"已发送{max_pic_num}张{theme}图片（已达上限），其中{request_fail_num}张图片请求失败。请再次调用以获取剩余{quantity - max_pic_num}张"
        return f"已发送{theme}图片{max_pic_num - request_fail_num}张，其中{request_fail_num}张图片请求失败"