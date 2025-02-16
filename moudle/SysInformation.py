# 这个库是用来获取系统信息（windows）的
# 导包
import sys  # 系统包
# win32api（提供系统接口）、win32gui（图形界面操作）、win32print（打印和设备上下文相关功能）
import win32con, win32api, win32gui, win32print

def get_operating_system():
    """
    获得当前是什么操作系统
    返回值： operating_system
    不会返回“不知道”、“空”、“假”的值，基于操作系统的标识符返回的
    如果系统完全未知或未被 Python 支持，返回值可能由底层 C 库的 uname 或其他系统调用决定，例如返回操作系统内核的名称
    """
    operating_system = sys.platform     # 使用sys的库来获得当前操作系统
    if operating_system == "win32":
        operating_system = "Windows"
    if operating_system == "linux":
        operating_system = "Linux"
    if operating_system == "darwin":
        operating_system = "macOS"
    if operating_system == "cygwin":
        operating_system = "Cygwin"
    if operating_system == "aix":
        operating_system = "IBM AIX"
    if operating_system == "freebsd":
        operating_system = "FreeBSD"
    return operating_system

def get_screen_resolution():
    """获得主显示器屏幕的当前分辨率、实际分辨率、可用分辨率、桌面窗口的设备上下文句柄
    当前的分辨率是经过缩放后的，鼠标最大位置受限当前分辨率。实际实际分辨率是缩放的100%的分辨率
    返回值
    screen_x : 屏幕x的当前分辨率
    screen_y : 屏幕y的当前分辨率
    real_screen_x : 屏幕x的实际分辨率
    real_screen_y : 屏幕y的实际分辨率
    available_screen_x : 屏幕x的可用分辨率（不包括菜单栏）
    available_screen_y : 屏幕y的可用分辨率（不包括菜单栏）
    HDC : 桌面窗口的设备上下文句柄
    """
    screen_x = win32api.GetSystemMetrics(0)  # 获取当前水平分辨率（缩放后的水平分辨率）
    screen_y = win32api.GetSystemMetrics(1)  # 获取当前垂直分辨率（缩放后的垂直分辨率）
    # 获取真实的分辨率（1.先获取桌面窗口设备上下文的句柄。2.使用GetDeviceCaps获得真实分辨率。3.释放句柄）
    HDC = win32gui.GetDC(0)  # 获取桌面窗口的设备上下文（Device Context, DC）。0 表示桌面窗口的句柄
    if not HDC:
        raise WindowsError("未能成功获取桌面窗口的设备上下文的句柄")
    try:
        real_screen_x = win32print.GetDeviceCaps(HDC, win32con.DESKTOPHORZRES)  # 使用 GetDeviceCaps 查询设备的水平物理分辨率
        real_screen_y = win32print.GetDeviceCaps(HDC, win32con.DESKTOPVERTRES)  # 查询设备的垂直物理分辨率
    except():
        raise WindowsError("未能成功获取主显示器的真实分辨率")
    finally:
        win32gui.ReleaseDC(0, HDC)
    # 获得主显示器的可用分辨率（使用win32api.GetMonitorInfo函数获取当前主显示器的信息）
    # win32con.MONITOR_DEFAULTTOPRIMARY表示获取主显示器，这里0表示获取与窗口关联的显示器
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromWindow(0, win32con.MONITOR_DEFAULTTOPRIMARY))
    # "Work"键的值是一个包含四个整数的元组，表示工作区的坐标：(left, top, right, bottom)
    available_screen_x = monitor_info["Work"][2] - monitor_info["Work"][0]  # 右边界减左边界
    available_screen_y = monitor_info["Work"][3] - monitor_info["Work"][1]  # 下边界减上边界
    return screen_x, screen_y, real_screen_x, real_screen_y, available_screen_x, available_screen_y, HDC

def get_scaling_factor():
    """获得主显示器的缩放比例
    返回值：正常来说任意一个都是都是当前屏幕的缩放百分比
    水平缩放百分比：scaling_factor_x（百分数整型）
    垂直缩放百分比：scaling_factor_y（百分数整型）
    """
    screen_resolution = get_screen_resolution() # 调用函数获得屏幕真实和当前分辨率
    # 计算缩放比例（物理宽 / 缩放宽），四舍五入保留两位小数（如 1.5 表示 150% 缩放）。
    scaling_factor_x = round(screen_resolution[2]/screen_resolution[0], 2)
    scaling_factor_y = round(screen_resolution[3] / screen_resolution[1], 2)
    scaling_factor_x = int(scaling_factor_x * 100) # 转换为百分制整型
    scaling_factor_y = int(scaling_factor_y * 100)  # 转换为百分制整型
    return scaling_factor_x, scaling_factor_y

if __name__ == '__main__':
    get_operating_system()
    get_screen_resolution()
    get_scaling_factor()