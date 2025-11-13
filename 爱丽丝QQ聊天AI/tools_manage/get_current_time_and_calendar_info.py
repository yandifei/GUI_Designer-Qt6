"""get_current_time_and_calendar_info.py
获取现在的年份, 月份, 日期, 小时, 分钟, 秒钟, 毫秒, 星期几, 星期, 秒级时间戳, 毫秒级时间戳,
公历日期, 农历日期, 农历年, 农历月, 农历日, 生肖, 天干地支, 是否为节假日, 节日名称,
是否为国际性节日, 二十四节气
"""
# 内置库
import datetime
from datetime import datetime
# 第三方库
from zhdate import ZhDate
# 自己的库
from tools_manage.base_tool import BaseTool
from qq_message_monitor import QQMessageMonitor

class GetCurrentTimeAndCalendarInfo(BaseTool):
    def __init__(self, qq_message_monitor: QQMessageMonitor):
        self.name = "get_current_time_and_calendar_info"
        self.description = "获取现在的年份, 月份, 日期, 小时, 分钟, 秒钟, 毫秒, 星期几, 星期, 秒级时间戳, 毫秒级时间戳, 公历日期, 农历日期, 农历年, 农历月, 农历日, 生肖, 天干地支, 是否为节假日, 节日名称, 是否为国际性节日, 二十四节气"
        self.parameters = None
        super().__init__(self.name, self.description, self.parameters)

    def execute(self, **kwargs) -> str:
        """
            获取现在的年份, 月份, 日期, 小时, 分钟, 秒钟, 毫秒, 星期几, 星期, 秒级时间戳, 毫秒级时间戳,
            公历日期, 农历日期, 农历年, 农历月, 农历日, 生肖, 天干地支, 是否为节假日, 节日名称, 是否为国际性节日, 二十四节气
            返回: dict: 包含精确时间、农历、节日、时间戳等信息的字典。
            """
        # 获取当前时间
        current_time = datetime.now()

        # 精确时间信息
        exact_time = {
            "年份": current_time.year,
            "月份": current_time.month,
            "日期": current_time.day,
            "小时": current_time.hour,
            "分钟": current_time.minute,
            "秒钟": current_time.second,
            "毫秒": current_time.microsecond // 1000,
            "星期几": current_time.isoweekday(),  # 周一为1, 周日为7
            "星期": current_time.strftime("%A")
        }

        # 时间戳信息
        timestamp = {
            "秒级时间戳": int(current_time.timestamp()),
            "毫秒级时间戳": int(current_time.timestamp() * 1000)
        }

        # 获取农历信息
        lunar_date = ZhDate.from_datetime(current_time)
        lunar_year = lunar_date.lunar_year
        lunar_month = lunar_date.lunar_month
        lunar_day = lunar_date.lunar_day

        # 农历年天干地支计算
        heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        zodiacs = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

        stem_index = (lunar_year - 4) % 10
        branch_index = (lunar_year - 4) % 12
        ganzhi_year = heavenly_stems[stem_index] + earthly_branches[branch_index]
        zodiac = zodiacs[branch_index]

        # 农历月天干地支计算（简化版）
        lunar_month_ganzhi = heavenly_stems[((lunar_year - 4) % 10 * 2 + lunar_month) % 10] + earthly_branches[
            (lunar_month + 1) % 12]

        # 农历日天干地支计算（简化版）
        base_date = datetime(1900, 1, 1)  # 1900年1月1日为甲子日
        days_diff = (current_time.date() - base_date.date()).days
        day_stem_index = (days_diff + 9) % 10  # 调整偏移量
        day_branch_index = (days_diff + 1) % 12  # 调整偏移量
        lunar_day_ganzhi = heavenly_stems[day_stem_index] + earthly_branches[day_branch_index]

        # 完整的农历天干地支
        complete_ganzhi = f"{ganzhi_year}年 {lunar_month_ganzhi}月 {lunar_day_ganzhi}日"

        # 农历月份和日期的中文表示
        lunar_month_chinese = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"][lunar_month - 1]
        lunar_day_chinese = ""
        if lunar_day == 10:
            lunar_day_chinese = "初十"
        elif lunar_day == 20:
            lunar_day_chinese = "二十"
        elif lunar_day == 30:
            lunar_day_chinese = "三十"
        else:
            first_digit = ["初", "十", "廿", "卅"][lunar_day // 10]
            second_digit = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"][lunar_day % 10]
            lunar_day_chinese = first_digit + second_digit

        # 日历信息
        calendar_info = {
            "公历日期": current_time.strftime("%Y年%m月%d日"),
            "农历日期": f"{ganzhi_year}年{lunar_month_chinese}月{lunar_day_chinese}",
            "农历详情": {
                "农历年": ganzhi_year,
                "农历月": f"{lunar_month_chinese}月",
                "农历日": lunar_day_chinese,
                "生肖": zodiac,
                "天干地支": complete_ganzhi
            },
            "二十四节气": "需要额外库支持 (例如: solartime)"
        }

        # 节日信息(检测中国节日信息) - 修正部分
        year, month, day = current_time.year, current_time.month, current_time.day  # 使用 current_time 而不是 datetime.date
        lunar_date_for_festival = ZhDate.from_datetime(current_time)  # 使用 current_time
        lunar_month, lunar_day = lunar_date_for_festival.lunar_month, lunar_date_for_festival.lunar_day

        # 2025年法定节假日（可根据需要更新）
        statutory_holidays_2025 = [
            "2025-01-01",  # 元旦
            "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31",  # 春节
            "2025-04-04",  # 清明节
            "2025-05-01", "2025-05-02",  # 劳动节
            "2025-05-31",  # 端午节
            "2025-10-01", "2025-10-02", "2025-10-03",  # 国庆节
            "2025-10-06",  # 中秋节
        ]

        # 节日名称映射
        festival_name = None
        is_statutory_holiday = False
        is_international = "否"

        date_str = current_time.strftime("%Y-%m-%d")  # 使用 current_time

        # 检查法定节假日
        if date_str in statutory_holidays_2025:
            is_statutory_holiday = True
            if date_str == "2025-01-01":
                festival_name = "元旦"
                is_international = "是"
            elif date_str in ["2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31"]:
                festival_name = "春节"
            elif date_str == "2025-04-04":
                festival_name = "清明节"
            elif date_str in ["2025-05-01", "2025-05-02"]:
                festival_name = "劳动节"
                is_international = "是"
            elif date_str == "2025-05-31":
                festival_name = "端午节"
            elif date_str in ["2025-10-01", "2025-10-02", "2025-10-03"]:
                festival_name = "国庆节"
            elif date_str == "2025-10-06":
                festival_name = "中秋节"

        # 检查非法定节日（公历）
        if not festival_name:
            if (month, day) == (1, 1):
                festival_name = "元旦"
                is_international = "是"
            elif (month, day) == (3, 8):
                festival_name = "国际妇女节"
                is_international = "是"
            elif (month, day) == (5, 1):
                festival_name = "劳动节"
                is_international = "是"
            elif (month, day) == (5, 4):
                festival_name = "五四青年节"
            elif (month, day) == (6, 1):
                festival_name = "国际儿童节"
                is_international = "是"
            elif (month, day) == (8, 1):
                festival_name = "建军节"
            elif (month, day) == (9, 10):
                festival_name = "教师节"
            elif (month, day) == (10, 1):
                festival_name = "国庆节"
            elif (month, day) == (11, 11):
                festival_name = "光棍节"

        # 检查农历节日
        if not festival_name:
            if (lunar_month, lunar_day) == (1, 1):
                festival_name = "春节"
            elif (lunar_month, lunar_day) == (1, 15):
                festival_name = "元宵节"
            elif (lunar_month, lunar_day) == (5, 5):
                festival_name = "端午节"
            elif (lunar_month, lunar_day) == (7, 7):
                festival_name = "七夕节"
            elif (lunar_month, lunar_day) == (8, 15):
                festival_name = "中秋节"
            elif (lunar_month, lunar_day) == (9, 9):
                festival_name = "重阳节"
            elif (lunar_month, lunar_day) == (12, 8):
                festival_name = "腊八节"
            elif lunar_month == 12 and lunar_day >= 23 and lunar_day <= 29:
                # 小年（北方腊月二十三，南方腊月二十四）
                if lunar_day == 23 or lunar_day == 24:
                    festival_name = "小年"

        festival_info = {
            "今日是否为节假日": is_statutory_holiday,
            "节日名称": festival_name if festival_name else "非节假日或未收录的节日",
            "是否为国际性节日": is_international
        }

        return str({
            "精确时间": exact_time,
            "时间戳": timestamp,
            "日历信息": calendar_info,
            "节日信息": festival_info
        })


