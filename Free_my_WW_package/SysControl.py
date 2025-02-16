# 用来对win系统进行控制的
"""
1. 鼠标范围限制（即使程序结束了，效果还在，但是切屏效果就没了）
"""
# 导包
import win32api
import win32con
# 自己的包
from UserFeedback import *  # 用户反馈
from SysInformation import *    # 获取系统信息

def limit_cursor(left = 0, top = 0, right = get_screen_resolution()[4] , bottom = get_screen_resolution()[5], report = True):
    """鼠标光标范围限制（即使程序结束了，效果还在，但是切屏效果就没了）
    填入参数：左、上、右、下、report    (left, top, right, bottom，是否报告)
    默认参数是屏幕可用分辨率（不包括任务栏，算的是逻辑分辨率）
    """
    if report: status_feedback("开始对鼠标光标范围进行限制")
    limit = (left, top, right, bottom)  # 转换为元组类型
    if report: progress_feedback(f"限制范围:{limit}")
    win32api.ClipCursor(limit)
    if report: status_feedback("完成对鼠标光标范围进行限制")

def release_cursor(report = True):
    """解除鼠标光标的范围的限制（当前屏幕的逻辑分辨率）
    参数：report, 填真假，默认开启报告
    """
    if report: status_feedback("开始解除鼠标光标的范围的限制")
    current_mxa_screen_resolution = get_screen_resolution() # 获得屏幕缩放后最大的分辨率（包括任务栏）
    release = (0, 0, current_mxa_screen_resolution[0], current_mxa_screen_resolution[1])    # 转为元组类型
    if report: progress_feedback(f"解除限制范围:{0, 0, current_mxa_screen_resolution[0], current_mxa_screen_resolution[1]}")
    # 因为参数不能为None，否者报错，所以我改为了最适合当前屏幕分辨率的范围
    win32api.ClipCursor(release)
    if report: status_feedback("完成解除鼠标光标的范围的限制")


if __name__ == "__main__":
    # 限制鼠标移动范围
    limit_cursor(report=False)
    # 释放鼠标限制
    release_cursor(False)