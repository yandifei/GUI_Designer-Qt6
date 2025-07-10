"""Qt无标题栏界面解决方案（仅限于Windows）
self.setWindowFlag(Qt.WindowType.FramelessWindowHint) 不仅会把标题栏去掉还会把原来的拖拽等功能去掉
我这里将使用win32api去掉标题栏（保留窗口圆角和拖拽等功能）
"""

# 导包
import sys  # 导入系统库
from time import sleep  # 睡眠
import win32api, win32con, win32gui, win32print
# 第三方包
from PyQt6.uic import loadUi  # 加载ui文件或ui装py的文件
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
# from PyQt6.QtCore import Qt  # 用来使用Qt.WindowType.FramelessWindowHint
from qframelesswindow import FramelessWindow as FramelessWindowWidget      # 导入FramelessWindow(无窗口类)
# 自己的包
from resources.frameless_window import Ui_FramelessWindow   # uic转后py文件
import resources.resources  # 这个必须存在（即使编译器报灰色）

# 可以通过多继承去调用uic转后py文件, Ui_FramelessWindow
class FramelessWindow(QWidget, Ui_FramelessWindow):
    def __init__(self):
        """构建一个无标题栏（自定义）的窗口"""
        super().__init__()
        """加载ui文件（Qt designer的文件）"""
        loadUi("./resources/Arisu.ui", self)  # 运行时动态加载ui文件
        # self.setupUi(self)    # 创建UI实例，为了后续控件的调用
        self.hwnd = int(self.winId())   # 拿到窗口句柄
        """窗口初始化"""
        self.move_center_window()   # 移动窗口的屏幕中间
        self.remove_title_bar()     # 去掉窗口的标题栏(必须展示窗口后才有句柄)


    """窗口初始化"""
    def move_center_window(self):
        """移动窗口到屏幕中间（支持多窗口）"""
        # 获取当前窗口所在屏幕（支持多显示器）
        screen = QApplication.screenAt(self.pos()) or QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()    # 获得可用的分辨率(逻辑分辨率)
        # 计算居中位置
        x = (screen_rect.width() - self.width()) // 2 + screen_rect.left()
        y = (screen_rect.height() - self.height()) // 2 + screen_rect.top()
        # 设置窗口位置
        self.move(x, y)


    def remove_title_bar(self):
        """去掉标题栏
        WS_MAXIMIZEBOX  最大化
        WS_MINIMIZEBOX  最小化
        WS_THICKFRAME   边缘缩放
        WS_SYSMENU      系统菜单和关闭按钮
        WS_CAPTION      窗口的标题栏区域（效果是包括以上等控件都没了）
        WS_POPUP        无边框
         & ~ 是去除， | 是使用
        """
        # 完全自定义边框方案
        # self.setContentsMargins(0, -100, 0, 0)   # 左、上、右、下
        # 使用win32api直接去标题栏和保留边缘拉伸
        current_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
        new_style = current_style & ~win32con.WS_CAPTION | win32con.WS_THICKFRAME    # 去掉标题栏（直接去掉）和保留窗口边缘拉伸
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, new_style)  # 应用新样式



        # 强制窗口重新绘制
        # SWP_NOMOVE保持窗口当前位置不变，忽略 SetWindowPos 函数中传入的 x 和 y 坐标参数。
        # SWP_NOSIZE保持窗口当前尺寸不变，忽略 SetWindowPos 函数中传入的 cx 和 cy（宽度和高度）参数。
        # SWP_FRAMECHANGED强制窗口重新计算非客户区（Non-Client Area，如标题栏、边框等）
        # WVR_REDRAW    标志确保窗口正确重绘
        win32gui.SetWindowPos(self.hwnd,
                              win32con.HWND_TOP,
                              0, 0, 0, 0,
                              win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE |
                              win32con.SWP_FRAMECHANGED |
                              win32con.WVR_REDRAW)

    """重写拖拽功能"""
    def moveWindow(self):
        win32gui.ReleaseCapture()
        win32api.SendMessage(
            self.hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MOVE + win32con.HTCAPTION, 0
        )



if __name__ == "__main__":
    app = QApplication(sys.argv)  # 管理控制事件流和设置(sys.argv控制台接收参数)
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec())  # 安全退出界面任务
