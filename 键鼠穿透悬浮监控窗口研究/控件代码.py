import os
import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QApplication, QWidget


class MyWin(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("D:\鸣潮脚本\Free-my-WW\Free my WW\Free my WW_UI\穿透悬浮监控窗口\穿透悬浮窗口.ui",           self)  # 创建ui窗口对象(实例)
        # 主窗口属性
        # self.move(0,0)
        """如果要通过字体移动窗口就必须去掉
        Qt.WindowType.WindowTransparentForInput |  # 窗口输入穿透
        """
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 无边框
            Qt.WindowType.WindowTransparentForInput |  # 窗口输入穿透
            Qt.WindowType.WindowStaysOnTopHint  # 保持置顶
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 设置主窗口背景透明
        # 标签属性(不知道什么即使标签窗口不写穿透也全都穿透了)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)  # 标签穿透
        self.label.setStyleSheet("""
                    QLabel {
                        color: white;                /* 文字颜色 */
                        background: transparent;     /* 完全透明背景 */
                        font: bold 24px "Arial";     /* 字体设置 */
                        border: none;                /* 移除边框 */
                    }
                """)
        # === 可选功能：窗口拖动 ===
        self.drag_pos = QPoint()
        """文字区域穿透验证,即使设置 WA_TransparentForMouseEvents，部分系统仍需强制禁用控件的交互："""
        self.label.setEnabled(False)  # 禁用控件交互（保留显示）

    def mousePressEvent(self, event):
        """ 允许通过非文字区域拖动窗口 """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """ 实现拖动逻辑 """
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    def paintEvent(self, event):
        """ 绘制装饰性边框（不影响穿透） """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(255, 255, 255, 30), 2))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)

app = QApplication(sys.argv)
"""高性能渲染模式,启用 OpenGL 加速避免透明窗口卡顿："""
app.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)  # 提升渲染性能

win = MyWin()
win.show()

sys.exit(app.exec())
