"""image_crawler.py
图片搜索，使用requests联网后通过某个图片搜索引擎来搜索图片，可能没有搜索结果。搜索成功后下载单个活多个图片
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
        self.description = "通过1个关键词下载并发送指定数量的图片(优先使用)"
        self.parameters = {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "description": "图片搜索的核心关键词(仅1个)，应准确描述期望的图片内容。"
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
        # 在特定网址上使用关键词搜索图片，这个response是全局使用
        response = get(fr"https://www.yeitu.com/index.php?m=sch&c=index&a=init&typeid=&siteid=1&q={theme}")
        # 正则查找元素看看是否有该图片的资料
        if re.search(r'<ul class="list_box">\s*未找到搜索结果\s*</ul>', response.text):
            return f"关键词`{theme}`未找到搜索结果"
        # 拿到所有搜索结果的链接
        all_search_link = re.findall(r'<h5><a href="(.*?)" target="_blank">', response.text)

        # 有效的搜索链接
        search_link: str = ""
        # 拿到有效的搜索链接，只有所有链接无效或者找到有效链接的时候才退出
        while all_search_link:
            # 拿到列表中随机一个值
            search_link = random.choice(all_search_link)
            # 将这个值从列表中移除
            all_search_link.remove(search_link)
            # 这是一个完整的url
            response = get(fr"{search_link}")
            # 判断这是一个有效的网址（不是进去直接提示没有该网址）
            if re.findall("<h5>提示信息</h5>", response.text):
                continue  # 跳过这个无效网址
            # 检查是否为图片集合网址(检查里面是否有文件)
            try:
                re.search(fr'src="https://file(.*?)"', response.text).group(1)
                break  # 符合条件退出循环
            except AttributeError:
                continue  # 跳过这个仅个人信息介绍的
        else:
            # 没救了，真就给他遍历完所有了
            return f"关键词'{theme}'搜索无结果"

        try:
            # 最大图片数
            max_pic_num = re.search(r'\.\.<a.*?>(?P<page_num>\d+)</a>', response.text).group("page_num")
            max_pic_num = int(max_pic_num)
        except AttributeError:
            # 就只有一张图片，所以检索不到图片
            max_pic_num = 1

        # 下载并发送图片(仅仅发送当前页面集合的最大数量且不得超过目标数量)
        for i in range(min(max_pic_num, quantity)):  # 下标问题
            # 拼接需要爬取图片的源网址（下标从1开始）,拼接路径(核心点，多张图片的实现)
            source_page_url = search_link.replace(".html", f"_{i + 1}.html", 1)
            # 网络请求
            response = get(fr"{source_page_url}")
            # 图片地址
            pic_url = re.search(fr'src="https://file(.*?)"', response.text).group(1)
            pic_url = "https://file" + pic_url  # 拼接图像文件url
            try:
                # 网络请求拿到图片二进制数据后Image转换数据格式为png
                with Image.open(io.BytesIO(get(fr"{pic_url}").content)) as img:
                    img.save("./logs/下载缓存/爬虫图片.png", "PNG")
                # 设置剪切板内容为图片
                self.qq_message_monitor.copy_pic("./logs/下载缓存/爬虫图片.png")  # 处理图片并复制到剪切板
                self.qq_message_monitor.ctrl_v()  # 模拟粘贴操作并发送
            except Timeout:
                print(f"第{i + 1}张图片请求超时")
                request_fail_num += 1 # 失败次数
            except Exception as e:
                # 设置剪切板内容出现异常
                print(f"图片无法发送，出现异常错误:{e}")
                request_fail_num += 1 # 失败次数

            self.qq_message_monitor.send_image("./logs/下载缓存/爬虫图片.png")

        # 当前图链接的片集合20张图片都不够
        if quantity > max_pic_num:
            return f"已发送{max_pic_num}张{theme}图片（已达上限），其中{request_fail_num}张图片请求失败。请再次调用以获取剩余{quantity - max_pic_num}张"
        return f"已发送{theme}图片{max_pic_num - request_fail_num}张，其中{request_fail_num}张图片请求失败"