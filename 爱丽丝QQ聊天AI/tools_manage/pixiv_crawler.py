"""pixiv_crawler.py
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

class PixivCrawler(BaseTool):
    def __init__(self, qq_message_monitor: QQMessageMonitor):
        # QQ消息监控者
        self.qq_message_monitor = qq_message_monitor
        self.name = "pixiv_crawler"
        self.description = "按排名精准下载Pixiv排行榜图片，支持离散排名和连续范围查询，涵盖日/周/月/新人榜及R18模式"
        self.parameters = {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "description": "排行榜类型(默认日榜)：daily-日榜，weekly-周榜，monthly-月榜，rookie-新人榜",
                    "enum": ["daily", "weekly", "monthly", "rookie"]
                },
                "r18": {
                    "type": "boolean",
                    "description": "是否r18，默认false"
                },
                "rank_list": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 500
                    },
                    "description": "需要下载的图片排名列表，支持单张或多张不连续排名。例如：[1]或[1, 51]"
                },
                "rank_range": {
                    "type": "object",
                    "properties": {
                        "rank_start": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 500
                        },
                        "rank_end": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 500
                        }
                    },
                    "required": ["rank_start", "rank_end"],
                    "description": "连续排名范围，连续时优先使用。例如：下载1-10名"
                }
            },
            "required": ["mode", "r18"],
            # 可以满足一个或多个条件（至少要满足一个）
            "anyOf": [
                {"required": ["rank_list"]},
                {"required": ["rank_range"]}
            ]
        }
        # cookie读取
        with open("用户设置/web_data/pixiv_cookies.txt", "r") as f:
            cookie = f.read().strip()
        self.headers = {  # 不带cookie无法爬取r18的数据
            "cookie": cookie,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "referer": "https://www.pixiv.net",
        }
        # 图片保存路径
        self.save_path = "logs/pixiv"
        # 是否r18(必须加cookie)
        self.r18: bool = False
        # 排行模式（daily、weekly、monthly、rookie）
        self.mode:  str = "daily"
        # 默认每日排行榜
        super().__init__(self.name, self.description, self.parameters)

    def execute(self, **kwargs) -> str:
        """
        执行Pixiv图片下载任务
        根据传入的参数下载指定排名的图片并发送到QQ
        """
        # 解析必需参数
        self.mode = kwargs.get("mode", "daily")  # 排行榜类型，默认日榜
        self.r18 = kwargs.get("r18", False)  # 是否R18，默认False
        # 反馈信息(用来累计)
        feedback_information = ""
        # 任务完成的列表、超时的图片、异常的图片
        mission_complete, over_time, error_image = [], [], []

        # 处理连续范围
        if "rank_range" in kwargs:
            rank_range = kwargs["rank_range"]
            rank_start = rank_range.get("rank_start", 1)
            rank_end = rank_range.get("rank_end", rank_start)
            self.list_download_image(rank_start, rank_end, over_time, error_image, mission_complete)

        # 处理离散排名
        if "rank_list" in kwargs:
            rank_list = kwargs["rank_list"]
            # 过滤有效范围（1-500）
            self.scatter_download_image(rank_list, over_time, error_image, mission_complete)

        if mission_complete:
            feedback_information += "完成任务的图片:" + "、".join(str(i) for i in mission_complete) + "。"
        if over_time:
            feedback_information += "超时图片:" + "、".join(str(i) for i in over_time) + "。"
        if error_image:
            feedback_information += "异常图片:" + "、".join(str(i) for i in error_image) + "。"
        print(feedback_information)
        return feedback_information

    def list_download_image(self, rank_start, rank_end, over_time, error_image, mission_complete):
        # 开始页，结束页
        start_page = (rank_start - 1) // 50 + 1
        end_page = (rank_end - 1) // 50 + 1
        # 遍历页码并加载图片
        for page in range(start_page, end_page + 1):
            # 请求 JSON 索引页
            url = f"https://www.pixiv.net/ranking.php?mode={self.mode}{"_r18" if self.r18 else ""}&content=illust&p={page}&format=json"
            responds = requests.get(url=url, headers=self.headers, timeout=10)
            contents = responds.json()["contents"]
            # 确定当前页需要处理的切片范围.如果是起始页，跳过前面的；如果是结束页，截断后面的
            curr_start = (rank_start - 1) % 50 if page == start_page else 0
            curr_end = (rank_end - 1) % 50 + 1 if page == end_page else 50

            target_list = contents[curr_start: curr_end]
            # 遍历下载图片
            for content in target_list:
                try:
                    # 转换原图 URL (逻辑保持你的替换方案)
                    original_url = content["url"].replace("c/480x960/", "").replace("img-master", "img-original").replace(
                        "_master1200", "")
                    # 原图请求
                    responds = requests.get(url=original_url, headers=self.headers, timeout=10)
                    if responds.status_code == 404:
                        # 原图是png，更新请求链接
                        png_url = original_url.replace(".jpg", ".png", 1)
                        # 图片请求
                        responds = requests.get(url=png_url, headers=self.headers, timeout=10)
                    # 保存转换并保存图片
                    with Image.open(io.BytesIO(responds.content)) as img:
                        # 使用pillow实现类型转换
                        img.save(f"{self.save_path}/{self.mode}{content["rank"]}.png", "PNG")
                    # QQ发送图片
                    self.qq_message_monitor.send_image(f"{self.save_path}/{self.mode}{content["rank"]}.png")
                except requests.exceptions.Timeout:
                    over_time.append(content["rank"]); continue
                except requests.exceptions:
                    error_image.append(content["rank"]); continue
                mission_complete.append(content["rank"])

    def scatter_download_image(self, rank_list: list, over_time, error_image, mission_complete):
        for rank in rank_list:
            # 第几页（1页50张画）
            page = (rank - 1) // 50 + 1
            # 该页的具体位置
            position_in_page = (rank - 1) % 50 + 1
            try:
                # 请求url
                url = f"https://www.pixiv.net/ranking.php?mode={self.mode}{"_r18" if self.r18 else ""}&content=illust&p={page}&format=json"

                # 请求拿到json数据
                responds = requests.get(url=url, headers=self.headers, timeout=10)

                # 目标url，但不是原图url（position_in_page - 1是因为下标的原因）
                position_url = responds.json()["contents"][position_in_page - 1]["url"]
                # 原图url
                original_url = position_url.replace("c/480x960/", "").replace("img-master", "img-original").replace(
                    "_master1200", "")
                # 原图请求
                responds = requests.get(url=original_url, headers=self.headers, timeout=10)
                if responds.status_code == 404:
                    # 原图是png，更新请求链接
                    original_png_url = original_url.replace(".jpg", ".png", 1)
                    # 图片请求
                    responds = requests.get(url=original_png_url, headers=self.headers, timeout=10)
                # 保存转换并保存图片
                with Image.open(io.BytesIO(responds.content)) as img:
                    # 使用pillow实现类型转换
                    img.save(f"{self.save_path}/{self.mode}{rank}.png", "PNG")
                # QQ发送图片
                self.qq_message_monitor.send_image(f"{self.save_path}/{self.mode}{rank}.png")
            except requests.exceptions.Timeout:
                over_time.append(rank);  continue
            except requests.exceptions:
                error_image.append(rank);  continue
            mission_complete.append(rank)


