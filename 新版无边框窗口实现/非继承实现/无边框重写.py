"""Qt无标题栏界面解决方案（仅限于Windows）
self.setWindowFlag(Qt.WindowType.FramelessWindowHint) 不仅会把标题栏去掉还会把原来的拖拽等功能去掉
我这里将使用win32api去掉标题栏（保留窗口圆角和拖拽等功能）
"""

# 导包
# 官方库
import sys  # 导入系统库
# 第三方包
import win32con, win32gui                                                           # 使用win32api
from PyQt6.QtCore import Qt, QEvent, QPoint                                         # Qt的核心类
from PyQt6.uic import loadUi                                                        # 加载ui文件或ui装py的文件
from PyQt6.QtGui import QIcon, QAction                                              # 图标处理
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget           # 界面处理类
# 自己的包
from resources.Arisu import Ui_Arisu                                                # uic转后py文件
import resources.resources                                                          # 这个必须存在（即使编译器报灰色）

# 可以通过多继承去调用uic转后py文件, Ui_FramelessWindow
class Arisu(QWidget):
# class Arisu(QWidget, Ui_Arisu):
    def __init__(self, class_name = "", title = "", show_system_tray = True):
        """构建一个无标题栏（自定义）的窗口
        class_name : 窗口类名（默认为""）
        title : 窗口标题（默认为""）
        show_system_tray : 是否展示系统托盘（False/True）,默认为True
        """
        super().__init__()
        """参数初始化"""
        self.show_system_tray = show_system_tray  # 接受初始化参数（是否显示系统托盘）
        """加载ui文件（Qt designer的文件）"""
        loadUi("./resources/Arisu.ui", self)  # 运行时动态加载ui文件
        # self.setupUi(self)    # 创建UI实例，为了后续控件的调用
        self.hwnd = int(self.winId())   # 拿到窗口句柄
        """预加载图标资源"""
        # 预加载图标资源
        self.QLogo = QIcon(":/Logo/Logo/256.ico")  # QLogo图标
        self.max_icon = QIcon(":/标题栏/标题栏/最大化.png")  # 需要切换的图标
        self.restore_icon = QIcon(":/标题栏/标题栏/窗口恢复.png")  # 需要切换的图标
        """系统托盘(有个系统托盘按钮需要链接)"""
        self.system_tray = QSystemTrayIcon(self)  # 创建系统托盘(self建立父子关系避免资源泄露)
        self.system_tray.setIcon(self.QLogo)# 设置系统托盘的图标
        self.system_tray.setToolTip(self.SoftwareName.text())     # 设置悬浮提示为软件名
        # 根据初始化参数来决定 隐藏系统托盘 还是 显示系统托盘
        self.system_tray.show() if self.show_system_tray else self.system_tray.hide()
        # 系统托盘菜单
        self.system_tray_menu = QMenu(self)                                 # 创建系统托盘菜单
        self.quit_action = QAction("退出", self)                            # 添加一级菜单动作选项（退出）
        self.quit_action.triggered.connect(self.system_tray_menu_exit)      # 链接动作行为
        self.system_tray_menu.addAction(self.quit_action)                   # 菜单把动作添加进去
        self.system_tray_menu.addSeparator()                              # 添加分隔符
        self.system_tray.setContextMenu(self.system_tray_menu)              # 设置系统托盘上下文菜单
        # 点击托盘触发的操作
        self.system_tray.activated.connect(self.system_tray_click)
        """窗口初始化(无边框和自定义按钮)"""
        self.remove_title_bat()    # 去掉标题栏
        self.setObjectName(class_name)  # 设置窗口类名(无效)
        self.setWindowTitle(title)  # 设置窗口标题
        self.setWindowIcon(self.QLogo)   # 设置窗口图标
        self.move_center_window()   # 移动窗口的屏幕中间
        self.offset = QPoint()  # 记录拖拽位置（重写拖拽）
        self.link_buttons()  # 链接自己的按钮
        self.Logo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # 设置Logo为可穿透(为了能够拖拽)
        self.SoftwareName.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # 设置标题栏名称为可穿透(为了能够拖拽)

    """窗口初始化"""
    def remove_title_bat(self):
        """去掉标题栏"""
        # 直接去标题栏（保留边缘拉伸）
        current_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)           # 拿到当前样式
        new_style = current_style & ~win32con.WS_CAPTION | win32con.WS_THICKFRAME       # 去掉标题栏（直接去掉）和保留窗口边缘拉伸
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, new_style)                # 应用新样式
        # 强制窗口重新绘制
        # SWP_NOMOVE保持窗口当前位置不变，忽略 SetWindowPos 函数中传入的 x 和 y 坐标参数。
        # SWP_NOSIZE保持窗口当前尺寸不变，忽略 SetWindowPos 函数中传入的 cx 和 cy（宽度和高度）参数。
        # SWP_FRAMECHANGED强制窗口重新计算非客户区（Non-Client Area，如标题栏、边框等）
        # WVR_REDRAW    标志确保窗口正确重绘
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP,0, 0, 0, 0,win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED |win32con.WVR_REDRAW)

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

    def link_buttons(self):
        """链接自己写好的按钮"""
        # 最基础的三个控件(关闭、最大化、最小化) + 额外按钮（置顶、系统托盘、隐藏）
        self.close_btn.clicked.connect(QApplication.quit)               # 关闭按钮(这里没有必要链接隐藏的按钮)
        self.max_btn.clicked.connect(self.toggle_maximize)              # 最大化按钮(其实叫toggle_maximize合适，有最大化和恢复功能)
        self.min_btn.clicked.connect(self.showMinimized)                # 最小化按钮
        self.top_btn.clicked.connect(self.switch_top)                   # 窗口置顶按钮
        self.min_system_tray_btn.clicked.connect(self.min_system_tray)  # 最小化到系统托盘按钮
        self.hide_btn.clicked.connect(self.hide_button_function)        # 隐藏窗口按钮(隐藏窗口和系统托盘)

    """系统托盘信号处理"""
    def system_tray_click(self, signal):
        """ 处理托盘图标点击事件 """
        if signal == QSystemTrayIcon.ActivationReason.Trigger:# 点击系统托盘(取名Trigger是因为在不同系统有不同的操作)
            # 是否隐藏系统托盘
            if not self.show_system_tray:   # 初始化时是不展示系统托盘（展示界面，隐藏系统托盘）
                win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED | win32con.WVR_REDRAW)
                self.system_tray.hide()     # 隐藏系统托盘
            # （点击系统托盘的功能）如果窗口最小化或隐藏，则显示
            if self.isMinimized() or not self.isVisible():
                self.showNormal()   # 如果窗口最小化或隐藏了则恢复窗口（show在窗口最小化没用）
            else:
                self.hide()  # 如果窗口已显示，则隐藏
        # elif signal == QSystemTrayIcon.ActivationReason.Context:
        #     print("右键单击")
        # elif signal == QSystemTrayIcon.ActivationReason.DoubleClick:
        #     print("双击")
        # elif signal == QSystemTrayIcon.ActivationReason.MiddleClick:
        #     print("中键单击")

    def system_tray_menu_exit(self):
        """系统托盘退出行为槽函数"""
        # self.hide() # 隐藏托盘窗口
        self.close()    # 关闭窗口释放当前的
        QApplication.exit() # 退出所有程序（释放所有Qt资源）


    """无边框窗口事件重写"""
    def toggle_maximize(self):
        """窗口最大化按钮
        切换窗口最大化状态
        """
        if self.isMaximized():
            self.showNormal()  # 恢复原始大小
        else:
            self.showMaximized()  # 最大化窗口

    def switch_top(self):
        """窗口置顶按钮
        窗口置顶切换
        """
        # 如果窗口置顶了就给他取消置顶
        if win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOPMOST:
            win32gui.SetWindowPos(self.hwnd,win32con.HWND_NOTOPMOST,0, 0, 0, 0,win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        else:   # 如果窗口没有置顶则置顶窗口
            win32gui.SetWindowPos(self.hwnd,win32con.HWND_TOPMOST,0, 0, 0, 0,win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def min_system_tray(self):
        """隐藏到托盘按钮
        窗口最小化到系统托盘
        """
        self.hide()                 # 隐藏窗口
        if not self.system_tray.isVisible():        # 如果系统托盘隐藏则显示系统托盘
            self.system_tray.show()     # 展示系统托盘

    def hide_button_function(self):
        """窗口隐藏按钮
        实现隐藏按钮的功能
        """
        self.hide() # 隐藏窗口
        if not self.show_system_tray:       # 如果创建界面后不想要系统托盘，那么设置属性后隐藏窗口后就也把系统托盘隐藏
            self.system_tray.hide() # 隐藏系统托盘

    def changeEvent(self, event):
        """处理窗口状态改变事件
        处理最大化图标切换
        """
        super().changeEvent(event)  # 继承父类的操作
        # 处理最大化图标切换的问题
        if event.type() == QEvent.Type.WindowStateChange:   # 判断是否为窗口事件（图标改变也算）
            if self.isMaximized():  # 判断是否最大化
                self.max_btn.setIcon(self.restore_icon) # 最大化则修改图标为回复
            else:
                self.max_btn.setIcon(self.max_icon) # 非最大化则修改图标为最大化

    def mousePressEvent(self, event):
        """这里重写窗口拖拽"""
        # 记录鼠标按下的初始位置
        self.offset = event.pos()  # 记录偏移位置
        super().mousePressEvent(event)  # 继承原来的事件

    def mouseMoveEvent(self, event):
        """这里重写窗口拖拽"""
        # 移动窗口位置
        if event.buttons() == Qt.MouseButton.LeftButton:  # 左击
            self.move(self.pos() + event.pos() - self.offset)
        super().mousePressEvent(event)  # 继承原来的事件





if __name__ == "__main__":
    app = QApplication(sys.argv)  # 管理控制事件流和设置(sys.argv控制台接收参数)
    # QApplication.processEvents()  # 强制Qt处理事件队列
    window = Arisu("1", "2", False)

    window.show()

    sys.exit(app.exec())  # 安全退出界面任务

